"""
Unit tests for meeting intelligence functionality
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from claudedirector.core.exceptions import AIDetectionError
from claudedirector.intelligence.meeting import MeetingIntelligence


class TestMeetingIntelligence:
    """Test meeting intelligence functionality"""

    def test_initialization_with_config(self, mock_config, temp_db):
        """Test meeting intelligence initialization with configuration"""
        mock_config.database_path = temp_db

        with patch("claudedirector.intelligence.meeting.MeetingIntelligenceManager"):
            meeting_ai = MeetingIntelligence(config=mock_config)

            assert meeting_ai.config == mock_config
            assert meeting_ai.db_path == temp_db

    def test_process_meeting_file(self, mock_config, temp_db, sample_meeting_content):
        """Test processing a single meeting file"""
        mock_config.database_path = temp_db

        mock_manager = Mock()
        mock_manager.process_meeting_file.return_value = {
            "meeting_type": "vp_1on1",
            "participants_detected": 2,
            "agenda_items": 3,
            "action_items": 3,
            "stakeholders_mentioned": ["sarah_chen", "john_smith"],
        }

        with patch(
            "claudedirector.intelligence.meeting.MeetingIntelligenceManager",
            return_value=mock_manager,
        ):
            meeting_ai = MeetingIntelligence(config=mock_config)

            file_path = Path("/test/meeting-prep/weekly-1on1.md")
            result = meeting_ai.process_meeting_file(file_path, sample_meeting_content)

            assert result["meeting_type"] == "vp_1on1"
            assert result["participants_detected"] == 2
            assert result["agenda_items"] == 3
            assert "sarah_chen" in result["stakeholders_mentioned"]
            mock_manager.process_meeting_file.assert_called_once()

    def test_scan_workspace_for_meetings(self, mock_config, temp_workspace):
        """Test scanning workspace for meeting files"""
        mock_config.database_path = str(temp_workspace / "test.db")
        mock_config.workspace_dir = str(temp_workspace)

        # Create some test meeting files
        meeting_prep_dir = temp_workspace / "meeting-prep"
        meeting_prep_dir.mkdir(exist_ok=True)

        (meeting_prep_dir / "weekly-1on1.md").write_text("# Weekly 1:1 with Sarah")
        (meeting_prep_dir / "team-meeting.md").write_text("# Team Meeting Notes")

        mock_manager = Mock()
        mock_manager.scan_directory.return_value = {
            "files_processed": 2,
            "meetings_detected": 2,
            "errors": 0,
            "new_sessions": 2,
        }

        with patch(
            "claudedirector.intelligence.meeting.MeetingIntelligenceManager",
            return_value=mock_manager,
        ):
            meeting_ai = MeetingIntelligence(config=mock_config)

            result = meeting_ai.scan_workspace_for_meetings()

            assert result["files_processed"] == 2
            assert result["meetings_detected"] == 2
            assert result["new_sessions"] == 2
            mock_manager.scan_directory.assert_called_once()

    def test_get_meeting_patterns(self, mock_config, temp_db):
        """Test retrieving meeting patterns and insights"""
        mock_config.database_path = temp_db

        mock_manager = Mock()
        mock_manager.get_meeting_patterns.return_value = {
            "total_sessions": 15,
            "stakeholder_patterns": {
                "sarah_chen": {"frequency": "weekly", "last_meeting": "2024-01-15"},
                "john_smith": {"frequency": "biweekly", "last_meeting": "2024-01-10"},
            },
            "meeting_types": {"vp_1on1": 4, "team_meeting": 6, "strategic_planning": 5},
        }

        with patch(
            "claudedirector.intelligence.meeting.MeetingIntelligenceManager",
            return_value=mock_manager,
        ):
            meeting_ai = MeetingIntelligence(config=mock_config)

            result = meeting_ai.get_meeting_patterns()

            assert result["total_sessions"] == 15
            assert "sarah_chen" in result["stakeholder_patterns"]
            assert result["meeting_types"]["vp_1on1"] == 4
            mock_manager.get_meeting_patterns.assert_called_once()

    def test_extract_meeting_metadata(self, mock_config, temp_db):
        """Test extracting metadata from meeting content"""
        mock_config.database_path = temp_db

        meeting_content = """
        # Weekly 1:1 with Sarah Chen (VP Engineering)
        Date: 2024-01-15
        Attendees: Sarah Chen, Chris Cantu

        ## Agenda
        - Q4 Platform roadmap
        - Team scaling

        ## Action Items
        - [ ] Review proposal by Friday
        - [ ] Schedule team meeting
        """

        mock_manager = Mock()
        mock_manager.extract_metadata.return_value = {
            "title": "Weekly 1:1 with Sarah Chen (VP Engineering)",
            "date": "2024-01-15",
            "attendees": ["Sarah Chen", "Chris Cantu"],
            "meeting_type": "vp_1on1",
            "agenda_items": ["Q4 Platform roadmap", "Team scaling"],
            "action_items": ["Review proposal by Friday", "Schedule team meeting"],
        }

        with patch(
            "claudedirector.intelligence.meeting.MeetingIntelligenceManager",
            return_value=mock_manager,
        ):
            meeting_ai = MeetingIntelligence(config=mock_config)

            result = meeting_ai.extract_meeting_metadata(meeting_content)

            assert result["title"] == "Weekly 1:1 with Sarah Chen (VP Engineering)"
            assert result["date"] == "2024-01-15"
            assert len(result["attendees"]) == 2
            assert len(result["action_items"]) == 2
            mock_manager.extract_metadata.assert_called_once()

    def test_suggest_optimal_personas(self, mock_config, temp_db):
        """Test suggesting optimal AI personas for meeting context"""
        mock_config.database_path = temp_db

        mock_manager = Mock()
        mock_manager.suggest_personas.return_value = [
            {"persona": "diego", "confidence": 0.9, "reason": "Engineering leadership context"},
            {"persona": "camille", "confidence": 0.7, "reason": "Strategic technology discussion"},
        ]

        with patch(
            "claudedirector.intelligence.meeting.MeetingIntelligenceManager",
            return_value=mock_manager,
        ):
            meeting_ai = MeetingIntelligence(config=mock_config)

            meeting_context = {
                "meeting_type": "vp_1on1",
                "attendees": ["Sarah Chen"],
                "topics": ["platform strategy", "team scaling"],
            }

            result = meeting_ai.suggest_optimal_personas(meeting_context)

            assert len(result) == 2
            assert result[0]["persona"] == "diego"
            assert result[0]["confidence"] == 0.9
            assert result[1]["persona"] == "camille"
            mock_manager.suggest_personas.assert_called_once()

    def test_error_handling_in_processing(self, mock_config, temp_db):
        """Test error handling during meeting processing"""
        mock_config.database_path = temp_db

        mock_manager = Mock()
        mock_manager.process_meeting_file.side_effect = Exception("Processing error")

        with patch(
            "claudedirector.intelligence.meeting.MeetingIntelligenceManager",
            return_value=mock_manager,
        ):
            meeting_ai = MeetingIntelligence(config=mock_config)

            with pytest.raises(AIDetectionError) as exc_info:
                meeting_ai.process_meeting_file(Path("/test/file.md"), "content")

            assert "Meeting processing failed" in str(exc_info.value)
            assert exc_info.value.detection_type == "meeting"

    def test_initialization_failure(self, mock_config, temp_db):
        """Test handling of initialization failures"""
        mock_config.database_path = temp_db

        with patch(
            "claudedirector.intelligence.meeting.MeetingIntelligenceManager",
            side_effect=Exception("Init error"),
        ):
            with pytest.raises(AIDetectionError) as exc_info:
                MeetingIntelligence(config=mock_config)

            assert "Failed to initialize meeting intelligence" in str(exc_info.value)

    def test_meeting_type_inference(self, mock_config, temp_db):
        """Test automatic meeting type inference"""
        mock_config.database_path = temp_db

        mock_manager = Mock()
        mock_manager.infer_meeting_type.return_value = "strategic_planning"

        with patch(
            "claudedirector.intelligence.meeting.MeetingIntelligenceManager",
            return_value=mock_manager,
        ):
            meeting_ai = MeetingIntelligence(config=mock_config)

            meeting_indicators = {
                "title": "Q1 Platform Strategy Session",
                "attendees": ["VP Engineering", "Product Director", "Design Lead"],
                "keywords": ["strategy", "roadmap", "planning"],
            }

            result = meeting_ai.infer_meeting_type(meeting_indicators)

            assert result == "strategic_planning"
            mock_manager.infer_meeting_type.assert_called_once()

    def test_stakeholder_relationship_tracking(self, mock_config, temp_db):
        """Test tracking stakeholder relationships through meetings"""
        mock_config.database_path = temp_db

        mock_manager = Mock()
        mock_manager.track_stakeholder_interactions.return_value = {
            "new_relationships": 2,
            "updated_patterns": 3,
            "interaction_frequency_changes": 1,
        }

        with patch(
            "claudedirector.intelligence.meeting.MeetingIntelligenceManager",
            return_value=mock_manager,
        ):
            meeting_ai = MeetingIntelligence(config=mock_config)

            session_data = {
                "session_id": "session_123",
                "attendees": ["sarah_chen", "john_smith"],
                "meeting_type": "cross_functional",
                "date": "2024-01-15",
            }

            result = meeting_ai.track_stakeholder_interactions(session_data)

            assert result["new_relationships"] == 2
            assert result["updated_patterns"] == 3
            mock_manager.track_stakeholder_interactions.assert_called_once()
