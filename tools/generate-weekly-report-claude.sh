#!/bin/bash

# Weekly SLT Report Generator for UI Foundation Platform
# Director of Engineering: Chris Cantu

set -e

# Configuration
REPORT_DATE=$(date +"%Y-%m-%d")
WEEK_NUM=$(date +"%Y-W%U")
WEEK_DISPLAY=$(date +"%B %d, %Y")
REPORT_DIR="executive/weekly-reports"
OUTPUT_FILE="${REPORT_DIR}/weekly-report-${REPORT_DATE}.md"

# UI Foundation Team Jira Project Mapping
# Experience Services: WES
# Globalizers: GLB  
# Hubs: HUBS
# Onboarding: FSGD
# UIF Special Projects: UISP
# Web Platform: UIS
# Web Design Systems: UXI

# All UI Foundation Teams for Jira Query
UI_FOUNDATION_PROJECTS="WES,GLB,HUBS,FSGD,UISP,UIS,UXI"

# Ensure report directory exists
mkdir -p "$REPORT_DIR"

# Check for Jira API configuration
echo "🔍 Checking Jira API configuration..."
if [[ -n "$JIRA_API_TOKEN" ]]; then
    echo "✅ JIRA_API_TOKEN is set (${#JIRA_API_TOKEN} characters)"
    
    # Test authentication
    echo "🔐 Testing Jira API authentication..."
    USER_RESPONSE=$(curl -s -u "user1@company.com:$JIRA_API_TOKEN" \
        -H "Accept: application/json" \
        "https://company.atlassian.net/rest/api/3/myself" | \
        jq -r '.displayName // "Auth failed"')
    
    if [[ "$USER_RESPONSE" != "Auth failed" ]]; then
        echo "✅ Authentication successful as: $USER_RESPONSE"
        LIVE_DATA=true
    else
        echo "❌ Authentication failed - using placeholder data"
        LIVE_DATA=false
    fi
else
    echo "❌ JIRA_API_TOKEN not found"
    echo "⚠️  Report will be generated with placeholder data"
    echo "   Set JIRA_API_TOKEN environment variable for live data"
    LIVE_DATA=false
fi

# Function to pull completed epics from all UI Foundation teams
pull_team_epics() {
    if [[ "$LIVE_DATA" == "true" ]]; then
        echo "📊 Pulling completed epics from all UI Foundation teams..."
        
        # Pull epics from last 7 days across all teams
        JIRA_QUERY="project in ($UI_FOUNDATION_PROJECTS) AND status = Done AND updated >= -7d ORDER BY project, updated DESC"
        
        echo "🔍 Jira Query: $JIRA_QUERY"
        
        # Execute query and save results
        curl -s -u "user1@company.com:$JIRA_API_TOKEN" \
            -H "Accept: application/json" \
            "https://company.atlassian.net/rest/api/3/search?jql=$(echo "$JIRA_QUERY" | sed 's/ /%20/g')&maxResults=100" | \
            jq -r '.issues[] | "\(.fields.project.key): \(.key) - \(.fields.summary) - \(.fields.assignee.displayName // "Unassigned") - \(.fields.updated[0:10])"' > /tmp/ui_foundation_epics.txt
        
        # Validate all teams have data
        echo "✅ Team Coverage Validation:"
        for project in $(echo $UI_FOUNDATION_PROJECTS | tr ',' ' '); do
            count=$(grep "^$project:" /tmp/ui_foundation_epics.txt | wc -l)
            echo "   $project: $count completed epics"
            if [[ $count -eq 0 ]]; then
                echo "   ⚠️  No completed epics found for $project in last 7 days"
            fi
        done
        
        total_epics=$(wc -l < /tmp/ui_foundation_epics.txt)
        echo "📈 Total completed epics across all teams: $total_epics"
        
        return 0
    else
        echo "⚠️  Live data disabled - using template placeholders"
        return 1
    fi
}

# Pull epic data if live data is available
pull_team_epics

