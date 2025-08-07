"""Authentication management for the Strategic Integration Service."""

from typing import Optional, Tuple

import keyring
import structlog

from .config import Settings
from .exceptions import AuthenticationError

logger = structlog.get_logger(__name__)


class JiraAuthenticator:
    """Manages Jira API authentication with secure credential storage."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.service_name = "strategic-integration-service"
        self.username = settings.jira_email

    def get_credentials(self) -> Tuple[str, str]:
        """Get Jira authentication credentials.

        Priority order:
        1. Environment variable (JIRA_API_TOKEN)
        2. Secure keyring storage
        3. Raise AuthenticationError if not found

        Returns:
            Tuple of (email, api_token)

        Raises:
            AuthenticationError: If credentials cannot be obtained
        """
        # Try environment variable first
        if self.settings.jira_api_token:
            logger.info("Using Jira API token from environment variable")
            return self.username, self.settings.jira_api_token

        # Try keyring storage
        try:
            stored_token = keyring.get_password(self.service_name, self.username)
            if stored_token:
                logger.info("Using Jira API token from secure keyring")
                return self.username, stored_token
        except Exception as e:
            logger.warning("Failed to access keyring", error=str(e))

        # No credentials found
        raise AuthenticationError(
            "Jira API token not found. Set JIRA_API_TOKEN environment variable "
            "or store credentials using store_credentials() method."
        )

    def store_credentials(self, api_token: str) -> None:
        """Store Jira API token securely in keyring.

        Args:
            api_token: The Jira API token to store

        Raises:
            AuthenticationError: If credential storage fails
        """
        try:
            keyring.set_password(self.service_name, self.username, api_token)
            logger.info("Jira API token stored securely in keyring")
        except Exception as e:
            raise AuthenticationError(f"Failed to store credentials: {e}")

    def remove_credentials(self) -> None:
        """Remove stored Jira API token from keyring.

        Raises:
            AuthenticationError: If credential removal fails
        """
        try:
            keyring.delete_password(self.service_name, self.username)
            logger.info("Jira API token removed from keyring")
        except keyring.errors.PasswordDeleteError:
            logger.warning("No stored credentials found to remove")
        except Exception as e:
            raise AuthenticationError(f"Failed to remove credentials: {e}")

    def validate_credentials(self) -> bool:
        """Validate that stored credentials work with Jira API.

        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            email, token = self.get_credentials()

            # Import here to avoid circular dependency
            from ..utils.jira_client import JiraClient

            client = JiraClient(self.settings)
            response = client._make_request("GET", "/rest/api/3/myself")

            if response.status_code == 200:
                user_data = response.json()
                logger.info(
                    "Credentials validated successfully",
                    display_name=user_data.get("displayName"),
                    email_address=user_data.get("emailAddress"),
                )
                return True
            else:
                logger.error("Credential validation failed", status_code=response.status_code)
                return False

        except Exception as e:
            logger.error("Credential validation error", error=str(e))
            return False

    def get_user_info(self) -> Optional[dict]:
        """Get authenticated user information from Jira.

        Returns:
            User information dict or None if authentication fails
        """
        try:
            from ..utils.jira_client import JiraClient

            client = JiraClient(self.settings)
            response = client._make_request("GET", "/rest/api/3/myself")

            if response.status_code == 200:
                return response.json()
            else:
                logger.error("Failed to get user info", status_code=response.status_code)
                return None

        except Exception as e:
            logger.error("Error getting user info", error=str(e))
            return None
