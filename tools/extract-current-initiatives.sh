#!/bin/bash

# Current UI Foundation Initiatives Extractor
# Pull comprehensive initiative data from Jira for strategic priority analysis
# Usage: ./extract-current-initiatives.sh

set -e

# Configuration
EXTRACT_DATE=$(date +"%Y-%m-%d")
OUTPUT_DIR="workspace/current-initiatives/jira-data"
ANALYSIS_FILE="${OUTPUT_DIR}/initiatives-analysis-${EXTRACT_DATE}.md"

# UI Foundation Team Jira Project Mapping
# Experience Services: WES
# Globalizers: GLB
# Hubs: HUBS
# Onboarding: FSGD
# UIF Special Projects: UISP
# Web Platform: UIS
# Web Design Systems: UXI
# Platform Initiatives: PI

UI_FOUNDATION_PROJECTS="WES,GLB,HUBS,FSGD,UISP,UIS,UXI,PI"

# Additional strategic initiative filters
STRATEGIC_LABELS="platform-foundation,design-system,quality-monitoring,mfe-migration,baseline-standards"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

echo "🎯 UI Foundation Current Initiatives Extractor"
echo "==============================================="
echo "Extract Date: $EXTRACT_DATE"
echo "Output Dir: $OUTPUT_DIR"
echo ""

# Check for Jira API configuration
echo "🔍 Checking Jira API configuration..."
if [[ -n "$JIRA_API_TOKEN" ]]; then
    echo "✅ JIRA_API_TOKEN is set (${#JIRA_API_TOKEN} characters)"

    # Test authentication
    echo "🔐 Testing Jira API authentication..."
    USER_RESPONSE=$(curl -s -u "chris.cantu@procore.com:$JIRA_API_TOKEN" \
        -H "Accept: application/json" \
        "https://procoretech.atlassian.net/rest/api/3/myself" | \
        jq -r '.displayName // "Auth failed"')

    if [[ "$USER_RESPONSE" != "Auth failed" ]]; then
        echo "✅ Authentication successful as: $USER_RESPONSE"
        LIVE_DATA=true
    else
        echo "❌ Authentication failed - cannot extract live data"
        echo "   Please verify JIRA_API_TOKEN and try again"
        exit 1
    fi
else
    echo "❌ JIRA_API_TOKEN not found"
    echo "   Set JIRA_API_TOKEN environment variable for data extraction"
    echo ""
    echo "   export JIRA_API_TOKEN='your-atlassian-api-token'"
    exit 1
fi

# Function to extract active initiatives
extract_active_initiatives() {
    echo "📊 Extracting active initiatives across all UI Foundation teams..."

    # Query for active initiatives (not done/closed)
    ACTIVE_QUERY="project in ($UI_FOUNDATION_PROJECTS) AND status not in (Done, Closed, Resolved) ORDER BY priority DESC, project, updated DESC"

    echo "🔍 Active Initiatives Query: $ACTIVE_QUERY"

    curl -s -u "chris.cantu@procore.com:$JIRA_API_TOKEN" \
        -H "Accept: application/json" \
        "https://procoretech.atlassian.net/rest/api/3/search?jql=$(echo "$ACTIVE_QUERY" | sed 's/ /%20/g')&maxResults=200&fields=summary,status,priority,assignee,project,labels,components,fixVersions,description,updated,created" | \
        jq -r '.issues[]' > "${OUTPUT_DIR}/active_initiatives_raw.json"

    # Count by project
    echo "📈 Active Initiatives by Team:"
    for project in $(echo $UI_FOUNDATION_PROJECTS | tr ',' ' '); do
        count=$(jq -r "select(.fields.project.key == \"$project\")" "${OUTPUT_DIR}/active_initiatives_raw.json" | jq -s length)
        echo "   $project: $count active initiatives"
    done

    total_active=$(jq -s length "${OUTPUT_DIR}/active_initiatives_raw.json")
    echo "   Total Active: $total_active initiatives"
}

