"""
Integration tests for database operations
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest
from claudedirector.core.config import ClaudeDirectorConfig
from claudedirector.core.database import DatabaseManager


class TestDatabaseIntegration:
    """Test database integration across components"""

    def test_database_schema_initialization(self):
        """Test that database schema can be initialized correctly"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            # Initialize database manager
            DatabaseManager._instance = None
            db_manager = DatabaseManager(db_path)

            # Apply some schema
            db_manager.execute_query(
                """
                CREATE TABLE IF NOT EXISTS test_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_type TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Verify table exists
            assert db_manager.table_exists("test_sessions")

            # Test data insertion and retrieval
            db_manager.execute_query(
                "INSERT INTO test_sessions (session_type) VALUES (?)", ("strategic_planning",)
            )

            result = db_manager.execute_query(
                "SELECT session_type FROM test_sessions WHERE session_type = ?",
                ("strategic_planning",),
                fetch_one=True,
            )

            assert result[0] == "strategic_planning"

        finally:
            # Cleanup
            if Path(db_path).exists():
                Path(db_path).unlink()

    def test_config_database_integration(self):
        """Test configuration integration with database"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "integration_test.db"

            # Create config with custom database path
            config = ClaudeDirectorConfig(database_path=str(db_path))

            # Initialize database using config
            DatabaseManager._instance = None
            db_manager = DatabaseManager(config.database_path)

            # Verify database was created at correct location
            assert Path(config.database_path).exists()
            assert str(config.database_path) == str(db_path)

            # Test basic operations
            db_manager.execute_query(
                """
                CREATE TABLE config_test (
                    id INTEGER PRIMARY KEY,
                    setting_name TEXT,
                    setting_value TEXT
                )
            """
            )

            db_manager.execute_query(
                "INSERT INTO config_test (setting_name, setting_value) VALUES (?, ?)",
                ("test_setting", "test_value"),
            )

            result = db_manager.execute_query(
                "SELECT setting_value FROM config_test WHERE setting_name = ?",
                ("test_setting",),
                fetch_one=True,
            )

            assert result[0] == "test_value"

    def test_concurrent_database_access(self):
        """Test concurrent database access patterns"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            # Initialize database
            DatabaseManager._instance = None
            db_manager = DatabaseManager(db_path)

            db_manager.execute_query(
                """
                CREATE TABLE concurrent_test (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT,
                    operation_num INTEGER
                )
            """
            )

            # Simulate concurrent operations
            for thread_id in ["thread_1", "thread_2", "thread_3"]:
                for op_num in range(5):
                    db_manager.execute_query(
                        "INSERT INTO concurrent_test (thread_id, operation_num) VALUES (?, ?)",
                        (thread_id, op_num),
                    )

            # Verify all operations completed
            result = db_manager.execute_query(
                "SELECT COUNT(*) FROM concurrent_test", fetch_one=True
            )

            assert result[0] == 15  # 3 threads * 5 operations each

            # Verify data integrity
            for thread_id in ["thread_1", "thread_2", "thread_3"]:
                count = db_manager.execute_query(
                    "SELECT COUNT(*) FROM concurrent_test WHERE thread_id = ?",
                    (thread_id,),
                    fetch_one=True,
                )
                assert count[0] == 5

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()

    def test_transaction_handling(self):
        """Test database transaction handling"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            DatabaseManager._instance = None
            db_manager = DatabaseManager(db_path)

            db_manager.execute_query(
                """
                CREATE TABLE transaction_test (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT
                )
            """
            )

            # Test successful transaction
            with db_manager.get_connection() as conn:
                conn.execute("INSERT INTO transaction_test (data) VALUES (?)", ("test1",))
                conn.execute("INSERT INTO transaction_test (data) VALUES (?)", ("test2",))
                conn.commit()

            # Verify data was committed
            count = db_manager.execute_query(
                "SELECT COUNT(*) FROM transaction_test", fetch_one=True
            )
            assert count[0] == 2

            # Test rollback on error
            try:
                with db_manager.get_connection() as conn:
                    conn.execute("INSERT INTO transaction_test (data) VALUES (?)", ("test3",))
                    # Force an error
                    conn.execute("INVALID SQL")
                    conn.commit()
            except sqlite3.Error:
                pass  # Expected error

            # Verify rollback occurred (should still be 2 records)
            count = db_manager.execute_query(
                "SELECT COUNT(*) FROM transaction_test", fetch_one=True
            )
            assert count[0] == 2

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()

    def test_database_schema_migration_simulation(self):
        """Test database schema changes/migrations"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            DatabaseManager._instance = None
            db_manager = DatabaseManager(db_path)

            # Create initial schema
            db_manager.execute_query(
                """
                CREATE TABLE migration_test (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            """
            )

            # Insert initial data
            db_manager.execute_query(
                "INSERT INTO migration_test (name) VALUES (?)", ("initial_data",)
            )

            # Simulate schema migration - add new column
            db_manager.execute_query(
                """
                ALTER TABLE migration_test
                ADD COLUMN description TEXT DEFAULT 'default_description'
            """
            )

            # Verify migration worked
            result = db_manager.execute_query(
                "SELECT name, description FROM migration_test WHERE name = ?",
                ("initial_data",),
                fetch_one=True,
            )

            assert result[0] == "initial_data"
            assert result[1] == "default_description"

            # Test that new inserts work with new schema
            db_manager.execute_query(
                "INSERT INTO migration_test (name, description) VALUES (?, ?)",
                ("new_data", "custom_description"),
            )

            count = db_manager.execute_query("SELECT COUNT(*) FROM migration_test", fetch_one=True)
            assert count[0] == 2

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()

    def test_database_backup_and_restore_simulation(self):
        """Test database backup and restore functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_db = Path(temp_dir) / "original.db"
            backup_db = Path(temp_dir) / "backup.db"

            # Create and populate original database
            DatabaseManager._instance = None
            db_manager = DatabaseManager(str(original_db))

            db_manager.execute_query(
                """
                CREATE TABLE backup_test (
                    id INTEGER PRIMARY KEY,
                    data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            test_data = ["item1", "item2", "item3"]
            for item in test_data:
                db_manager.execute_query("INSERT INTO backup_test (data) VALUES (?)", (item,))

            # Simulate backup (copy database file)
            import shutil

            shutil.copy2(original_db, backup_db)

            # Verify backup file exists and has same data
            DatabaseManager._instance = None
            backup_manager = DatabaseManager(str(backup_db))

            backup_data = backup_manager.execute_query(
                "SELECT data FROM backup_test ORDER BY data", fetch_all=True
            )

            assert len(backup_data) == 3
            assert [row[0] for row in backup_data] == sorted(test_data)

            # Verify tables are identical
            original_tables = db_manager.get_tables()
            backup_tables = backup_manager.get_tables()
            assert original_tables == backup_tables
