"""
Task Intelligence Module
Unified interface for task detection, tracking, and management
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Get logger for module
try:
    import structlog

    logger = structlog.get_logger()
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

# Backward compatibility imports
try:
    # Try new package structure first
    from ..core.config import get_config
    from ..core.exceptions import AIDetectionError, DatabaseError
except ImportError:
    # Fallback to legacy structure
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "memory"))
    sys.path.insert(0, str(project_root / "bin"))

    # Create minimal config for backward compatibility
    class MinimalConfig:
        def __init__(self):
            self.database_path = str(project_root / "memory" / "strategic_memory.db")
            self.workspace_dir = str(project_root / "workspace")

    def get_config():
        return MinimalConfig()

    class AIDetectionError(Exception):
        def __init__(self, message, detection_type=None):
            super().__init__(message)
            self.detection_type = detection_type

    class DatabaseError(Exception):
        pass


# Import legacy modules for functionality
try:
    from intelligent_task_detector import IntelligentTaskDetector
    from strategic_task_manager import StrategicTaskManager
except ImportError:
    # If legacy imports fail, create minimal stubs
    class IntelligentTaskDetector:
        def __init__(self, *args, **kwargs):
            pass

        def detect_tasks_in_content(self, content, context):
            return []

    class StrategicTaskManager:
        def __init__(self, *args, **kwargs):
            pass

        def scan_workspace(self):
            return {"files_processed": 0, "tasks_detected": 0, "tasks_stored": 0, "errors": 0}

        def get_my_tasks(self):
            return []

        def get_overdue_tasks(self):
            return []

        def update_task_status(self, task_id, status):
            return True

        def link_task_to_stakeholder(self, task_id, stakeholder_key, involvement_type):
            return True


class TaskIntelligence:
    """
    Unified task intelligence interface
    Provides modern API while maintaining backward compatibility
    """

    def __init__(self, config=None, db_path: Optional[str] = None):
        """Initialize task intelligence with optional config override"""
        self.config = config or get_config()
        self.db_path = db_path or self.config.database_path

        # Initialize legacy components for functionality
        try:
            self.detector = IntelligentTaskDetector(self.db_path)
            self.task_manager = StrategicTaskManager(self.db_path)
        except Exception as e:
            raise AIDetectionError(f"Failed to initialize task intelligence: {e}")

    def detect_tasks_in_content(
        self, content: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect tasks in content using AI

        Args:
            content: Text content to analyze
            context: Context information (source_path, category, etc.)

        Returns:
            List of detected task candidates with metadata
        """
        try:
            return self.detector.detect_tasks_in_content(content, context)
        except Exception as e:
            raise AIDetectionError(f"Task detection failed: {e}", detection_type="task")

    def process_workspace_for_tasks(self, workspace_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Process entire workspace for task detection

        Args:
            workspace_path: Optional workspace path override

        Returns:
            Processing results with counts and statistics
        """
        try:
            if workspace_path:
                # Set workspace path for this operation
                original_workspace = getattr(self.task_manager, "workspace_dir", None)
                if hasattr(self.task_manager, "workspace_dir"):
                    self.task_manager.workspace_dir = workspace_path

            result = self.task_manager.scan_workspace()

            # Restore original workspace path if changed
            if (
                workspace_path
                and original_workspace
                and hasattr(self.task_manager, "workspace_dir")
            ):
                self.task_manager.workspace_dir = original_workspace

            return result
        except Exception as e:
            raise AIDetectionError(f"Workspace task processing failed: {e}", detection_type="task")

    def get_my_tasks(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get tasks assigned to the user

        Args:
            status_filter: Optional status filter ('pending', 'in_progress', 'completed', etc.)

        Returns:
            List of user's tasks
        """
        try:
            tasks = self.task_manager.get_my_tasks()

            if status_filter:
                tasks = [task for task in tasks if task.get("status") == status_filter]

            return tasks
        except Exception as e:
            raise DatabaseError(f"Failed to get user tasks: {e}")

    def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """
        Get tasks that are overdue

        Returns:
            List of overdue tasks with days overdue
        """
        try:
            return self.task_manager.get_overdue_tasks()
        except Exception as e:
            raise DatabaseError(f"Failed to get overdue tasks: {e}")

    def get_tasks_by_assignee(self, assignee: str) -> List[Dict[str, Any]]:
        """
        Get tasks assigned to a specific person

        Args:
            assignee: Name or identifier of the assignee

        Returns:
            List of tasks assigned to the person
        """
        try:
            if hasattr(self.task_manager, "get_tasks_by_assignee"):
                return self.task_manager.get_tasks_by_assignee(assignee)
            else:
                # Fallback: filter all tasks
                all_tasks = self.task_manager.get_my_tasks() if assignee == "self" else []
                return [task for task in all_tasks if task.get("assigned_to") == assignee]
        except Exception as e:
            raise DatabaseError(f"Failed to get tasks for assignee {assignee}: {e}")

    def get_follow_up_tasks(self) -> List[Dict[str, Any]]:
        """
        Get tasks that need follow-up action

        Returns:
            List of tasks requiring follow-up
        """
        try:
            if hasattr(self.task_manager, "get_follow_up_tasks"):
                return self.task_manager.get_follow_up_tasks()
            else:
                # Fallback: get tasks with follow_up_date
                all_tasks = self.task_manager.get_my_tasks()
                return [task for task in all_tasks if task.get("follow_up_date")]
        except Exception as e:
            raise DatabaseError(f"Failed to get follow-up tasks: {e}")

    def update_task_status(self, task_id: int, status: str) -> bool:
        """
        Update the status of a task

        Args:
            task_id: ID of the task to update
            status: New status ('pending', 'in_progress', 'completed', 'blocked', 'cancelled')

        Returns:
            True if successful, False otherwise
        """
        try:
            return self.task_manager.update_task_status(task_id, status)
        except Exception as e:
            raise DatabaseError(f"Failed to update task status: {e}")

    def add_task(self, description: str, **kwargs) -> Optional[int]:
        """
        Add a new task manually

        Args:
            description: Task description
            **kwargs: Additional task attributes (priority, due_date, assigned_to, etc.)

        Returns:
            Task ID if successful, None otherwise
        """
        try:
            if hasattr(self.task_manager, "add_task"):
                return self.task_manager.add_task(description, **kwargs)
            else:
                logger.warning("Manual task addition not supported in current version")
                return None
        except Exception as e:
            raise DatabaseError(f"Failed to add task: {e}")

    def link_task_to_stakeholder(
        self, task_id: int, stakeholder_key: str, involvement_type: str
    ) -> bool:
        """
        Link a task to a stakeholder

        Args:
            task_id: ID of the task
            stakeholder_key: Key of the stakeholder
            involvement_type: Type of involvement ('assignee', 'reviewer', 'collaborator', etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            return self.task_manager.link_task_to_stakeholder(
                task_id, stakeholder_key, involvement_type
            )
        except Exception as e:
            raise DatabaseError(f"Failed to link task to stakeholder: {e}")

    def get_task_stakeholders(self, task_id: int) -> List[Dict[str, Any]]:
        """
        Get stakeholders involved with a specific task

        Args:
            task_id: ID of the task

        Returns:
            List of stakeholders and their involvement types
        """
        try:
            if hasattr(self.task_manager, "get_task_stakeholders"):
                return self.task_manager.get_task_stakeholders(task_id)
            else:
                # Fallback: return empty list
                return []
        except Exception as e:
            raise DatabaseError(f"Failed to get task stakeholders: {e}")

    def get_tasks_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """
        Get tasks by priority level

        Args:
            priority: Priority level ('critical', 'high', 'medium', 'low')

        Returns:
            List of tasks with the specified priority
        """
        try:
            all_tasks = self.task_manager.get_my_tasks()
            return [task for task in all_tasks if task.get("priority") == priority]
        except Exception as e:
            raise DatabaseError(f"Failed to get tasks by priority: {e}")

    def get_tasks_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get tasks by strategic category

        Args:
            category: Strategic category ('platform_initiative', 'stakeholder_followup', etc.)

        Returns:
            List of tasks in the specified category
        """
        try:
            all_tasks = self.task_manager.get_my_tasks()
            return [task for task in all_tasks if task.get("strategic_category") == category]
        except Exception as e:
            raise DatabaseError(f"Failed to get tasks by category: {e}")

    def generate_task_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of task status and metrics

        Returns:
            Dictionary with task summary statistics
        """
        try:
            all_tasks = self.task_manager.get_my_tasks()
            overdue_tasks = self.get_overdue_tasks()
            follow_up_tasks = self.get_follow_up_tasks()

            summary = {
                "total_tasks": len(all_tasks),
                "overdue_tasks": len(overdue_tasks),
                "follow_up_tasks": len(follow_up_tasks),
                "status_breakdown": {},
                "priority_breakdown": {},
                "category_breakdown": {},
            }

            # Calculate breakdowns
            for task in all_tasks:
                status = task.get("status", "unknown")
                priority = task.get("priority", "unknown")
                category = task.get("strategic_category", "unknown")

                summary["status_breakdown"][status] = summary["status_breakdown"].get(status, 0) + 1
                summary["priority_breakdown"][priority] = (
                    summary["priority_breakdown"].get(priority, 0) + 1
                )
                summary["category_breakdown"][category] = (
                    summary["category_breakdown"].get(category, 0) + 1
                )

            return summary
        except Exception as e:
            raise DatabaseError(f"Failed to generate task summary: {e}")


# Backward compatibility functions
def get_task_intelligence(db_path: Optional[str] = None) -> TaskIntelligence:
    """Get task intelligence instance"""
    return TaskIntelligence(db_path=db_path)


def detect_tasks(
    content: str, context: Dict[str, Any], db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Convenience function for task detection"""
    intelligence = get_task_intelligence(db_path)
    return intelligence.detect_tasks_in_content(content, context)