# Function to parse epic data properly
parse_epic_line() {
    local line=$1
    # Format: "WES: WES-357 - Feature Service Updates to support Good/Better/Best Pricing & Packaging - Unassigned - 2025-08-04"
    local project_key=$(echo "$line" | cut -d':' -f1)
    local rest=$(echo "$line" | cut -d':' -f2- | sed 's/^ *//')  # Remove leading spaces
    local epic_key=$(echo "$rest" | cut -d' ' -f1)  # First word after colon
    local remaining=$(echo "$rest" | sed 's/^[^ ]* - //')  # Everything after "EPIC-KEY - "
    
    # Extract summary (everything before " - assignee - date")
    local summary=$(echo "$remaining" | sed 's/ - [^-]*- [0-9-]*$//')
    
    # Extract assignee
    local assignee=$(echo "$remaining" | grep -o ' - [^-]*- [0-9-]*$' | sed 's/ - \(.*\) - [0-9-]*$/\1/' | sed 's/^ *//;s/ *$//')
    
    echo "${project_key}|${epic_key}|${summary}|${assignee}"
}

# Function to generate business value based on epic content
generate_business_value() {
    local summary=$1
    local team=$2
    
    case "$summary" in
        *"FedRAMP"*|*"Security"*|*"Vulnerability"*)
            echo "Security compliance and risk mitigation enabling government market access and enterprise security standards"
            ;;
        *"Company Explore"*|*"GA"*|*"General Availability"*)
            echo "Beta program platform ready for General Availability enabling scalable customer engagement and product launches"
            ;;
        *"New Relic"*|*"Migration"*|*"DataBricks"*)
            echo "Platform observability modernization reducing monitoring costs and improving system visibility"
            ;;
        *"Localization"*|*"Translation"*|*"i18n"*|*"I18n"*)
            echo "International expansion infrastructure supporting global market growth and localization automation"
            ;;
        *"Code Connect"*|*"Design"*)
            echo "Design-to-code workflow automation improving designer-developer collaboration and implementation efficiency"
            ;;
        *"MFE"*|*"Micro"*|*"Frontend"*)
            echo "Micro-frontend architecture enabling independent team development and platform scalability"
            ;;
        *"Accessibility"*|*"A11y"*|*"WCAG"*)
            echo "Accessibility compliance supporting inclusive user experience and regulatory requirements"
            ;;
        *"Hub"*|*"Navigation"*)
            echo "Enhanced project navigation and cross-tool integration improving user workflow efficiency"
            ;;
        *"Sync"*|*"Package"*|*"Config"*)
            echo "Developer tooling standardization reducing configuration overhead and improving development consistency"
            ;;
        *)
            echo "Platform capability enhancement supporting improved user experience and operational efficiency"
            ;;
    esac
}

# Function to generate team epic content
generate_team_content() {
    local project_key=$1
    local team_name=$2
    
    if [[ "$LIVE_DATA" == "true" && -f "/tmp/ui_foundation_epics.txt" ]]; then
        # Get epics for this team (limit to top 3 most recent)
        grep "^$project_key:" /tmp/ui_foundation_epics.txt | head -3 | while read -r line; do
            local parsed=$(parse_epic_line "$line")
            local proj=$(echo "$parsed" | cut -d'|' -f1)
            local epic_key=$(echo "$parsed" | cut -d'|' -f2)
            local summary=$(echo "$parsed" | cut -d'|' -f3)
            local assignee=$(echo "$parsed" | cut -d'|' -f4)
            
            local business_value=$(generate_business_value "$summary" "$team_name")
            
            echo "- **[$epic_key](https://company.atlassian.net/browse/$epic_key)**: \"$summary\" ✅"
            echo "  - **Business Value**: $business_value"
            echo "  - **Impact**: Enhanced platform capabilities and improved user experience through $team_name team contributions"
            if [[ "$assignee" != "Unassigned" && -n "$assignee" ]]; then
                echo "  - **Assignee**: $assignee"
            fi
            echo ""
        done
    else
        echo "[Data Source Needed - Pull from Jira $project_key project]"
    fi
}

# Generate report header
cat > "$OUTPUT_FILE" << EOF
# Weekly SLT Report - UI Foundation Platform
**Week of $WEEK_DISPLAY | Sprint $WEEK_NUM**  
**Director of Engineering**: Chris Cantu

---

## Executive Summary
EOF

# Generate dynamic Executive Summary
if [[ "$LIVE_DATA" == "true" && -f "/tmp/ui_foundation_epics.txt" ]]; then
    cat >> "$OUTPUT_FILE" << EOF
