"""Unit tests for L2 Initiative Extractor."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import responses

from strategic_integration_service.core.config import Settings
from strategic_integration_service.core.exceptions import ExtractionError
from strategic_integration_service.extractors.l2_initiatives import L2InitiativeExtractor
from strategic_integration_service.models.initiative import InitiativeStatus, L2Initiative


class TestL2InitiativeExtractor:
    """Test cases for L2InitiativeExtractor."""

    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings(
            jira_api_token="test-token",
            jira_email="test@example.com",
            jira_base_url="https://test.atlassian.net",
            l2_division_filter="UI Foundations",
            debug=True,
        )

    @pytest.fixture
    def extractor(self, settings):
        """Create L2InitiativeExtractor instance."""
        return L2InitiativeExtractor(settings)

    @pytest.fixture
    def sample_l2_issue(self):
        """Sample L2 initiative issue data."""
        return {
            "key": "PI-123",
            "fields": {
                "summary": "Platform Foundation Architecture Modernization",
                "description": {
                    "content": [
                        {"content": [{"text": "Modernize platform architecture for scalability"}]}
                    ]
                },
                "status": {"name": "In Progress", "statusCategory": {"key": "indeterminate"}},
                "priority": {"name": "High"},
                "assignee": {
                    "accountId": "12345",
                    "displayName": "Chris Cantu",
                    "emailAddress": "chris.cantu@procore.com",
                    "active": True,
                },
                "reporter": {
                    "accountId": "12345",
                    "displayName": "Chris Cantu",
                    "emailAddress": "chris.cantu@procore.com",
                    "active": True,
                },
                "project": {"key": "PI", "name": "Platform Initiatives"},
                "labels": ["platform", "architecture", "strategic"],
                "components": [],
                "created": "2025-01-01T10:00:00.000Z",
                "updated": "2025-01-08T15:30:00.000Z",
                "duedate": None,
                "resolutiondate": None,
                "customfield_18270": {"value": "UI Foundations"},
                "customfield_18271": {"name": "L2"},
                "customfield_18272": 1,
            },
        }

    def test_get_jql_query(self, extractor):
        """Test JQL query generation."""
        jql = extractor.get_jql_query()

        expected_parts = [
            "project = PI",
            'division in ("UI Foundations")',
            "type = L2",
            'status not in ("Done", "Closed", "Completed", "Canceled", "Released")',
            "ORDER BY cf[18272] ASC, priority DESC, updated ASC",
        ]

        for part in expected_parts:
            assert part in jql

    def test_validate_l2_initiative_valid(self, extractor, sample_l2_issue):
        """Test validation of valid L2 initiative."""
        initiative = L2Initiative.from_jira_issue(sample_l2_issue)
        assert extractor._validate_l2_initiative(initiative) is True

    def test_validate_l2_initiative_wrong_division(self, extractor, sample_l2_issue):
        """Test validation fails for wrong division."""
        sample_l2_issue["fields"]["customfield_18270"]["value"] = "Other Division"
        initiative = L2Initiative.from_jira_issue(sample_l2_issue)
        assert extractor._validate_l2_initiative(initiative) is False

    def test_validate_l2_initiative_wrong_type(self, extractor, sample_l2_issue):
        """Test validation fails for wrong type."""
        sample_l2_issue["fields"]["customfield_18271"]["name"] = "L1"
        initiative = L2Initiative.from_jira_issue(sample_l2_issue)
        assert extractor._validate_l2_initiative(initiative) is False

    def test_validate_l2_initiative_excluded_status(self, extractor, sample_l2_issue):
        """Test validation fails for excluded status."""
        sample_l2_issue["fields"]["status"]["name"] = "Done"
        initiative = L2Initiative.from_jira_issue(sample_l2_issue)
        assert extractor._validate_l2_initiative(initiative) is False

    @responses.activate
    def test_extract_success(self, extractor, sample_l2_issue):
        """Test successful L2 initiative extraction."""
        # Mock Jira search response
        search_response = {"issues": [sample_l2_issue], "total": 1, "startAt": 0, "maxResults": 100}

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search",
            json=search_response,
            status=200,
        )

        # Mock authentication check
        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/myself",
            json={"displayName": "Test User"},
            status=200,
        )

        initiatives = extractor.extract()

        assert len(initiatives) == 1
        assert initiatives[0].key == "PI-123"
        assert initiatives[0].summary == "Platform Foundation Architecture Modernization"
        assert initiatives[0].division == "UI Foundations"
        assert initiatives[0].initiative_type == "L2"
        assert initiatives[0].strategic_priority_rank == 1

    @responses.activate
    def test_extract_no_results(self, extractor):
        """Test extraction with no results."""
        search_response = {"issues": [], "total": 0, "startAt": 0, "maxResults": 100}

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search",
            json=search_response,
            status=200,
        )

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/myself",
            json={"displayName": "Test User"},
            status=200,
        )

        initiatives = extractor.extract()
        assert len(initiatives) == 0

    @responses.activate
    def test_extract_api_error(self, extractor):
        """Test extraction with API error."""
        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search",
            json={"error": "Invalid JQL"},
            status=400,
        )

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/myself",
            json={"displayName": "Test User"},
            status=200,
        )

        with pytest.raises(ExtractionError):
            extractor.extract()

    @responses.activate
    def test_extract_l1_context(self, extractor, sample_l2_issue):
        """Test L1 context extraction."""
        # Create L1 version of sample issue
        l1_issue = sample_l2_issue.copy()
        l1_issue["key"] = "PI-456"
        l1_issue["fields"] = sample_l2_issue["fields"].copy()
        l1_issue["fields"]["customfield_18271"] = {"name": "L1"}
        l1_issue["fields"]["summary"] = "L1 Supporting Initiative"

        search_response = {"issues": [l1_issue], "total": 1, "startAt": 0, "maxResults": 100}

        responses.add(
            responses.GET,
            "https://test.atlassian.net/rest/api/3/search",
            json=search_response,
            status=200,
        )

        l1_initiatives = extractor._extract_l1_context()

        assert len(l1_initiatives) == 1
        assert l1_initiatives[0].key == "PI-456"
        assert l1_initiatives[0].initiative_type == "L1"

    def test_save_initiatives_json(self, extractor, sample_l2_issue, tmp_path):
        """Test saving initiatives to JSON."""
        initiative = L2Initiative.from_jira_issue(sample_l2_issue)
        output_file = tmp_path / "test_initiatives.json"

        extractor._save_initiatives_json([initiative], output_file)

        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert data["total_count"] == 1
        assert data["division"] == "UI Foundations"
        assert len(data["initiatives"]) == 1
        assert data["initiatives"][0]["key"] == "PI-123"

    def test_build_report_content(self, extractor, sample_l2_issue):
        """Test report content generation."""
        l2_initiative = L2Initiative.from_jira_issue(sample_l2_issue)

        # Create L1 initiative for context
        l1_issue = sample_l2_issue.copy()
        l1_issue["key"] = "PI-456"
        l1_issue["fields"] = sample_l2_issue["fields"].copy()
        l1_issue["fields"]["customfield_18271"] = {"name": "L1"}
        l1_initiative = L2Initiative.from_jira_issue(l1_issue)

        content = extractor._build_report_content([l2_initiative], [l1_initiative])

        # Check report structure
        assert "# UI Foundation L2 Strategic Initiatives Analysis" in content
        assert "## Executive Summary" in content
        assert "**Total L2 Strategic Initiatives**: 1" in content
        assert "**Total L1 Supporting Initiatives**: 1" in content
        assert "## L2 Strategic Initiatives (Business Level)" in content
        assert "## L1 Supporting Initiatives Context" in content
        assert "PI-123" in content
        assert "PI-456" in content
        assert "Platform Foundation Architecture Modernization" in content

    @patch("strategic_integration_service.extractors.l2_initiatives.datetime")
    def test_extract_and_save(self, mock_datetime, extractor, sample_l2_issue, tmp_path):
        """Test complete extract and save workflow."""
        # Mock datetime for consistent filenames
        mock_datetime.now.return_value.strftime.return_value = "2025-01-08"
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-08T10:00:00"

        # Mock the extract method
        initiative = L2Initiative.from_jira_issue(sample_l2_issue)
        with patch.object(extractor, "extract", return_value=[initiative]):
            with patch.object(extractor, "_extract_l1_context", return_value=[]):
                # Set output directory to temp path
                extractor.settings.output_base_dir = tmp_path

                report_file = extractor.extract_and_save()

                # Check files were created
                assert report_file.exists()
                assert report_file.name == "l2-strategic-analysis-2025-01-08.md"

                # Check JSON file was created
                json_file = tmp_path / "jira-data" / "l2-strategic-initiatives-2025-01-08.json"
                assert json_file.exists()

    def test_extractor_cleanup(self, extractor):
        """Test extractor cleanup."""
        # Mock the jira_client close method
        extractor.jira_client.close = Mock()

        extractor.close()

        extractor.jira_client.close.assert_called_once()
