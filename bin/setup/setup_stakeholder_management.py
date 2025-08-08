#!/usr/bin/env python3
"""
Setup script for ClaudeDirector Stakeholder Management System
Initializes the system and provides guidance for strategic relationship management
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from memory.stakeholder_engagement_engine import StakeholderEngagementEngine


class StakeholderManagementSetup:
    """Setup and configuration for strategic stakeholder management"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.memory_dir = self.project_root / "memory"

    def print_header(self):
        """Print setup header with branding"""
        print("🎯 ClaudeDirector Stakeholder Management System")
        print("=" * 50)
        print("Strategic relationship intelligence for engineering directors")
        print("Proactive engagement management with AI-powered recommendations")
        print()

    def initialize_system(self) -> bool:
        """Initialize the stakeholder management system"""
        print("🔧 Initializing stakeholder management system...")

        try:
            engine = StakeholderEngagementEngine()

            # Apply database schema
            if not engine.apply_engagement_schema():
                print("   ❌ Failed to apply database schema")
                return False

            print("   ✅ Database schema applied successfully")

            # Create sample stakeholders for demonstration
            self._create_sample_stakeholders(engine)

            # Generate initial recommendations
            recommendations = engine.generate_engagement_recommendations()
            print(f"   ✅ Generated {len(recommendations)} initial recommendations")

            return True

        except Exception as e:
            print(f"   ❌ System initialization failed: {e}")
            return False

    def _create_sample_stakeholders(self, engine: StakeholderEngagementEngine):
        """Create sample stakeholders to demonstrate the system"""
        print("   📝 Creating sample stakeholder profiles...")

        sample_stakeholders = [
            {
                "stakeholder_key": "vp_engineering",
                "display_name": "VP Engineering",
                "role_title": "Vice President of Engineering",
                "organization": "Engineering",
                "strategic_importance": "critical",
                "frequency": "weekly",
                "channels": ["in_person", "slack"],
                "style": "data_driven",
                "personas": ["camille", "alvaro"],
            },
            {
                "stakeholder_key": "product_director",
                "display_name": "Director of Product",
                "role_title": "Director of Product Management",
                "organization": "Product",
                "strategic_importance": "high",
                "frequency": "biweekly",
                "channels": ["video", "slack"],
                "style": "collaborative",
                "personas": ["alvaro", "rachel"],
            },
            {
                "stakeholder_key": "design_director",
                "display_name": "Director of Design",
                "role_title": "Director of Design Systems",
                "organization": "Design",
                "strategic_importance": "high",
                "frequency": "biweekly",
                "channels": ["in_person", "video"],
                "style": "visual",
                "personas": ["rachel", "diego"],
            },
        ]

        for stakeholder in sample_stakeholders:
            # Add basic stakeholder
            engine.add_stakeholder(
                stakeholder_key=stakeholder["stakeholder_key"],
                display_name=stakeholder["display_name"],
                role_title=stakeholder["role_title"],
                organization=stakeholder["organization"],
                strategic_importance=stakeholder["strategic_importance"],
            )

            # Update detailed preferences
            try:
                with engine.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE stakeholder_profiles_enhanced
                        SET optimal_meeting_frequency = ?,
                            preferred_communication_channels = ?,
                            communication_style = ?,
                            most_effective_personas = ?
                        WHERE stakeholder_key = ?
                    """,
                        (
                            stakeholder["frequency"],
                            json.dumps(stakeholder["channels"]),
                            stakeholder["style"],
                            json.dumps(stakeholder["personas"]),
                            stakeholder["stakeholder_key"],
                        ),
                    )

            except Exception as e:
                print(
                    f"      ⚠️  Failed to update preferences for {stakeholder['stakeholder_key']}: {e}"
                )

        print(f"   ✅ Created {len(sample_stakeholders)} sample stakeholder profiles")

    def create_alert_system(self) -> bool:
        """Create proactive alert and notification system"""
        print("\n🔔 Setting up proactive engagement alerts...")

        # Create a simple daily alert script
        alert_script_path = self.project_root / "daily_stakeholder_alerts.py"

        alert_script_content = '''#!/usr/bin/env python3
"""
Daily Stakeholder Engagement Alerts
Runs daily to check for engagement opportunities and send notifications
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from memory.stakeholder_engagement_engine import StakeholderEngagementEngine


