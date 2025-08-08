"""
Unit tests for configuration management
"""

import os
import tempfile
from pathlib import Path

import pytest
from claudedirector.core.config import ClaudeDirectorConfig


class TestClaudeDirectorConfig:
    """Test configuration management functionality"""

    def test_default_config_creation(self):
        """Test that default configuration is created correctly"""
        config = ClaudeDirectorConfig()

        assert config.stakeholder_auto_create_threshold == 0.85
        assert config.task_auto_create_threshold == 0.80
        assert config.cache_ttl_seconds == 3600
        assert config.parallel_requests == 5
        assert config.max_memory_mb == 512
        assert config.enable_caching is True

    def test_config_with_overrides(self):
        """Test configuration with manual overrides"""
        config = ClaudeDirectorConfig(
            stakeholder_auto_create_threshold=0.95, cache_ttl_seconds=7200, enable_caching=False
        )

        assert config.stakeholder_auto_create_threshold == 0.95
        assert config.cache_ttl_seconds == 7200
        assert config.enable_caching is False
        # Other values should remain default
        assert config.task_auto_create_threshold == 0.80
        assert config.parallel_requests == 5

    def test_environment_override(self):
        """Test that environment variables override defaults"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set environment variables
            os.environ["CLAUDEDIRECTOR_STAKEHOLDER_AUTO_CREATE_THRESHOLD"] = "0.75"
            os.environ["CLAUDEDIRECTOR_DATABASE_PATH"] = str(Path(temp_dir) / "test.db")
            os.environ["CLAUDEDIRECTOR_ENABLE_CACHING"] = "false"

            try:
                config = ClaudeDirectorConfig()

                assert config.stakeholder_auto_create_threshold == 0.75
                assert str(config.database_path) == str(Path(temp_dir) / "test.db")
                assert config.enable_caching is False

            finally:
                # Cleanup environment
                del os.environ["CLAUDEDIRECTOR_STAKEHOLDER_AUTO_CREATE_THRESHOLD"]
                del os.environ["CLAUDEDIRECTOR_DATABASE_PATH"]
                del os.environ["CLAUDEDIRECTOR_ENABLE_CACHING"]

    def test_project_root_detection(self):
        """Test that project root is detected correctly"""
        config = ClaudeDirectorConfig()

        # Should detect a valid project root
        assert config.project_root.exists()
        assert config.project_root.is_dir()

    def test_database_path_construction(self):
        """Test that database path is constructed correctly"""
        config = ClaudeDirectorConfig()

        expected_path = config.project_root / "memory" / "strategic_memory.db"
        assert str(config.database_path) == str(expected_path)

    def test_workspace_path_construction(self):
        """Test that workspace path is constructed correctly"""
        config = ClaudeDirectorConfig()

        expected_path = config.project_root / "workspace"
        assert str(config.workspace_dir) == str(expected_path)

    def test_threshold_validation(self):
        """Test that threshold values are validated properly"""
        # Valid thresholds should work
        config = ClaudeDirectorConfig(
            stakeholder_auto_create_threshold=0.5, task_auto_create_threshold=0.9
        )
        assert config.stakeholder_auto_create_threshold == 0.5
        assert config.task_auto_create_threshold == 0.9

    def test_performance_settings(self):
        """Test performance-related configuration options"""
        config = ClaudeDirectorConfig(
            parallel_requests=10, max_memory_mb=1024, cache_ttl_seconds=1800
        )

        assert config.parallel_requests == 10
        assert config.max_memory_mb == 1024
        assert config.cache_ttl_seconds == 1800
