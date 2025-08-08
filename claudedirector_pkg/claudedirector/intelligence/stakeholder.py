"""
Stakeholder Intelligence Module
Unified interface for stakeholder detection, profiling, and management
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
    from local_stakeholder_ai import LocalStakeholderAI
    from intelligent_stakeholder_detector import IntelligentStakeholderDetector
    from stakeholder_engagement_engine import StakeholderEngagementEngine
except ImportError:
    # If legacy imports fail, create minimal stubs
    class LocalStakeholderAI:
        def __init__(self, *args, **kwargs):
            pass
    
    class IntelligentStakeholderDetector:
        def __init__(self, *args, **kwargs):
            pass
    
    class StakeholderEngagementEngine:
        def __init__(self, *args, **kwargs):
            pass


class StakeholderIntelligence:
    """
    Unified stakeholder intelligence interface
    Provides modern API while maintaining backward compatibility
    """
    
    def __init__(self, config=None, db_path: Optional[str] = None):
        """Initialize stakeholder intelligence with optional config override"""
        self.config = config or get_config()
        self.db_path = db_path or self.config.database_path
        
        # Initialize legacy components for functionality
        try:
            self.ai_engine = LocalStakeholderAI(self.db_path)
            self.detector = IntelligentStakeholderDetector(self.db_path)
            self.engagement_engine = StakeholderEngagementEngine(self.db_path)
        except Exception as e:
            raise AIDetectionError(f"Failed to initialize stakeholder intelligence: {e}")
    
    def detect_stakeholders_in_content(self, content: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect stakeholders in content using AI
        
        Args:
            content: Text content to analyze
            context: Context information (file_path, meeting_type, etc.)
            
        Returns:
            List of detected stakeholder candidates with confidence scores
        """
        try:
            return self.ai_engine.detect_stakeholders_in_content(content, context)
        except Exception as e:
            raise AIDetectionError(f"Stakeholder detection failed: {e}", detection_type="stakeholder")
    
    def process_content_for_stakeholders(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process content and automatically handle stakeholder detection and creation
        
        Args:
            content: Text content to analyze
            context: Context information
            
        Returns:
            Processing results with counts and actions taken
        """
        try:
            return self.detector.process_content_for_stakeholders(content, context)
        except Exception as e:
            raise AIDetectionError(f"Stakeholder processing failed: {e}", detection_type="stakeholder")
    
    def get_pending_profiling_tasks(self) -> List[Dict[str, Any]]:
        """Get stakeholders that need manual profiling"""
        try:
            return self.detector.get_pending_profiling_tasks()
        except Exception as e:
            raise DatabaseError(f"Failed to get profiling tasks: {e}")
    
    def get_pending_update_suggestions(self) -> List[Dict[str, Any]]:
        """Get pending stakeholder update suggestions"""
        try:
            return self.detector.get_pending_update_suggestions()
        except Exception as e:
            raise DatabaseError(f"Failed to get update suggestions: {e}")
    
    def list_stakeholders(self, filter_by: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List all stakeholders with optional filtering
        
        Args:
            filter_by: Optional filters (importance, role, etc.)
            
        Returns:
            List of stakeholder profiles
        """
        try:
            return self.engagement_engine.list_stakeholders(filter_by or {})
        except Exception as e:
            raise DatabaseError(f"Failed to list stakeholders: {e}")
    
    def add_stakeholder(self, stakeholder_key: str, display_name: str, **kwargs) -> bool:
        """
        Add a new stakeholder manually
        
        Args:
            stakeholder_key: Unique identifier
            display_name: Human-readable name
            **kwargs: Additional stakeholder attributes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.engagement_engine.add_stakeholder(
                stakeholder_key=stakeholder_key,
                display_name=display_name,
                **kwargs
            )
        except Exception as e:
            raise DatabaseError(f"Failed to add stakeholder: {e}")
    
    def get_stakeholder(self, stakeholder_key: str) -> Optional[Dict[str, Any]]:
        """Get specific stakeholder by key"""
        try:
            return self.engagement_engine.get_stakeholder(stakeholder_key)
        except Exception as e:
            raise DatabaseError(f"Failed to get stakeholder: {e}")
    
    def update_stakeholder(self, stakeholder_key: str, **updates) -> bool:
        """Update stakeholder information"""
        try:
            return self.engagement_engine.update_stakeholder(stakeholder_key, **updates)
        except Exception as e:
            raise DatabaseError(f"Failed to update stakeholder: {e}")
    
    def generate_engagement_recommendations(self) -> List[Dict[str, Any]]:
        """Generate engagement recommendations for stakeholders"""
        try:
            return self.engagement_engine.generate_engagement_recommendations()
        except Exception as e:
            raise AIDetectionError(f"Failed to generate recommendations: {e}", detection_type="engagement")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get stakeholder system statistics"""
        try:
            # Try new database manager first
            try:
                db_manager = get_database_manager(self.db_path)
                return db_manager.get_table_info("stakeholder_profiles_enhanced")
            except:
                # Fallback to basic stats
                return {"total_stakeholders": len(self.list_stakeholders())}
        except Exception as e:
            return {"error": str(e)}


# Backward compatibility functions
def get_stakeholder_intelligence(db_path: Optional[str] = None) -> StakeholderIntelligence:
    """Get stakeholder intelligence instance"""
    return StakeholderIntelligence(db_path=db_path)

def detect_stakeholders(content: str, context: Dict[str, Any], db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Convenience function for stakeholder detection"""
    intelligence = get_stakeholder_intelligence(db_path)
    return intelligence.detect_stakeholders_in_content(content, context)
