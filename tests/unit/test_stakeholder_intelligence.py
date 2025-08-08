"""
Unit tests for stakeholder intelligence functionality
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from claudedirector.core.exceptions import AIDetectionError
from claudedirector.intelligence.stakeholder import StakeholderIntelligence


class TestStakeholderIntelligence:
    """Test stakeholder intelligence AI functionality"""

    def test_initialization_with_config(self, mock_config, temp_db):
        """Test stakeholder intelligence initialization with configuration"""
        mock_config.database_path = temp_db

        with patch("claudedirector.intelligence.stakeholder.LocalStakeholderAI"), patch(
            "claudedirector.intelligence.stakeholder.IntelligentStakeholderDetector"
        ), patch("claudedirector.intelligence.stakeholder.StakeholderEngagementEngine"):
            stakeholder_ai = StakeholderIntelligence(config=mock_config)

            assert stakeholder_ai.config == mock_config
            assert stakeholder_ai.db_path == temp_db
            assert stakeholder_ai.enable_performance is True

    def test_initialization_without_performance(self, mock_config, temp_db):
        """Test initialization with performance features disabled"""
        mock_config.database_path = temp_db

        with patch("claudedirector.intelligence.stakeholder.LocalStakeholderAI"), patch(
            "claudedirector.intelligence.stakeholder.IntelligentStakeholderDetector"
        ), patch("claudedirector.intelligence.stakeholder.StakeholderEngagementEngine"):
            stakeholder_ai = StakeholderIntelligence(config=mock_config, enable_performance=False)

            assert stakeholder_ai.enable_performance is False

    def test_detect_stakeholders_in_content(self, mock_config, temp_db, sample_meeting_content):
        """Test stakeholder detection in content"""
        mock_config.database_path = temp_db

        mock_ai_engine = Mock()
        mock_ai_engine.detect_stakeholders_in_content.return_value = [
            {"name": "Sarah Chen", "role": "VP Engineering", "confidence": 0.9},
            {"name": "John Smith", "role": "Staff Engineer", "confidence": 0.8},
        ]

        with patch(
            "claudedirector.intelligence.stakeholder.LocalStakeholderAI",
            return_value=mock_ai_engine,
        ), patch("claudedirector.intelligence.stakeholder.IntelligentStakeholderDetector"), patch(
            "claudedirector.intelligence.stakeholder.StakeholderEngagementEngine"
        ):
            stakeholder_ai = StakeholderIntelligence(config=mock_config, enable_performance=False)

            context = {"category": "meeting_prep", "meeting_type": "vp_1on1"}
            result = stakeholder_ai.detect_stakeholders_in_content(sample_meeting_content, context)

            assert len(result) == 2
            assert result[0]["name"] == "Sarah Chen"
            assert result[1]["name"] == "John Smith"
            mock_ai_engine.detect_stakeholders_in_content.assert_called_once()

    def test_process_content_for_stakeholders_with_cache(self, mock_config, temp_db):
        """Test stakeholder processing with caching enabled"""
        mock_config.database_path = temp_db

        mock_detector = Mock()
        mock_detector.process_content_for_stakeholders.return_value = {
            "candidates_detected": 2,
            "auto_created": 1,
            "profiling_needed": 1,
            "updates_suggested": 0,
        }

        mock_cache_manager = Mock()
        mock_cache_manager.get.return_value = None  # Cache miss

        with patch("claudedirector.intelligence.stakeholder.LocalStakeholderAI"), patch(
            "claudedirector.intelligence.stakeholder.IntelligentStakeholderDetector",
            return_value=mock_detector,
        ), patch("claudedirector.intelligence.stakeholder.StakeholderEngagementEngine"), patch(
            "claudedirector.intelligence.stakeholder.CacheManager", return_value=mock_cache_manager
        ):
            stakeholder_ai = StakeholderIntelligence(config=mock_config)

            content = "Meeting with Sarah Chen (VP) and John Smith"
            context = {"category": "meeting_prep"}
            result = stakeholder_ai.process_content_for_stakeholders(content, context)

            assert result["candidates_detected"] == 2
            assert result["auto_created"] == 1
            mock_cache_manager.set.assert_called_once()

    def test_process_content_fallback_mechanism(self, mock_config, temp_db):
        """Test fallback mechanism when new methods are not available"""
        mock_config.database_path = temp_db

        mock_detector = Mock()
        # Simulate old detector without new method
        del mock_detector.process_content_for_stakeholders

        mock_ai_engine = Mock()
        mock_ai_engine.detect_stakeholders_in_content.return_value = [
            {"name": "Sarah Chen", "confidence": 0.9}
        ]

        with patch(
            "claudedirector.intelligence.stakeholder.LocalStakeholderAI",
            return_value=mock_ai_engine,
        ), patch(
            "claudedirector.intelligence.stakeholder.IntelligentStakeholderDetector",
            return_value=mock_detector,
        ), patch(
            "claudedirector.intelligence.stakeholder.StakeholderEngagementEngine"
        ):
            stakeholder_ai = StakeholderIntelligence(config=mock_config, enable_performance=False)

            content = "Meeting with Sarah Chen"
            context = {"category": "meeting_prep"}
            result = stakeholder_ai.process_content_for_stakeholders(content, context)

            assert result["candidates_detected"] == 1
            assert result["auto_created"] == 0
            assert result["profiling_needed"] == 0
            assert result["updates_suggested"] == 0

    def test_error_handling_in_processing(self, mock_config, temp_db):
        """Test error handling during stakeholder processing"""
        mock_config.database_path = temp_db

        mock_detector = Mock()
        mock_detector.process_content_for_stakeholders.side_effect = Exception("Processing error")

        with patch("claudedirector.intelligence.stakeholder.LocalStakeholderAI"), patch(
            "claudedirector.intelligence.stakeholder.IntelligentStakeholderDetector",
            return_value=mock_detector,
        ), patch("claudedirector.intelligence.stakeholder.StakeholderEngagementEngine"):
            stakeholder_ai = StakeholderIntelligence(config=mock_config, enable_performance=False)

            with pytest.raises(AIDetectionError) as exc_info:
                stakeholder_ai.process_content_for_stakeholders("test content", {})

            assert "Stakeholder processing failed" in str(exc_info.value)
            assert exc_info.value.detection_type == "stakeholder"

    def test_initialization_failure(self, mock_config, temp_db):
        """Test handling of initialization failures"""
        mock_config.database_path = temp_db

        with patch(
            "claudedirector.intelligence.stakeholder.LocalStakeholderAI",
            side_effect=Exception("Init error"),
        ):
            with pytest.raises(AIDetectionError) as exc_info:
                StakeholderIntelligence(config=mock_config)

            assert "Failed to initialize stakeholder intelligence" in str(exc_info.value)

    def test_cache_hit_scenario(self, mock_config, temp_db):
        """Test cache hit scenario"""
        mock_config.database_path = temp_db

        cached_result = {
            "candidates_detected": 1,
            "auto_created": 1,
            "profiling_needed": 0,
            "updates_suggested": 0,
        }

        mock_cache_manager = Mock()
        mock_cache_manager.get.return_value = cached_result  # Cache hit

        with patch("claudedirector.intelligence.stakeholder.LocalStakeholderAI"), patch(
            "claudedirector.intelligence.stakeholder.IntelligentStakeholderDetector"
        ), patch("claudedirector.intelligence.stakeholder.StakeholderEngagementEngine"), patch(
            "claudedirector.intelligence.stakeholder.CacheManager", return_value=mock_cache_manager
        ):
            stakeholder_ai = StakeholderIntelligence(config=mock_config)

            result = stakeholder_ai.process_content_for_stakeholders("test content", {})

            assert result == cached_result
            # Should not call set on cache for cache hits
            mock_cache_manager.set.assert_not_called()

    def test_workspace_processing_with_parallel(self, mock_config, temp_workspace):
        """Test workspace processing with parallel execution"""
        mock_config.database_path = str(temp_workspace / "test.db")
        mock_config.workspace_dir = str(temp_workspace)

        mock_parallel_processor = Mock()
        mock_parallel_processor.process_files_parallel.return_value = {
            "files_processed": 5,
            "stakeholders_detected": 3,
            "errors": 0,
        }

        with patch("claudedirector.intelligence.stakeholder.LocalStakeholderAI"), patch(
            "claudedirector.intelligence.stakeholder.IntelligentStakeholderDetector"
        ), patch("claudedirector.intelligence.stakeholder.StakeholderEngagementEngine"), patch(
            "claudedirector.intelligence.stakeholder.ParallelProcessor",
            return_value=mock_parallel_processor,
        ):
            stakeholder_ai = StakeholderIntelligence(config=mock_config)

            result = stakeholder_ai.process_workspace_for_stakeholders()

            assert result["files_processed"] == 5
            assert result["stakeholders_detected"] == 3
            mock_parallel_processor.process_files_parallel.assert_called_once()