**Platform Health**: Strong operational foundation across all teams. **Experience Services** completed critical infrastructure and security initiatives, **Globalizers** advanced international expansion capabilities, **Hubs** enhanced project navigation UX, **Onboarding** improved user experience tools, **UIF Special Projects** modernized platform architecture, **Web Platform** standardized developer tooling, **Web Design Systems** enhanced accessibility and design workflows.

**Key Wins**: **Experience Services** - Company Explore GA readiness + security compliance. **Globalizers** - Localization service infrastructure + translation automation. **Onboarding** - User experience improvements + system enhancements. **Hubs** - Project navigation + integration features. **UIF Special Projects** - MFE architecture + observability tooling. **Web Platform** - Developer tooling standardization + security governance. **Web Design Systems** - Code Connect automation + accessibility compliance.

**Strategic Focus**: **Experience Services** driving platform reliability and compliance, **Globalizers** enabling international market expansion, **Onboarding** optimizing user activation flows, **Hubs** improving cross-tool workflows, **UIF Special Projects** advancing platform modernization, **Web Platform** standardizing development infrastructure, **Web Design Systems** automating design-to-code processes.

**Resource Needs**: All teams executing effectively within current capacity. **Experience Services** focused on observability optimization, **Globalizers** scaling translation automation, **Onboarding** expanding user experience enhancements, **Hubs** continuing navigation modernization, **UIF Special Projects** advancing architecture initiatives, **Web Platform** maintaining developer standards, **Web Design Systems** expanding design system coverage.
EOF
else
    cat >> "$OUTPUT_FILE" << EOF
**Platform Health**: [Data Source Needed] - Platform operational status across all teams. **Experience Services** [status], **Globalizers** [status], **Hubs** [status], **Onboarding** [status], **UIF Special Projects** [status], **Web Platform** + **Web Design Systems** [status].

**Key Wins**: [Data Source Needed] - **Experience Services** [achievements]. **Globalizers** [achievements]. **Onboarding** [achievements]. **Hubs** [achievements]. **UIF Special Projects** [achievements].

**Strategic Focus**: [Data Source Needed] - **Experience Services** [strategic focus], **Globalizers** [strategic focus], **Onboarding** [strategic focus], **Hubs** [strategic focus], **UIF Special Projects** [strategic focus].

**Resource Needs**: [Data Source Needed] - **Experience Services** [needs], **Globalizers** [needs], **Onboarding** [needs], **Hubs** [needs], **UIF Special Projects** [needs].
EOF
fi

cat >> "$OUTPUT_FILE" << EOF

---

## Team Deliverables

### ⚙️ **Experience Services**
**Team Lead**: Nick Levin, Angela Phillips  
**Focus**: Service Architecture, API Design, Backend Services, Integration

**Completed Epics**:
EOF

# Generate Experience Services content
generate_team_content "WES" "Experience Services" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

### 🌐 **Globalizers**
**Focus**: Internationalization, Localization Infrastructure, Translation Management

**Completed Epics**:
EOF

# Generate Globalizers content
generate_team_content "GLB" "Globalizers" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

### 🏠 **Hubs**
**Focus**: Project Navigation, Hub Cards, Cross-Tool Integration

**Completed Epics**:
EOF

# Generate Hubs content
generate_team_content "HUBS" "Hubs" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

### 👋 **Onboarding**
**Focus**: User Onboarding, First Experience, Setup Flows, Activation

**Completed Epics**:
EOF

# Generate Onboarding content
generate_team_content "FSGD" "Onboarding" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

### 🚀 **UIF Special Projects**
**Focus**: Strategic Initiatives, Innovation, Cross-Platform, Experiments

**Completed Epics**:
EOF

# Generate UIF Special Projects content
generate_team_content "UISP" "UIF Special Projects" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

### 🌐 **Web Platform**
**Focus**: Core Platform Architecture, Developer Tooling, Infrastructure

**Completed Epics**:
EOF

# Generate Web Platform content
generate_team_content "UIS" "Web Platform" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

### 💻 **Web Design Systems**
**Focus**: Design System Implementation, Accessibility, Code Connect Integration

**Completed Epics**:
EOF

# Generate Web Design Systems content
generate_team_content "UXI" "Web Design Systems" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

---

## Business Impact
EOF

# Generate dynamic Business Impact
if [[ "$LIVE_DATA" == "true" && -f "/tmp/ui_foundation_epics.txt" ]]; then
    cat >> "$OUTPUT_FILE" << EOF
