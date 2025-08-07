"""Data validation utilities for the Strategic Integration Service."""

import re
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from ..core.exceptions import DataValidationError


class DataValidator:
    """Utility class for validating extracted data."""

    @staticmethod
    def validate_initiative_key(key: str) -> bool:
        """Validate Jira issue key format.

        Args:
            key: Jira issue key to validate

        Returns:
            True if valid, False otherwise
        """
        if not key or not isinstance(key, str):
            return False

        # Standard Jira key format: PROJECT-NUMBER
        pattern = r"^[A-Z][A-Z0-9]*-\d+$"
        return bool(re.match(pattern, key))

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_jql_query(jql: str) -> bool:
        """Basic JQL query validation.

        Args:
            jql: JQL query string to validate

        Returns:
            True if basic validation passes, False otherwise
        """
        if not jql or not isinstance(jql, str):
            return False

        # Basic validation - check for common JQL keywords
        jql_lower = jql.lower()
        required_keywords = ["project", "and", "or", "=", "in"]

        # Must contain at least "project" and "="
        if "project" not in jql_lower or "=" not in jql:
            return False

        # Check for common SQL injection patterns
        dangerous_patterns = [
            "drop table",
            "delete from",
            "insert into",
            "update set",
            "union select",
            "--",
            "/*",
            "*/",
        ]

        for pattern in dangerous_patterns:
            if pattern in jql_lower:
                return False

        return True

    @staticmethod
    def validate_initiative_data(data: Dict[str, Any]) -> List[str]:
        """Validate initiative data structure.

        Args:
            data: Initiative data dictionary

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Required fields
        required_fields = ["key", "fields"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        if "fields" in data:
            fields = data["fields"]

            # Validate key format
            if "key" in data:
                if not DataValidator.validate_initiative_key(data["key"]):
                    errors.append(f"Invalid issue key format: {data['key']}")

            # Check for required nested fields
            required_nested = ["summary", "status", "project", "created", "updated"]
            for field in required_nested:
                if field not in fields:
                    errors.append(f"Missing required field: fields.{field}")

            # Validate email addresses in assignee/reporter
            for user_field in ["assignee", "reporter"]:
                if user_field in fields and fields[user_field]:
                    email = fields[user_field].get("emailAddress")
                    if email and not DataValidator.validate_email(email):
                        errors.append(f"Invalid email in {user_field}: {email}")

            # Validate status structure
            if "status" in fields and fields["status"]:
                if "name" not in fields["status"]:
                    errors.append("Missing status.name field")

            # Validate project structure
            if "project" in fields and fields["project"]:
                if "key" not in fields["project"]:
                    errors.append("Missing project.key field")

        return errors

    @staticmethod
    def validate_l2_initiative_data(data: Dict[str, Any]) -> List[str]:
        """Validate L2-specific initiative data.

        Args:
            data: L2 initiative data dictionary

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = DataValidator.validate_initiative_data(data)

        if "fields" in data:
            fields = data["fields"]

            # L2-specific validations

            # Check division field
            division_fields = ["customfield_18270", "cf[18270]"]
            has_division = any(field in fields for field in division_fields)
            if not has_division:
                errors.append("Missing division field for L2 initiative")

            # Check type field
            type_fields = ["customfield_18271", "cf[18271]", "issuetype"]
            has_type = any(field in fields for field in type_fields)
            if not has_type:
                errors.append("Missing type field for L2 initiative")

            # Validate project is PI
            if "project" in fields and fields["project"]:
                project_key = fields["project"].get("key")
                if project_key != "PI":
                    errors.append(f"L2 initiatives must be in PI project, found: {project_key}")

        return errors

    @staticmethod
    def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
        """Sanitize text for safe output.

        Args:
            text: Text to sanitize
            max_length: Optional maximum length to truncate to

        Returns:
            Sanitized text
        """
        if not text or not isinstance(text, str):
            return ""

        # Remove control characters and normalize whitespace
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
        sanitized = re.sub(r"\s+", " ", sanitized).strip()

        # Truncate if needed
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[: max_length - 3] + "..."

        return sanitized

    @staticmethod
    def mask_pii(text: str) -> str:
        """Mask potential PII in text.

        Args:
            text: Text that may contain PII

        Returns:
            Text with PII masked
        """
        if not text or not isinstance(text, str):
            return text

        # Email addresses
        text = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL_MASKED]", text
        )

        # Phone numbers (basic patterns)
        text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE_MASKED]", text)

        # Social Security Numbers (basic pattern)
        text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_MASKED]", text)

        # Credit card numbers (basic pattern)
        text = re.sub(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[CARD_MASKED]", text)

        return text

    @classmethod
    def validate_and_clean_initiative(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean initiative data.

        Args:
            data: Raw initiative data from Jira

        Returns:
            Cleaned and validated data

        Raises:
            DataValidationError: If validation fails
        """
        # Validate data structure
        errors = cls.validate_initiative_data(data)
        if errors:
            raise DataValidationError(
                "Initiative data validation failed",
                field_errors={f"validation_{i}": error for i, error in enumerate(errors)},
                invalid_data=data,
            )

        # Clean sensitive data
        cleaned_data = data.copy()

        if "fields" in cleaned_data:
            fields = cleaned_data["fields"]

            # Sanitize text fields
            text_fields = ["summary", "description"]
            for field in text_fields:
                if field in fields and fields[field]:
                    if isinstance(fields[field], str):
                        fields[field] = cls.sanitize_text(fields[field], max_length=500)
                    elif isinstance(fields[field], dict):
                        # Handle ADF format
                        pass  # Keep as-is for now, handle in model conversion

            # Mask PII in comments/descriptions
            if "description" in fields and isinstance(fields["description"], str):
                fields["description"] = cls.mask_pii(fields["description"])

        return cleaned_data
