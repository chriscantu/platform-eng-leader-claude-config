#!/bin/bash

# L2 Strategic UI Foundation Initiatives Extractor
# Pull L2 business initiatives from PI project for strategic priority analysis
# Usage: ./extract-l2-strategic-initiatives.sh

set -e

# Configuration
EXTRACT_DATE=$(date +"%Y-%m-%d")
OUTPUT_DIR="workspace/current-initiatives/jira-data"
L2_ANALYSIS_FILE="${OUTPUT_DIR}/l2-strategic-analysis-${EXTRACT_DATE}.md"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

echo "🎯 UI Foundation L2 Strategic Initiatives Extractor"
echo "=================================================="
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
    exit 1
fi

# Function to extract L2 strategic initiatives
extract_l2_initiatives() {
    echo "📊 Extracting L2 strategic initiatives for UI Foundations..."

    # The strategic L2 query provided by user
    L2_QUERY='project = PI AND division in ("UI Foundations") and type = L2 AND status not in (Done, Closed, Completed, Canceled, Released) ORDER BY cf[18272] ASC, priority DESC, updated ASC'

    echo "🔍 L2 Strategic Query: $L2_QUERY"

    curl -s -u "chris.cantu@procore.com:$JIRA_API_TOKEN" \
        -H "Accept: application/json" \
        "https://procoretech.atlassian.net/rest/api/3/search?jql=$(echo "$L2_QUERY" | sed 's/ /%20/g')&maxResults=100&fields=summary,status,priority,assignee,project,labels,components,fixVersions,description,updated,created,cf[18272],cf[18280],cf[18281],cf[18282]" | \
        jq -r '.issues[]' > "${OUTPUT_DIR}/l2_strategic_raw.json"

    # Count and validate
    local total_l2=$(jq -s length "${OUTPUT_DIR}/l2_strategic_raw.json")
    echo "   L2 Strategic Initiatives: $total_l2 found"

    if [[ $total_l2 -eq 0 ]]; then
        echo "⚠️  No L2 initiatives found - check query or permissions"
        return 1
    fi

    return 0
}

# Function to extract related L1 initiatives for context
extract_l1_context() {
    echo "📋 Extracting related L1 initiatives for context..."

    # L1 initiatives for UI Foundations
    L1_QUERY='project = PI AND division in ("UI Foundations") and type = L1 AND status not in (Done, Closed, Completed, Canceled, Released) ORDER BY priority DESC, updated DESC'

    echo "🔍 L1 Context Query: $L1_QUERY"

    curl -s -u "chris.cantu@procore.com:$JIRA_API_TOKEN" \
        -H "Accept: application/json" \
        "https://procoretech.atlassian.net/rest/api/3/search?jql=$(echo "$L1_QUERY" | sed 's/ /%20/g')&maxResults=50&fields=summary,status,priority,assignee,project,labels,components,parent,updated,created" | \
        jq -r '.issues[]' > "${OUTPUT_DIR}/l1_context_raw.json"

    local total_l1=$(jq -s length "${OUTPUT_DIR}/l1_context_raw.json")
    echo "   L1 Context Initiatives: $total_l1 found"
}

