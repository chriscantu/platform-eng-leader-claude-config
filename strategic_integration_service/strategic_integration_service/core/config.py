"""Configuration management for the Strategic Integration Service."""

import os
from pathlib import Path
from typing import Optional, Set

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import ConfigurationError


class Settings(BaseSettings):
    """Configuration settings for the Strategic Integration Service.

    Settings are loaded from environment variables, .env files, and configuration files.
    Priority order: environment variables > .env file > config file > defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application settings
    app_name: str = Field(default="Strategic Integration Service", description="Application name")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Jira API configuration
    jira_base_url: str = Field(
        default="https://procoretech.atlassian.net", description="Jira base URL"
    )
    jira_api_token: Optional[str] = Field(
        default=None, description="Jira API token for authentication"
    )
    jira_email: str = Field(
        default="chris.cantu@procore.com", description="Email for Jira authentication"
    )
    jira_timeout: int = Field(default=30, description="Jira API timeout in seconds")
    jira_max_retries: int = Field(default=3, description="Maximum number of API retries")
    jira_retry_backoff: float = Field(default=1.0, description="Retry backoff factor")
    jira_max_results: int = Field(default=200, description="Maximum results per Jira query")

    # UI Foundation team configuration
    ui_foundation_projects: Set[str] = Field(
        default={"WES", "GLB", "HUBS", "FSGD", "UISP", "UIS", "UXI", "PI"},
        description="UI Foundation Jira project keys",
    )

    # L2 Strategic initiative configuration
    l2_division_filter: str = Field(
        default="UI Foundations", description="Division filter for L2 strategic initiatives"
    )
    l2_custom_field_priority: str = Field(
        default="cf[18272]", description="Custom field for L2 initiative priority ordering"
    )

    # Output configuration
    output_base_dir: Path = Field(
        default=Path("workspace/current-initiatives"), description="Base directory for output files"
    )
    report_output_dir: Path = Field(
        default=Path("executive/reports"), description="Directory for generated reports"
    )

    # Security and data protection
    mask_pii: bool = Field(default=True, description="Enable PII masking in outputs")
    encrypt_sensitive_data: bool = Field(default=True, description="Encrypt sensitive data at rest")
    audit_log_enabled: bool = Field(default=True, description="Enable audit logging")

    # Performance settings
    enable_caching: bool = Field(default=True, description="Enable response caching")
    cache_ttl_seconds: int = Field(default=300, description="Cache TTL in seconds")
    parallel_requests: int = Field(default=5, description="Maximum parallel API requests")

    @field_validator("jira_base_url")
    @classmethod
    def validate_jira_url(cls, v: str) -> str:
        """Validate Jira base URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Jira base URL must start with http:// or https://")
        return v.rstrip("/")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @field_validator("output_base_dir", "report_output_dir", mode="before")
    @classmethod
    def validate_path(cls, v) -> Path:
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v

    def validate_configuration(self) -> None:
        """Validate configuration completeness and consistency."""
        errors = []

        # Check required settings for production
        if not self.debug and not self.jira_api_token:
            errors.append("JIRA_API_TOKEN is required in production mode")

        # Check directory permissions
        try:
            self.output_base_dir.mkdir(parents=True, exist_ok=True)
            self.report_output_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            errors.append(f"Cannot create output directories: {e}")

        # Check reasonable values
        if self.jira_timeout <= 0:
            errors.append("jira_timeout must be positive")

        if self.jira_max_retries < 0:
            errors.append("jira_max_retries must be non-negative")

        if self.parallel_requests <= 0:
            errors.append("parallel_requests must be positive")

        if errors:
            raise ConfigurationError("Configuration validation failed", details={"errors": errors})

    @classmethod
    def load_from_file(cls, config_file: Path) -> "Settings":
        """Load settings from a YAML configuration file."""
        import yaml

        if not config_file.exists():
            raise ConfigurationError(f"Configuration file not found: {config_file}")

        try:
            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f)

            return cls(**config_data)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading config file: {e}")

    def get_jira_auth(self) -> tuple[str, str]:
        """Get Jira authentication credentials."""
        if not self.jira_api_token:
            raise AuthenticationError("Jira API token not configured")

        return self.jira_email, self.jira_api_token

    def get_output_path(self, filename: str, subdir: Optional[str] = None) -> Path:
        """Get full output path for a file."""
        base_path = self.output_base_dir
        if subdir:
            base_path = base_path / subdir

        base_path.mkdir(parents=True, exist_ok=True)
        return base_path / filename

    def get_report_path(self, filename: str, subdir: Optional[str] = None) -> Path:
        """Get full report path for a file."""
        base_path = self.report_output_dir
        if subdir:
            base_path = base_path / subdir

        base_path.mkdir(parents=True, exist_ok=True)
        return base_path / filename


# Global settings instance
settings = Settings()
