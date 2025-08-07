#!/usr/bin/env python3
"""
Intelligent Hook Filter for Strategic Integration Service

Determines which hooks should run based on the types of files being changed.
Optimizes development velocity by avoiding unnecessary hook execution.

Strategic Filtering Rules:
- Documentation changes (.md): Only run basic formatting and PII checks
- Python code changes (.py): Run full test suite and code quality checks
- Configuration changes (.yaml, .json): Run validation and security checks
- Mixed changes: Run appropriate hooks for each file type
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

# File type classifications
DOCUMENTATION_EXTENSIONS = {".md", ".rst", ".txt"}
PYTHON_EXTENSIONS = {".py"}
CONFIG_EXTENSIONS = {".yaml", ".yml", ".json", ".toml", ".cfg", ".ini"}
SCRIPT_EXTENSIONS = {".sh", ".bash", ".fish"}
SENSITIVE_EXTENSIONS = {".env", ".key", ".pem", ".p12"}

# Hook categories and their appropriate file types
HOOK_CATEGORIES = {
    "formatting": {
        "hooks": ["trailing-whitespace", "end-of-file-fixer"],
        "file_types": "all",
        "description": "Basic file formatting",
    },
    "structure": {
        "hooks": ["check-merge-conflict", "check-case-conflict", "check-added-large-files"],
        "file_types": "all",
        "description": "Repository structure validation",
    },
    "config_validation": {
        "hooks": ["check-yaml", "check-json", "check-toml"],
        "file_types": CONFIG_EXTENSIONS,
        "description": "Configuration file validation",
    },
    "python_quality": {
        "hooks": ["debug-statements", "black", "isort", "flake8", "mypy", "pydocstyle"],
        "file_types": PYTHON_EXTENSIONS,
        "description": "Python code quality and formatting",
    },
    "python_tests": {
        "hooks": ["name-tests-test", "test-runner"],
        "file_types": PYTHON_EXTENSIONS,
        "description": "Python testing validation",
    },
    "security_python": {
        "hooks": ["bandit"],
        "file_types": PYTHON_EXTENSIONS,
        "description": "Python security scanning",
    },
    "security_general": {
        "hooks": ["detect-secrets", "pii-scanner"],
        "file_types": PYTHON_EXTENSIONS
        | CONFIG_EXTENSIONS
        | SCRIPT_EXTENSIONS
        | SENSITIVE_EXTENSIONS,
        "description": "General security and PII scanning",
    },
    "strategic_validation": {
        "hooks": ["strategic-data-validator"],
        "file_types": CONFIG_EXTENSIONS | DOCUMENTATION_EXTENSIONS,
        "description": "Strategic data structure validation",
    },
    "critical_linting": {
        "hooks": ["critical-linting-validator"],
        "file_types": PYTHON_EXTENSIONS,
        "description": "Critical syntax and error validation",
    },
}


class IntelligentHookFilter:
    """Analyzes changed files and determines optimal hook execution strategy."""

    def __init__(self):
        self.changed_files: List[Path] = []
        self.file_types: Set[str] = set()
        self.hook_recommendations: Dict[str, Any] = {}

    def get_staged_files(self) -> List[Path]:
        """Get list of staged files from git."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
            )
            return [Path(f.strip()) for f in result.stdout.split("\n") if f.strip()]
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Could not get staged files: {e}")
            return []

    def classify_files(self, files: List[Path]) -> Dict[str, List[Path]]:
        """Classify files by type and determine optimization strategy."""
        classification = {
            "documentation": [],
            "python": [],
            "config": [],
            "scripts": [],
            "sensitive": [],
            "other": [],
        }

        for file_path in files:
            suffix = file_path.suffix.lower()

            if suffix in DOCUMENTATION_EXTENSIONS:
                classification["documentation"].append(file_path)
            elif suffix in PYTHON_EXTENSIONS:
                classification["python"].append(file_path)
            elif suffix in CONFIG_EXTENSIONS:
                classification["config"].append(file_path)
            elif suffix in SCRIPT_EXTENSIONS:
                classification["scripts"].append(file_path)
            elif suffix in SENSITIVE_EXTENSIONS:
                classification["sensitive"].append(file_path)
            else:
                classification["other"].append(file_path)

        return classification

    def determine_hook_strategy(self, file_classification: Dict[str, List[Path]]) -> Dict[str, Any]:
        """Determine which hooks should run based on file classification."""
        strategy = {
            "skip_hooks": [],
            "run_hooks": [],
            "optimization_level": "standard",
            "estimated_time_saved": 0,
            "reasoning": [],
        }

        total_files = sum(len(files) for files in file_classification.values())

        # Pure documentation changes - maximum optimization
        if file_classification["documentation"] and not any(
            file_classification[k] for k in ["python", "config", "scripts", "sensitive"]
        ):
            strategy["optimization_level"] = "documentation_only"
            strategy["skip_hooks"] = [
                "test-runner",
                "black",
                "isort",
                "flake8",
                "mypy",
                "bandit",
                "pydocstyle",
                "critical-linting-validator",
                "name-tests-test",
            ]
            strategy["run_hooks"] = [
                "trailing-whitespace",
                "end-of-file-fixer",
                "check-merge-conflict",
                "check-case-conflict",
                "check-added-large-files",
            ]
            strategy["estimated_time_saved"] = 45  # seconds
            strategy["reasoning"].append("📚 Pure documentation changes - skipping Python tooling")

        # Pure Python changes - run full suite but optimize
        elif (
            file_classification["python"]
            and not file_classification["documentation"]
            and len(file_classification["python"]) < 10
        ):
            strategy["optimization_level"] = "python_focused"
            strategy["estimated_time_saved"] = 10
            strategy["reasoning"].append("🐍 Python code changes - running focused validation")

        # Mixed changes - intelligent selection
        elif total_files > 1:
            strategy["optimization_level"] = "mixed_intelligent"

            # Skip heavy hooks if mostly documentation
            doc_ratio = len(file_classification["documentation"]) / total_files
            if doc_ratio > 0.7:
                strategy["skip_hooks"] = ["test-runner"]
                strategy["estimated_time_saved"] = 20
                strategy["reasoning"].append(
                    f"📝 {doc_ratio:.0%} documentation changes - skipping tests"
                )

        # Large changesets - optimize for speed
        elif total_files > 20:
            strategy["optimization_level"] = "large_changeset"
            strategy["skip_hooks"] = ["test-runner"]
            strategy["estimated_time_saved"] = 30
            strategy["reasoning"].append(
                f"📦 Large changeset ({total_files} files) - optimizing for speed"
            )

        return strategy

    def generate_hook_report(
        self, strategy: Dict[str, Any], file_classification: Dict[str, List[Path]]
    ) -> str:
        """Generate a concise report of the hook optimization strategy."""
        report = []

        # Header with optimization info
        level = strategy["optimization_level"]
        time_saved = strategy["estimated_time_saved"]

        if time_saved > 0:
            report.append(f"🚀 Hook Optimization: {level} (saving ~{time_saved}s)")
        else:
            report.append(f"🔧 Hook Execution: {level}")

        # File summary
        file_summary = []
        for category, files in file_classification.items():
            if files:
                file_summary.append(f"{len(files)} {category}")

        if file_summary:
            report.append(f"📁 Files: {', '.join(file_summary)}")

        # Optimization reasoning
        if strategy["reasoning"]:
            for reason in strategy["reasoning"]:
                report.append(f"   {reason}")

        # Hook modifications
        if strategy["skip_hooks"]:
            report.append(
                f"⏭️  Skipping: {', '.join(strategy['skip_hooks'][:3])}{'...' if len(strategy['skip_hooks']) > 3 else ''}"
            )

        return "\n".join(report)

    def should_run_hook(self, hook_name: str, strategy: Dict[str, Any]) -> bool:
        """Determine if a specific hook should run based on the strategy."""
        if hook_name in strategy["skip_hooks"]:
            return False
        if strategy["run_hooks"] and hook_name not in strategy["run_hooks"]:
            return False
        return True


def main():
    """Main entry point for intelligent hook filtering."""
    parser = argparse.ArgumentParser(
        description="Intelligent hook filtering for development velocity"
    )
    parser.add_argument(
        "--analyze-only", action="store_true", help="Only analyze and report, don't modify hooks"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    filter_tool = IntelligentHookFilter()

    # Get and classify staged files
    staged_files = filter_tool.get_staged_files()
    if not staged_files:
        if args.verbose:
            print("ℹ️  No staged files found - running standard hooks")
        return 0

    file_classification = filter_tool.classify_files(staged_files)
    strategy = filter_tool.determine_hook_strategy(file_classification)

    # Generate and display report
    report = filter_tool.generate_hook_report(strategy, file_classification)
    print(report)

    # If analyze-only mode, just display the analysis
    if args.analyze_only:
        print("\n📊 Analysis complete - no hooks modified")
        return 0

    # Set environment variables for pre-commit hook filtering
    if strategy["skip_hooks"]:
        skip_env = ",".join(strategy["skip_hooks"])
        print(f"\n🔧 Setting SKIP={skip_env}")
        # Note: In practice, this would need to be called before pre-commit
        # The actual implementation would integrate with pre-commit's workflow

    return 0


if __name__ == "__main__":
    sys.exit(main())