# Function to generate strategic analysis report
generate_l2_analysis() {
    echo "📄 Generating L2 strategic analysis report..."

    cat > "$L2_ANALYSIS_FILE" << EOF
# UI Foundation L2 Strategic Initiatives Analysis
**Generated**: $EXTRACT_DATE
**Source**: Procore Jira PI project - L2 business initiatives
**Division**: UI Foundations

---

## Executive Summary

**Total L2 Strategic Initiatives**: $(jq -s length "${OUTPUT_DIR}/l2_strategic_raw.json")
**Total L1 Supporting Initiatives**: $(jq -s length "${OUTPUT_DIR}/l1_context_raw.json")

This analysis focuses on L2 business-level initiatives that represent our true strategic priorities, as opposed to operational/tactical work.

---

## L2 Strategic Initiatives (Business Level)

EOF

    # Generate L2 initiative breakdown
    if [[ -f "${OUTPUT_DIR}/l2_strategic_raw.json" && $(jq -s length "${OUTPUT_DIR}/l2_strategic_raw.json") -gt 0 ]]; then
        jq -r '. | "### [\(.key)](https://procoretech.atlassian.net/browse/\(.key)): \(.fields.summary)
**Status**: \(.fields.status.name)
**Priority**: \(.fields.priority.name // "No Priority")
**Assignee**: \(.fields.assignee.displayName // "Unassigned")
**Updated**: \(.fields.updated[0:10])

**Description**: \(.fields.description.content[0].content[0].text // "No description available")

---
"' "${OUTPUT_DIR}/l2_strategic_raw.json" >> "$L2_ANALYSIS_FILE"
    else
        echo "*No L2 strategic initiatives found*" >> "$L2_ANALYSIS_FILE"
    fi

    cat >> "$L2_ANALYSIS_FILE" << EOF

## L1 Supporting Initiatives Context

EOF

    # Generate L1 context
    if [[ -f "${OUTPUT_DIR}/l1_context_raw.json" && $(jq -s length "${OUTPUT_DIR}/l1_context_raw.json") -gt 0 ]]; then
        jq -r '. | "- [\(.key)](https://procoretech.atlassian.net/browse/\(.key)): \(.fields.summary) - \(.fields.status.name) - \(.fields.priority.name // "No Priority")"' "${OUTPUT_DIR}/l1_context_raw.json" >> "$L2_ANALYSIS_FILE"
    else
        echo "*No L1 initiatives found*" >> "$L2_ANALYSIS_FILE"
    fi

    cat >> "$L2_ANALYSIS_FILE" << EOF

---

## Strategic Priority Validation

Based on the L2 business initiatives above, we can now validate our strategic priority ranking:

### Priority 1: Platform Foundation & Baseline Standards
**L2 Initiatives Mapped**: [Analysis needed based on above data]
- Platform infrastructure and standardization initiatives
- MFE migration and architecture modernization
- Design system maturity and adoption

### Priority 2: Quality Infrastructure & SLO Framework
**L2 Initiatives Mapped**: [Analysis needed based on above data]
- Observability and monitoring initiatives
- Quality metrics and SLO implementation
- Performance and reliability improvements

### Priority 3: Strategic Planning & Organizational Development
**L2 Initiatives Mapped**: [Analysis needed based on above data]
- Team development and capability building
- Cross-functional alignment initiatives
- Innovation and exploration projects

---

## Resource Allocation Analysis

### Current L2 Focus Distribution
- **Platform/Infrastructure**: [Count] initiatives
- **Quality/Observability**: [Count] initiatives
- **Strategic/Organizational**: [Count] initiatives
- **Other/Unclassified**: [Count] initiatives

### Recommendations for VP/SLT

1. **Strategic Alignment**: Compare L2 initiative distribution against our force-ranked priorities
2. **Resource Gaps**: Identify strategic areas lacking L2-level investment
3. **Priority Conflicts**: Highlight competing L2 initiatives that may need consolidation
4. **Execution Focus**: Ensure tactical work (team-level) supports L2 strategic objectives

---

## Data Sources
- **Procore Jira PI Project**: L2 and L1 initiatives for UI Foundations division
- **Query Date**: $EXTRACT_DATE
- **Raw Data**: Available in $OUTPUT_DIR/

**Note**: This analysis represents true strategic business initiatives (L2 level) rather than operational/tactical work, providing accurate insight for executive decision-making.

EOF

    echo "✅ L2 strategic analysis report generated: $L2_ANALYSIS_FILE"
}

# Main execution
echo "🚀 Starting L2 strategic data extraction..."
extract_l2_initiatives

if [[ $? -eq 0 ]]; then
    extract_l1_context
    generate_l2_analysis

    echo ""
    echo "✅ L2 Strategic Extraction Complete!"
    echo "📊 Analysis Report: $L2_ANALYSIS_FILE"
    echo "📁 Raw Data Directory: $OUTPUT_DIR"
    echo ""
    echo "🔧 Next Steps:"
    echo "   1. Review L2 strategic initiatives to validate priority ranking"
    echo "   2. Map L2 initiatives to our three strategic priorities"
    echo "   3. Identify resource gaps or priority conflicts"
    echo "   4. Prepare VP/SLT briefing with L2-level strategic recommendations"
else
    echo "❌ L2 extraction failed - check query permissions or Jira access"
    exit 1
fi
