"""
Test configuration and fixtures for ClaudeDirector
"""

import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # Initialize with basic schema
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """
    )
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace_path = Path(temp_dir)

        # Create basic workspace structure
        (workspace_path / "meeting-prep").mkdir(exist_ok=True)
        (workspace_path / "l2-initiatives.json").touch()

        yield workspace_path


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    from claudedirector.core.config import ClaudeDirectorConfig

    with tempfile.TemporaryDirectory() as temp_dir:
        config = ClaudeDirectorConfig(
            database_path=str(Path(temp_dir) / "test.db"),
            workspace_dir=str(Path(temp_dir) / "workspace"),
            cache_ttl_seconds=60,
            parallel_requests=2,
            max_memory_mb=128,
            enable_caching=False,  # Disable caching for consistent tests
            stakeholder_auto_create_threshold=0.9,
            task_auto_create_threshold=0.9,
        )
        yield config


@pytest.fixture
def sample_meeting_content():
    """Sample meeting content for testing AI detection"""
    return """
    # Weekly 1:1 with Sarah Chen (VP Engineering)

    ## Agenda
    - Q4 Platform roadmap review
    - Team headcount planning
    - Design system adoption metrics

    ## Discussion Points
    - Need to follow up with John Smith on API gateway migration
    - Action: Schedule meeting with DevOps team for scaling discussion
    - Sarah mentioned budget concerns for Q1 hiring

    ## Next Steps
    - [ ] Send roadmap draft to stakeholders by Friday
    - [ ] Review performance metrics with David Kim
    - [ ] Follow up on accessibility audit with Rachel Torres
    """


@pytest.fixture
def sample_stakeholder_data():
    """Sample stakeholder data for testing"""
    return [
        {
            "stakeholder_key": "sarah_chen",
            "display_name": "Sarah Chen",
            "role_title": "VP Engineering",
            "strategic_importance": "critical",
            "optimal_meeting_frequency": "weekly",
        },
        {
            "stakeholder_key": "john_smith",
            "display_name": "John Smith",
            "role_title": "Staff Engineer",
            "strategic_importance": "high",
            "optimal_meeting_frequency": "biweekly",
        },
    ]


@pytest.fixture
def mock_jira_response():
    """Mock Jira API response for testing"""
    return {
        "issues": [
            {
                "key": "PLAT-123",
                "fields": {
                    "summary": "Implement new design system components",
                    "status": {"name": "In Progress"},
                    "priority": {"name": "High"},
                    "assignee": {"displayName": "John Smith"},
                },
            }
        ],
        "total": 1,
    }


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    # Reset any singleton patterns used in the codebase
    from claudedirector.core.database import DatabaseManager

    if hasattr(DatabaseManager, "_instance"):
        DatabaseManager._instance = None

    yield

    # Cleanup after test
    if hasattr(DatabaseManager, "_instance"):
        DatabaseManager._instance = None


@pytest.fixture
def capture_logs():
    """Capture structured logs during testing"""
    logs = []

    def mock_log(event, **kwargs):
        logs.append({"event": event, **kwargs})

    with patch("structlog.get_logger") as mock_logger:
        mock_logger.return_value.info = mock_log
        mock_logger.return_value.warning = mock_log
        mock_logger.return_value.error = mock_log
        mock_logger.return_value.debug = mock_log
        yield logs
