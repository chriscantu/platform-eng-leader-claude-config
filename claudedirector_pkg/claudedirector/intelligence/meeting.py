"""
Meeting Intelligence Module
Unified interface for meeting tracking, processing, and intelligence
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
    
    # Create minimal config for backward compatibility
    class MinimalConfig:
        def __init__(self):
            self.database_path = str(project_root / "memory" / "strategic_memory.db")
            self.workspace_dir = str(project_root / "workspace")
    
    def get_config():
        return MinimalConfig()
    
    class AIDetectionError(Exception):
        pass
    
    class DatabaseError(Exception):
        pass

# Import legacy modules for functionality
try:
    from meeting_intelligence import MeetingIntelligenceManager
except ImportError:
    # If legacy imports fail, create minimal stub
    class MeetingIntelligenceManager:
        def __init__(self, *args, **kwargs):
            pass
        
        def scan_and_process_meeting_prep(self):
            return {"processed": 0, "meetings": []}


class MeetingIntelligence:
    """
    Unified meeting intelligence interface
    Provides modern API while maintaining backward compatibility
    """
    
    def __init__(self, config=None, db_path: Optional[str] = None):
        """Initialize meeting intelligence with optional config override"""
        self.config = config or get_config()
        self.db_path = db_path or self.config.database_path
        
        # Initialize legacy components for functionality
        try:
            self.manager = MeetingIntelligenceManager(self.db_path)
        except Exception as e:
            raise AIDetectionError(f"Failed to initialize meeting intelligence: {e}")
    
    def scan_and_process_meetings(self, workspace_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Scan workspace and process meeting files
        
        Args:
            workspace_path: Optional workspace path override
            
        Returns:
            Processing results with counts and meeting data
        """
        try:
            return self.manager.scan_and_process_meeting_prep()
        except Exception as e:
            raise AIDetectionError(f"Meeting processing failed: {e}", detection_type="meeting")
    
    def process_meeting_file(self, file_path: str, meeting_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a specific meeting file
        
        Args:
            file_path: Path to meeting file
            meeting_type: Optional meeting type override
            
        Returns:
            Processing results for the file
        """
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                raise AIDetectionError(f"Meeting file not found: {file_path}")
            
            # Extract meeting intelligence from file
            meeting_data = self.manager.extract_meeting_metadata(file_path_obj)
            
            if meeting_type:
                meeting_data['meeting_type'] = meeting_type
            
            # Store in database
            meeting_id = self.manager.store_meeting_session(meeting_data)
            
            return {
                'meeting_id': meeting_id,
                'file_path': file_path,
                'meeting_data': meeting_data,
                'processed': True
            }
            
        except Exception as e:
            raise AIDetectionError(f"Failed to process meeting file: {e}", detection_type="meeting")
    
    def get_meetings(self, filter_by: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get meetings with optional filtering
        
        Args:
            filter_by: Optional filters (meeting_type, date_range, stakeholders, etc.)
            
        Returns:
            List of meetings matching criteria
        """
        try:
            # This would need to be implemented in the legacy meeting manager
            # For now, return empty list as placeholder
            return []
        except Exception as e:
            raise DatabaseError(f"Failed to get meetings: {e}")
    
    def get_meeting_by_id(self, meeting_id: int) -> Optional[Dict[str, Any]]:
        """Get specific meeting by ID"""
        try:
            return self.manager.get_meeting_session(meeting_id)
        except Exception as e:
            raise DatabaseError(f"Failed to get meeting: {e}")
    
    def get_stakeholder_meetings(self, stakeholder_key: str) -> List[Dict[str, Any]]:
        """Get meetings involving a specific stakeholder"""
        try:
            return self.manager.get_stakeholder_meetings(stakeholder_key)
        except Exception as e:
            raise DatabaseError(f"Failed to get stakeholder meetings: {e}")
    
    def get_meeting_patterns(self, stakeholder_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze meeting patterns and insights
        
        Args:
            stakeholder_key: Optional stakeholder to focus analysis on
            
        Returns:
            Meeting pattern analysis and insights
        """
        try:
            return self.manager.analyze_meeting_patterns(stakeholder_key)
        except Exception as e:
            raise AIDetectionError(f"Failed to analyze meeting patterns: {e}", detection_type="meeting")
    
    def get_recent_meetings(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get meetings from the last N days"""
        try:
            return self.manager.get_recent_meetings(days)
        except Exception as e:
            raise DatabaseError(f"Failed to get recent meetings: {e}")
    
    def start_workspace_monitoring(self, workspace_path: Optional[str] = None) -> bool:
        """
        Start monitoring workspace for new meeting files
        
        Args:
            workspace_path: Optional workspace path override
            
        Returns:
            True if monitoring started successfully
        """
        try:
            # This would integrate with the workspace monitor
            return self.manager.start_monitoring(workspace_path)
        except Exception as e:
            raise AIDetectionError(f"Failed to start monitoring: {e}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get meeting system statistics"""
        try:
            # Try new database manager first
            try:
                db_manager = get_database_manager(self.db_path)
                return db_manager.get_table_info("meeting_sessions")
            except:
                # Fallback to basic stats
                return {"total_meetings": len(self.get_meetings())}
        except Exception as e:
            return {"error": str(e)}


# Backward compatibility functions
def get_meeting_intelligence(db_path: Optional[str] = None) -> MeetingIntelligence:
    """Get meeting intelligence instance"""
    return MeetingIntelligence(db_path=db_path)

def process_meetings(workspace_path: Optional[str] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for meeting processing"""
    intelligence = get_meeting_intelligence(db_path)
    return intelligence.scan_and_process_meetings(workspace_path)
