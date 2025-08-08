"""
Task Intelligence Module
Unified interface for task detection, management, and tracking
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Backward compatibility imports
try:
    # Try new package structure first
    from ..core.config import get_config
    from ..core.database import get_database_manager
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
    
    def get_config():
        return MinimalConfig()
    
    class AIDetectionError(Exception):
        pass
    
    class DatabaseError(Exception):
        pass

# Import legacy modules for functionality
try:
    from intelligent_task_detector import IntelligentTaskDetector
except ImportError:
    # If legacy imports fail, create minimal stub
    class IntelligentTaskDetector:
        def __init__(self, *args, **kwargs):
            pass
        
        def detect_tasks_in_content(self, content, context):
            return []


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
        except Exception as e:
            raise AIDetectionError(f"Failed to initialize task intelligence: {e}")
    
    def detect_tasks_in_content(self, content: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect tasks in content using AI
        
        Args:
            content: Text content to analyze
            context: Context information (file_path, meeting_type, etc.)
            
        Returns:
            List of detected task candidates with confidence scores
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
            Processing results with counts and actions taken
        """
        try:
            workspace_dir = Path(workspace_path) if workspace_path else self.config.workspace_path_obj
            
            total_processed = 0
            total_tasks = 0
            results = {
                'files_processed': 0,
                'tasks_detected': 0,
                'auto_created': 0,
                'needs_review': 0,
                'errors': []
            }
            
            # Process all relevant files
            file_patterns = ["*.md", "*.txt"]
            
            for pattern in file_patterns:
                for file_path in workspace_dir.rglob(pattern):
                    try:
                        if file_path.stat().st_size < 10:  # Skip very small files
                            continue
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if len(content.strip()) < 20:  # Skip empty files
                            continue
                        
                        # Build context
                        context = self._build_file_context(file_path, workspace_dir)
                        
                        # Detect tasks
                        detected_tasks = self.detect_tasks_in_content(content, context)
                        
                        if detected_tasks:
                            results['tasks_detected'] += len(detected_tasks)
                            
                            # Process tasks based on confidence
                            for task in detected_tasks:
                                if task.get('confidence_score', 0) >= 0.8:
                                    results['auto_created'] += 1
                                else:
                                    results['needs_review'] += 1
                        
                        results['files_processed'] += 1
                        
                    except Exception as e:
                        results['errors'].append({
                            'file': str(file_path),
                            'error': str(e)
                        })
            
            return results
            
        except Exception as e:
            raise AIDetectionError(f"Workspace processing failed: {e}", detection_type="task")
    
    def _build_file_context(self, file_path: Path, workspace_dir: Path) -> Dict[str, Any]:
        """Build context for file analysis"""
        relative_path = file_path.relative_to(workspace_dir)
        
        context = {
            'file_path': str(file_path),
            'relative_path': str(relative_path),
            'category': 'general',
            'meeting_type': None,
        }
        
        # Determine category from path
        path_parts = relative_path.parts
        
        if 'meeting-prep' in path_parts:
            context['category'] = 'meeting_prep'
            # Infer meeting type from directory name
            for part in path_parts:
                if 'vp' in part.lower():
                    context['meeting_type'] = 'vp_1on1'
                    break
                elif '1on1' in part.lower():
                    context['meeting_type'] = '1on1'
                    break
                elif 'strategic' in part.lower() or 'planning' in part.lower():
                    context['meeting_type'] = 'strategic_planning'
                    break
        
        elif 'initiatives' in path_parts or 'projects' in path_parts:
            context['category'] = 'current_initiatives'
        
        elif 'strategic' in path_parts or 'planning' in path_parts:
            context['category'] = 'strategic_docs'
        
        return context
    
    def get_tasks(self, filter_by: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get tasks with optional filtering
        
        Args:
            filter_by: Optional filters (status, priority, assignment_direction, etc.)
            
        Returns:
            List of tasks matching criteria
        """
        try:
            # This would need to be implemented in the legacy task manager
            # For now, return empty list as placeholder
            return []
        except Exception as e:
            raise DatabaseError(f"Failed to get tasks: {e}")
    
    def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks that are overdue"""
        try:
            return self.get_tasks({'status': 'active', 'overdue': True})
        except Exception as e:
            raise DatabaseError(f"Failed to get overdue tasks: {e}")
    
    def get_follow_ups_due(self) -> List[Dict[str, Any]]:
        """Get follow-ups that are due"""
        try:
            return self.get_tasks({'follow_up_required': True, 'follow_up_due': True})
        except Exception as e:
            raise DatabaseError(f"Failed to get follow-ups: {e}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get task system statistics"""
        try:
            # Try new database manager first
            try:
                db_manager = get_database_manager(self.db_path)
                return db_manager.get_table_info("strategic_tasks")
            except:
                # Fallback to basic stats
                return {"total_tasks": len(self.get_tasks())}
        except Exception as e:
            return {"error": str(e)}


# Backward compatibility functions
def get_task_intelligence(db_path: Optional[str] = None) -> TaskIntelligence:
    """Get task intelligence instance"""
    return TaskIntelligence(db_path=db_path)

def detect_tasks(content: str, context: Dict[str, Any], db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Convenience function for task detection"""
    intelligence = get_task_intelligence(db_path)
    return intelligence.detect_tasks_in_content(content, context)
