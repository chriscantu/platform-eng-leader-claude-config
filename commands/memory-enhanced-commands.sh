#!/bin/bash

# SuperClaude Memory-Enhanced Commands
# Director of Engineering: Strategic context persistence integration

# Memory system configuration
MEMORY_MANAGER="/Users/chris.cantu/repos/platform-eng-leader-claude-config/memory/memory_manager.py"
MEMORY_DB_PATH="$HOME/.superclaude/memory/strategic_memory.db"

# Ensure Python requirements are available
check_dependencies() {
    if ! python3 -c "import sqlite3, json, pathlib" 2>/dev/null; then
        echo "⚠️  Required Python modules not available"
        echo "   Standard library modules should be available by default"
    fi
}

# Initialize memory system
init_memory() {
    echo "🧠 Initializing SuperClaude Strategic Memory System..."
    python3 "$MEMORY_MANAGER" test
    if [ $? -eq 0 ]; then
        echo "✅ Memory system initialized successfully"
        echo "📊 Database location: $MEMORY_DB_PATH"
        python3 "$MEMORY_MANAGER" stats
    else
        echo "❌ Memory system initialization failed"
        exit 1
    fi
}

# Memory-enhanced VP meeting preparation
prep_vp_meeting_memory() {
    local stakeholder_key="$1"
    local meeting_date="$2"

    if [ -z "$stakeholder_key" ]; then
        echo "Usage: prep_vp_meeting_memory <stakeholder_key> [meeting_date]"
        echo "Available stakeholders: vp_engineering, vp_product, vp_design"
        return 1
    fi

    if [ -z "$meeting_date" ]; then
        meeting_date=$(date +"%Y-%m-%d")
    fi

    echo "🎯 Preparing VP meeting with memory context..."
    echo "📋 Stakeholder: $stakeholder_key"
    echo "📅 Meeting Date: $meeting_date"
    echo ""

    # Retrieve stakeholder context
    echo "🔍 Retrieving stakeholder context..."
    python3 "$MEMORY_MANAGER" recall --type executive_session --stakeholder "$stakeholder_key" --days 90 > /tmp/stakeholder_context.json

    if [ $? -eq 0 ]; then
        echo "✅ Context retrieved successfully"

        # Extract key context for meeting prep
        python3 -c "
import json
import sys

try:
    with open('/tmp/stakeholder_context.json', 'r') as f:
        context = json.load(f)

    profile = context.get('profile', {})
    sessions = context.get('recent_sessions', [])

    print('📊 STAKEHOLDER CONTEXT SUMMARY')
    print('=' * 40)

    if profile:
        print(f'Name: {profile.get(\"display_name\", \"Unknown\")}')
        print(f'Role: {profile.get(\"role_title\", \"Unknown\")}')
        print(f'Communication Style: {profile.get(\"communication_style\", \"Unknown\")}')
        print(f'Relationship Strength: {profile.get(\"relationship_strength\", \"Unknown\")}/5')
        print(f'Preferred Personas: {profile.get(\"preferred_personas\", [])}')
        print('')

    if sessions:
        print('📋 RECENT INTERACTIONS')
        print('-' * 25)
        for session in sessions[:3]:  # Most recent 3
            print(f'Date: {session.get(\"meeting_date\", \"Unknown\")}')
            print(f'Type: {session.get(\"session_type\", \"Unknown\")}')
            print(f'Outcome Rating: {session.get(\"outcome_rating\", \"Unknown\")}/5')
            print(f'Persona Used: {session.get(\"persona_activated\", \"Unknown\")}')

            decisions = session.get('decisions_made', [])
            if decisions:
                print('Key Decisions:')
                for decision in decisions[:2]:  # Top 2 decisions
                    if isinstance(decision, dict):
                        print(f'  • {decision.get(\"decision\", decision)}')
                    else:
                        print(f'  • {decision}')

            action_items = session.get('action_items', [])
            if action_items:
                print('Outstanding Actions:')
                for action in action_items[:2]:  # Top 2 actions
                    if isinstance(action, dict):
                        print(f'  • {action.get(\"action\", action)}')
                    else:
                        print(f'  • {action}')
            print('')

        print(f'📈 Total Sessions (90 days): {context.get(\"session_count\", 0)}')
    else:
        print('ℹ️  No recent interaction history found')
        print('   This is a fresh stakeholder relationship')

except Exception as e:
    print(f'Error processing context: {str(e)}', file=sys.stderr)
    sys.exit(1)
"
    else
        echo "❌ Failed to retrieve stakeholder context"
        echo "   Creating new stakeholder profile..."
    fi

    # Get active initiatives context
    echo ""
    echo "🚀 ACTIVE INITIATIVES CONTEXT"
    echo "=" * 30
    python3 "$MEMORY_MANAGER" recall --type strategic_initiative --status in_progress > /tmp/initiatives_context.json

    python3 -c "
import json
import sys

try:
    with open('/tmp/initiatives_context.json', 'r') as f:
        context = json.load(f)

    initiatives = context.get('initiatives', [])

    if initiatives:
        print(f'Active Initiatives: {len(initiatives)}')
        print('-' * 20)

        # Group by risk level
        risk_groups = {'red': [], 'yellow': [], 'green': []}
        for init in initiatives:
            risk = init.get('risk_level', 'unknown')
            if risk in risk_groups:
                risk_groups[risk].append(init)

        for risk_level, risk_initiatives in risk_groups.items():
            if risk_initiatives:
                emoji = {'red': '🔴', 'yellow': '🟡', 'green': '🟢'}.get(risk_level, '⚫')
                print(f'{emoji} {risk_level.upper()} RISK ({len(risk_initiatives)})')

                for init in risk_initiatives[:3]:  # Top 3 per risk level
                    print(f'  • {init.get(\"initiative_key\", \"Unknown\")}: {init.get(\"initiative_name\", \"Unknown\")}')
                    print(f'    Status: {init.get(\"status\", \"Unknown\")} | Assignee: {init.get(\"assignee\", \"Unknown\")}')
                    if init.get('completion_probability'):
                        prob = int(init['completion_probability'] * 100)
                        print(f'    Completion Probability: {prob}%')
                print('')
    else:
        print('ℹ️  No active initiatives found')

except Exception as e:
    print(f'Error processing initiatives: {str(e)}', file=sys.stderr)
"

    echo ""
    echo "💡 MEETING PREPARATION RECOMMENDATIONS"
    echo "=" * 35
    echo "1. Review stakeholder communication style and adjust persona accordingly"
    echo "2. Address any outstanding action items from previous meetings"
    echo "3. Present initiative updates aligned with stakeholder priorities"
    echo "4. Prepare business impact narrative for any resource requests"
    echo "5. Follow single-question protocol for executive efficiency"
    echo ""
    echo "🎯 Ready for SuperClaude-enhanced meeting preparation!"
}

