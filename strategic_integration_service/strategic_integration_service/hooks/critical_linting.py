#!/usr/bin/env python3
"""Critical linting validator for pre-commit hooks."""

import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def run_flake8_check(files: List[str]) -> Tuple[List[str], List[str]]:
    """Run flake8 and categorize issues by severity."""
    if not files:
        return [], []

    # Critical errors that must be fixed
    critical_codes = {"F821", "F822", "F831", "E999", "F633", "F811", "E902", "E901"}

    # Run flake8
    cmd = ["flake8", "--select=E,W,F"] + files

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return [], []

        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []

        critical = []
        warnings = []

        for line in lines:
            # Extract error code
            if ": " in line:
                parts = line.split(": ", 2)
                if len(parts) >= 2:
                    error_code = parts[1].split()[0]
                    if error_code in critical_codes:
                        critical.append(line)
                    else:
                        warnings.append(line)
                else:
                    warnings.append(line)
            else:
                warnings.append(line)

        return critical, warnings

    except Exception as e:
        print(f"Error running flake8: {e}")
        return [f"Failed to run linting: {e}"], []


def check_syntax_errors(file_path: str) -> List[str]:
    """Check for Python syntax errors."""
    issues = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        ast.parse(content, filename=file_path)

    except SyntaxError as e:
        issues.append(f"{file_path}:{e.lineno}:{e.offset}: E999 SyntaxError: {e.msg}")
    except Exception as e:
        issues.append(f"{file_path}:1:1: E902 IOError: {e}")

    return issues


def main():
    """Main entry point."""
    # Get files from command line
    if len(sys.argv) > 1:
        files = [f for f in sys.argv[1:] if f.endswith(".py") and os.path.exists(f)]
    else:
        files = []

    if not files:
        print("ℹ️  No Python files to check")
        return True

    print(f"🔍 Running critical linting validation on {len(files)} files...")

    # Check for syntax errors first
    all_syntax_issues = []
    for file_path in files:
        all_syntax_issues.extend(check_syntax_errors(file_path))

    if all_syntax_issues:
        print("❌ Critical syntax errors found:")
        for issue in all_syntax_issues:
            print(f"  {issue}")
        return False

    # Run flake8 checks
    critical_issues, warning_issues = run_flake8_check(files)

    # Report results
    has_critical_issues = bool(critical_issues)

    if critical_issues:
        print("❌ Critical linting issues (must fix before commit):")
        for issue in critical_issues:
            print(f"  {issue}")

    if warning_issues:
        print(f"⚠️  Found {len(warning_issues)} non-critical issues")
        # Show first few as examples
        for issue in warning_issues[:3]:
            print(f"  {issue}")
        if len(warning_issues) > 3:
            print(f"  ... and {len(warning_issues) - 3} more")

    if not has_critical_issues and not warning_issues:
        print("✅ All linting checks passed!")
    elif not has_critical_issues:
        print("✅ No critical issues found. Commit allowed.")

    return not has_critical_issues


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Critical linting issues found. Please fix before committing.")
        sys.exit(1)
    else:
        print("\n✅ Critical linting validation passed!")
        sys.exit(0)
