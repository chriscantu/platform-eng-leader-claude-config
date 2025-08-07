#!/usr/bin/env python3
"""
Strategic PII Scanner for Git Pre-commit Hook

Scans code and data files for potential PII leakage before commits reach GitHub.
This is critical for protecting strategic leadership data and compliance.
"""

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


@dataclass
class PIIPattern:
    """PII detection pattern configuration."""

    name: str
    pattern: str
    severity: str  # 'high', 'medium', 'low'
    description: str


class PIIScanner:
    """Strategic PII scanner for executive and platform data protection."""

    def __init__(self):
        self.patterns = self._load_pii_patterns()
        self.violations = []

    def _load_pii_patterns(self) -> List[PIIPattern]:
        """Load PII detection patterns for strategic data."""
        return [
            # Email addresses
            PIIPattern(
                name="email",
                pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                severity="high",
                description="Email address detected",
            ),
            # API tokens and keys
            PIIPattern(
                name="api_token",
                pattern=r'(?i)(api[_-]?key|token|secret|password|pwd)\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}["\']?',
                severity="high",
                description="API token or key detected",
            ),
            # Jira/Atlassian tokens
            PIIPattern(
                name="jira_token",
                pattern=r"ATATT[a-zA-Z0-9_-]{40,}",
                severity="high",
                description="Jira API token detected",
            ),
            # Phone numbers
            PIIPattern(
                name="phone",
                pattern=r"(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
                severity="medium",
                description="Phone number detected",
            ),
            # Employee IDs
            PIIPattern(
                name="employee_id",
                pattern=r"\b(EMP|EID|EMPID)[-_]?\d{4,8}\b",
                severity="medium",
                description="Employee ID detected",
            ),
            # SSN patterns
            PIIPattern(
                name="ssn",
                pattern=r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b",
                severity="high",
                description="Social Security Number pattern detected",
            ),
            # Internal system URLs
            PIIPattern(
                name="internal_url",
                pattern=r"https?://[a-zA-Z0-9.-]*\.internal[a-zA-Z0-9./]*",
                severity="medium",
                description="Internal system URL detected",
            ),
            # Database connection strings
            PIIPattern(
                name="db_connection",
                pattern=r"(mongodb|mysql|postgres|oracle)://[^\s]+",
                severity="high",
                description="Database connection string detected",
            ),
            # Strategic project codes (custom pattern)
            PIIPattern(
                name="project_code",
                pattern=r"\b(PROJ|PID|PRJ)[-_]?\d{6,}\b",
                severity="low",
                description="Project identifier detected",
            ),
            # AWS/Cloud credentials
            PIIPattern(
                name="aws_key",
                pattern=r"AKIA[0-9A-Z]{16}",
                severity="high",
                description="AWS access key detected",
            ),
            # Generic secrets in quotes
            PIIPattern(
                name="quoted_secret",
                pattern=r'(secret|password|token|key)\s*[:=]\s*["\'][^"\']{20,}["\']',
                severity="medium",
                description="Potential secret in quotes detected",
            ),
        ]

    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan a file for PII violations."""
        violations = []

        try:
            # Skip binary files and certain extensions
            if self._should_skip_file(file_path):
                return violations

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Scan for each pattern
            for line_num, line in enumerate(content.splitlines(), 1):
                for pattern in self.patterns:
                    matches = re.finditer(pattern.pattern, line, re.IGNORECASE)
                    for match in matches:
                        violations.append(
                            {
                                "file": str(file_path),
                                "line": line_num,
                                "column": match.start() + 1,
                                "pattern": pattern.name,
                                "severity": pattern.severity,
                                "description": pattern.description,
                                "match": match.group(),
                                "context": line.strip(),
                            }
                        )

        except Exception as e:
            print(f"Warning: Could not scan {file_path}: {e}")

        return violations

    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if file should be skipped."""
        skip_extensions = {
            ".pyc",
            ".pyo",
            ".so",
            ".dylib",
            ".dll",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".wav",
            ".zip",
            ".tar",
            ".gz",
            ".bz2",
            ".xz",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
        }

        skip_patterns = [
            "venv/",
            "node_modules/",
            ".git/",
            "__pycache__/",
            ".pytest_cache/",
            "htmlcov/",
            ".coverage",
            ".egg-info/",
            "build/",
            "dist/",
        ]

        # Check extension
        if file_path.suffix.lower() in skip_extensions:
            return True

        # Check path patterns
        path_str = str(file_path)
        for pattern in skip_patterns:
            if pattern in path_str:
                return True

        return False

    def get_staged_files(self) -> List[Path]:
        """Get list of staged files for commit."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
            )

            files = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    path = Path(line)
                    if path.exists():
                        files.append(path)

            return files

        except subprocess.CalledProcessError:
            print("Warning: Could not get staged files")
            return []

    def scan_staged_files(self) -> List[Dict[str, Any]]:
        """Scan all staged files for PII violations."""
        staged_files = self.get_staged_files()
        all_violations = []

        for file_path in staged_files:
            violations = self.scan_file(file_path)
            all_violations.extend(violations)

        return all_violations

    def format_violation_report(self, violations: List[Dict[str, Any]]) -> str:
        """Format violations into a readable report."""
        if not violations:
            return "✅ No PII violations detected"

        # Group by severity
        high_violations = [v for v in violations if v["severity"] == "high"]
        medium_violations = [v for v in violations if v["severity"] == "medium"]
        low_violations = [v for v in violations if v["severity"] == "low"]

        report = []
        report.append("🚨 PII VIOLATIONS DETECTED 🚨")
        report.append("=" * 50)

        if high_violations:
            report.append(f"\n❌ HIGH SEVERITY ({len(high_violations)} violations):")
            for v in high_violations:
                report.append(f"  {v['file']}:{v['line']}:{v['column']} - {v['description']}")
                report.append(f"    Pattern: {v['pattern']}")
                report.append(f"    Context: {v['context'][:80]}...")
                report.append("")

        if medium_violations:
            report.append(f"\n⚠️  MEDIUM SEVERITY ({len(medium_violations)} violations):")
            for v in medium_violations:
                report.append(f"  {v['file']}:{v['line']}:{v['column']} - {v['description']}")

        if low_violations:
            report.append(f"\n💡 LOW SEVERITY ({len(low_violations)} violations):")
            for v in low_violations:
                report.append(f"  {v['file']}:{v['line']} - {v['description']}")

        report.append("\n" + "=" * 50)
        report.append("COMMIT BLOCKED: Please remove or mask PII before committing")
        report.append("For help: Contact security team or see PII handling guidelines")

        return "\n".join(report)


def main() -> int:
    """Main entry point for pre-commit hook."""
    print("🔍 Scanning for PII violations...")

    scanner = PIIScanner()
    violations = scanner.scan_staged_files()

    # Filter out high severity violations for blocking
    high_violations = [v for v in violations if v["severity"] == "high"]

    if violations:
        print(scanner.format_violation_report(violations))

        # Block commit only for high severity violations
        if high_violations:
            print(f"\n❌ COMMIT BLOCKED: {len(high_violations)} high-severity PII violations found")
            return 1
        else:
            print(f"\n⚠️  COMMIT ALLOWED: Only medium/low severity violations found")
            return 0
    else:
        print("✅ No PII violations detected")
        return 0


if __name__ == "__main__":
    sys.exit(main())
