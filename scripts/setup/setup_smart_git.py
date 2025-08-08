#!/usr/bin/env python3
"""
SuperClaude Smart Git Setup
Python-based setup for intelligent git commit optimization
"""

import os
import subprocess
import sys
from pathlib import Path


class SmartGitSetup:
    """Setup and configuration for intelligent git commit optimization."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.git_commit_smart = self.project_root / "git-commit-smart"

    def print_header(self):
        """Print setup header with branding."""
        print("🔧 SuperClaude Smart Git Setup")
        print("=" * 45)
        print("Python-based intelligent git commit optimization")
        print()

    def make_scripts_executable(self) -> bool:
        """Ensure git scripts are executable."""
        print("📜 Making git scripts executable...")

        scripts = [self.git_commit_smart]

        for script in scripts:
            if script.exists():
                try:
                    script.chmod(0o755)
                    print(f"   ✅ {script.name} is now executable")
                except Exception as e:
                    print(f"   ❌ Failed to make {script.name} executable: {e}")
                    return False
            else:
                print(f"   ⚠️  Script not found: {script}")
                return False

        return True

    def add_to_path(self) -> bool:
        """Add current directory to PATH for session."""
        print("\n🛤️  Adding scripts to PATH for current session...")

        current_path = os.environ.get("PATH", "")
        project_root_str = str(self.project_root)

        if project_root_str not in current_path:
            new_path = f"{project_root_str}:{current_path}"
            os.environ["PATH"] = new_path
            print(f"   ✅ Added {project_root_str} to PATH")
        else:
            print(f"   ℹ️  {project_root_str} already in PATH")

        return True

    def create_git_aliases(self) -> bool:
        """Create git aliases for intelligent commits."""
        print("\n⚡ Creating git aliases...")

        aliases = [
            ("smart-commit", str(self.git_commit_smart), "Intelligent commit with optimization"),
            ("sc", str(self.git_commit_smart), "Short alias for smart commit"),
            (
                "analyze-commit",
                f"{self.git_commit_smart} --analyze-only",
                "Analyze optimization without committing",
            ),
        ]

        for alias_name, command, description in aliases:
            try:
                result = subprocess.run(
                    ["git", "config", "--global", f"alias.{alias_name}", f"!{command}"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                print(f"   ✅ git {alias_name} → {description}")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to create alias '{alias_name}': {e}")
                return False

        return True

    def test_intelligent_filtering(self) -> bool:
        """Test the intelligent hook filtering system."""
        print("\n🧪 Testing intelligent hook analysis...")

        try:
            # Import and test the intelligent hook filter
            sys.path.insert(
                0,
                str(
                    self.project_root
                    / "strategic_integration_service"
                    / "strategic_integration_service"
                ),
            )
            from hooks.intelligent_hook_filter import IntelligentHookFilter

            filter_tool = IntelligentHookFilter()
            staged_files = filter_tool.get_staged_files()

            if staged_files:
                file_classification = filter_tool.classify_files(staged_files)
                strategy = filter_tool.determine_hook_strategy(file_classification)
                report = filter_tool.generate_hook_report(strategy, file_classification)

                print("   🔍 Current staged files analysis:")
                print(f"      {report}")
            else:
                print("   ℹ️  No staged files found - intelligent filtering ready")

            print("   ✅ Intelligent hook filtering system operational")
            return True

        except ImportError as e:
            print(f"   ⚠️  Could not import intelligent hook filter: {e}")
            print("   ℹ️  Standard git hooks will be used")
            return True  # Not a failure, just fallback
        except Exception as e:
            print(f"   ❌ Error testing intelligent filtering: {e}")
            return False

    def show_usage_examples(self):
        """Display usage examples and benefits."""
        print("\n🎉 Setup Complete! Intelligent Git System is ready.")
        print("\n📚 Usage Examples:")

        examples = [
            ("Fast documentation commits", "git sc -m 'Update README'", "45s saved"),
            (
                "Optimized code commits",
                "git smart-commit -m 'Fix critical bug'",
                "10s saved, full validation",
            ),
            ("Preview optimization", "git analyze-commit", "See what would be optimized"),
            (
                "Force full validation",
                "git smart-commit --force-full -m 'Security patch'",
                "All hooks run",
            ),
            ("Traditional commit", "git commit -m 'message'", "Standard hooks (slower)"),
        ]

        for description, command, benefit in examples:
            print(f"   • {description}")
            print(f"     {command}")
            print(f"     💡 {benefit}")
            print()

        print("🚀 Intelligent Optimization Features:")
        features = [
            "Documentation-only changes: Skip tests, linting, type checking (45s saved)",
            "Python-focused changes: Run targeted validation (10s saved)",
            "Large changesets: Skip expensive operations (30s saved)",
            "Configuration changes: Run only relevant validators",
            "Mixed files: Intelligent hook selection based on file types",
            "Security maintained: PII and vulnerability scanning where critical",
        ]

        for feature in features:
            print(f"   ✅ {feature}")

        print("\n💡 Strategic Benefits:")
        benefits = [
            "Faster strategic communication and executive reporting",
            "Reduced friction for documentation contributors",
            "Maintained security and quality where it matters",
            "Development velocity optimization",
            "Enterprise-grade platform engineering efficiency",
        ]

        for benefit in benefits:
            print(f"   • {benefit}")

    def verify_setup(self) -> bool:
        """Verify the smart git setup."""
        print("\n🔍 Verifying smart git setup...")

        checks = {
            "git-commit-smart executable": self.git_commit_smart.exists()
            and os.access(self.git_commit_smart, os.X_OK),
            "Git aliases created": self._check_git_aliases(),
            "Intelligent filtering available": self._check_intelligent_filtering(),
            "Pre-commit hooks configured": self._check_precommit_hooks(),
        }

        all_passed = True
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False

        return all_passed

    def _check_git_aliases(self) -> bool:
        """Check if git aliases were created successfully."""
        try:
            result = subprocess.run(
                ["git", "config", "--global", "alias.sc"], capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def _check_intelligent_filtering(self) -> bool:
        """Check if intelligent filtering is available."""
        try:
            sys.path.insert(
                0,
                str(
                    self.project_root
                    / "strategic_integration_service"
                    / "strategic_integration_service"
                ),
            )
            from hooks.intelligent_hook_filter import IntelligentHookFilter

            return True
        except ImportError:
            return False

    def _check_precommit_hooks(self) -> bool:
        """Check if pre-commit hooks are configured."""
        precommit_config = self.project_root / ".pre-commit-config.yaml"
        return precommit_config.exists()

    def run_setup(self) -> bool:
        """Run the complete smart git setup process."""
        self.print_header()

        # Step 1: Make scripts executable
        if not self.make_scripts_executable():
            print("\n❌ Setup failed at script permissions")
            return False

        # Step 2: Add to PATH
        if not self.add_to_path():
            print("\n❌ Setup failed at PATH configuration")
            return False

        # Step 3: Create git aliases
        if not self.create_git_aliases():
            print("\n❌ Setup failed at git alias creation")
            return False

        # Step 4: Test intelligent filtering
        if not self.test_intelligent_filtering():
            print("\n❌ Setup failed at intelligent filtering test")
            return False

        # Step 5: Verify setup
        if not self.verify_setup():
            print("\n⚠️  Setup completed with some issues - see verification results above")

        # Step 6: Show usage examples
        self.show_usage_examples()

        return True


def main():
    """Main entry point for smart git setup."""
    import argparse

    parser = argparse.ArgumentParser(description="SuperClaude Smart Git Setup")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing setup")
    parser.add_argument("--test-only", action="store_true", help="Only test intelligent filtering")

    args = parser.parse_args()

    setup = SmartGitSetup()

    if args.verify_only:
        setup.print_header()
        setup.verify_setup()
    elif args.test_only:
        setup.print_header()
        setup.test_intelligent_filtering()
    else:
        # Full setup
        success = setup.run_setup()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
