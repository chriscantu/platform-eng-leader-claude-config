"""
Intelligent caching system with multiple tiers and fallback mechanisms
Quality-centric implementation ensuring reliability over performance
"""

import hashlib
import json
import pickle
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import structlog
    logger = structlog.get_logger()
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    # Try new package structure first
    from ..core.config import get_config
    from ..core.database import get_database_manager
    from ..core.exceptions import ClaudeDirectorError
except ImportError:
    # Fallback for backward compatibility
    class ClaudeDirectorError(Exception):
        pass
    
    class MinimalConfig:
        def __init__(self):
            self.cache_ttl_seconds = 3600
            self.enable_caching = True
            self.database_path = "memory/strategic_memory.db"
    
    def get_config():
        return MinimalConfig()


class CacheManager:
    """
    Multi-tier caching with graceful degradation
    Ensures system continues to function even if caching fails
    """
    
    def __init__(self, config=None, enable_validation: bool = True):
        """
        Initialize cache manager with quality safeguards
        
        Args:
            config: Optional configuration override
            enable_validation: Enable cache validation (default: True)
        """
        self.config = config or get_config()
        self.enable_validation = enable_validation
        self.cache_enabled = self.config.enable_caching
        self.ttl_seconds = self.config.cache_ttl_seconds
        
        # Cache tiers (in order of preference)
        self.memory_cache = {}  # Tier 1: In-memory (fastest)
        self.file_cache_dir = None  # Tier 2: File-based (persistent)
        self.db_cache_available = False  # Tier 3: Database (shared)
        
        # Performance tracking
        self.stats = {
            'hits': {'memory': 0, 'file': 0, 'database': 0},
            'misses': 0,
            'writes': {'memory': 0, 'file': 0, 'database': 0},
            'errors': 0,
            'validation_failures': 0,
            'cache_bypasses': 0
        }
        
        if self.cache_enabled:
            self._initialize_cache_tiers()
        
        logger.info(
            "Cache manager initialized",
            enabled=self.cache_enabled,
            ttl_seconds=self.ttl_seconds,
            tiers_available=self._get_available_tiers(),
            validation_enabled=self.enable_validation
        )
    
    def _initialize_cache_tiers(self):
        """Initialize available cache tiers with error handling"""
        
        # Tier 2: File cache
        try:
            cache_dir = Path(self.config.database_path).parent / "cache"
            cache_dir.mkdir(exist_ok=True)
            self.file_cache_dir = cache_dir
            logger.debug("File cache tier initialized", path=str(cache_dir))
        except Exception as e:
            logger.warning("File cache tier unavailable", error=str(e))
        
        # Tier 3: Database cache
        try:
            db_manager = get_database_manager()
            self._setup_database_cache(db_manager)
            self.db_cache_available = True
            logger.debug("Database cache tier initialized")
        except Exception as e:
            logger.warning("Database cache tier unavailable", error=str(e))
    
    def _setup_database_cache(self, db_manager):
        """Setup database cache table"""
        with db_manager.get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS claudedirector_cache (
                    cache_key TEXT PRIMARY KEY,
                    cache_value BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    cache_type TEXT DEFAULT 'general',
                    hit_count INTEGER DEFAULT 0
                )
            """)
            
            # Create index for efficient cleanup
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_expires 
                ON claudedirector_cache(expires_at)
            """)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache with tier fallback
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        if not self.cache_enabled:
            self.stats['cache_bypasses'] += 1
            return default
        
        cache_key = self._generate_cache_key(key)
        
        try:
            # Tier 1: Memory cache (fastest)
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if self._is_cache_entry_valid(entry):
                    self.stats['hits']['memory'] += 1
                    logger.debug("Cache hit (memory)", key=key)
                    return entry['value']
                else:
                    # Expired, remove from memory
                    del self.memory_cache[cache_key]
            
            # Tier 2: File cache
            if self.file_cache_dir:
                value = self._get_from_file_cache(cache_key)
                if value is not None:
                    # Promote to memory cache
                    self._store_in_memory_cache(cache_key, value)
                    self.stats['hits']['file'] += 1
                    logger.debug("Cache hit (file)", key=key)
                    return value
            
            # Tier 3: Database cache
            if self.db_cache_available:
                value = self._get_from_database_cache(cache_key)
                if value is not None:
                    # Promote to higher tiers
                    self._store_in_memory_cache(cache_key, value)
                    if self.file_cache_dir:
                        self._store_in_file_cache(cache_key, value)
                    self.stats['hits']['database'] += 1
                    logger.debug("Cache hit (database)", key=key)
                    return value
            
            # Cache miss
            self.stats['misses'] += 1
            logger.debug("Cache miss", key=key)
            return default
            
        except Exception as e:
            logger.error("Cache get operation failed", key=key, error=str(e))
            self.stats['errors'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl_override: Optional[int] = None) -> bool:
        """
        Store value in cache across all available tiers
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_override: Optional TTL override in seconds
            
        Returns:
            True if successfully cached, False otherwise
        """
        if not self.cache_enabled:
            self.stats['cache_bypasses'] += 1
            return False
        
        cache_key = self._generate_cache_key(key)
        ttl = ttl_override or self.ttl_seconds
        
        try:
            # Validation: Ensure value is cacheable
            if self.enable_validation and not self._is_value_cacheable(value):
                logger.warning("Value not cacheable", key=key, type=type(value).__name__)
                self.stats['validation_failures'] += 1
                return False
            
            success_count = 0
            
            # Store in all available tiers
            if self._store_in_memory_cache(cache_key, value, ttl):
                self.stats['writes']['memory'] += 1
                success_count += 1
            
            if self.file_cache_dir and self._store_in_file_cache(cache_key, value, ttl):
                self.stats['writes']['file'] += 1
                success_count += 1
            
            if self.db_cache_available and self._store_in_database_cache(cache_key, value, ttl):
                self.stats['writes']['database'] += 1
                success_count += 1
            
            if success_count > 0:
                logger.debug("Cache write successful", key=key, tiers=success_count)
                return True
            else:
                logger.warning("Cache write failed on all tiers", key=key)
                return False
                
        except Exception as e:
            logger.error("Cache set operation failed", key=key, error=str(e))
            self.stats['errors'] += 1
            return False
    
    def _generate_cache_key(self, key: str) -> str:
        """Generate consistent cache key"""
        # Use SHA-256 for consistent, URL-safe keys
        return hashlib.sha256(key.encode('utf-8')).hexdigest()[:32]
    
    def _is_cache_entry_valid(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        return time.time() < entry.get('expires_at', 0)
    
    def _is_value_cacheable(self, value: Any) -> bool:
        """Validate that value can be safely cached"""
        try:
            # Test serialization
            json.dumps(value, default=str)
            return True
        except (TypeError, ValueError):
            try:
                # Try pickle as fallback
                pickle.dumps(value)
                return True
            except:
                return False
    
    def _store_in_memory_cache(self, cache_key: str, value: Any, ttl: int = None) -> bool:
        """Store in memory cache"""
        try:
            ttl = ttl or self.ttl_seconds
            self.memory_cache[cache_key] = {
                'value': value,
                'created_at': time.time(),
                'expires_at': time.time() + ttl
            }
            return True
        except Exception:
            return False
    
    def _store_in_file_cache(self, cache_key: str, value: Any, ttl: int = None) -> bool:
        """Store in file cache"""
        try:
            ttl = ttl or self.ttl_seconds
            cache_file = self.file_cache_dir / f"{cache_key}.cache"
            
            cache_data = {
                'value': value,
                'created_at': time.time(),
                'expires_at': time.time() + ttl
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, default=str)
            
            return True
        except Exception:
            return False
    
    def _store_in_database_cache(self, cache_key: str, value: Any, ttl: int = None) -> bool:
        """Store in database cache"""
        try:
            ttl = ttl or self.ttl_seconds
            expires_at = time.time() + ttl
            
            # Serialize value
            try:
                serialized_value = json.dumps(value, default=str).encode('utf-8')
            except:
                serialized_value = pickle.dumps(value)
            
            db_manager = get_database_manager()
            with db_manager.get_cursor() as cursor:
                cursor.execute("""
                    INSERT OR REPLACE INTO claudedirector_cache 
                    (cache_key, cache_value, expires_at, cache_type)
                    VALUES (?, ?, datetime(?, 'unixepoch'), ?)
                """, (cache_key, serialized_value, expires_at, 'general'))
            
            return True
        except Exception:
            return False
    
    def _get_from_file_cache(self, cache_key: str) -> Any:
        """Get from file cache"""
        try:
            cache_file = self.file_cache_dir / f"{cache_key}.cache"
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            if self._is_cache_entry_valid(cache_data):
                return cache_data['value']
            else:
                # Expired, remove file
                cache_file.unlink(missing_ok=True)
                return None
                
        except Exception:
            return None
    
    def _get_from_database_cache(self, cache_key: str) -> Any:
        """Get from database cache"""
        try:
            db_manager = get_database_manager()
            with db_manager.get_cursor() as cursor:
                cursor.execute("""
                    SELECT cache_value, expires_at FROM claudedirector_cache 
                    WHERE cache_key = ? AND expires_at > datetime('now')
                """, (cache_key,))
                
                result = cursor.fetchone()
                if not result:
                    return None
                
                # Update hit count
                cursor.execute("""
                    UPDATE claudedirector_cache 
                    SET hit_count = hit_count + 1 
                    WHERE cache_key = ?
                """, (cache_key,))
                
                # Deserialize value
                try:
                    return json.loads(result[0].decode('utf-8'))
                except:
                    return pickle.loads(result[0])
                    
        except Exception:
            return None
    
    def cleanup_expired_cache(self) -> Dict[str, int]:
        """Clean up expired cache entries across all tiers"""
        cleanup_stats = {'memory': 0, 'file': 0, 'database': 0}
        
        try:
            # Memory cache cleanup
            current_time = time.time()
            expired_keys = [
                key for key, entry in self.memory_cache.items()
                if not self._is_cache_entry_valid(entry)
            ]
            
            for key in expired_keys:
                del self.memory_cache[key]
                cleanup_stats['memory'] += 1
            
            # File cache cleanup
            if self.file_cache_dir and self.file_cache_dir.exists():
                for cache_file in self.file_cache_dir.glob("*.cache"):
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        if not self._is_cache_entry_valid(cache_data):
                            cache_file.unlink()
                            cleanup_stats['file'] += 1
                    except:
                        # Remove corrupted cache files
                        cache_file.unlink(missing_ok=True)
                        cleanup_stats['file'] += 1
            
            # Database cache cleanup
            if self.db_cache_available:
                db_manager = get_database_manager()
                with db_manager.get_cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM claudedirector_cache 
                        WHERE expires_at < datetime('now')
                    """)
                    cleanup_stats['database'] = cursor.rowcount
            
            logger.info("Cache cleanup completed", **cleanup_stats)
            return cleanup_stats
            
        except Exception as e:
            logger.error("Cache cleanup failed", error=str(e))
            return cleanup_stats
    
    def _get_available_tiers(self) -> List[str]:
        """Get list of available cache tiers"""
        tiers = ['memory']
        
        if self.file_cache_dir:
            tiers.append('file')
        
        if self.db_cache_available:
            tiers.append('database')
        
        return tiers
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_hits = sum(self.stats['hits'].values())
        total_operations = total_hits + self.stats['misses']
        hit_rate = (total_hits / total_operations) if total_operations > 0 else 0
        
        return {
            'enabled': self.cache_enabled,
            'hit_rate': round(hit_rate, 3),
            'total_hits': total_hits,
            'total_misses': self.stats['misses'],
            'total_operations': total_operations,
            'hits_by_tier': self.stats['hits'].copy(),
            'writes_by_tier': self.stats['writes'].copy(),
            'errors': self.stats['errors'],
            'validation_failures': self.stats['validation_failures'],
            'cache_bypasses': self.stats['cache_bypasses'],
            'available_tiers': self._get_available_tiers(),
            'memory_cache_size': len(self.memory_cache),
            'ttl_seconds': self.ttl_seconds
        }


# Backward compatibility functions
def get_cache_manager(config=None) -> CacheManager:
    """Get cache manager instance"""
    return CacheManager(config=config)

def cache_get(key: str, default: Any = None) -> Any:
    """Convenience function for cache get"""
    cache_manager = get_cache_manager()
    return cache_manager.get(key, default)

def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Convenience function for cache set"""
    cache_manager = get_cache_manager()
    return cache_manager.set(key, value, ttl)