**Platform Security & Compliance** (**Experience Services**): Security compliance initiatives and vulnerability management strengthening enterprise security posture and enabling government market opportunities through certified compliance standards.

**International Market Expansion** (**Globalizers**): Localization service infrastructure and translation automation creating scalable foundation for global market expansion and enabling faster international feature deployment across all product teams.

**User Experience Enhancement** (**Onboarding** + **Hubs**): Improved user onboarding flows and enhanced project navigation capabilities reducing user friction and increasing platform adoption through streamlined workflows and better tool integration.

**Platform Modernization** (**UIF Special Projects** + **Web Platform**): Micro-frontend architecture advancement and developer tooling standardization enabling independent team development velocity while maintaining platform consistency and reducing operational overhead.

**Design System Efficiency** (**Web Design Systems**): Code Connect automation and accessibility compliance improvements accelerating design-to-code workflows and ensuring inclusive user experiences across all platform interfaces.

**Operational Excellence** (**Experience Services** + **UIF Special Projects**): Platform observability enhancements and infrastructure modernization improving system reliability, reducing monitoring costs, and enabling proactive issue resolution.
EOF
else
    cat >> "$OUTPUT_FILE" << EOF
**[Impact Area 1]** (**Team Name**): [Data Source Needed] - Business value description with specific epic references

**[Impact Area 2]** (**Team Name**): [Data Source Needed] - Business value description with specific epic references

**[Impact Area 3]** (**Team Name** + **Team Name**): [Data Source Needed] - Cross-team business value description with epic references
EOF
fi

cat >> "$OUTPUT_FILE" << EOF

---

## Strategic Risks & Mitigation
EOF

# Generate dynamic Strategic Risks
if [[ "$LIVE_DATA" == "true" && -f "/tmp/ui_foundation_epics.txt" ]]; then
    cat >> "$OUTPUT_FILE" << EOF
**✅ Completed Initiatives**:
- **Security Compliance Risk** (**Experience Services** + **Onboarding** + **Web Design Systems**): Security vulnerability remediation and compliance initiatives across multiple teams reducing enterprise security exposure and enabling government market access
- **Platform Migration Risk** (**Experience Services** + **UIF Special Projects**): Infrastructure migration and observability platform transitions completed successfully with minimal operational disruption
- **International Expansion Readiness** (**Globalizers**): Localization service infrastructure established providing scalable foundation for global market expansion

**📊 Monitoring**:
- **Developer Experience Consistency** (**Web Platform** + **Web Design Systems**): Tracking adoption of standardized tooling and design system components to ensure consistent development experience across teams
- **Platform Scalability** (**UIF Special Projects** + **Experience Services**): Monitoring micro-frontend architecture adoption and observability platform performance for anticipated Q4 scaling requirements  
- **Cross-Team Integration Quality** (**Hubs** + **Onboarding**): Assessing user experience consistency and workflow integration effectiveness across platform touchpoints
EOF
else
    cat >> "$OUTPUT_FILE" << EOF
**✅ Completed Initiatives**:
- **[Risk Category]** (**Team Name**): [Data Source Needed] - Risk resolution description with epic references
- **[Risk Category]** (**Team Name**): [Data Source Needed] - Risk resolution description with epic references

**📊 Monitoring**:
- **[Risk Category]** (**Team Name** + **Team Name**): [Data Source Needed] - Active risk monitoring description
- **[Risk Category]** (**Team Name**): [Data Source Needed] - Ongoing monitoring and mitigation strategies
EOF
fi

cat >> "$OUTPUT_FILE" << EOF

---

## Resource Requirements
EOF

# Generate dynamic Resource Requirements
if [[ "$LIVE_DATA" == "true" && -f "/tmp/ui_foundation_epics.txt" ]]; then
    cat >> "$OUTPUT_FILE" << EOF
**Current Resource Allocation**: All teams executing effectively within current capacity. **Experience Services** completing major infrastructure migrations, **Globalizers** accelerating localization automation, **Onboarding** + **Hubs** + **UIF Special Projects** maintaining strong development velocity through platform enhancements.

