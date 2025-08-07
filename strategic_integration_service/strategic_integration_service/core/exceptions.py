"""Custom exceptions for the Strategic Integration Service."""

from typing import Any, Dict, Optional


class StrategicIntegrationError(Exception):
    """Base exception for all Strategic Integration Service errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class JiraAPIError(StrategicIntegrationError):
    """Raised when Jira API operations fail."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_url: Optional[str] = None,
    ) -> None:
        details = {}
        if status_code:
            details["status_code"] = status_code
        if response_data:
            details["response_data"] = response_data
        if request_url:
            details["request_url"] = request_url

        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data
        self.request_url = request_url


class AuthenticationError(StrategicIntegrationError):
    """Raised when authentication fails."""

    pass


class DataValidationError(StrategicIntegrationError):
    """Raised when data validation fails."""

    def __init__(
        self,
        message: str,
        field_errors: Optional[Dict[str, str]] = None,
        invalid_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        details = {}
        if field_errors:
            details["field_errors"] = field_errors
        if invalid_data:
            details["invalid_data"] = invalid_data

        super().__init__(message, details)
        self.field_errors = field_errors
        self.invalid_data = invalid_data


class ConfigurationError(StrategicIntegrationError):
    """Raised when configuration is invalid or missing."""

    pass


class ExtractionError(StrategicIntegrationError):
    """Raised when data extraction fails."""

    pass


class ReportGenerationError(StrategicIntegrationError):
    """Raised when report generation fails."""

    pass
