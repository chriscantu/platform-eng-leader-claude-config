#!/usr/bin/env python3
"""
Demo: SuperClaude Meeting Intelligence System
Shows automatic meeting tracking and strategic memory integration
"""

import json
import sqlite3
import time
from pathlib import Path

from memory.meeting_intelligence import MeetingIntelligenceManager


def demo_meeting_intelligence():
    """Demonstrate the meeting intelligence system capabilities."""
    print("🎯 SuperClaude Meeting Intelligence System Demo")
    print("=" * 55)

    manager = MeetingIntelligenceManager()

    # Show current state
    print("\n📊 Current Meeting Intelligence:")
    summary = manager.get_meeting_intelligence_summary()

    print(f"   Total meetings tracked: {summary['total_meetings']}")

    if summary["meeting_types"]:
        print("   Meeting Types:")
        for mt in summary["meeting_types"]:
            print(f"      {mt['meeting_type']}: {mt['count']} meetings")

    if summary["stakeholder_frequency"]:
        print("   Stakeholder Frequency:")
        for sf in summary["stakeholder_frequency"]:
            stakeholder = sf["stakeholder_primary"] or "unknown"
            print(f"      {stakeholder}: {sf['count']} meetings")

    # Show sample meeting data
    print("\n📄 Sample Meeting Data:")
    with sqlite3.connect(manager.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT meeting_key, meeting_type, stakeholder_primary,
                   agenda_items, strategic_themes, persona_activated
            FROM meeting_sessions
            LIMIT 2
        """
        )

        meetings = cursor.fetchall()
        for i, meeting in enumerate(meetings, 1):
            print(f"\n   Meeting {i}: {meeting['meeting_key']}")
            print(f"      Type: {meeting['meeting_type']}")
            print(f"      Stakeholder: {meeting['stakeholder_primary'] or 'Not detected'}")

            # Parse JSON fields safely
            try:
                agenda_items = json.loads(meeting["agenda_items"] or "[]")
                if agenda_items:
                    print(f"      Agenda Items: {len(agenda_items)} detected")
                    for item in agenda_items[:3]:  # Show first 3
                        print(f"         • {item}")
            except json.JSONDecodeError:
                pass

            try:
                personas = json.loads(meeting["persona_activated"] or "[]")
                if personas:
                    print(f"      Recommended Personas: {', '.join(personas)}")
            except json.JSONDecodeError:
                pass

    # Demonstrate directory creation simulation
    print("\n🔧 Demonstration: Create New Meeting Directory")
    demo_dir = Path("workspace/meeting-prep/demo-michael-1on1")

    if demo_dir.exists():
        print(f"   Demo directory already exists: {demo_dir}")
    else:
        print(f"   Creating demo directory: {demo_dir}")
        demo_dir.mkdir(parents=True, exist_ok=True)

        # Create sample prep file
        prep_file = demo_dir / "prep-notes.md"
        prep_content = """# 1-on-1 Prep: Michael
## Strategic Context
- Platform engineering velocity improvements
- Intelligent git hooks implementation success
- Meeting tracking system deployment

## Agenda Items
1. Review intelligent hooks adoption and feedback
2. Strategic platform roadmap alignment
3. Cross-team coordination opportunities
4. Resource allocation for Q1 initiatives
5. Executive communication strategy

## Key Topics
- Developer experience optimization
- Strategic automation initiatives
- Platform engineering excellence
"""
        prep_file.write_text(prep_content)
        print(f"   Created prep file: {prep_file.name}")

        # Process the new directory
        print("\n   🔍 Processing new meeting directory...")
        meeting_data = manager.parse_meeting_prep_directory(demo_dir)
        meeting_id = manager.store_meeting_session(meeting_data)

        print(f"   ✅ Meeting processed: {meeting_data['meeting_key']} -> ID {meeting_id}")
        print(f"   📊 Meeting Type: {meeting_data['meeting_type']}")
        print(f"   👤 Primary Stakeholder: {meeting_data['stakeholder_primary'] or 'Not detected'}")
        print(f"   🎭 Recommended Personas: {', '.join(meeting_data['persona_activated'])}")
        print(f"   📋 Agenda Items: {len(meeting_data['agenda_items'])} detected")

    # Show workspace monitoring capabilities
    print(f"\n🔍 Workspace Monitoring Capabilities:")
    print(f"   📁 Monitors: workspace/ directory recursively")
    print(f"   🎯 Detects: New directories, file changes, meeting prep updates")
    print(f"   🧠 Analyzes: Stakeholders, meeting types, strategic themes")
    print(f"   💾 Stores: Meeting intelligence in strategic memory database")
    print(f"   🤖 Triggers: Automatic template creation and persona suggestions")

    print(f"\n🚀 To Start Automatic Monitoring:")
    print(f"   python memory/workspace_monitor.py")
    print(f"   (Then create new directories in workspace/meeting-prep/)")

    print(f"\n✅ Demo Complete! Meeting Intelligence System is ready for production use.")


if __name__ == "__main__":
    demo_meeting_intelligence()
