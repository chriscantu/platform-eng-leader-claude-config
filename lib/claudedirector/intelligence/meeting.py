"""
Meeting Intelligence Module
Unified interface for meeting analysis, tracking, and insights
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
    from meeting_intelligence import MeetingIntelligenceManager
except ImportError:
    # If legacy imports fail, create minimal stub
    class MeetingIntelligenceManager:
        def __init__(self, *args, **kwargs):
            pass

        def process_meeting_file(self, file_path, content):
            return {
                "meeting_type": "general_meeting",
                "participants_detected": 0,
                "agenda_items": 0,
                "action_items": 0,
                "stakeholders_mentioned": [],
            }

        def scan_directory(self, directory_path=None):
            return {"files_processed": 0, "meetings_detected": 0, "errors": 0, "new_sessions": 0}

        def get_meeting_patterns(self):
            return {"total_sessions": 0, "stakeholder_patterns": {}, "meeting_types": {}}

        def extract_metadata(self, content):
            return {
                "title": "Unknown Meeting",
                "date": None,
                "attendees": [],
                "meeting_type": "general_meeting",
                "agenda_items": [],
                "action_items": [],
            }

        def suggest_personas(self, context):
            return []

        def infer_meeting_type(self, indicators):
            return "general_meeting"

        def track_stakeholder_interactions(self, session_data):
            return {
                "new_relationships": 0,
                "updated_patterns": 0,
                "interaction_frequency_changes": 0,
            }


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
            self.meeting_manager = MeetingIntelligenceManager(self.db_path)
        except Exception as e:
            raise AIDetectionError(f"Failed to initialize meeting intelligence: {e}")

    def process_meeting_file(self, file_path: Path, content: str) -> Dict[str, Any]:
        """
        Process a single meeting file for intelligence extraction

        Args:
            file_path: Path to the meeting file
            content: Content of the meeting file

        Returns:
            Processing results with extracted intelligence
        """
        try:
            return self.meeting_manager.process_meeting_file(file_path, content)
        except Exception as e:
            raise AIDetectionError(f"Meeting processing failed: {e}", detection_type="meeting")

    def scan_workspace_for_meetings(self, workspace_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Scan workspace for meeting files and process them

        Args:
            workspace_path: Optional workspace path override

        Returns:
            Scanning results with counts and statistics
        """
        try:
            directory_path = workspace_path or self.config.workspace_dir
            return self.meeting_manager.scan_directory(directory_path)
        except Exception as e:
            raise AIDetectionError(
                f"Workspace meeting scanning failed: {e}", detection_type="meeting"
            )

    def get_meeting_patterns(self, stakeholder_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Get meeting patterns and insights

        Args:
            stakeholder_filter: Optional filter by stakeholder key

        Returns:
            Meeting patterns and statistics
        """
        try:
            patterns = self.meeting_manager.get_meeting_patterns()

            if stakeholder_filter and "stakeholder_patterns" in patterns:
                # Filter patterns for specific stakeholder
                filtered_patterns = patterns.copy()
                stakeholder_patterns = patterns["stakeholder_patterns"]

                if stakeholder_filter in stakeholder_patterns:
                    filtered_patterns["stakeholder_patterns"] = {
                        stakeholder_filter: stakeholder_patterns[stakeholder_filter]
                    }
                else:
                    filtered_patterns["stakeholder_patterns"] = {}

                return filtered_patterns

            return patterns
        except Exception as e:
            raise DatabaseError(f"Failed to get meeting patterns: {e}")

    def extract_meeting_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract structured metadata from meeting content

        Args:
            content: Raw meeting content

        Returns:
            Extracted metadata (title, date, attendees, agenda, etc.)
        """
        try:
            return self.meeting_manager.extract_metadata(content)
        except Exception as e:
            raise AIDetectionError(f"Metadata extraction failed: {e}", detection_type="meeting")

    def suggest_optimal_personas(self, meeting_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggest optimal AI personas for meeting context

        Args:
            meeting_context: Context information (type, attendees, topics, etc.)

        Returns:
            List of recommended personas with confidence scores
        """
        try:
            return self.meeting_manager.suggest_personas(meeting_context)
        except Exception as e:
            raise AIDetectionError(f"Persona suggestion failed: {e}", detection_type="meeting")

    def infer_meeting_type(self, meeting_indicators: Dict[str, Any]) -> str:
        """
        Automatically infer meeting type from indicators

        Args:
            meeting_indicators: Indicators like title, attendees, keywords

        Returns:
            Inferred meeting type
        """
        try:
            return self.meeting_manager.infer_meeting_type(meeting_indicators)
        except Exception as e:
            raise AIDetectionError(f"Meeting type inference failed: {e}", detection_type="meeting")

    def track_stakeholder_interactions(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track stakeholder interactions through meeting data

        Args:
            session_data: Meeting session data with attendees and context

        Returns:
            Interaction tracking results
        """
        try:
            return self.meeting_manager.track_stakeholder_interactions(session_data)
        except Exception as e:
            raise DatabaseError(f"Stakeholder interaction tracking failed: {e}")

    def get_meeting_frequency_analysis(
        self, stakeholder_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze meeting frequency patterns

        Args:
            stakeholder_key: Optional filter by specific stakeholder

        Returns:
            Frequency analysis with recommendations
        """
        try:
            patterns = self.get_meeting_patterns(stakeholder_key)

            analysis = {
                "total_meetings": patterns.get("total_sessions", 0),
                "frequency_analysis": {},
                "recommendations": [],
            }

            if "stakeholder_patterns" in patterns:
                for stakeholder, data in patterns["stakeholder_patterns"].items():
                    frequency = data.get("frequency", "unknown")
                    last_meeting = data.get("last_meeting")

                    analysis["frequency_analysis"][stakeholder] = {
                        "frequency": frequency,
                        "last_meeting": last_meeting,
                        "needs_follow_up": self._should_follow_up(frequency, last_meeting),
                    }

                    if analysis["frequency_analysis"][stakeholder]["needs_follow_up"]:
                        analysis["recommendations"].append(
                            {
                                "stakeholder": stakeholder,
                                "action": "schedule_follow_up",
                                "reason": f"No meeting in expected {frequency} cycle",
                            }
                        )

            return analysis
        except Exception as e:
            raise DatabaseError(f"Meeting frequency analysis failed: {e}")

    def get_meeting_effectiveness_metrics(self) -> Dict[str, Any]:
        """
        Calculate meeting effectiveness metrics

        Returns:
            Effectiveness metrics and insights
        """
        try:
            patterns = self.get_meeting_patterns()

            metrics = {
                "total_meetings": patterns.get("total_sessions", 0),
                "meeting_type_distribution": patterns.get("meeting_types", {}),
                "average_attendees": 0,
                "action_item_completion_rate": 0,  # Would need historical data
                "stakeholder_engagement_score": 0,
            }

            # Calculate stakeholder engagement score
            stakeholder_patterns = patterns.get("stakeholder_patterns", {})
            if stakeholder_patterns:
                engagement_scores = []
                for stakeholder, data in stakeholder_patterns.items():
                    frequency = data.get("frequency", "unknown")
                    score = self._calculate_engagement_score(frequency)
                    engagement_scores.append(score)

                if engagement_scores:
                    metrics["stakeholder_engagement_score"] = sum(engagement_scores) / len(
                        engagement_scores
                    )

            return metrics
        except Exception as e:
            raise DatabaseError(f"Meeting effectiveness metrics calculation failed: {e}")

    def _should_follow_up(self, frequency: str, last_meeting: Optional[str]) -> bool:
        """Check if stakeholder needs follow-up based on frequency and last meeting"""
        if not last_meeting:
            return True

        # Simple heuristic based on frequency
        frequency_days = {"weekly": 7, "biweekly": 14, "monthly": 30, "quarterly": 90}

        if frequency in frequency_days:
            try:
                from datetime import datetime, timedelta

                last_date = datetime.fromisoformat(last_meeting.replace("Z", "+00:00"))
                days_since = (datetime.now() - last_date).days
                return days_since > frequency_days[frequency] * 1.5  # 50% buffer
            except:
                return True

        return False

    def _calculate_engagement_score(self, frequency: str) -> float:
        """Calculate engagement score based on meeting frequency"""
        frequency_scores = {
            "weekly": 1.0,
            "biweekly": 0.8,
            "monthly": 0.6,
            "quarterly": 0.4,
            "as_needed": 0.3,
            "unknown": 0.1,
        }

        return frequency_scores.get(frequency, 0.1)

    def get_meeting_preparation_suggestions(
        self, meeting_type: str, attendees: List[str]
    ) -> Dict[str, Any]:
        """
        Get suggestions for meeting preparation

        Args:
            meeting_type: Type of meeting to prepare for
            attendees: List of expected attendees

        Returns:
            Preparation suggestions and recommended personas
        """
        try:
            context = {"meeting_type": meeting_type, "attendees": attendees}

            personas = self.suggest_optimal_personas(context)

            suggestions = {
                "recommended_personas": personas,
                "preparation_checklist": self._get_preparation_checklist(meeting_type),
                "stakeholder_context": self._get_stakeholder_context(attendees),
            }

            return suggestions
        except Exception as e:
            raise AIDetectionError(
                f"Meeting preparation suggestions failed: {e}", detection_type="meeting"
            )

    def _get_preparation_checklist(self, meeting_type: str) -> List[str]:
        """Get preparation checklist based on meeting type"""
        checklists = {
            "vp_1on1": [
                "Review previous meeting notes",
                "Prepare strategic updates",
                "List any escalations or blockers",
                "Update on key initiatives",
            ],
            "team_meeting": [
                "Prepare team updates",
                "Review project status",
                "Gather team feedback",
                "Prepare announcements",
            ],
            "strategic_planning": [
                "Review market analysis",
                "Prepare strategic options",
                "Gather stakeholder input",
                "Update strategic metrics",
            ],
        }

        return checklists.get(meeting_type, ["Prepare agenda", "Review objectives"])

    def _get_stakeholder_context(self, attendees: List[str]) -> Dict[str, Any]:
        """Get relevant context for meeting attendees"""
        # This would integrate with stakeholder intelligence
        # For now, return basic structure
        return {
            "attendee_count": len(attendees),
            "key_stakeholders": attendees[:3],  # First 3 as key
            "communication_preferences": {},
            "previous_interactions": {},
        }


# Backward compatibility functions
def get_meeting_intelligence(db_path: Optional[str] = None) -> MeetingIntelligence:
    """Get meeting intelligence instance"""
    return MeetingIntelligence(db_path=db_path)


def process_meeting_content(
    file_path: Path, content: str, db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function for meeting content processing"""
    intelligence = get_meeting_intelligence(db_path)
    return intelligence.process_meeting_file(file_path, content)
