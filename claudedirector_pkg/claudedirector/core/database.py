"""
Centralized database management with connection pooling and schema management
"""

import sqlite3
import threading
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager

try:
    import structlog
    logger = structlog.get_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .exceptions import DatabaseError
from .config import get_config


class DatabaseManager:
    """
    Centralized database management with connection pooling and schema management
    Thread-safe singleton pattern for consistent database access
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: Optional[str] = None):
        """Thread-safe singleton initialization"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager with optional path override"""
        if self._initialized:
            return
            
        config = get_config()
        self.db_path = Path(db_path) if db_path else config.database_path_obj
        self.config = config
        self._local = threading.local()
        self._schema_versions = {}
        self._initialized = True
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database with basic structure
        self._initialize_database()
        
        logger.info("Database manager initialized", db_path=str(self.db_path))
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get thread-local database connection
        Each thread gets its own connection for thread safety
        """
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            try:
                self._local.connection = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=30.0  # 30 second timeout
                )
                # Enable foreign keys and WAL mode for better performance
                self._local.connection.execute("PRAGMA foreign_keys = ON")
                self._local.connection.execute("PRAGMA journal_mode = WAL")
                self._local.connection.execute("PRAGMA synchronous = NORMAL")
                
            except Exception as e:
                raise DatabaseError(
                    f"Failed to connect to database: {e}",
                    db_path=str(self.db_path)
                )
        
        return self._local.connection
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor with automatic commit/rollback"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise DatabaseError(f"Database operation failed: {e}", db_path=str(self.db_path))
        finally:
            cursor.close()
    
    def _initialize_database(self):
        """Initialize database with basic structure"""
        try:
            with self.get_cursor() as cursor:
                # Create basic metadata table for schema versioning
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS claudedirector_metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Record database initialization
                cursor.execute("""
                    INSERT OR REPLACE INTO claudedirector_metadata (key, value)
                    VALUES ('database_version', '1.0.0')
                """)
                
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {e}", db_path=str(self.db_path))
    
    def ensure_schema(self, schema_name: str, schema_path: Optional[Path] = None) -> bool:
        """
        Ensure specific schema is applied to database
        Returns True if schema was applied, False if already current
        """
        if schema_path is None:
            # Auto-detect schema path based on name
            schema_mapping = {
                'meeting': self.config.meeting_schema_path,
                'stakeholder': self.config.stakeholder_schema_path,
                'task': self.config.task_schema_path
            }
            schema_path = schema_mapping.get(schema_name)
        
        if not schema_path or not schema_path.exists():
            logger.warning("Schema file not found", schema_name=schema_name, schema_path=str(schema_path))
            return False
        
        # Check if schema is already applied
        schema_version_key = f"schema_{schema_name}_version"
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "SELECT value FROM claudedirector_metadata WHERE key = ?",
                    (schema_version_key,)
                )
                result = cursor.fetchone()
                
                # Get file modification time as version
                current_version = str(schema_path.stat().st_mtime)
                
                if result and result[0] == current_version:
                    logger.debug("Schema already current", schema_name=schema_name)
                    return False
                
                # Apply schema
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                
                # Execute schema (may contain multiple statements)
                cursor.executescript(schema_sql)
                
                # Update schema version
                cursor.execute("""
                    INSERT OR REPLACE INTO claudedirector_metadata (key, value)
                    VALUES (?, ?)
                """, (schema_version_key, current_version))
                
                logger.info("Schema applied successfully", schema_name=schema_name)
                return True
                
        except Exception as e:
            raise DatabaseError(
                f"Failed to apply schema '{schema_name}': {e}",
                db_path=str(self.db_path)
            )
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a specific table"""
        try:
            with self.get_cursor() as cursor:
                # Check if table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table_name,))
                
                if not cursor.fetchone():
                    return {"exists": False}
                
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                return {
                    "exists": True,
                    "columns": [
                        {
                            "name": col[1],
                            "type": col[2],
                            "not_null": bool(col[3]),
                            "default": col[4],
                            "primary_key": bool(col[5])
                        }
                        for col in columns
                    ],
                    "row_count": row_count
                }
                
        except Exception as e:
            raise DatabaseError(f"Failed to get table info for '{table_name}': {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        try:
            with self.get_cursor() as cursor:
                # Get all tables
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                # Get stats for each table
                table_stats = {}
                total_rows = 0
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_stats[table] = count
                    total_rows += count
                
                # Get database size
                db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
                
                return {
                    "database_path": str(self.db_path),
                    "database_size_bytes": db_size,
                    "database_size_mb": round(db_size / (1024 * 1024), 2),
                    "total_tables": len(tables),
                    "total_rows": total_rows,
                    "tables": table_stats
                }
                
        except Exception as e:
            raise DatabaseError(f"Failed to get database stats: {e}")
    
    def close(self):
        """Close database connections"""
        try:
            if hasattr(self._local, 'connection') and self._local.connection:
                self._local.connection.close()
                self._local.connection = None
            logger.info("Database connections closed")
        except Exception as e:
            logger.error("Error closing database connections", error=str(e))
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.close()
        except:
            pass


# Convenience functions for backward compatibility
def get_database_manager(db_path: Optional[str] = None) -> DatabaseManager:
    """Get the database manager instance"""
    return DatabaseManager(db_path)

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Get database connection (backward compatibility)"""
    return get_database_manager(db_path).get_connection()
