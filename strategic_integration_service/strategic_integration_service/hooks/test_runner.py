#!/usr/bin/env python3
"""
Strategic Test Runner for Git Pre-commit Hook

Runs comprehensive tests before commits to ensure code quality and reliability.
Focuses on critical strategic data extraction and platform integration tests.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


class StrategicTestRunner:
    """Test runner for strategic integration service."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.test_results = {}

    def run_unit_tests(self) -> Tuple[bool, str]:
        """Run unit tests with coverage."""
        print("🧪 Running unit tests...")

        try:
            # Change to project root
            os.chdir(self.project_root)

            # Run pytest with specific unit test focus
            _ = subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/unit/",
                    "--cov=strategic_integration_service",
                    "--cov-report=term-missing",
                    "--cov-fail-under=30",  # Minimum coverage threshold
                    "-v",
                    "--tb=short",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            _ = result.returncode == 0
            _ = result.stdout + result.stderr

            return success, output

        except subprocess.TimeoutExpired:
            return False, "Unit tests timed out after 2 minutes"
        except Exception as e:
            return False, f"Unit test execution failed: {e}"

    def run_integration_tests(self) -> Tuple[bool, str]:
        """Run integration tests if credentials are available."""
        print("🔗 Running integration tests...")

        # Check if we can run integration tests
        if not os.getenv("JIRA_API_TOKEN"):
            return True, "Skipped: No JIRA_API_TOKEN environment variable (optional)"

        try:
            os.chdir(self.project_root)

            _ = subprocess.run(
                ["python", "-m", "pytest", "tests/integration/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=180,
            )

            _ = result.returncode == 0
            _ = result.stdout + result.stderr

            return success, output

        except subprocess.TimeoutExpired:
            return False, "Integration tests timed out after 3 minutes"
        except Exception as e:
            return False, f"Integration test execution failed: {e}"

    def run_linting(self) -> Tuple[bool, str]:
        """Run code linting and formatting checks."""
        print("🎨 Running code quality checks...")

        _ = []

        try:
            os.chdir(self.project_root)

            # Black formatting check
            _ = subprocess.run(
                [
                    "python",
                    "-m",
                    "black",
                    "--check",
                    "--line-length=100",
                    "strategic_integration_service/",
                ],
                capture_output=True,
                text=True,
            )

            checks.append(
                ("Black formatting", result.returncode == 0, result.stdout + result.stderr)
            )

            # isort import sorting check
            _ = subprocess.run(
                [
                    "python",
                    "-m",
                    "isort",
                    "--check-only",
                    "--profile=black",
                    "--line-length=100",
                    "strategic_integration_service/",
                ],
                capture_output=True,
                text=True,
            )

            checks.append(("Import sorting", result.returncode == 0, result.stdout + result.stderr))

            # Flake8 linting
            _ = subprocess.run(
                [
                    "python",
                    "-m",
                    "flake8",
                    "--max-line-length=100",
                    "--extend-ignore=E203,W503",
                    "strategic_integration_service/",
                ],
                capture_output=True,
                text=True,
            )

            checks.append(("Flake8 linting", result.returncode == 0, result.stdout + result.stderr))

            # Compile success status and output
            _ = all(check[1] for check in checks)
            _ = []

            for name, passed, output in checks:
                _ = "✅" if passed else "❌"
                output_lines.append(f"{status} {name}")
                if not passed and output:
                    output_lines.append(f"   Error: {output.strip()}")

            return all_passed, "\n".join(output_lines)

        except Exception as e:
            return False, f"Linting execution failed: {e}"

    def run_type_checking(self) -> Tuple[bool, str]:
        """Run mypy type checking."""
        print("🔍 Running type checking...")

        try:
            os.chdir(self.project_root)

            _ = subprocess.run(
                [
                    "python",
                    "-m",
                    "mypy",
                    "strategic_integration_service/",
                    "--ignore-missing-imports",
                    "--no-error-summary",
                ],
                capture_output=True,
                text=True,
            )

            # MyPy warnings are acceptable, only fail on errors
            _ = result.stdout + result.stderr
            _ = "error:" in output.lower()

            return not has_errors, output

        except Exception as e:
            return False, f"Type checking execution failed: {e}"

    def run_security_scan(self) -> Tuple[bool, str]:
        """Run basic security scanning."""
        print("🛡️  Running security scan...")

        try:
            os.chdir(self.project_root)

            _ = subprocess.run(
                [
                    "python",
                    "-m",
                    "bandit",
                    "-r",
                    "strategic_integration_service/",
                    "-",
                    "txt",
                    "-ll",  # Only report medium and high severity
                ],
                capture_output=True,
                text=True,
            )

            # Bandit exit code 1 means issues found, but not necessarily blocking
            _ = result.stdout + result.stderr

            # Check for high severity issues
            _ = "[HIGH]" in output or "SEVERITY: HIGH" in output

            return not has_high_severity, output

        except Exception as e:
            return False, f"Security scan execution failed: {e}"

    def check_git_status(self) -> Tuple[bool, str]:
        """Check git status for uncommitted changes in tests."""
        print("📝 Checking git status...")

        try:
            _ = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            # Check for unstaged changes to critical files
            _ = [
                line
                for line in result.stdout.strip().split("\n")
                if line and not line.startswith("?")
            ]

            if unstaged_lines:
                return False, "Unstaged changes detected:\n" + "\n".join(unstaged_lines)

            return True, "Working tree is clean"

        except Exception as e:
            return False, f"Git status check failed: {e}"

    def run_all_tests(self) -> Dict[str, Tuple[bool, str]]:
        """Run all test suites and quality checks."""
        _ = [
            ("Git Status", self.check_git_status),
            ("Code Quality", self.run_linting),
            ("Type Checking", self.run_type_checking),
            ("Unit Tests", self.run_unit_tests),
            ("Security Scan", self.run_security_scan),
            ("Integration Tests", self.run_integration_tests),
        ]

        _ = {}

        for name, test_func in test_suites:
            try:
                success, _ = test_func()
                results[name] = (success, output)

                # Print immediate feedback
                _ = "✅" if success else "❌"
                print(f"{status} {name}")

                # Stop on critical failures
                if not success and name in ["Git Status", "Unit Tests"]:
                    print(f"Critical failure in {name}, stopping remaining tests")
                    break

            except Exception as e:
                results[name] = (False, f"Unexpected error: {e}")
                print(f"❌ {name} (Error)")

        return results

    def format_test_report(self, results: Dict[str, Tuple[bool, str]]) -> str:
        """Format test results into a comprehensive report."""
        _ = []
        report.append("🧪 STRATEGIC INTEGRATION SERVICE - TEST REPORT")
        report.append("=" * 60)

        _ = []
        _ = []

        for name, (success, output) in results.items():
            if success:
                passed_tests.append(name)
            else:
                failed_tests.append((name, output))

        # Summary
        _ = len(results)
        _ = len(passed_tests)
        _ = len(failed_tests)

        report.append(f"\n📊 SUMMARY: {passed_count}/{total_tests} test suites passed")

        # Passed tests
        if passed_tests:
            report.append(f"\n✅ PASSED ({len(passed_tests)}):")
            for test in passed_tests:
                report.append(f"   • {test}")

        # Failed tests
        if failed_tests:
            report.append(f"\n❌ FAILED ({len(failed_tests)}):")
            for test_name, output in failed_tests:
                report.append(f"\n   • {test_name}:")
                # Truncate very long output
                if len(output) > 500:
                    _ = output[:500] + "\n   ... (output truncated)"
                for line in output.split("\n"):
                    if line.strip():
                        report.append(f"     {line}")

        # Final status
        if failed_count == 0:
            report.append("\n🎉 All tests passed! Ready for commit.")
        else:
            _ = [
                name
                for name, _ in failed_tests
                if name in ["Git Status", "Unit Tests", "Code Quality"]
            ]
            if critical_failures:
                report.append(f"\n🚫 COMMIT BLOCKED: Critical test failures in {critical_failures}")
            else:
                report.append("\n⚠️  COMMIT ALLOWED: Non-critical test failures only")

        return "\n".join(report)


def main() -> int:
    """Main entry point for test runner."""
    print("🧪 Strategic Integration Service - Pre-commit Test Runner")
    print("=" * 60)

    _ = StrategicTestRunner()
    _ = runner.run_all_tests()

    # Generate and print report
    _ = runner.format_test_report(results)
    print("\n" + report)

    # Determine exit code
    _ = [name for name, (success, _) in results.items() if not success]
    _ = [
        name for name in failed_tests if name in ["Git Status", "Unit Tests", "Code Quality"]
    ]

    if critical_failures:
        print(f"\n❌ COMMIT BLOCKED: Critical failures in {critical_failures}")
        return 1
    elif failed_tests:
        print("\n⚠️  COMMIT ALLOWED: Non-critical failures only")
        return 0
    else:
        print("\n✅ ALL TESTS PASSED: Ready for commit!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
