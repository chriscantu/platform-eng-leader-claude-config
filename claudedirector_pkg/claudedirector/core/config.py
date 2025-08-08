"""
Centralized configuration management with environment override support
"""

import os
from pathlib import Path
from typing import Optional

try:
    from pydantic import BaseSettings, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback for systems without pydantic
    PYDANTIC_AVAILABLE = False
    BaseSettings = object


class ClaudeDirectorConfig:
    """
    Centralized configuration with environment override support
    Falls back to simple class if pydantic is not available
    """
    
    def __init__(self, **kwargs):
        # Get project root - works from package or legacy location
        current_file = Path(__file__)
        if "claudedirector_pkg" in str(current_file):
            # Running from new package structure
            self.project_root = current_file.parent.parent.parent.parent
        else:
            # Running from legacy structure
            self.project_root = Path.cwd()
        
        # Database settings
        self.database_path = self._get_setting("database_path", str(self.project_root / "memory" / "strategic_memory.db"), **kwargs)
        
        # AI Detection thresholds
        self.stakeholder_auto_create_threshold = self._get_setting("stakeholder_auto_create_threshold", 0.85, **kwargs)
        self.stakeholder_profiling_threshold = self._get_setting("stakeholder_profiling_threshold", 0.65, **kwargs)
        self.task_auto_create_threshold = self._get_setting("task_auto_create_threshold", 0.80, **kwargs)
        self.task_review_threshold = self._get_setting("task_review_threshold", 0.60, **kwargs)
        
        # Performance settings  
        self.cache_ttl_seconds = self._get_setting("cache_ttl_seconds", 3600, **kwargs)
        self.parallel_requests = self._get_setting("parallel_requests", 5, **kwargs)
        self.max_memory_mb = self._get_setting("max_memory_mb", 512, **kwargs)
        
        # Workspace settings
        self.workspace_dir = self._get_setting("workspace_dir", str(self.project_root / "workspace"), **kwargs)
        self.enable_caching = self._get_setting("enable_caching", True, **kwargs)
        
        # Logging settings
        self.log_level = self._get_setting("log_level", "INFO", **kwargs)
        self.enable_debug = self._get_setting("enable_debug", False, **kwargs)
        
        # Schema paths
        self.schema_dir = self.project_root / "memory"
        self.meeting_schema_path = self.schema_dir / "enhanced_schema.sql"
        self.stakeholder_schema_path = self.schema_dir / "stakeholder_engagement_schema.sql"
        self.task_schema_path = self.schema_dir / "task_tracking_schema.sql"
    
    def _get_setting(self, key: str, default, **kwargs):
        """Get setting from kwargs, environment, or default"""
        # 1. Check kwargs (programmatic override)
        if key in kwargs:
            return kwargs[key]
        
        # 2. Check environment variables
        env_key = f"CLAUDEDIRECTOR_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            # Type conversion for common types
            if isinstance(default, bool):
                return env_value.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(default, int):
                try:
                    return int(env_value)
                except ValueError:
                    pass
            elif isinstance(default, float):
                try:
                    return float(env_value)
                except ValueError:
                    pass
            return env_value
        
        # 3. Return default
        return default
    
    @property
    def database_path_obj(self) -> Path:
        """Get database path as Path object"""
        return Path(self.database_path)
    
    @property
    def workspace_path_obj(self) -> Path:
        """Get workspace path as Path object"""
        return Path(self.workspace_dir)
    
    def to_dict(self) -> dict:
        """Export configuration as dictionary"""
        return {
            "database_path": self.database_path,
            "stakeholder_auto_create_threshold": self.stakeholder_auto_create_threshold,
            "stakeholder_profiling_threshold": self.stakeholder_profiling_threshold,
            "task_auto_create_threshold": self.task_auto_create_threshold,
            "task_review_threshold": self.task_review_threshold,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "parallel_requests": self.parallel_requests,
            "max_memory_mb": self.max_memory_mb,
            "workspace_dir": self.workspace_dir,
            "enable_caching": self.enable_caching,
            "log_level": self.log_level,
            "enable_debug": self.enable_debug
        }
    
    def __repr__(self):
        return f"ClaudeDirectorConfig(database_path='{self.database_path}', workspace_dir='{self.workspace_dir}')"


if PYDANTIC_AVAILABLE:
    class PydanticClaudeDirectorConfig(BaseSettings):
        """Pydantic-based configuration with validation (when available)"""
        
        # Database settings
        database_path: str = Field(default="memory/strategic_memory.db", description="Path to SQLite database")
        
        # AI Detection thresholds
        stakeholder_auto_create_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
        stakeholder_profiling_threshold: float = Field(default=0.65, ge=0.0, le=1.0)
        task_auto_create_threshold: float = Field(default=0.80, ge=0.0, le=1.0)
        task_review_threshold: float = Field(default=0.60, ge=0.0, le=1.0)
        
        # Performance settings
        cache_ttl_seconds: int = Field(default=3600, ge=60)
        parallel_requests: int = Field(default=5, ge=1, le=20)
        max_memory_mb: int = Field(default=512, ge=128)
        
        # Workspace settings
        workspace_dir: str = Field(default="workspace", description="Workspace directory path")
        enable_caching: bool = Field(default=True, description="Enable caching")
        
        # Logging settings
        log_level: str = Field(default="INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
        enable_debug: bool = Field(default=False, description="Enable debug mode")
        
        class Config:
            env_prefix = "CLAUDEDIRECTOR_"
            env_file = ".env"
            case_sensitive = False
    
    # Use Pydantic version when available for validation
    def create_config(**kwargs) -> ClaudeDirectorConfig:
        """Create configuration with optional Pydantic validation"""
        if PYDANTIC_AVAILABLE and not kwargs.get('skip_validation', False):
            pydantic_config = PydanticClaudeDirectorConfig(**kwargs)
            return ClaudeDirectorConfig(**pydantic_config.dict())
        else:
            return ClaudeDirectorConfig(**kwargs)
else:
    def create_config(**kwargs) -> ClaudeDirectorConfig:
        """Create configuration (fallback without Pydantic)"""
        return ClaudeDirectorConfig(**kwargs)


# Default configuration instance
default_config = create_config()

def get_config() -> ClaudeDirectorConfig:
    """Get the default configuration instance"""
    return default_config

def update_config(**kwargs) -> ClaudeDirectorConfig:
    """Update default configuration with new values"""
    global default_config
    current_dict = default_config.to_dict()
    current_dict.update(kwargs)
    default_config = create_config(**current_dict)
    return default_config
