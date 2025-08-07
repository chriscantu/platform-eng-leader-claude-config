"""Integration tests for Jira API connectivity and L2 extraction."""

import os
from unittest.mock import patch

import pytest

from strategic_integration_service.core.config import Settings
from strategic_integration_service.core.exceptions import AuthenticationError, JiraAPIError
from strategic_integration_service.extractors.l2_initiatives import L2InitiativeExtractor
from strategic_integration_service.utils.jira_client import JiraClient


@pytest.mark.integration
class TestJiraIntegration:
    """Integration tests that require actual Jira API access.

    These tests are marked with @pytest.mark.integration and can be run separately.
    They require JIRA_API_TOKEN environment variable to be set.
    """

    @pytest.fixture(scope="class")
    def settings(self):
        """Create settings for integration tests."""
        # Skip if no API token available
        if not os.getenv("JIRA_API_TOKEN"):
            pytest.skip("JIRA_API_TOKEN not set - skipping integration tests")

        return Settings(
            jira_api_token=os.getenv("JIRA_API_TOKEN"),
            jira_email="chris.cantu@procore.com",
            jira_base_url="https://procoretech.atlassian.net",
            debug=True,
        )

    @pytest.fixture
    def jira_client(self, settings):
        """Create Jira client for integration tests."""
        return JiraClient(settings)

    @pytest.fixture
    def l2_extractor(self, settings):
        """Create L2 extractor for integration tests."""
        return L2InitiativeExtractor(settings)

    def test_jira_authentication(self, jira_client):
        """Test that Jira authentication works."""
        user_info = jira_client.get_user_info()

        assert user_info is not None
        assert "displayName" in user_info
        assert "emailAddress" in user_info
        assert user_info["emailAddress"] == "chris.cantu@procore.com"

    def test_jira_search_basic(self, jira_client):
        """Test basic Jira search functionality."""
        # Simple search that should return some results
        results = jira_client.search_issues(jql="project = PI", max_results=5)

        assert "issues" in results
        assert "total" in results
        assert isinstance(results["issues"], list)
        assert results["total"] >= 0

    def test_l2_jql_validation(self, l2_extractor):
        """Test that L2 JQL query is valid."""
        jql = l2_extractor.get_jql_query()

        # Validate JQL without executing full search
        is_valid = l2_extractor.validate_jql(jql)
        assert is_valid is True

    def test_l2_extraction_dry_run(self, l2_extractor):
        """Test L2 extraction with limited results to avoid performance issues."""
        # Patch the max results to limit the test
        with patch.object(l2_extractor, "extract_raw_issues") as mock_extract:
            mock_extract.return_value = []

            initiatives = l2_extractor.extract()

            # Should not raise an exception
            assert isinstance(initiatives, list)
            mock_extract.assert_called_once()

    def test_jql_error_handling(self, jira_client):
        """Test JQL error handling."""
        with pytest.raises(JiraAPIError):
            jira_client.search_issues(jql="INVALID JQL SYNTAX")

    def test_invalid_authentication(self):
        """Test handling of invalid authentication."""
        settings = Settings(
            jira_api_token="invalid-token",
            jira_email="test@example.com",
            jira_base_url="https://procoretech.atlassian.net",
        )

        client = JiraClient(settings)

        with pytest.raises(AuthenticationError):
            client.get_user_info()


@pytest.mark.skip_integration
class TestJiraMocked:
    """Tests that use mocked Jira responses for CI/CD environments."""

    def test_l2_extractor_structure(self):
        """Test L2 extractor structure without real API calls."""
        settings = Settings(jira_api_token="mock-token", jira_email="test@example.com", debug=True)

        extractor = L2InitiativeExtractor(settings)

        # Test basic structure
        assert extractor.settings is not None
        assert extractor.division_filter == "UI Foundations"
        assert extractor.priority_field == "cf[18272]"

        # Test JQL generation
        jql = extractor.get_jql_query()
        assert "project = PI" in jql
        assert "UI Foundations" in jql
        assert "type = L2" in jql
