#!/usr/bin/env python3
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
    urgent_recs = [r for r in recommendations if r.get("urgency_level") in ["urgent", "high"]]

    if not urgent_recs:
        print("✅ No urgent stakeholder engagements needed today")
        return

    print(f"⚠️  {len(urgent_recs)} urgent/high priority engagement opportunities:")
    print()

    for rec in urgent_recs:
        urgency_emoji = "🔴" if rec.get("urgency_level") == "urgent" else "🟡"
        print(f"{urgency_emoji} {rec['stakeholder_key']}")
        print(f"   Reason: {rec['trigger_reason']}")
        print(f"   Suggested: {rec['suggested_approach']}")
        print()

    print("💡 Use 'python stakeholder_manager.py recommendations' for full details")


if __name__ == "__main__":
    check_daily_alerts()