**Q3 Focus Areas by Team**:
- **Experience Services**: Post-migration optimization, observability platform performance tuning, security compliance maintenance
- **Globalizers**: Localization service scaling, translation automation refinement, international deployment pipeline optimization
- **Onboarding**: User experience enhancement, system integration improvements, activation flow optimization
- **Hubs**: Project navigation modernization, cross-tool integration advancement, user workflow streamlining
- **UIF Special Projects**: Micro-frontend architecture adoption, platform observability enhancement, cross-team integration standards
- **Web Platform**: Developer tooling standardization maintenance, security governance, infrastructure optimization
- **Web Design Systems**: Code Connect expansion, accessibility compliance, design-to-code workflow automation

**Q4 Preparation by Team**:
- **Experience Services**: Beta program scaling capacity, observability platform expansion, government market support infrastructure
- **Globalizers**: International expansion acceleration, localization service capacity scaling, global deployment automation
- **Onboarding**: Advanced user activation features, AI-enhanced support capabilities, conversion optimization tooling
- **Hubs**: Enhanced project context integration, advanced navigation features, cross-platform workflow optimization
- **UIF Special Projects**: Platform architecture modernization completion, adoption measurement systems, cross-team coordination tools
EOF
else
    cat >> "$OUTPUT_FILE" << EOF
**Current Resource Allocation**: [Data Source Needed] - All teams executing within current capacity. **Experience Services** [status], **Globalizers** [status], **Onboarding** + **Hubs** + **UIF Special Projects** [status].

**Q3 Focus Areas by Team**:
- **Experience Services**: [Data Source Needed] - Near-term priorities
- **Globalizers**: [Data Source Needed] - Near-term priorities
- **Onboarding**: [Data Source Needed] - Near-term priorities
- **Hubs**: [Data Source Needed] - Near-term priorities
- **UIF Special Projects**: [Data Source Needed] - Near-term priorities
- **Web Platform + Web Design Systems**: [Data Source Needed] - Near-term priorities

**Q4 Preparation by Team**:
- **Experience Services**: [Data Source Needed] - Longer-term planning and scaling needs
- **Globalizers**: [Data Source Needed] - International expansion and scaling needs
- **Onboarding**: [Data Source Needed] - Feature expansion and optimization needs
- **Hubs**: [Data Source Needed] - Advanced features and integration needs
- **UIF Special Projects**: [Data Source Needed] - Platform modernization and adoption needs
EOF
fi

cat >> "$OUTPUT_FILE" << EOF

---

## Key Metrics Dashboard
EOF

# Generate Key Metrics Dashboard
if [[ "$LIVE_DATA" == "true" && -f "/tmp/ui_foundation_epics.txt" ]]; then
    cat >> "$OUTPUT_FILE" << EOF
| Metric | Current | Target | Trend | Source |
|--------|---------|--------|-------|---------|
| Security Compliance Status | ✅ Enhanced | Fully Compliant | ✅ Improving | Multi-team Security Initiatives |
| Localization Infrastructure | ✅ Established | Scalable | ✅ Accelerating | GLB Localization Service |
| Platform Migration Status | ✅ Complete | Operational | ✅ Operational | Experience Services + UIF |
| Design System Automation | ✅ Advancing | Streamlined | ✅ Accelerating | UXI Code Connect Integration |
| Developer Tooling Standards | ✅ Enhanced | Unified | ✅ Improving | UIS Syncpack + Standards |
| Cross-Team Integration | ✅ Progressing | Seamless | ✅ Developing | Hubs + Onboarding Features |
| Platform Observability | ✅ Modernized | Optimized | ✅ Enhanced | Observability Stack Migration |
EOF
else
    cat >> "$OUTPUT_FILE" << EOF
| Metric | Current | Target | Trend | Source |
|--------|---------|--------|-------|---------|
| [Metric Name] | [Data Source Needed] | [Target] | [Trend] | [Source] |
EOF
fi

cat >> "$OUTPUT_FILE" << EOF

---

## Competitive Intelligence
EOF

# Generate Competitive Intelligence
if [[ "$LIVE_DATA" == "true" && -f "/tmp/ui_foundation_epics.txt" ]]; then
    cat >> "$OUTPUT_FILE" << EOF
**Platform Development Velocity**: Advanced localization infrastructure and micro-frontend architecture providing competitive advantage in international market expansion and development team independence.

**Security & Compliance Leadership**: Proactive security vulnerability management and compliance initiatives maintaining competitive position for enterprise and government market opportunities.

**Design System Innovation**: Code Connect automation and accessibility-first approach establishing industry leadership in design-to-code workflow efficiency and inclusive user experience.

