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

# JQL Query for UI Foundation epics - ONLY completed or story-complete epics
SEVEN_DAYS_AGO=$(date -d '7 days ago' '+%Y-%m-%d' 2>/dev/null || date -v-7d '+%Y-%m-%d')
JQL="project in (\"Web Platform\", \"Web Design Systems\", \"UIF Special Projects\", \"Hubs\", \"Onboarding\", \"Globalizers\", \"Experience Services\") AND issueType = Epic AND (status IN (\"Done\", \"Released\", \"Closed\") OR status CHANGED TO (\"Done\", \"Released\", \"Closed\") AFTER \"${SEVEN_DAYS_AGO}\") ORDER BY updated DESC"

echo "📊 Fetching completed epics from Procore Jira (since ${SEVEN_DAYS_AGO})..."

# Fetch Jira data
JIRA_DATA=$(curl -s \
    -u "${JIRA_EMAIL}:${JIRA_API_TOKEN}" \
    -H "Accept: application/json" \
    "${JIRA_BASE_URL}/rest/api/3/search" \
    -G \
    --data-urlencode "jql=${JQL}" \
    --data-urlencode "fields=key,summary,status,assignee,customfield_10030,description,priority,project,progress,aggregateprogress,updated" \
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

Task: Generate an **ULTRA-BRIEF** weekly SLT report (MAX 1 PAGE) focusing ONLY on completed epics:

1. **Ultra-brief format** - maximum 1 page, bullet points only
2. **ONLY completed epics** - status = Done/Released/Closed OR recently completed
3. **Include epic links** - add clickable Jira links for each epic
4. **Business value focus** - one sentence per epic explaining business impact
5. **Structure**:
   - **Executive Summary** (2-3 sentences max)
   - **Completed Deliverables** (bullet list with links)
   - **Business Impact** (1-2 sentences total)
   - **Next Week Focus** (1 sentence)
6. **Maximum length**: 1 page / ~300 words total

Auto-activate: --executive-brief + --platform-health + --stakeholder-align + camille + diego + alvaro

Please read the Jira data file and generate the complete weekly report.
EOF

echo "✅ Weekly SLT Report generated: ${OUTPUT_FILE}"
echo "📧 Ready for VP/SLT distribution"

# Cleanup temp files
rm -f "jira-data-${REPORT_DATE}.json"
EOF