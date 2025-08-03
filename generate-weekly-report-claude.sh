#!/bin/bash

# Weekly SLT Report Generator with Claude Code Integration
# Director of Engineering: Chris Cantu

set -e

REPORT_DATE=$(date +"%Y-%m-%d")
OUTPUT_FILE="weekly-report-${REPORT_DATE}.md"

# Jira Configuration from Environment
JIRA_BASE_URL="${JIRA_BASE_URL:-https://procoretech.atlassian.net}"
JIRA_EMAIL="${JIRA_EMAIL:-user1@company.com}"

# Check required environment variables
if [[ -z "$JIRA_API_TOKEN" ]]; then
    echo "❌ Error: JIRA_API_TOKEN environment variable not set"
    echo "Please run: export JIRA_API_TOKEN='your-api-token'"
    exit 1
fi

echo "🚀 Generating Weekly SLT Report - $(date '+%B %d, %Y')"

# JQL Query for UI Foundation epics
JQL='project in ("Web Platform", "Web Design Systems", "UIF Special Projects", "Hubs", "Onboarding", "Globalizers", "Experience Services") AND issueType = Epic AND (sprint in openSprints() OR status in ("In Progress", "In Review", "Ready for Release", "Done")) ORDER BY project, priority DESC'

echo "📊 Fetching epic data from Procore Jira..."

# Fetch Jira data
JIRA_DATA=$(curl -s \
    -u "${JIRA_EMAIL}:${JIRA_API_TOKEN}" \
    -H "Accept: application/json" \
    "${JIRA_BASE_URL}/rest/api/3/search" \
    -G \
    --data-urlencode "jql=${JQL}" \
    --data-urlencode "fields=key,summary,status,assignee,customfield_10030,description,priority,project,progress" \
    --data-urlencode "maxResults=100")

# Validate response
if echo "$JIRA_DATA" | jq -e '.errorMessages' > /dev/null 2>&1; then
    echo "❌ Jira API Error:"
    echo "$JIRA_DATA" | jq -r '.errorMessages[]'
    exit 1
fi

EPIC_COUNT=$(echo "$JIRA_DATA" | jq '.issues | length')
echo "✅ Fetched ${EPIC_COUNT} epics from UI Foundation teams"

# Save Jira data for Claude processing
echo "$JIRA_DATA" > "jira-data-${REPORT_DATE}.json"

echo "🤖 Processing with SuperClaude framework..."

# Generate report using Claude Code with SuperClaude personas
claude << 'EOF'
I need you to generate this week's UI Foundation Platform SLT report using the live Jira data I just fetched.

Context: You are operating as Director of Engineering for UI Foundation Platform at Procore, using your SuperClaude strategic leadership framework.

Data Source: The file jira-data-$(date +"%Y-%m-%d").json contains live epic data from our 7 UI Foundation teams.

Task: Generate the weekly SLT report following these requirements:

1. **Use the approved template format** from weekly-report-2025-02-03.md as the structure
2. **Process actual Jira data** - replace sample data with real epic information
3. **Apply business value translation** using the frameworks from weekly-report-config.yaml
4. **Follow data integrity rules** - cite actual sources, use "[Data Source Needed]" for missing metrics
5. **Generate executive summary** with single focused question for leadership
6. **Include proper VP/SLT formatting** with business impact and competitive positioning

Auto-activate: --executive-brief + --platform-health + --stakeholder-align + camille + diego + alvaro

Please read the Jira data file and generate the complete weekly report.
EOF

echo "✅ Weekly SLT Report generated: ${OUTPUT_FILE}"
echo "📧 Ready for VP/SLT distribution"

# Cleanup temp files
rm -f "jira-data-${REPORT_DATE}.json"
EOF