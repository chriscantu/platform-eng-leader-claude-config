#!/usr/bin/env python3
"""
Strategic Data Validator for Git Pre-commit Hook

Validates strategic data files for consistency, format, and security compliance.
Ensures executive reports and platform data meet quality standards.
"""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class ValidationError:
    """Validation error details."""

    file: str
    line: Optional[int]
    severity: str
    message: str
    rule: str


class StrategicValidator:
    """Validator for strategic platform and executive data files."""

    def __init__(self):
        self.errors = []

    def validate_json_file(self, file_path: Path) -> List[ValidationError]:
        """Validate JSON files for strategic data compliance."""
        errors = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Strategic initiative validation
            if self._is_initiative_file(file_path):
                errors.extend(self._validate_initiative_data(file_path, data))

            # General JSON validation
            errors.extend(self._validate_json_structure(file_path, data))

        except json.JSONDecodeError as e:
            errors.append(
                ValidationError(
                    file=str(file_path),
                    line=e.lineno,
                    severity="high",
                    message=f"Invalid JSON syntax: {e.msg}",
                    rule="json_syntax",
                )
            )
        except Exception as e:
            errors.append(
                ValidationError(
                    file=str(file_path),
                    line=None,
                    severity="medium",
                    message=f"Could not validate JSON: {e}",
                    rule="json_access",
                )
            )

        return errors

    def validate_markdown_file(self, file_path: Path) -> List[ValidationError]:
        """Validate Markdown files for strategic reporting compliance."""
        errors = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Executive report validation
            if self._is_executive_report(file_path):
                errors.extend(self._validate_executive_report(file_path, content))

            # General markdown validation
            errors.extend(self._validate_markdown_structure(file_path, content))

        except Exception as e:
            errors.append(
                ValidationError(
                    file=str(file_path),
                    line=None,
                    severity="medium",
                    message=f"Could not validate Markdown: {e}",
                    rule="markdown_access",
                )
            )

        return errors

    def validate_yaml_file(self, file_path: Path) -> List[ValidationError]:
        """Validate YAML configuration files."""
        errors = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Configuration validation
            if file_path.name.endswith(".yaml") or file_path.name.endswith(".yml"):
                errors.extend(self._validate_config_data(file_path, data))

        except yaml.YAMLError as e:
            errors.append(
                ValidationError(
                    file=str(file_path),
                    line=getattr(e, "problem_mark", {}).get("line", None),
                    severity="high",
                    message=f"Invalid YAML syntax: {e}",
                    rule="yaml_syntax",
                )
            )
        except Exception as e:
            errors.append(
                ValidationError(
                    file=str(file_path),
                    line=None,
                    severity="medium",
                    message=f"Could not validate YAML: {e}",
                    rule="yaml_access",
                )
            )

        return errors

    def _is_initiative_file(self, file_path: Path) -> bool:
        """Check if file contains initiative data."""
        return any(
            keyword in str(file_path).lower()
            for keyword in ["initiative", "l2-strategic", "l1-context"]
        )

    def _is_executive_report(self, file_path: Path) -> bool:
        """Check if file is an executive report."""
        return any(
            keyword in str(file_path).lower()
            for keyword in ["report", "executive", "strategic-analysis"]
        )

    def _validate_initiative_data(self, file_path: Path, data: Any) -> List[ValidationError]:
        """Validate strategic initiative data structure."""
        errors = []

        if isinstance(data, list):
            for i, item in enumerate(data):
                errors.extend(self._validate_initiative_item(file_path, item, i))
        elif isinstance(data, dict):
            if "initiatives" in data:
                for i, item in enumerate(data["initiatives"]):
                    errors.extend(self._validate_initiative_item(file_path, item, i))

        return errors

    def _validate_initiative_item(
        self, file_path: Path, item: Dict, index: int
    ) -> List[ValidationError]:
        """Validate individual initiative item."""
        errors = []

        # Required fields for initiatives
        required_fields = ["key", "summary", "status"]
        for field in required_fields:
            if field not in item:
                errors.append(
                    ValidationError(
                        file=str(file_path),
                        line=None,
                        severity="high",
                        message=f"Initiative {index}: Missing required field '{field}'",
                        rule="initiative_required_fields",
                    )
                )

        # Validate status values
        if "status" in item:
            valid_statuses = {
                "To Do",
                "In Progress",
                "Done",
                "Closed",
                "Completed",
                "Canceled",
                "Released",
                "Backlog",
                "Paused",
                "Refinement",
            }
            if item["status"] not in valid_statuses:
                errors.append(
                    ValidationError(
                        file=str(file_path),
                        line=None,
                        severity="medium",
                        message=f"Initiative {index}: Invalid status '{item['status']}'",
                        rule="initiative_status_validation",
                    )
                )

        # Validate key format
        if "key" in item:
            if not re.match(r"^[A-Z]+-\d+$", item["key"]):
                errors.append(
                    ValidationError(
                        file=str(file_path),
                        line=None,
                        severity="low",
                        message=f"Initiative {index}: Key '{item['key']}' doesn't match expected format",
                        rule="initiative_key_format",
                    )
                )

        return errors

    def _validate_json_structure(self, file_path: Path, data: Any) -> List[ValidationError]:
        """General JSON structure validation."""
        errors = []

        # Check for excessively deep nesting
        max_depth = 10
        if self._get_json_depth(data) > max_depth:
            errors.append(
                ValidationError(
                    file=str(file_path),
                    line=None,
                    severity="medium",
                    message=f"JSON structure exceeds maximum depth of {max_depth}",
                    rule="json_max_depth",
                )
            )

        return errors

    def _validate_executive_report(self, file_path: Path, content: str) -> List[ValidationError]:
        """Validate executive report structure and content."""
        errors = []

        # Check for required sections in executive reports
        required_sections = ["## Summary", "## Key Metrics", "## Strategic Initiatives"]
        for section in required_sections:
            if section not in content:
                errors.append(
                    ValidationError(
                        file=str(file_path),
                        line=None,
                        severity="medium",
                        message=f"Missing required section: {section}",
                        rule="executive_report_structure",
                    )
                )

        # Check for proper date format
        date_pattern = r"\d{4}-\d{2}-\d{2}"
        if not re.search(date_pattern, content):
            errors.append(
                ValidationError(
                    file=str(file_path),
                    line=None,
                    severity="low",
                    message="Report should include date in YYYY-MM-DD format",
                    rule="executive_report_date",
                )
            )

        return errors

    def _validate_markdown_structure(self, file_path: Path, content: str) -> List[ValidationError]:
        """General markdown structure validation."""
        errors = []

        lines = content.split("\n")

        # Check for proper heading hierarchy
        heading_levels = []
        for i, line in enumerate(lines, 1):
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                heading_levels.append((i, level))

        # Validate heading hierarchy
        for i in range(1, len(heading_levels)):
            prev_line, prev_level = heading_levels[i - 1]
            curr_line, curr_level = heading_levels[i]

            if curr_level > prev_level + 1:
                errors.append(
                    ValidationError(
                        file=str(file_path),
                        line=curr_line,
                        severity="low",
                        message=f"Heading level skipped from h{prev_level} to h{curr_level}",
                        rule="markdown_heading_hierarchy",
                    )
                )

        return errors

    def _validate_config_data(self, file_path: Path, data: Any) -> List[ValidationError]:
        """Validate configuration file structure."""
        errors = []

        # Development config validation
        if "development.yaml" in str(file_path):
            required_keys = ["jira", "logging", "output"]
            if isinstance(data, dict):
                for key in required_keys:
                    if key not in data:
                        errors.append(
                            ValidationError(
                                file=str(file_path),
                                line=None,
                                severity="medium",
                                message=f"Missing required configuration section: {key}",
                                rule="config_required_sections",
                            )
                        )

        return errors

    def _get_json_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum depth of JSON structure."""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._get_json_depth(value, current_depth + 1) for value in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._get_json_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth

    def validate_file(self, file_path: Path) -> List[ValidationError]:
        """Validate file based on extension."""
        if file_path.suffix.lower() == ".json":
            return self.validate_json_file(file_path)
        elif file_path.suffix.lower() == ".md":
            return self.validate_markdown_file(file_path)
        elif file_path.suffix.lower() in [".yaml", ".yml"]:
            return self.validate_yaml_file(file_path)
        else:
            return []

    def format_error_report(self, errors: List[ValidationError]) -> str:
        """Format validation errors into a readable report."""
        if not errors:
            return "✅ All strategic data files validated successfully"

        # Group by severity
        high_errors = [e for e in errors if e.severity == "high"]
        medium_errors = [e for e in errors if e.severity == "medium"]
        low_errors = [e for e in errors if e.severity == "low"]

        report = []
        report.append("📋 STRATEGIC DATA VALIDATION REPORT")
        report.append("=" * 50)

        if high_errors:
            report.append(f"\n❌ HIGH SEVERITY ({len(high_errors)} errors):")
            for error in high_errors:
                location = f"{error.file}:{error.line}" if error.line else error.file
                report.append(f"  {location} - {error.message}")

        if medium_errors:
            report.append(f"\n⚠️  MEDIUM SEVERITY ({len(medium_errors)} errors):")
            for error in medium_errors:
                location = f"{error.file}:{error.line}" if error.line else error.file
                report.append(f"  {location} - {error.message}")

        if low_errors:
            report.append(f"\n💡 LOW SEVERITY ({len(low_errors)} errors):")
            for error in low_errors:
                location = f"{error.file}:{error.line}" if error.line else error.file
                report.append(f"  {location} - {error.message}")

        return "\n".join(report)


def main() -> int:
    """Main entry point for strategic data validation."""
    import subprocess

    print("📋 Validating strategic data files...")

    # Get staged files
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True
        )

        staged_files = [
            Path(f) for f in result.stdout.strip().split("\n") if f and Path(f).exists()
        ]

    except subprocess.CalledProcessError:
        print("Warning: Could not get staged files")
        return 0

    validator = StrategicValidator()
    all_errors = []

    # Validate each staged file
    for file_path in staged_files:
        if file_path.suffix.lower() in [".json", ".md", ".yaml", ".yml"]:
            errors = validator.validate_file(file_path)
            all_errors.extend(errors)

    # Report results
    if all_errors:
        print(validator.format_error_report(all_errors))

        # Block commit only for high severity errors
        high_errors = [e for e in all_errors if e.severity == "high"]
        if high_errors:
            print(f"\n❌ COMMIT BLOCKED: {len(high_errors)} high-severity validation errors")
            return 1
        else:
            print(f"\n⚠️  COMMIT ALLOWED: Only medium/low severity validation errors")
            return 0
    else:
        print("✅ All strategic data files validated successfully")
        return 0


if __name__ == "__main__":
    sys.exit(main())