# Store meeting outcomes in memory
store_meeting_outcome() {
    local stakeholder_key="$1"
    local session_type="$2"
    local meeting_date="$3"
    local outcome_rating="$4"
    local business_impact="$5"

    if [ -z "$stakeholder_key" ] || [ -z "$session_type" ] || [ -z "$outcome_rating" ]; then
        echo "Usage: store_meeting_outcome <stakeholder_key> <session_type> <meeting_date> <outcome_rating> [business_impact]"
        echo "Session types: vp_slt, 1on1, cross_team, strategic_planning"
        echo "Outcome rating: 1-5 (5 = excellent)"
        return 1
    fi

    if [ -z "$meeting_date" ]; then
        meeting_date=$(date +"%Y-%m-%d")
    fi

    echo "💾 Storing meeting outcome in strategic memory..."

    # Create temporary JSON for meeting data
    cat > /tmp/meeting_outcome.json << EOF
{
    "session_type": "$session_type",
    "stakeholder_key": "$stakeholder_key",
    "meeting_date": "$meeting_date",
    "agenda_topics": ["Strategic discussion", "Platform updates"],
    "decisions_made": [{"decision": "Manual entry - add specific decisions"}],
    "action_items": [{"action": "Manual entry - add specific action items", "owner": "TBD", "deadline": "TBD"}],
    "business_impact": "$business_impact",
    "next_session_prep": "Review progress on action items and initiative updates",
    "persona_activated": "camille",
    "outcome_rating": $outcome_rating,
    "follow_up_required": true
}
EOF

    # Store via Python interface (would need enhancement to memory_manager.py for JSON input)
    echo "⚠️  Manual storage interface needed - data prepared in /tmp/meeting_outcome.json"
    echo "✅ Meeting outcome template created for manual processing"
}

# Get memory statistics
memory_stats() {
    echo "📊 SuperClaude Strategic Memory Statistics"
    echo "=" * 40
    python3 "$MEMORY_MANAGER" stats
}

# Cleanup old memory data
memory_cleanup() {
    local retention_days="${1:-365}"

    echo "🧹 Cleaning up memory data older than $retention_days days..."
    python3 "$MEMORY_MANAGER" cleanup --days "$retention_days"
}

# Main command interface
case "${1:-help}" in
    "init")
        check_dependencies
        init_memory
        ;;
    "prep-meeting")
        prep_vp_meeting_memory "$2" "$3"
        ;;
    "store-outcome")
        store_meeting_outcome "$2" "$3" "$4" "$5" "$6"
        ;;
    "stats")
        memory_stats
        ;;
    "cleanup")
        memory_cleanup "$2"
        ;;
    "help"|*)
        echo "SuperClaude Memory-Enhanced Commands"
        echo "===================================="
        echo ""
        echo "Available commands:"
        echo "  init                    Initialize memory system"
        echo "  prep-meeting <stakeholder> [date]    Prepare VP meeting with context"
        echo "  store-outcome <stakeholder> <type> <date> <rating> [impact]"
        echo "  stats                   Show memory statistics"
        echo "  cleanup [days]          Clean up old data (default: 365 days)"
        echo "  help                    Show this help"
        echo ""
        echo "Stakeholder keys: vp_engineering, vp_product, vp_design"
        echo "Session types: vp_slt, 1on1, cross_team, strategic_planning"
        echo "Outcome ratings: 1-5 (5 = excellent)"
        ;;
esac
