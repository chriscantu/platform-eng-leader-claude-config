"""Jira API client with retry logic and error handling."""

import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote, urljoin

import requests
import structlog
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from ..core.authentication import JiraAuthenticator
from ..core.config import Settings
from ..core.exceptions import AuthenticationError, JiraAPIError

logger = structlog.get_logger(__name__)


class JiraClient:
    """Enhanced Jira API client with retry logic, error handling, and rate limiting."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.authenticator = JiraAuthenticator(settings)
        self.session = self._create_session()
        self._rate_limit_remaining = 1000  # Default rate limit
        self._rate_limit_reset = time.time() + 3600

    def _create_session(self) -> requests.Session:
        """Create configured requests session with retry strategy."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.settings.jira_max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=self.settings.jira_retry_backoff,
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": f"StrategicIntegrationService/1.0.0",
            }
        )

        # Set authentication
        try:
            email, token = self.authenticator.get_credentials()
            session.auth = (email, token)
        except AuthenticationError as e:
            logger.error("Failed to set authentication", error=str(e))
            raise

        # Set timeout
        session.timeout = self.settings.jira_timeout

        return session

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Make authenticated request to Jira API with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/rest/api/3/search')
            params: Query parameters
            data: Form data
            json_data: JSON data for request body

        Returns:
            Response object

        Raises:
            JiraAPIError: If request fails or returns error status
        """
        url = urljoin(self.settings.jira_base_url, endpoint)

        # Check rate limiting
        self._check_rate_limit()

        try:
            logger.debug("Making Jira API request", method=method, url=url, params=params)

            response = self.session.request(
                method=method, url=url, params=params, data=data, json=json_data
            )

            # Update rate limit tracking
            self._update_rate_limit(response)

            # Log response details
            logger.debug(
                "Jira API response",
                status_code=response.status_code,
                response_size=len(response.content) if response.content else 0,
            )

            # Handle specific error cases
            if response.status_code == 401:
                raise AuthenticationError("Jira authentication failed")
            elif response.status_code == 403:
                raise JiraAPIError(
                    "Jira access forbidden - check permissions",
                    status_code=response.status_code,
                    request_url=url,
                )
            elif response.status_code == 429:
                raise JiraAPIError(
                    "Jira API rate limit exceeded",
                    status_code=response.status_code,
                    request_url=url,
                )
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"message": response.text}

                raise JiraAPIError(
                    f"Jira API error: {response.status_code}",
                    status_code=response.status_code,
                    response_data=error_data,
                    request_url=url,
                )

            return response

        except requests.RequestException as e:
            raise JiraAPIError(f"Network error communicating with Jira: {e}", request_url=url)

    def _check_rate_limit(self) -> None:
        """Check and handle rate limiting."""
        current_time = time.time()

        if self._rate_limit_remaining <= 10 and current_time < self._rate_limit_reset:
            sleep_time = self._rate_limit_reset - current_time
            logger.warning(
                "Approaching rate limit, sleeping",
                remaining=self._rate_limit_remaining,
                sleep_time=sleep_time,
            )
            time.sleep(min(sleep_time, 60))  # Cap at 60 seconds

    def _update_rate_limit(self, response: requests.Response) -> None:
        """Update rate limit tracking from response headers."""
        if "X-RateLimit-Remaining" in response.headers:
            self._rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])

        if "X-RateLimit-Reset" in response.headers:
            self._rate_limit_reset = int(response.headers["X-RateLimit-Reset"])

    def search_issues(
        self,
        jql: str,
        fields: Optional[List[str]] = None,
        max_results: int = 100,
        start_at: int = 0,
    ) -> Dict[str, Any]:
        """Search for issues using JQL.

        Args:
            jql: JQL query string
            fields: List of fields to include in response
            max_results: Maximum number of results to return
            start_at: Starting index for pagination

        Returns:
            Search results dictionary

        Raises:
            JiraAPIError: If search fails
        """
        params = {"jql": jql, "maxResults": max_results, "startAt": start_at}

        if fields:
            params["fields"] = ",".join(fields)

        response = self._make_request("GET", "/rest/api/3/search", params=params)

        if response.status_code != 200:
            raise JiraAPIError(
                f"Issue search failed: {response.status_code}",
                status_code=response.status_code,
                request_url=response.url,
            )

        return response.json()

    def get_issue(self, issue_key: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific issue by key.

        Args:
            issue_key: Jira issue key (e.g., 'PI-123')
            fields: List of fields to include in response

        Returns:
            Issue data dictionary

        Raises:
            JiraAPIError: If issue retrieval fails
        """
        params = {}
        if fields:
            params["fields"] = ",".join(fields)

        endpoint = f"/rest/api/3/issue/{quote(issue_key)}"
        response = self._make_request("GET", endpoint, params=params)

        if response.status_code == 404:
            raise JiraAPIError(f"Issue not found: {issue_key}")
        elif response.status_code != 200:
            raise JiraAPIError(
                f"Failed to retrieve issue {issue_key}: {response.status_code}",
                status_code=response.status_code,
            )

        return response.json()

    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information.

        Returns:
            User information dictionary

        Raises:
            JiraAPIError: If user info retrieval fails
        """
        response = self._make_request("GET", "/rest/api/3/myself")

        if response.status_code != 200:
            raise JiraAPIError(
                f"Failed to get user info: {response.status_code}", status_code=response.status_code
            )

        return response.json()

    def search_all_issues(
        self, jql: str, fields: Optional[List[str]] = None, max_total: int = 1000
    ) -> List[Dict[str, Any]]:
        """Search for all issues matching JQL, handling pagination automatically.

        Args:
            jql: JQL query string
            fields: List of fields to include in response
            max_total: Maximum total number of issues to return

        Returns:
            List of all matching issues

        Raises:
            JiraAPIError: If search fails
        """
        all_issues = []
        start_at = 0
        page_size = min(100, max_total)

        while len(all_issues) < max_total:
            logger.debug(
                "Fetching issue page",
                start_at=start_at,
                page_size=page_size,
                total_so_far=len(all_issues),
            )

            results = self.search_issues(
                jql=jql, fields=fields, max_results=page_size, start_at=start_at
            )

            issues = results.get("issues", [])
            if not issues:
                break

            all_issues.extend(issues)

            # Check if we've got all available issues
            total_available = results.get("total", 0)
            if len(all_issues) >= total_available:
                break

            start_at += page_size

            # Ensure we don't exceed max_total
            remaining = max_total - len(all_issues)
            page_size = min(100, remaining)

        logger.info("Issue search completed", total_issues=len(all_issues), jql=jql)

        return all_issues[:max_total]

    def validate_jql(self, jql: str) -> bool:
        """Validate a JQL query without executing it.

        Args:
            jql: JQL query string to validate

        Returns:
            True if JQL is valid, False otherwise
        """
        try:
            # Try a search with limit 1 to validate JQL
            self.search_issues(jql=jql, max_results=1)
            return True
        except JiraAPIError as e:
            if e.status_code == 400:
                logger.warning("Invalid JQL query", jql=jql, error=str(e))
                return False
            raise  # Re-raise other errors

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