def check_daily_alerts():
    """Check for urgent stakeholder engagement opportunities"""
    print("🔔 ClaudeDirector Daily Stakeholder Alerts")
    print("=" * 45)

    engine = StakeholderEngagementEngine()

    # Generate fresh recommendations
    recommendations = engine.generate_engagement_recommendations()

    # Filter for urgent and high priority
    urgent_recs = [r for r in recommendations if r.get('urgency_level') in ['urgent', 'high']]

    if not urgent_recs:
        print("✅ No urgent stakeholder engagements needed today")
        return

    print(f"⚠️  {len(urgent_recs)} urgent/high priority engagement opportunities:")
    print()

    for rec in urgent_recs:
        urgency_emoji = '🔴' if rec.get('urgency_level') == 'urgent' else '🟡'
        print(f"{urgency_emoji} {rec['stakeholder_key']}")
        print(f"   Reason: {rec['trigger_reason']}")
        print(f"   Suggested: {rec['suggested_approach']}")
        print()

    print("💡 Use 'python stakeholder_manager.py recommendations' for full details")


if __name__ == "__main__":
    check_daily_alerts()
'''

        try:
            with open(alert_script_path, "w") as f:
                f.write(alert_script_content)

            # Make script executable
            alert_script_path.chmod(0o755)

            print("   ✅ Created daily alert script: daily_stakeholder_alerts.py")

            return True

        except Exception as e:
            print(f"   ❌ Failed to create alert system: {e}")
            return False

    def show_usage_guide(self):
        """Display comprehensive usage guide"""
        print("\n🎉 Stakeholder Management System Ready!")
        print("\n📚 Core Commands:")

        commands = [
            (
                "Add stakeholder",
                "python stakeholder_manager.py add",
                "Interactive stakeholder creation",
            ),
            (
                "List stakeholders",
                "python stakeholder_manager.py list",
                "View all tracked stakeholders",
            ),
            (
                "Record engagement",
                "python stakeholder_manager.py engage",
                "Log meetings and interactions",
            ),
            (
                "View recommendations",
                "python stakeholder_manager.py recommendations",
                "See engagement opportunities",
            ),
            (
                "Stakeholder details",
                "python stakeholder_manager.py show vp_engineering",
                "Detailed relationship view",
            ),
            (
                "Generate fresh recs",
                "python stakeholder_manager.py generate",
                "Update recommendations",
            ),
        ]

        for description, command, details in commands:
            print(f"   • {description}")
            print(f"     {command}")
            print(f"     💡 {details}")
            print()

        print("🚀 Automated Features:")
        features = [
            "Proactive engagement recommendations based on relationship patterns",
            "Strategic importance scoring and priority management",
            "Communication preference tracking and optimization",
            "Meeting frequency analysis and overdue detection",
            "SuperClaude persona effectiveness tracking",
            "Strategic project and stakeholder interest mapping",
        ]

        for feature in features:
            print(f"   ✅ {feature}")

        print("\n💡 Daily Workflow:")
        workflow = [
            "Morning: Run 'python daily_stakeholder_alerts.py' for urgent items",
            "Weekly: Review 'python stakeholder_manager.py recommendations'",
            "After meetings: Record with 'python stakeholder_manager.py engage'",
            "Monthly: Analyze relationship health and adjust strategies",
        ]

        for i, step in enumerate(workflow, 1):
            print(f"   {i}. {step}")

        print("\n🎯 Strategic Benefits:")
        benefits = [
            "Never miss critical stakeholder engagement opportunities",
            "Maintain consistent relationship momentum across all key stakeholders",
            "Optimize communication approach based on individual preferences",
            "Track relationship health and identify at-risk strategic partnerships",
            "Automate strategic relationship intelligence for executive effectiveness",
        ]

        for benefit in benefits:
            print(f"   • {benefit}")

    def demonstrate_system(self):
        """Show the system in action with sample data"""
        print("\n🎮 System Demonstration:")
        print("=" * 30)

        try:
            # Show sample recommendations
            engine = StakeholderEngagementEngine()
            recommendations = engine.get_pending_recommendations()

            if recommendations:
                print(f"📋 {len(recommendations)} engagement recommendations generated:")

                for i, rec in enumerate(recommendations[:3], 1):  # Show first 3
                    urgency_emoji = {"urgent": "🔴", "high": "🟡", "medium": "🟢", "low": "🔵"}.get(
                        rec["urgency_level"], "⚪"
                    )

                    print(f"\n   {i}. {urgency_emoji} {rec['display_name']}")
                    print(f"      {rec['recommendation_type'].replace('_', ' ').title()}")
                    print(f"      {rec['trigger_reason']}")
                    print(f"      💡 {rec['suggested_approach']}")

                if len(recommendations) > 3:
                    print(f"\n   ... and {len(recommendations) - 3} more recommendations")
            else:
                print("   No recommendations generated yet")

        except Exception as e:
            print(f"   ❌ Demo failed: {e}")

    def verify_setup(self) -> bool:
        """Verify the setup was successful"""
        print("\n🔍 Verifying setup...")

        checks = {
            "Database schema applied": self._check_database_schema(),
            "Stakeholder engine functional": self._check_stakeholder_engine(),
            "Alert system created": self._check_alert_system(),
            "Sample data loaded": self._check_sample_data(),
        }

        all_passed = True
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False

        return all_passed

    def _check_database_schema(self) -> bool:
        """Check if database schema is properly applied"""
        try:
            engine = StakeholderEngagementEngine()
            with engine.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='stakeholder_profiles_enhanced'
                """
                )
                return cursor.fetchone() is not None
        except Exception:
            return False

    def _check_stakeholder_engine(self) -> bool:
        """Check if stakeholder engine is functional"""
        try:
            engine = StakeholderEngagementEngine()
            # Try to generate recommendations (should work even with no data)
            engine.generate_engagement_recommendations()
            return True
        except Exception:
            return False

    def _check_alert_system(self) -> bool:
        """Check if alert system was created"""
        alert_script = self.project_root / "daily_stakeholder_alerts.py"
        return alert_script.exists()

    def _check_sample_data(self) -> bool:
        """Check if sample stakeholders were created"""
        try:
            engine = StakeholderEngagementEngine()
            with engine.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM stakeholder_profiles_enhanced")
                count = cursor.fetchone()[0]
                return count > 0
        except Exception:
            return False

    def run_setup(self) -> bool:
        """Run the complete setup process"""
        self.print_header()

        # Step 1: Initialize system
        if not self.initialize_system():
            print("\n❌ Setup failed at system initialization")
            return False

        # Step 2: Create alert system
        if not self.create_alert_system():
            print("\n❌ Setup failed at alert system creation")
            return False

        # Step 3: Demonstrate system
        self.demonstrate_system()

        # Step 4: Verify setup
        if not self.verify_setup():
            print("\n⚠️  Setup completed with some issues - see verification results above")

        # Step 5: Show usage guide
        self.show_usage_guide()

        return True


def main():
    """Main entry point for setup script"""
    import argparse

    parser = argparse.ArgumentParser(description="ClaudeDirector Stakeholder Management Setup")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing setup")
    parser.add_argument("--demo-only", action="store_true", help="Only show system demonstration")

    args = parser.parse_args()

    setup = StakeholderManagementSetup()

    if args.verify_only:
        setup.print_header()
        if setup.verify_setup():
            print("\n✅ All systems operational")
        else:
            print("\n❌ Issues detected - re-run setup")
        return

    if args.demo_only:
        setup.print_header()
        setup.demonstrate_system()
        return

    # Full setup
    if setup.run_setup():
        print("\n🎉 Stakeholder Management System setup complete!")
        print("\n🚀 Ready to revolutionize your strategic relationship management!")
    else:
        print("\n❌ Setup failed - please check error messages above")
        sys.exit(1)


if __name__ == "__main__":
    main()
