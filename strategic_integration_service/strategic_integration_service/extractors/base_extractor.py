"""Base extractor class for all initiative extractors."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import structlog

from ..core.config import Settings
from ..utils.jira_client import JiraClient

logger = structlog.get_logger(__name__)


class BaseExtractor(ABC):
    """Base class for all initiative extractors."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.jira_client = JiraClient(settings)
        self.logger = structlog.get_logger(self.__class__.__name__)

    @abstractmethod
    def extract(self) -> List[Any]:
        """Extract initiatives from Jira.

        Returns:
            List of extracted initiative objects
        """
        pass

    @abstractmethod
    def get_jql_query(self) -> str:
        """Get the JQL query for this extractor.

        Returns:
            JQL query string
        """
        pass

    def get_required_fields(self) -> List[str]:
        """Get the list of required Jira fields for this extractor.

        Returns:
            List of field names to request from Jira API
        """
        return [
            "summary",
            "status",
            "priority",
            "assignee",
            "reporter",
            "project",
            "labels",
            "components",
            "fixVersions",
            "description",
            "updated",
            "created",
            "duedate",
            "resolutiondate",
            "parent",
            "issuelinks",
            # Common custom fields
            "customfield_18270",  # Division
            "customfield_18271",  # Type
            "customfield_18272",  # Priority rank
            "customfield_18280",  # Additional field 1
            "customfield_18281",  # Additional field 2
            "customfield_18282",  # Additional field 3
        ]

    def validate_jql(self, jql: str) -> bool:
        """Validate JQL query before execution.

        Args:
            jql: JQL query string

        Returns:
            True if valid, False otherwise
        """
        try:
            return self.jira_client.validate_jql(jql)
        except Exception as e:
            self.logger.error("JQL validation failed", jql=jql, error=str(e))
            return False

    def extract_raw_issues(
        self, jql: Optional[str] = None, max_results: int = 1000
    ) -> List[Dict[str, Any]]:
        """Extract raw issue data from Jira.

        Args:
            jql: Optional custom JQL query (uses get_jql_query() if None)
            max_results: Maximum number of issues to return

        Returns:
            List of raw Jira issue dictionaries
        """
        if jql is None:
            jql = self.get_jql_query()

        self.logger.info("Starting issue extraction", jql=jql, max_results=max_results)

        # Validate JQL first
        if not self.validate_jql(jql):
            raise ValueError(f"Invalid JQL query: {jql}")

        # Extract issues
        try:
            issues = self.jira_client.search_all_issues(
                jql=jql, fields=self.get_required_fields(), max_total=max_results
            )

            self.logger.info("Issue extraction completed", total_issues=len(issues), jql=jql)

            return issues

        except Exception as e:
            self.logger.error("Issue extraction failed", error=str(e), jql=jql)
            raise

    def close(self) -> None:
        """Close underlying resources."""
        if hasattr(self.jira_client, "close"):
            self.jira_client.close()
