"""
Integration tests for CLI command functionality
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


class TestCLICommands:
    """Test CLI command integration"""

    def test_claudedirector_help(self):
        """Test that claudedirector help command works"""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; sys.path.insert(0, '.'); from claudedirector import cli; cli.main(['--help'])",
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        assert result.returncode == 0
        assert "ClaudeDirector" in result.stdout or "usage:" in result.stdout

    def test_claudedirector_status(self):
        """Test claudedirector status command"""
        result = subprocess.run(
            ["./claudedirector", "status"], capture_output=True, text=True, cwd=Path.cwd()
        )

        # Should succeed or give informative error
        assert result.returncode in [0, 1]  # May fail if not fully set up
        # Basic validation that it's attempting to run
        assert len(result.stdout) > 0 or len(result.stderr) > 0

    def test_claudedirector_setup_help(self):
        """Test claudedirector setup help"""
        result = subprocess.run(
            ["./claudedirector", "setup", "--help"], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0
        assert "setup" in result.stdout.lower()
        assert "--component" in result.stdout

    def test_claudedirector_alerts_help(self):
        """Test claudedirector alerts help"""
        result = subprocess.run(
            ["./claudedirector", "alerts", "--help"], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0
        assert "alerts" in result.stdout.lower()

    def test_claudedirector_stakeholders_help(self):
        """Test claudedirector stakeholders help"""
        result = subprocess.run(
            ["./claudedirector", "stakeholders", "--help"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        assert result.returncode == 0
        assert "stakeholder" in result.stdout.lower()
        assert "scan" in result.stdout

    def test_claudedirector_tasks_help(self):
        """Test claudedirector tasks help"""
        result = subprocess.run(
            ["./claudedirector", "tasks", "--help"], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0
        assert "task" in result.stdout.lower()
        assert "scan" in result.stdout

    def test_claudedirector_meetings_help(self):
        """Test claudedirector meetings help"""
        result = subprocess.run(
            ["./claudedirector", "meetings", "--help"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        assert result.returncode == 0
        assert "meeting" in result.stdout.lower()
        assert "scan" in result.stdout

    def test_claudedirector_git_help(self):
        """Test claudedirector git help"""
        result = subprocess.run(
            ["./claudedirector", "git", "--help"], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0
        assert "git" in result.stdout.lower()

    @pytest.mark.slow
    def test_claudedirector_setup_verify(self):
        """Test claudedirector setup verification"""
        result = subprocess.run(
            ["./claudedirector", "setup", "--verify"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
            timeout=30,  # Prevent hanging
        )

        # Should either succeed or give clear feedback
        assert result.returncode in [0, 1]
        # Should produce some output
        assert len(result.stdout) > 0 or len(result.stderr) > 0

    def test_invalid_command(self):
        """Test handling of invalid commands"""
        result = subprocess.run(
            ["./claudedirector", "invalid_command"], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode != 0
        assert "invalid" in result.stderr.lower() or "error" in result.stderr.lower()


class TestCLIPackageIntegration:
    """Test CLI integration with the Python package"""

    def test_package_import(self):
        """Test that the package can be imported correctly"""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from claudedirector import ClaudeDirectorConfig; print('SUCCESS')",
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        assert result.returncode == 0
        assert "SUCCESS" in result.stdout

    def test_config_creation_via_package(self):
        """Test configuration creation through package interface"""
        test_script = """
from claudedirector import ClaudeDirectorConfig
config = ClaudeDirectorConfig(enable_caching=False)
print(f"Cache enabled: {config.enable_caching}")
print("CONFIG_SUCCESS")
"""

        result = subprocess.run(
            [sys.executable, "-c", test_script], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0
        assert "Cache enabled: False" in result.stdout
        assert "CONFIG_SUCCESS" in result.stdout

    def test_intelligence_module_import(self):
        """Test importing intelligence modules"""
        test_script = """
try:
    from claudedirector.intelligence import StakeholderIntelligence, TaskIntelligence, MeetingIntelligence
    print("INTELLIGENCE_IMPORT_SUCCESS")
except ImportError as e:
    print(f"IMPORT_ERROR: {e}")
"""

        result = subprocess.run(
            [sys.executable, "-c", test_script], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0
        assert "INTELLIGENCE_IMPORT_SUCCESS" in result.stdout

    def test_database_manager_import(self):
        """Test importing database manager"""
        test_script = """
try:
    from claudedirector.core.database import DatabaseManager
    print("DATABASE_IMPORT_SUCCESS")
except ImportError as e:
    print(f"IMPORT_ERROR: {e}")
"""

        result = subprocess.run(
            [sys.executable, "-c", test_script], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0
        assert "DATABASE_IMPORT_SUCCESS" in result.stdout

    def test_exception_handling_import(self):
        """Test importing exception classes"""
        test_script = """
try:
    from claudedirector.core.exceptions import ClaudeDirectorError, DatabaseError, AIDetectionError
    print("EXCEPTIONS_IMPORT_SUCCESS")
except ImportError as e:
    print(f"IMPORT_ERROR: {e}")
"""

        result = subprocess.run(
            [sys.executable, "-c", test_script], capture_output=True, text=True, cwd=Path.cwd()
        )

        assert result.returncode == 0
        assert "EXCEPTIONS_IMPORT_SUCCESS" in result.stdout
