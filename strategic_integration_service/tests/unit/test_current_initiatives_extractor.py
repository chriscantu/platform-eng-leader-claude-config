"""Unit tests for Current Initiatives Extractor."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

import pytest
import responses

from strategic_integration_service.core.config import Settings
from strategic_integration_service.core.exceptions import ExtractionError
from strategic_integration_service.extractors.current_initiatives import CurrentInitiativesExtractor
from strategic_integration_service.models.initiative import (
    CurrentInitiative,
    StrategicEpic,
    UIFoundationTeam,
)


class TestCurrentInitiativesExtractor:
    """Test cases for CurrentInitiativesExtractor."""

    @pytest.fixture
    def settings(self) -> Settings:
        """Create test settings."""
        return Settings(
            jira_base_url="https://test.atlassian.net",
            jira_email="test@test.com",
            jira_api_token="test-token",
            jira_max_results=50,
            output_base_dir=Path("/tmp/test-output"),
        )

    @pytest.fixture
    def extractor(self, settings: Settings) -> CurrentInitiativesExtractor:
        """Create test extractor."""
        return CurrentInitiativesExtractor(settings)

    @pytest.fixture
    def sample_jira_issue(self) -> Dict[str, Any]:
        """Create sample Jira issue data."""
        return {
            "key": "UIS-123",
            "fields": {
                "summary": "Test Initiative",
                "status": {"name": "In Progress"},
                "priority": {"name": "High"},
                "assignee": {
                    "accountId": "123",
                    "displayName": "Test User",
                    "emailAddress": "test@test.com",
                },
                "project": {"key": "UIS", "name": "Web Platform"},
                "labels": ["platform-foundation", "test-label"],
                "components": [{"name": "Frontend"}, {"name": "API"}],
                "fixVersions": [{"name": "v2.1.0"}],
                "description": "Test description",
                "updated": "2025-01-08T10:00:00.000Z",
                "created": "2025-01-01T10:00:00.000Z",
                "issuetype": {"name": "Story"},
                "timeestimate": 28800,  # 8 hours in seconds
                "timeoriginalestimate": 36000,  # 10 hours in seconds
                "customfield_10014": "UIS-100",  # Epic Link
            },
        }

    @pytest.fixture
    def sample_epic_issue(self) -> Dict[str, Any]:
        """Create sample epic issue data."""
        return {
            "key": "PI-456",
            "fields": {
                "summary": "Platform Migration Epic",
                "status": {"name": "In Progress"},
                "priority": {"name": "Highest"},
                "assignee": {
                    "accountId": "456",
                    "displayName": "Epic Owner",
                    "emailAddress": "owner@test.com",
                },
                "project": {"key": "PI", "name": "Platform Initiatives"},
                "labels": ["platform-foundation", "architecture"],
                "components": [{"name": "Platform"}],
                "fixVersions": [{"name": "Q1-2025"}],
                "description": "Major platform migration",
                "updated": "2025-01-08T10:00:00.000Z",
                "created": "2024-12-01T10:00:00.000Z",
                "issuetype": {"name": "Epic"},
                "customfield_10011": "Platform Migration",  # Epic Name
                "customfield_10010": {"value": "In Progress"},  # Epic Status
            },
        }

    def test_get_active_initiatives_jql(self, extractor: CurrentInitiativesExtractor):
        """Test JQL generation for active initiatives."""
        jql = extractor.get_active_initiatives_jql()

        assert "project in (WES,GLB,HUBS,FSGD,UISP,UIS,UXI,PI)" in jql
        assert "status not in (Done, Closed, Resolved)" in jql
        assert "ORDER BY priority DESC, project, updated DESC" in jql

    def test_get_strategic_epics_jql(self, extractor: CurrentInitiativesExtractor):
        """Test JQL generation for strategic epics."""
        jql = extractor.get_strategic_epics_jql()

        assert "project in (WES,GLB,HUBS,FSGD,UISP,UIS,UXI,PI)" in jql
        assert (
            "labels in (platform-foundation,design-system,quality-monitoring,mfe-migration,baseline-standards)"
            in jql
        )
        assert "issuetype = Epic" in jql
        assert "status not in (Done, Closed)" in jql

    def test_get_recent_completed_jql(self, extractor: CurrentInitiativesExtractor):
        """Test JQL generation for recent completed work."""
        jql = extractor.get_recent_completed_jql(14)

        assert "project in (WES,GLB,HUBS,FSGD,UISP,UIS,UXI,PI)" in jql
        assert "status in (Done, Closed, Resolved)" in jql
        assert "updated >= -14d" in jql

    @pytest.mark.asyncio
    async def test_extract_active_initiatives_success(
        self, extractor: CurrentInitiativesExtractor, sample_jira_issue: Dict[str, Any]
    ):
        """Test successful active initiatives extraction."""

        with patch.object(extractor, "__init__", lambda x, y: None):
            extractor.settings = Settings(
                jira_base_url="https://test.atlassian.net",
                jira_email="test@test.com",
                jira_api_token="test-token",
            )
            extractor.ui_foundation_projects = ["UIS", "PI"]

            # Mock JiraClient
            with patch(
                "strategic_integration_service.extractors.current_initiatives.JiraClient"
            ) as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                mock_client.search_issues.return_value = [sample_jira_issue]

                initiatives = await extractor.extract_active_initiatives()

                assert len(initiatives) == 1
                assert isinstance(initiatives[0], CurrentInitiative)
                assert initiatives[0].key == "UIS-123"
                assert initiatives[0].summary == "Test Initiative"
                assert initiatives[0].issue_type == "Story"
                assert initiatives[0].components == ["Frontend", "API"]
                assert initiatives[0].ui_foundation_team == UIFoundationTeam.WEB_PLATFORM

    @pytest.mark.asyncio
    async def test_extract_strategic_epics_success(
        self, extractor: CurrentInitiativesExtractor, sample_epic_issue: Dict[str, Any]
    ):
        """Test successful strategic epics extraction."""

        with patch.object(extractor, "__init__", lambda x, y: None):
            extractor.settings = Settings(
                jira_base_url="https://test.atlassian.net",
                jira_email="test@test.com",
                jira_api_token="test-token",
            )
            extractor.ui_foundation_projects = ["PI"]
            extractor.strategic_labels = ["platform-foundation"]

            # Mock JiraClient
            with patch(
                "strategic_integration_service.extractors.current_initiatives.JiraClient"
            ) as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                mock_client.search_issues.return_value = [sample_epic_issue]

                epics = await extractor.extract_strategic_epics()

                assert len(epics) == 1
                assert isinstance(epics[0], StrategicEpic)
                assert epics[0].key == "PI-456"
                assert epics[0].epic_name == "Platform Migration"
                assert epics[0].is_platform_related() is True

    def test_generate_team_breakdown(
        self, extractor: CurrentInitiativesExtractor, sample_jira_issue: Dict[str, Any]
    ):
        """Test team breakdown generation."""

        # Create test initiatives
        initiative1 = CurrentInitiative.from_jira_issue(sample_jira_issue)

        sample_jira_issue["key"] = "GLB-789"
        sample_jira_issue["fields"]["project"]["key"] = "GLB"
        sample_jira_issue["fields"]["project"]["name"] = "Globalizers"
        initiative2 = CurrentInitiative.from_jira_issue(sample_jira_issue)

        initiatives = [initiative1, initiative2]
        breakdown = extractor.generate_team_breakdown(initiatives)

        assert "Web Platform" in breakdown
        assert "Globalizers" in breakdown
        assert len(breakdown["Web Platform"]) == 1
        assert len(breakdown["Globalizers"]) == 1

    def test_generate_priority_analysis(
        self, extractor: CurrentInitiativesExtractor, sample_jira_issue: Dict[str, Any]
    ):
        """Test priority analysis generation."""

        # Create high priority initiative
        high_priority_issue = sample_jira_issue.copy()
        high_priority_issue["fields"]["priority"]["name"] = "High"
        initiative1 = CurrentInitiative.from_jira_issue(high_priority_issue)

        # Create at-risk initiative
        at_risk_issue = sample_jira_issue.copy()
        at_risk_issue["key"] = "UIS-124"
        at_risk_issue["fields"]["status"]["name"] = "Blocked"
        at_risk_issue["fields"]["priority"]["name"] = "Medium"
        initiative2 = CurrentInitiative.from_jira_issue(at_risk_issue)

        initiatives = [initiative1, initiative2]
        analysis = extractor.generate_priority_analysis(initiatives)

        assert len(analysis["high_priority"]) == 1
        assert len(analysis["at_risk"]) == 1
        assert len(analysis["strategic"]) == 2  # Both have strategic labels

    def test_generate_markdown_report(
        self,
        extractor: CurrentInitiativesExtractor,
        sample_jira_issue: Dict[str, Any],
        sample_epic_issue: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test markdown report generation."""

        # Create test data
        active_initiative = CurrentInitiative.from_jira_issue(sample_jira_issue)
        strategic_epic = StrategicEpic.from_jira_issue(sample_epic_issue)

        completed_issue = sample_jira_issue.copy()
        completed_issue["key"] = "UIS-125"
        completed_issue["fields"]["status"]["name"] = "Done"
        completed_issue["fields"]["resolutiondate"] = "2025-01-07T10:00:00.000Z"
        recent_completed = CurrentInitiative.from_jira_issue(completed_issue)

        report_path = tmp_path / "test-report.md"

        content = extractor.generate_markdown_report(
            [active_initiative], [strategic_epic], [recent_completed], report_path
        )

        assert report_path.exists()
        assert "UI Foundation Current Initiatives Analysis" in content
        assert "Web Platform" in content
        assert "UIS-123" in content
        assert "PI-456" in content
        assert "Platform Foundation & Architecture" in content

    @pytest.mark.asyncio
    async def test_extract_all_parallel_execution(
        self,
        extractor: CurrentInitiativesExtractor,
        sample_jira_issue: Dict[str, Any],
        sample_epic_issue: Dict[str, Any],
    ):
        """Test that extract_all runs extractions in parallel."""

        with patch.object(extractor, "__init__", lambda x, y: None):
            extractor.settings = Settings(
                jira_base_url="https://test.atlassian.net",
                jira_email="test@test.com",
                jira_api_token="test-token",
            )
            extractor.ui_foundation_projects = ["UIS", "PI"]
            extractor.strategic_labels = ["platform-foundation"]

            with patch.object(extractor, "extract_active_initiatives") as mock_active, patch.object(
                extractor, "extract_strategic_epics"
            ) as mock_epics, patch.object(extractor, "extract_recent_completed") as mock_completed:
                # Set return values
                mock_active.return_value = [CurrentInitiative.from_jira_issue(sample_jira_issue)]
                mock_epics.return_value = [StrategicEpic.from_jira_issue(sample_epic_issue)]
                mock_completed.return_value = []

                active, epics, completed = await extractor.extract_all()

                # Verify all methods were called
                mock_active.assert_called_once()
                mock_epics.assert_called_once()
                mock_completed.assert_called_once()

                assert len(active) == 1
                assert len(epics) == 1
                assert len(completed) == 0

    @pytest.mark.asyncio
    async def test_run_end_to_end(
        self,
        extractor: CurrentInitiativesExtractor,
        sample_jira_issue: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test complete run method end-to-end."""

        with patch.object(extractor, "extract_all") as mock_extract_all:
            # Mock the extraction
            initiative = CurrentInitiative.from_jira_issue(sample_jira_issue)
            mock_extract_all.return_value = ([initiative], [], [])

            # Run extraction
            result = await extractor.run(tmp_path)

            # Verify results
            assert result["active_initiatives"] == 1
            assert result["strategic_epics"] == 0
            assert result["recent_completed"] == 0
            assert "output_files" in result

            # Verify files were created
            output_files = result["output_files"]
            assert Path(output_files["analysis_report"]).exists()
            assert Path(output_files["active_initiatives"]).exists()

    def test_ui_foundation_team_mapping(self):
        """Test UI Foundation team enum mappings."""

        assert UIFoundationTeam.WEB_PLATFORM.value == "UIS"
        assert UIFoundationTeam.WEB_PLATFORM.team_name == "Web Platform"
        assert UIFoundationTeam.PLATFORM_INITIATIVES.value == "PI"
        assert UIFoundationTeam.PLATFORM_INITIATIVES.team_name == "Platform Initiatives"

    def test_current_initiative_methods(self, sample_jira_issue: Dict[str, Any]):
        """Test CurrentInitiative helper methods."""

        # Test high priority
        sample_jira_issue["fields"]["priority"]["name"] = "High"
        initiative = CurrentInitiative.from_jira_issue(sample_jira_issue)
        assert initiative.is_high_priority() is True

        # Test strategic labels
        assert initiative.has_strategic_labels() is True

        # Test team mapping
        assert initiative.ui_foundation_team == UIFoundationTeam.WEB_PLATFORM
        assert initiative.team_name == "Web Platform"

    def test_strategic_epic_methods(self, sample_epic_issue: Dict[str, Any]):
        """Test StrategicEpic helper methods."""

        epic = StrategicEpic.from_jira_issue(sample_epic_issue)

        # Test platform detection
        assert epic.is_platform_related() is True

        # Test quality detection (should be false for this epic)
        assert epic.is_quality_related() is False
