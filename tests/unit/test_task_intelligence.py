"""
Unit tests for task intelligence functionality
"""

from unittest.mock import Mock, patch

import pytest
from claudedirector.core.exceptions import AIDetectionError
from claudedirector.intelligence.task import TaskIntelligence


class TestTaskIntelligence:
    """Test task intelligence AI functionality"""

    def test_initialization_with_config(self, mock_config, temp_db):
        """Test task intelligence initialization with configuration"""
        mock_config.database_path = temp_db

        with patch("claudedirector.intelligence.task.IntelligentTaskDetector"), patch(
            "claudedirector.intelligence.task.StrategicTaskManager"
        ):
            task_ai = TaskIntelligence(config=mock_config)

            assert task_ai.config == mock_config
            assert task_ai.db_path == temp_db

    def test_detect_tasks_in_content(self, mock_config, temp_db, sample_meeting_content):
        """Test task detection in meeting content"""
        mock_config.database_path = temp_db

        mock_detector = Mock()
        mock_detector.detect_tasks_in_content.return_value = [
            {
                "description": "Send roadmap draft to stakeholders by Friday",
                "assigned_to": "self",
                "due_date": "2024-01-15",
                "priority": "high",
                "confidence": 0.9,
            },
            {
                "description": "Schedule meeting with DevOps team",
                "assigned_to": "self",
                "due_date": None,
                "priority": "medium",
                "confidence": 0.8,
            },
        ]

        with patch(
            "claudedirector.intelligence.task.IntelligentTaskDetector", return_value=mock_detector
        ), patch("claudedirector.intelligence.task.StrategicTaskManager"):
            task_ai = TaskIntelligence(config=mock_config)

            context = {"source_path": "meeting-prep/weekly-1on1.md", "category": "meeting_prep"}
            result = task_ai.detect_tasks_in_content(sample_meeting_content, context)

            assert len(result) == 2
            assert result[0]["description"] == "Send roadmap draft to stakeholders by Friday"
            assert result[0]["assigned_to"] == "self"
            assert result[0]["priority"] == "high"
            assert result[1]["description"] == "Schedule meeting with DevOps team"
            mock_detector.detect_tasks_in_content.assert_called_once()

    def test_process_workspace_for_tasks(self, mock_config, temp_workspace):
        """Test workspace processing for task detection"""
        mock_config.database_path = str(temp_workspace / "test.db")
        mock_config.workspace_dir = str(temp_workspace)

        mock_detector = Mock()
        mock_task_manager = Mock()
        mock_task_manager.scan_workspace.return_value = {
            "files_processed": 3,
            "tasks_detected": 5,
            "tasks_stored": 4,
            "errors": 0,
        }

        with patch(
            "claudedirector.intelligence.task.IntelligentTaskDetector", return_value=mock_detector
        ), patch(
            "claudedirector.intelligence.task.StrategicTaskManager", return_value=mock_task_manager
        ):
            task_ai = TaskIntelligence(config=mock_config)

            result = task_ai.process_workspace_for_tasks()

            assert result["files_processed"] == 3
            assert result["tasks_detected"] == 5
            assert result["tasks_stored"] == 4
            mock_task_manager.scan_workspace.assert_called_once()

    def test_get_my_tasks(self, mock_config, temp_db):
        """Test retrieving tasks assigned to user"""
        mock_config.database_path = temp_db

        mock_task_manager = Mock()
        mock_task_manager.get_my_tasks.return_value = [
            {
                "id": 1,
                "description": "Review Q4 roadmap",
                "status": "pending",
                "priority": "high",
                "due_date": "2024-01-15",
            },
            {
                "id": 2,
                "description": "Follow up with stakeholders",
                "status": "in_progress",
                "priority": "medium",
                "due_date": None,
            },
        ]

        with patch("claudedirector.intelligence.task.IntelligentTaskDetector"), patch(
            "claudedirector.intelligence.task.StrategicTaskManager", return_value=mock_task_manager
        ):
            task_ai = TaskIntelligence(config=mock_config)

            result = task_ai.get_my_tasks()

            assert len(result) == 2
            assert result[0]["description"] == "Review Q4 roadmap"
            assert result[1]["status"] == "in_progress"
            mock_task_manager.get_my_tasks.assert_called_once()

    def test_get_overdue_tasks(self, mock_config, temp_db):
        """Test retrieving overdue tasks"""
        mock_config.database_path = temp_db

        mock_task_manager = Mock()
        mock_task_manager.get_overdue_tasks.return_value = [
            {
                "id": 3,
                "description": "Overdue task",
                "status": "pending",
                "priority": "critical",
                "due_date": "2024-01-01",
                "days_overdue": 14,
            }
        ]

        with patch("claudedirector.intelligence.task.IntelligentTaskDetector"), patch(
            "claudedirector.intelligence.task.StrategicTaskManager", return_value=mock_task_manager
        ):
            task_ai = TaskIntelligence(config=mock_config)

            result = task_ai.get_overdue_tasks()

            assert len(result) == 1
            assert result[0]["priority"] == "critical"
            assert result[0]["days_overdue"] == 14
            mock_task_manager.get_overdue_tasks.assert_called_once()

    def test_update_task_status(self, mock_config, temp_db):
        """Test updating task status"""
        mock_config.database_path = temp_db

        mock_task_manager = Mock()
        mock_task_manager.update_task_status.return_value = True

        with patch("claudedirector.intelligence.task.IntelligentTaskDetector"), patch(
            "claudedirector.intelligence.task.StrategicTaskManager", return_value=mock_task_manager
        ):
            task_ai = TaskIntelligence(config=mock_config)

            result = task_ai.update_task_status(task_id=1, status="completed")

            assert result is True
            mock_task_manager.update_task_status.assert_called_once_with(1, "completed")

    def test_error_handling_in_detection(self, mock_config, temp_db):
        """Test error handling during task detection"""
        mock_config.database_path = temp_db

        mock_detector = Mock()
        mock_detector.detect_tasks_in_content.side_effect = Exception("Detection error")

        with patch(
            "claudedirector.intelligence.task.IntelligentTaskDetector", return_value=mock_detector
        ), patch("claudedirector.intelligence.task.StrategicTaskManager"):
            task_ai = TaskIntelligence(config=mock_config)

            with pytest.raises(AIDetectionError) as exc_info:
                task_ai.detect_tasks_in_content("test content", {})

            assert "Task detection failed" in str(exc_info.value)
            assert exc_info.value.detection_type == "task"

    def test_initialization_failure(self, mock_config, temp_db):
        """Test handling of initialization failures"""
        mock_config.database_path = temp_db

        with patch(
            "claudedirector.intelligence.task.IntelligentTaskDetector",
            side_effect=Exception("Init error"),
        ):
            with pytest.raises(AIDetectionError) as exc_info:
                TaskIntelligence(config=mock_config)

            assert "Failed to initialize task intelligence" in str(exc_info.value)

    def test_assignment_direction_detection(self, mock_config, temp_db):
        """Test detection of task assignment direction"""
        mock_config.database_path = temp_db

        mock_detector = Mock()
        mock_detector.detect_tasks_in_content.return_value = [
            {
                "description": "I need to review the proposal",
                "assigned_to": "self",
                "assigned_by": "self",
                "priority": "medium",
                "confidence": 0.85,
            },
            {
                "description": "Sarah asked me to prepare the metrics",
                "assigned_to": "self",
                "assigned_by": "Sarah Chen",
                "priority": "high",
                "confidence": 0.9,
            },
        ]

        with patch(
            "claudedirector.intelligence.task.IntelligentTaskDetector", return_value=mock_detector
        ), patch("claudedirector.intelligence.task.StrategicTaskManager"):
            task_ai = TaskIntelligence(config=mock_config)

            content = "I need to review the proposal. Sarah asked me to prepare the metrics."
            result = task_ai.detect_tasks_in_content(content, {})

            assert len(result) == 2
            assert result[0]["assigned_by"] == "self"  # Self-assigned
            assert result[1]["assigned_by"] == "Sarah Chen"  # Assigned by Sarah

    def test_stakeholder_mapping(self, mock_config, temp_db):
        """Test mapping tasks to stakeholders"""
        mock_config.database_path = temp_db

        mock_detector = Mock()
        mock_task_manager = Mock()
        mock_task_manager.link_task_to_stakeholder.return_value = True

        with patch(
            "claudedirector.intelligence.task.IntelligentTaskDetector", return_value=mock_detector
        ), patch(
            "claudedirector.intelligence.task.StrategicTaskManager", return_value=mock_task_manager
        ):
            task_ai = TaskIntelligence(config=mock_config)

            result = task_ai.link_task_to_stakeholder(
                task_id=1, stakeholder_key="sarah_chen", involvement_type="assignee"
            )

            assert result is True
            mock_task_manager.link_task_to_stakeholder.assert_called_once_with(
                1, "sarah_chen", "assignee"
            )