# Function to extract strategic epics
extract_strategic_epics() {
    echo "🎯 Extracting strategic epics and platform initiatives..."

    # Query for strategic initiatives with specific labels
    STRATEGIC_QUERY="(project in ($UI_FOUNDATION_PROJECTS) OR labels in ($STRATEGIC_LABELS)) AND issuetype = Epic AND status not in (Done, Closed) ORDER BY priority DESC, updated DESC"

    echo "🔍 Strategic Epics Query: $STRATEGIC_QUERY"

    curl -s -u "chris.cantu@procore.com:$JIRA_API_TOKEN" \
        -H "Accept: application/json" \
        "https://procoretech.atlassian.net/rest/api/3/search?jql=$(echo "$STRATEGIC_QUERY" | sed 's/ /%20/g')&maxResults=100&fields=summary,status,priority,assignee,project,labels,components,fixVersions,description,updated,created,timeestimate,timeoriginalestimate" | \
        jq -r '.issues[]' > "${OUTPUT_DIR}/strategic_epics_raw.json"

    total_strategic=$(jq -s length "${OUTPUT_DIR}/strategic_epics_raw.json")
    echo "   Strategic Epics: $total_strategic found"
}

# Function to extract recent completed work for context
extract_recent_completed() {
    echo "✅ Extracting recently completed work (last 30 days)..."

    COMPLETED_QUERY="project in ($UI_FOUNDATION_PROJECTS) AND status in (Done, Closed, Resolved) AND updated >= -30d ORDER BY updated DESC"

    echo "🔍 Recent Completed Query: $COMPLETED_QUERY"

    curl -s -u "chris.cantu@procore.com:$JIRA_API_TOKEN" \
        -H "Accept: application/json" \
        "https://procoretech.atlassian.net/rest/api/3/search?jql=$(echo "$COMPLETED_QUERY" | sed 's/ /%20/g')&maxResults=100&fields=summary,status,priority,assignee,project,labels,components,resolutiondate,updated" | \
        jq -r '.issues[]' > "${OUTPUT_DIR}/recent_completed_raw.json"

    total_completed=$(jq -s length "${OUTPUT_DIR}/recent_completed_raw.json")
    echo "   Recent Completed: $total_completed in last 30 days"
}

