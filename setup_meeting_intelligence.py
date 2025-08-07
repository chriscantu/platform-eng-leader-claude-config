#!/usr/bin/env python3
"""
SuperClaude Meeting Intelligence Setup
Python-based setup for automated meeting tracking and strategic memory integration
"""

import subprocess
import sys
from pathlib import Path

from memory.meeting_intelligence import MeetingIntelligenceManager


class MeetingIntelligenceSetup:
    """Setup and configuration for the SuperClaude Meeting Intelligence System."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.memory_dir = self.project_root / "memory"
        self.workspace_dir = self.project_root / "workspace"

    def print_header(self):
        """Print setup header with branding."""
        print("🎯 SuperClaude Meeting Intelligence Setup")
        print("=" * 55)
        print("Python-based strategic meeting tracking and memory integration")
        print()

    def install_dependencies(self) -> bool:
        """Install required Python dependencies."""
        print("📦 Installing Python dependencies...")

        dependencies = ["watchdog"]

        for dep in dependencies:
            try:
                print(f"   Installing {dep}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                print(f"   ✅ {dep} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to install {dep}: {e}")
                print(f"      Error output: {e.stderr}")
                return False

        return True

    def setup_database_schema(self) -> bool:
        """Apply enhanced database schema for meeting intelligence."""
        print("\n🗄️  Setting up strategic memory database...")

        try:
            manager = MeetingIntelligenceManager()
            print("   ✅ Enhanced database schema applied")
            return True
        except Exception as e:
            print(f"   ❌ Database setup failed: {e}")
            return False

    def scan_existing_meetings(self) -> dict:
        """Scan existing meeting-prep directory for intelligence."""
        print("\n🔍 Scanning existing meeting preparations...")

        try:
            manager = MeetingIntelligenceManager()
            results = manager.scan_and_process_meeting_prep()

            print(f"   ✅ Processed {results['processed']} meeting directories")
            print(f"   📊 New meetings: {results['new_meetings']}")
            print(f"   🔄 Updated meetings: {results['updated_meetings']}")

            if results["errors"]:
                print(f"   ⚠️  {len(results['errors'])} errors encountered:")
                for error in results["errors"][:3]:  # Show first 3 errors
                    print(f"      • {error}")

            return results
        except Exception as e:
            print(f"   ❌ Meeting scan failed: {e}")
            return {"processed": 0, "new_meetings": 0, "updated_meetings": 0, "errors": [str(e)]}

    def show_intelligence_summary(self):
        """Display current meeting intelligence summary."""
        print("\n📊 Meeting Intelligence Summary:")

        try:
            manager = MeetingIntelligenceManager()
            summary = manager.get_meeting_intelligence_summary()

            print(f"   Total meetings tracked: {summary['total_meetings']}")

            if summary["meeting_types"]:
                print("   Meeting Types:")
                for mt in summary["meeting_types"]:
                    print(f"      • {mt['meeting_type']}: {mt['count']} meetings")

            if summary["stakeholder_frequency"]:
                print("   Stakeholder Frequency:")
                for sf in summary["stakeholder_frequency"][:5]:  # Top 5
                    stakeholder = sf["stakeholder_primary"] or "Unknown"
                    print(f"      • {stakeholder}: {sf['count']} meetings")

            if summary["recent_meetings"]:
                print("   Recent Meetings:")
                for rm in summary["recent_meetings"][:3]:  # Most recent 3
                    print(f"      • {rm['meeting_key']} ({rm['meeting_type']})")

        except Exception as e:
            print(f"   ❌ Could not retrieve intelligence summary: {e}")

    def verify_setup(self) -> bool:
        """Verify the setup was successful."""
        print("\n🔍 Verifying setup...")

        checks = {
            "Database accessible": self._check_database(),
            "Workspace directory exists": self.workspace_dir.exists(),
            "Meeting-prep directory exists": (self.workspace_dir / "meeting-prep").exists(),
            "Python modules importable": self._check_imports(),
        }

        all_passed = True
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False

        return all_passed

    def _check_database(self) -> bool:
        """Check if database is accessible."""
        try:
            manager = MeetingIntelligenceManager()
            manager.get_meeting_intelligence_summary()
            return True
        except Exception:
            return False

    def _check_imports(self) -> bool:
        """Check if required modules can be imported."""
        try:
            import watchdog

            from memory.meeting_intelligence import MeetingIntelligenceManager
            from memory.workspace_monitor import WorkspaceMonitor

            return True
        except ImportError:
            return False

    def print_usage_guide(self):
        """Print comprehensive usage guide."""
        print("\n🎉 Setup Complete! Meeting Intelligence System is now active.")
        print("\n📚 Available Commands:")

        commands = [
            ("Scan meeting preparations", "python memory/meeting_intelligence.py --scan"),
            ("Show intelligence summary", "python memory/meeting_intelligence.py --summary"),
            ("Start filesystem monitoring", "python memory/workspace_monitor.py"),
            ("Run system demonstration", "python demo-meeting-intelligence.py"),
            ("Test workspace handler", "python memory/workspace_monitor.py --test"),
        ]

        for description, command in commands:
            print(f"   • {description}")
            print(f"     {command}")
            print()

        print("🚀 Automatic Features Now Active:")
        features = [
            "Existing meeting data captured and analyzed",
            "Strategic stakeholder detection (Raghu, VP Engineering, etc.)",
            "Meeting type classification (1-on-1s, VP meetings, etc.)",
            "Agenda item and strategic theme extraction",
            "SuperClaude persona recommendations",
            "Automatic template creation for new directories",
        ]

        for feature in features:
            print(f"   ✅ {feature}")

        print("\n🔮 Next Steps:")
        next_steps = [
            "Start the workspace monitor: python memory/workspace_monitor.py",
            "Create new directories in workspace/meeting-prep/",
            "Watch automatic intelligence capture and template creation",
            "Review captured data: python memory/meeting_intelligence.py --summary",
        ]

        for i, step in enumerate(next_steps, 1):
            print(f"   {i}. {step}")

        print("\n💡 Strategic Value:")
        values = [
            "Persistent meeting context across sessions",
            "Automatic stakeholder relationship tracking",
            "Strategic theme analysis and pattern recognition",
            "Cross-meeting intelligence for better preparation",
            "Enterprise-grade Python infrastructure reliability",
        ]

        for value in values:
            print(f"   • {value}")

    def run_setup(self) -> bool:
        """Run the complete setup process."""
        self.print_header()

        # Step 1: Install dependencies
        if not self.install_dependencies():
            print("\n❌ Setup failed at dependency installation")
            return False

        # Step 2: Setup database
        if not self.setup_database_schema():
            print("\n❌ Setup failed at database configuration")
            return False

        # Step 3: Scan existing meetings
        scan_results = self.scan_existing_meetings()

        # Step 4: Show intelligence summary
        self.show_intelligence_summary()

        # Step 5: Verify setup
        if not self.verify_setup():
            print("\n⚠️  Setup completed with some issues - see verification results above")

        # Step 6: Print usage guide
        self.print_usage_guide()

        return True


def main():
    """Main entry point for setup script."""
    import argparse

    parser = argparse.ArgumentParser(description="SuperClaude Meeting Intelligence Setup")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing setup")
    parser.add_argument("--scan-only", action="store_true", help="Only scan existing meetings")
    parser.add_argument(
        "--summary-only", action="store_true", help="Only show intelligence summary"
    )

    args = parser.parse_args()

    setup = MeetingIntelligenceSetup()

    if args.verify_only:
        setup.print_header()
        setup.verify_setup()
    elif args.scan_only:
        setup.print_header()
        setup.scan_existing_meetings()
        setup.show_intelligence_summary()
    elif args.summary_only:
        setup.print_header()
        setup.show_intelligence_summary()
    else:
        # Full setup
        success = setup.run_setup()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
