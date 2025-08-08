#!/usr/bin/env python3
"""
ClaudeDirector Stakeholder Manager
Comprehensive CLI tool for strategic stakeholder relationship management
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from memory.stakeholder_engagement_engine import StakeholderEngagementEngine


class StakeholderManager:
    """User-friendly CLI interface for stakeholder management"""

    def __init__(self):
        self.engine = StakeholderEngagementEngine()

    def add_stakeholder_interactive(self):
        """Interactive stakeholder addition"""
        print("🎯 Add New Stakeholder")
        print("=" * 30)

        stakeholder_key = input(
            "Stakeholder key (e.g., 'vp_engineering', 'rachel_design'): "
        ).strip()
        if not stakeholder_key:
            print("❌ Stakeholder key is required")
            return

        display_name = input("Full name: ").strip()
        if not display_name:
            print("❌ Display name is required")
            return

        role_title = input("Role/Title: ").strip()
        organization = input("Organization/Team: ").strip()

        print("\nStrategic Importance:")
        print("1. Critical (CEO, VP, direct impact on major decisions)")
        print("2. High (Senior leaders, key stakeholders)")
        print("3. Medium (Important partners, contributors)")
        print("4. Low (Occasional interaction)")

        importance_map = {"1": "critical", "2": "high", "3": "medium", "4": "low"}
        importance_choice = input("Select importance level (1-4): ").strip()
        strategic_importance = importance_map.get(importance_choice, "medium")

        # Optional: Communication preferences
        print(f"\nOptional: Communication preferences for {display_name}")
        frequency = input(
            "Meeting frequency (weekly/biweekly/monthly/quarterly/as_needed) [monthly]: "
        ).strip()
        if not frequency:
            frequency = "monthly"

        channels = input(
            "Preferred channels (comma-separated: slack,email,in_person,video) [in_person]: "
        ).strip()
        if not channels:
            channels = "in_person"
        channel_list = [c.strip() for c in channels.split(",")]

        style = input(
            "Communication style (direct/collaborative/data_driven/narrative/visual) [collaborative]: "
        ).strip()
        if not style:
            style = "collaborative"

        # Add stakeholder to database
        success = self.engine.add_stakeholder(
            stakeholder_key=stakeholder_key,
            display_name=display_name,
            role_title=role_title,
            organization=organization,
            strategic_importance=strategic_importance,
        )

        if success:
            # Update preferences if provided
            try:
                with self.engine.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE stakeholder_profiles_enhanced
                        SET optimal_meeting_frequency = ?,
                            preferred_communication_channels = ?,
                            communication_style = ?
                        WHERE stakeholder_key = ?
                    """,
                        (frequency, json.dumps(channel_list), style, stakeholder_key),
                    )

                print(f"✅ Added stakeholder: {display_name} ({stakeholder_key})")
                print(f"   Strategic importance: {strategic_importance}")
                print(f"   Meeting frequency: {frequency}")
                print(f"   Communication style: {style}")

                # Generate initial recommendations
                self.engine.generate_engagement_recommendations()
                print("\n💡 Generated initial engagement recommendations")

            except Exception as e:
                print(f"⚠️  Stakeholder added but failed to update preferences: {e}")
        else:
            print("❌ Failed to add stakeholder")

    def record_engagement_interactive(self):
        """Interactive engagement recording"""
        print("📝 Record Stakeholder Engagement")
        print("=" * 35)

        # Show available stakeholders
        self.list_stakeholders(brief=True)

        stakeholder_key = input("\nStakeholder key: ").strip()
        if not stakeholder_key:
            print("❌ Stakeholder key is required")
            return

        print("\nEngagement Type:")
        print("1. Meeting (formal scheduled meeting)")
        print("2. Slack (informal chat/quick sync)")
        print("3. Email (email exchange)")
        print("4. Informal (hallway conversation, etc.)")
        print("5. Strategic session (planning, review, etc.)")

        type_map = {
            "1": "meeting",
            "2": "slack",
            "3": "email",
            "4": "informal",
            "5": "strategic_session",
        }
        type_choice = input("Select engagement type (1-5): ").strip()
        engagement_type = type_map.get(type_choice, "meeting")

        engagement_date = input("Date (YYYY-MM-DD) [today]: ").strip()
        if not engagement_date:
            engagement_date = datetime.now().strftime("%Y-%m-%d")

        print("\nEngagement Quality:")
        print("1. Excellent (very productive, strong outcomes)")
        print("2. Good (productive, positive)")
        print("3. Adequate (okay, neutral)")
        print("4. Poor (unproductive, issues)")

        quality_map = {"1": "excellent", "2": "good", "3": "adequate", "4": "poor"}
        quality_choice = input("Select quality (1-4): ").strip()
        engagement_quality = quality_map.get(quality_choice, "good")

        # Optional: Topics and outcomes
        topics_input = input("\nTopics discussed (comma-separated): ").strip()
        topics_discussed = [t.strip() for t in topics_input.split(",")] if topics_input else []

        action_items = []
        print("\nAction items (press Enter on empty line to finish):")
        while True:
            action = input("Action item: ").strip()
            if not action:
                break
            owner = input("Owner: ").strip()
            due_date = input("Due date (YYYY-MM-DD): ").strip()
            action_items.append({"action": action, "owner": owner, "due_date": due_date})

        # Record engagement
        success = self.engine.record_engagement(
            stakeholder_key=stakeholder_key,
            engagement_type=engagement_type,
            engagement_date=engagement_date,
            engagement_quality=engagement_quality,
            topics_discussed=topics_discussed,
            action_items=action_items,
        )

        if success:
            print(f"✅ Recorded engagement with {stakeholder_key}")
            print(f"   Type: {engagement_type}")
            print(f"   Quality: {engagement_quality}")
            print(f"   Topics: {', '.join(topics_discussed)}")
            if action_items:
                print(f"   Action items: {len(action_items)}")
        else:
            print("❌ Failed to record engagement")

    def show_recommendations(self, urgency_filter=None):
        """Show pending recommendations with enhanced formatting"""
        print("🧠 Strategic Engagement Recommendations")
        print("=" * 45)

        recommendations = self.engine.get_pending_recommendations(urgency_filter)

        if not recommendations:
            print("🎉 No pending recommendations found!")
            print("All stakeholder relationships are up to date.")
            return

        # Group by urgency
        by_urgency = {}
        for rec in recommendations:
            urgency = rec["urgency_level"]
            if urgency not in by_urgency:
                by_urgency[urgency] = []
            by_urgency[urgency].append(rec)

        urgency_order = ["urgent", "high", "medium", "low"]
        urgency_emojis = {
            "urgent": "🔴 URGENT",
            "high": "🟡 HIGH",
            "medium": "🟢 MEDIUM",
            "low": "🔵 LOW",
        }

        for urgency in urgency_order:
            if urgency not in by_urgency:
                continue

            print(f"\n{urgency_emojis[urgency]} Priority ({len(by_urgency[urgency])} items)")
            print("-" * 30)

            for rec in by_urgency[urgency]:
                print(f"👤 {rec['display_name']} ({rec['stakeholder_key']})")
                print(f"   📋 {rec['recommendation_type'].replace('_', ' ').title()}")
                print(f"   💡 {rec['trigger_reason']}")
                print(f"   🎯 {rec['suggested_approach']}")
                print(f"   📊 Confidence: {rec['confidence_score']:.1%}")
                print()

    def list_stakeholders(self, brief=False):
        """List all stakeholders with summary info"""
        try:
            with self.engine.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT stakeholder_key, display_name, role_title, organization,
                           strategic_importance, optimal_meeting_frequency
                    FROM stakeholder_profiles_enhanced
                    ORDER BY
                        CASE strategic_importance
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2
                            WHEN 'medium' THEN 3
                            WHEN 'low' THEN 4
                            ELSE 5
                        END,
                        display_name
                """
                )

                stakeholders = cursor.fetchall()

                if not stakeholders:
                    print("No stakeholders found. Add some with 'add' command.")
                    return

                if brief:
                    print("\nAvailable stakeholders:")
                    for s in stakeholders:
                        importance_emoji = {
                            "critical": "🔴",
                            "high": "🟡",
                            "medium": "🟢",
                            "low": "🔵",
                        }.get(s[4], "⚪")
                        print(f"  {importance_emoji} {s[0]} - {s[1]}")
                    return

                print("👥 Stakeholder Directory")
                print("=" * 25)

                for stakeholder in stakeholders:
                    key, name, role, org, importance, frequency = stakeholder

                    importance_emoji = {
                        "critical": "🔴",
                        "high": "🟡",
                        "medium": "🟢",
                        "low": "🔵",
                    }.get(importance, "⚪")

                    print(f"{importance_emoji} {name} ({key})")
                    if role:
                        print(f"   📋 {role}")
                    if org:
                        print(f"   🏢 {org}")
                    print(f"   📅 {frequency or 'as_needed'} meetings")
                    print(f"   🎯 {importance} strategic importance")

                    # Get last engagement
                    cursor.execute(
                        """
                        SELECT engagement_date, engagement_type
                        FROM stakeholder_engagements
                        WHERE stakeholder_key = ?
                        ORDER BY engagement_date DESC
                        LIMIT 1
                    """,
                        (key,),
                    )

                    last_engagement = cursor.fetchone()
                    if last_engagement:
                        last_date = last_engagement[0]
                        last_type = last_engagement[1]
                        print(f"   🕒 Last contact: {last_date} ({last_type})")
                    else:
                        print(f"   🕒 No recorded engagements")

                    print()

        except Exception as e:
            print(f"❌ Failed to list stakeholders: {e}")

    def stakeholder_detail(self, stakeholder_key):
        """Show detailed stakeholder information"""
        summary = self.engine.get_stakeholder_summary(stakeholder_key)

        if not summary:
            print(f"❌ Stakeholder '{stakeholder_key}' not found")
            return

        print(f"👤 {summary['display_name']} ({stakeholder_key})")
        print("=" * (len(summary["display_name"]) + len(stakeholder_key) + 5))

        print(f"📋 Role: {summary['role_title'] or 'Not specified'}")
        print(f"🏢 Organization: {summary['organization'] or 'Not specified'}")
        print(f"🎯 Strategic Importance: {summary['strategic_importance']}")

        if summary["preferred_channels"]:
            print(f"📞 Preferred Channels: {', '.join(summary['preferred_channels'])}")

        if summary["effective_personas"]:
            print(f"🎭 Effective Personas: {', '.join(summary['effective_personas'])}")

        print(f"\n📈 Recent Engagements ({len(summary['recent_engagements'])}):")
        if summary["recent_engagements"]:
            for eng in summary["recent_engagements"]:
                quality_emoji = {"excellent": "🟢", "good": "🟡", "adequate": "🟠", "poor": "🔴"}.get(
                    eng["quality"], "⚪"
                )

                print(f"  {quality_emoji} {eng['date']} - {eng['type']} ({eng['quality']})")
                if eng["topics"]:
                    print(f"     Topics: {', '.join(eng['topics'])}")
        else:
            print("  No recorded engagements")

        print(f"\n💡 Pending Recommendations ({len(summary['pending_recommendations'])}):")
        if summary["pending_recommendations"]:
            for rec in summary["pending_recommendations"]:
                urgency_emoji = {"urgent": "🔴", "high": "🟡", "medium": "🟢", "low": "🔵"}.get(
                    rec["urgency"], "⚪"
                )

                print(f"  {urgency_emoji} {rec['type'].replace('_', ' ').title()}")
                print(f"     {rec['reason']}")
                print(f"     💡 {rec['approach']}")
        else:
            print("  No pending recommendations")

    def generate_recommendations(self):
        """Generate fresh recommendations"""
        print("🧠 Generating engagement recommendations...")
        recommendations = self.engine.generate_engagement_recommendations()
        print(f"✅ Generated {len(recommendations)} recommendations")

        if recommendations:
            print("\n📋 Summary by urgency:")
            urgency_counts = {}
            for rec in recommendations:
                urgency = rec.get("urgency_level", "unknown")
                urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1

            for urgency, count in urgency_counts.items():
                emoji = {"urgent": "🔴", "high": "🟡", "medium": "🟢", "low": "🔵"}.get(urgency, "⚪")
                print(f"  {emoji} {urgency.title()}: {count}")


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="ClaudeDirector Stakeholder Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python stakeholder_manager.py add                    # Add stakeholder interactively
  python stakeholder_manager.py list                   # List all stakeholders
  python stakeholder_manager.py show vp_engineering    # Show detailed stakeholder info
  python stakeholder_manager.py engage                 # Record engagement interactively
  python stakeholder_manager.py recommendations        # Show pending recommendations
  python stakeholder_manager.py recommendations --urgency high  # Show high priority only
  python stakeholder_manager.py generate               # Generate fresh recommendations
  python stakeholder_manager.py init                   # Initialize the system
        """,
    )

    parser.add_argument(
        "command",
        choices=["init", "add", "list", "show", "engage", "recommendations", "generate"],
        help="Command to execute",
    )
    parser.add_argument("stakeholder", nargs="?", help="Stakeholder key (for 'show' command)")
    parser.add_argument(
        "--urgency",
        choices=["urgent", "high", "medium", "low"],
        help="Filter recommendations by urgency",
    )

    args = parser.parse_args()

    manager = StakeholderManager()

    try:
        if args.command == "init":
            print("🚀 Initializing ClaudeDirector Stakeholder Management System")
            print("=" * 60)
            if manager.engine.apply_engagement_schema():
                print("✅ Database schema applied successfully")
                print("\n💡 Next steps:")
                print("  1. Add stakeholders: python stakeholder_manager.py add")
                print("  2. Record engagements: python stakeholder_manager.py engage")
                print("  3. Check recommendations: python stakeholder_manager.py recommendations")
            else:
                print("❌ Failed to initialize database schema")
                sys.exit(1)

        elif args.command == "add":
            manager.add_stakeholder_interactive()

        elif args.command == "list":
            manager.list_stakeholders()

        elif args.command == "show":
            if not args.stakeholder:
                print("❌ Stakeholder key required for 'show' command")
                print("Usage: python stakeholder_manager.py show <stakeholder_key>")
                sys.exit(1)
            manager.stakeholder_detail(args.stakeholder)

        elif args.command == "engage":
            manager.record_engagement_interactive()

        elif args.command == "recommendations":
            manager.show_recommendations(args.urgency)

        elif args.command == "generate":
            manager.generate_recommendations()

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