# Function to generate analysis report
generate_analysis_report() {
    echo "📄 Generating initiatives analysis report..."

    cat > "$ANALYSIS_FILE" << EOF
# UI Foundation Current Initiatives Analysis
**Generated**: $EXTRACT_DATE
**Source**: Company Jira API across all UI Foundation teams

---

## Executive Summary

**Total Active Initiatives**: $(jq -s length "${OUTPUT_DIR}/active_initiatives_raw.json")
**Strategic Epics**: $(jq -s length "${OUTPUT_DIR}/strategic_epics_raw.json")
**Recent Completions (30d)**: $(jq -s length "${OUTPUT_DIR}/recent_completed_raw.json")

---

## Active Initiatives by Team

EOF

    # Generate team-by-team breakdown
    for project in $(echo $UI_FOUNDATION_PROJECTS | tr ',' ' '); do
        team_name=$(get_team_name "$project")
        cat >> "$ANALYSIS_FILE" << EOF

### $team_name ($project)

EOF

        # Extract initiatives for this team
        jq -r "select(.fields.project.key == \"$project\") | \"- [\(.key)](https://procoretech.atlassian.net/browse/\(.key)): \(.fields.summary)\"" "${OUTPUT_DIR}/active_initiatives_raw.json" >> "$ANALYSIS_FILE"

        if [[ $(jq -r "select(.fields.project.key == \"$project\")" "${OUTPUT_DIR}/active_initiatives_raw.json" | wc -l) -eq 0 ]]; then
            echo "  *No active initiatives found*" >> "$ANALYSIS_FILE"
        fi
    done

    cat >> "$ANALYSIS_FILE" << EOF

---

## Strategic Epics Analysis

### Platform Foundation & Architecture
EOF

    # Extract platform-related epics
    jq -r 'select(.fields.labels[]? | test("platform|foundation|architecture|mfe|design-system"; "i")) | "- [\(.key)](https://procoretech.atlassian.net/browse/\(.key)): \(.fields.summary) - \(.fields.status.name) - \(.fields.priority.name // "No Priority")"' "${OUTPUT_DIR}/strategic_epics_raw.json" >> "$ANALYSIS_FILE"

    cat >> "$ANALYSIS_FILE" << EOF

### Quality & Monitoring
EOF

    # Extract quality-related epics
    jq -r 'select(.fields.labels[]? | test("quality|monitoring|slo|observability"; "i")) | "- [\(.key)](https://procoretech.atlassian.net/browse/\(.key)): \(.fields.summary) - \(.fields.status.name) - \(.fields.priority.name // "No Priority")"' "${OUTPUT_DIR}/strategic_epics_raw.json" >> "$ANALYSIS_FILE"

    cat >> "$ANALYSIS_FILE" << EOF

### Other Strategic Initiatives
EOF

    # Extract other strategic epics
    jq -r 'select(.fields.labels[]? | test("platform|foundation|architecture|quality|monitoring"; "i") | not) | "- [\(.key)](https://procoretech.atlassian.net/browse/\(.key)): \(.fields.summary) - \(.fields.status.name) - \(.fields.priority.name // "No Priority")"' "${OUTPUT_DIR}/strategic_epics_raw.json" >> "$ANALYSIS_FILE"

    cat >> "$ANALYSIS_FILE" << EOF

---

## Priority Analysis for Strategic Planning

### High Priority Initiatives
$(jq -r 'select(.fields.priority.name == "High" or .fields.priority.name == "Highest") | "- [\(.key)](https://procoretech.atlassian.net/browse/\(.key)): \(.fields.summary) - \(.fields.project.key)"' "${OUTPUT_DIR}/active_initiatives_raw.json")

### At Risk / Blocked Initiatives
$(jq -r 'select(.fields.status.name | test("blocked|risk"; "i")) | "- [\(.key)](https://procoretech.atlassian.net/browse/\(.key)): \(.fields.summary) - \(.fields.status.name)"' "${OUTPUT_DIR}/active_initiatives_raw.json")

---

## Recommendations for Strategic Priority Ranking

Based on this analysis:

1. **Platform Foundation Priority**: [Number] initiatives related to platform/foundation work
2. **Quality Infrastructure Priority**: [Number] initiatives related to monitoring/quality
3. **Team Capacity**: [Number] total active initiatives across teams
4. **Resource Constraints**: [Analysis needed based on high priority + at risk items]

---

## Data Sources
- **Company Jira API**: All UI Foundation teams ($UI_FOUNDATION_PROJECTS)
- **Strategic Labels**: $STRATEGIC_LABELS
- **Query Date**: $EXTRACT_DATE
- **Raw Data**: Available in $OUTPUT_DIR/

EOF

    echo "✅ Analysis report generated: $ANALYSIS_FILE"
}

# Function to get team name from project key
get_team_name() {
    case $1 in
        WES) echo "Experience Services" ;;
        GLB) echo "Globalizers" ;;
        HUBS) echo "Hubs" ;;
        FSGD) echo "Onboarding" ;;
        UISP) echo "UIF Special Projects" ;;
        UIS) echo "Web Platform" ;;
        UXI) echo "Web Design Systems" ;;
        PI) echo "Platform Initiatives" ;;
        *) echo "Unknown Team" ;;
    esac
}

# Main execution
echo "🚀 Starting data extraction..."
extract_active_initiatives
extract_strategic_epics
extract_recent_completed
generate_analysis_report

echo ""
echo "✅ Extraction Complete!"
echo "📊 Analysis Report: $ANALYSIS_FILE"
echo "📁 Raw Data Directory: $OUTPUT_DIR"
echo ""
echo "🔧 Next Steps:"
echo "   1. Review the analysis report for current initiative landscape"
echo "   2. Compare against strategic priority ranking"
echo "   3. Identify gaps or conflicts between current work and strategic priorities"
echo "   4. Use data for VP/SLT priority alignment discussions"
echo ""