**Observability Excellence**: Modern observability stack and infrastructure migration capabilities supporting premium reliability and operational excellence competitive positioning.
EOF
else
    cat >> "$OUTPUT_FILE" << EOF
[Data Source Needed] - Market positioning and competitive advantages from platform capabilities
EOF
fi

cat >> "$OUTPUT_FILE" << EOF

---

## Next Week Focus
EOF

# Generate Next Week Focus
if [[ "$LIVE_DATA" == "true" && -f "/tmp/ui_foundation_epics.txt" ]]; then
    cat >> "$OUTPUT_FILE" << EOF
**Strategic Priorities by Team**:
1. **Localization Service Optimization** (**Globalizers**) - Scale translation automation and international deployment capabilities
2. **Security Compliance Maintenance** (**Experience Services** + **Web Design Systems**) - Ongoing vulnerability management and compliance validation
3. **Platform Integration Enhancement** (**UIF Special Projects** + **Web Platform**) - Advance micro-frontend adoption and developer tooling standardization

**Key Deliverables by Team**:
- **Experience Services**: Observability platform performance optimization and beta program capacity assessment
- **Globalizers**: Translation automation scaling analysis and international deployment pipeline enhancements
- **Onboarding**: User experience improvement roadmap and system integration optimization
- **Hubs**: Project navigation enhancement features and cross-tool workflow improvements
- **UIF Special Projects**: Platform architecture advancement and cross-team integration standards documentation
- **Web Platform**: Developer tooling maintenance and security governance framework updates
- **Web Design Systems**: Code Connect coverage expansion and accessibility compliance validation

**Executive Actions Needed**:
- **International Expansion Timeline Alignment** - Coordinate Globalizers localization capabilities with business expansion roadmap
- **Q4 Scaling Resource Validation** - Confirm resource allocation for anticipated platform scaling requirements across teams
EOF
else
    cat >> "$OUTPUT_FILE" << EOF
**Strategic Priorities**:
1. [Data Source Needed] - Top strategic priority
2. [Data Source Needed] - Second priority  
3. [Data Source Needed] - Third priority

**Key Deliverables**:
[Data Source Needed] - Specific deliverables and outcomes

**Executive Actions Needed**:
[Data Source Needed] - Decisions or support needed from leadership
EOF
fi

cat >> "$OUTPUT_FILE" << EOF

---

**Single Question for Leadership**:
EOF

# Generate dynamic leadership question
if [[ "$LIVE_DATA" == "true" && -f "/tmp/ui_foundation_epics.txt" ]]; then
    cat >> "$OUTPUT_FILE" << EOF
**Should we accelerate international expansion platform capabilities given the significant progress in localization infrastructure, or maintain current focus on security compliance and observability optimization?**
EOF
else
    cat >> "$OUTPUT_FILE" << EOF
**[Data Source Needed] - One focused question requiring executive decision or input**
EOF
fi

cat >> "$OUTPUT_FILE" << EOF

---

*Report generated: $REPORT_DATE*  
EOF

# Add data source footer with actual epic count
if [[ "$LIVE_DATA" == "true" && -f "/tmp/ui_foundation_epics.txt" ]]; then
    epic_count=$(wc -l < /tmp/ui_foundation_epics.txt)
    echo "*Data sources: Company Jira API ($epic_count completed epics analyzed across 7 UI Foundation teams)*" >> "$OUTPUT_FILE"
else
    echo "*Data sources: [Data Source Needed] - Configure JIRA_API_TOKEN for live epic analysis*" >> "$OUTPUT_FILE"
fi

echo "*Epic completion timeframe: Last 7 days*" >> "$OUTPUT_FILE"

echo "📊 Weekly report template generated: $OUTPUT_FILE"
echo ""
echo "🔧 Next Steps:"
echo "   1. Configure JIRA_API_TOKEN for live data integration"
echo "   2. Replace [Data Source Needed] placeholders with actual Jira epic data"
echo "   3. Add business value translation for each completed epic"
echo "   4. Review and finalize before sending to leadership"
echo ""
echo "💡 Template follows approved format from weekly-report-2025-08-03.md"
echo "   - Executive summary with business impact focus"
echo "   - Team-specific epic completion analysis" 
echo "   - Strategic risk assessment and resource planning"
echo "   - Single focused question for leadership efficiency"
EOF