#!/bin/bash

# SuperClaude Platform Leadership Configuration Setup
# Automated installation and configuration script for Directors of Engineering

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_GLOBAL_DIR="${HOME}/.claude"
PROJECT_CLAUDE_DIR="${SCRIPT_DIR}/.claude"
DATE_STAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging
LOG_FILE="/tmp/supercloud-setup-${DATE_STAMP}.log"

log() {
    echo -e "${1}" | tee -a "${LOG_FILE}"
}

error_exit() {
    log "${RED}❌ ERROR: ${1}${NC}"
    log "📋 Setup log: ${LOG_FILE}"
    exit 1
}

# Header
print_header() {
    clear
    log "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    log "${BLUE}║                                                               ║${NC}"
    log "${BLUE}║         ${GREEN}SuperClaude Platform Leadership Configuration${BLUE}         ║${NC}"
    log "${BLUE}║                                                               ║${NC}"
    log "${BLUE}║     ${PURPLE}Strategic AI framework for Directors of Engineering${BLUE}      ║${NC}"
    log "${BLUE}║                                                               ║${NC}"
    log "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    log ""
    log "${YELLOW}🎯 Setting up strategic platform leadership capabilities...${NC}"
    log ""
}

# Prerequisites check
check_prerequisites() {
    log "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check if Claude Code is installed
    if ! command -v claude &> /dev/null; then
        error_exit "Claude Code CLI not found. Please install from: https://docs.anthropic.com/en/docs/claude-code"
    fi
    
    # Check Claude Code version
    local claude_version=$(claude --version 2>/dev/null || echo "unknown")
    log "  ✅ Claude Code CLI: ${claude_version}"
    
    # Check bash version
    if [[ ${BASH_VERSION%%.*} -lt 4 ]]; then
        log "  ⚠️  Bash version ${BASH_VERSION} detected. Version 4+ recommended for optimal performance."
    else
        log "  ✅ Bash version: ${BASH_VERSION}"
    fi
    
    # Check operating system
    case "$(uname -s)" in
        Darwin*) log "  ✅ macOS detected" ;;
        Linux*)  log "  ✅ Linux detected" ;;
        *)       log "  ⚠️  Unsupported OS detected. Proceeding with caution." ;;
    esac
    
    # Check for git
    if ! command -v git &> /dev/null; then
        log "  ⚠️  Git not found. Some features may be limited."
    else
        log "  ✅ Git available"
    fi
    
    log "${GREEN}✅ Prerequisites check completed${NC}"
    log ""
}

# Backup existing configuration
backup_existing_config() {
    if [[ -d "${CLAUDE_GLOBAL_DIR}" ]]; then
        log "${BLUE}💾 Backing up existing Claude configuration...${NC}"
        
        local backup_dir="${CLAUDE_GLOBAL_DIR}/backups/pre-supercloud-${DATE_STAMP}"
        mkdir -p "${backup_dir}"
        
        # Backup core files if they exist
        local core_files=(
            "CLAUDE.md" "PERSONAS.md" "COMMANDS.md" "FLAGS.md" 
            "PRINCIPLES.md" "RULES.md" "MCP.md" "ORCHESTRATOR.md" "MODES.md"
        )
        
        local backed_up_count=0
        for file in "${core_files[@]}"; do
            if [[ -f "${CLAUDE_GLOBAL_DIR}/${file}" ]]; then
                cp "${CLAUDE_GLOBAL_DIR}/${file}" "${backup_dir}/"
                ((backed_up_count++))
            fi
        done
        
        # Backup directories
        for dir in "context" "workflows" "logs"; do
            if [[ -d "${CLAUDE_GLOBAL_DIR}/${dir}" ]]; then
                cp -r "${CLAUDE_GLOBAL_DIR}/${dir}" "${backup_dir}/"
                ((backed_up_count++))
            fi
        done
        
        if [[ ${backed_up_count} -gt 0 ]]; then
            log "  ✅ Backed up ${backed_up_count} items to: ${backup_dir}"
        else
            log "  ℹ️  No existing configuration found to backup"
        fi
    else
        log "${BLUE}📁 No existing Claude configuration found${NC}"
    fi
}

# Install global configuration
install_global_config() {
    log "${BLUE}📦 Installing SuperClaude global configuration...${NC}"
    
    # Create global directory structure
    mkdir -p "${CLAUDE_GLOBAL_DIR}"
    mkdir -p "${CLAUDE_GLOBAL_DIR}/context"
    mkdir -p "${CLAUDE_GLOBAL_DIR}/workflows"
    mkdir -p "${CLAUDE_GLOBAL_DIR}/logs"
    mkdir -p "${CLAUDE_GLOBAL_DIR}/backups"
    
    # Copy core framework files
    local core_files=(
        "CLAUDE.md" "PERSONAS.md" "COMMANDS.md" "FLAGS.md" 
        "PRINCIPLES.md" "RULES.md" "MCP.md" "ORCHESTRATOR.md" "MODES.md"
    )
    
    log "  📋 Installing core framework files..."
    for file in "${core_files[@]}"; do
        if [[ -f "${SCRIPT_DIR}/${file}" ]]; then
            cp "${SCRIPT_DIR}/${file}" "${CLAUDE_GLOBAL_DIR}/"
            log "    ✅ ${file}"
        else
            log "    ⚠️  Missing: ${file}"
        fi
    done
    
    log "${GREEN}✅ Global configuration installed${NC}"
}

# Setup context intelligence
setup_context_intelligence() {
    log "${BLUE}🧠 Setting up context intelligence system...${NC}"
    
    # Create STAKEHOLDERS.yaml template
    cat > "${CLAUDE_GLOBAL_DIR}/context/STAKEHOLDERS.yaml" << 'EOF'
# Dynamic Stakeholder Intelligence
# VP-level stakeholder profiles with decision patterns and communication preferences

stakeholders:
  vp_engineering:
    name: "VP of Engineering"
    role: "Engineering Leadership"
    communication_style: "data-driven, metrics-focused, single-question efficiency"
    decision_criteria: 
      - "team productivity metrics"
      - "platform ROI quantification"
      - "technical risk assessment"
      - "resource optimization strategies"
    escalation_threshold: ">$100K investment, >20% productivity impact, platform-wide breaking changes"
    meeting_preferences:
      - "concise executive summaries"
      - "clear action items and owners"
      - "quantified business impact"
    communication_frequency: "weekly 1-on-1, monthly strategic review"
    
  vp_product:
    name: "VP of Product"
    role: "Product Leadership"
    communication_style: "user-focused, business-impact oriented, competitive positioning"
    decision_criteria:
      - "user experience impact"
      - "product-market fit correlation"
      - "competitive differentiation"
      - "development velocity enablement"
    escalation_threshold: "user experience degradation, product roadmap conflicts, cross-team blockers"
    meeting_preferences:
      - "user journey impact analysis"
      - "competitive positioning insights"
      - "platform capability correlation to product outcomes"
    communication_frequency: "bi-weekly alignment, quarterly strategy review"
    
  vp_design:
    name: "VP of Design"
    role: "Design Leadership"
    communication_style: "design system strategy, accessibility compliance, user experience consistency"
    decision_criteria:
      - "design system adoption rates"
      - "accessibility compliance scores"
      - "cross-team design coordination"
      - "user experience consistency metrics"
    escalation_threshold: "accessibility violations, design system breaking changes, brand inconsistency"
    meeting_preferences:
      - "design impact metrics"
      - "accessibility compliance status"
      - "cross-functional design coordination"
    communication_frequency: "monthly design system review, quarterly UX strategy"

# Add your organization's stakeholders here
# Examples: CEO, CTO, Product Directors, Engineering Directors, etc.
EOF

    # Create TECHNOLOGY_RADAR.yaml template
    cat > "${CLAUDE_GLOBAL_DIR}/context/TECHNOLOGY_RADAR.yaml" << 'EOF'
# Technology Radar & Platform Intelligence
# Platform health metrics, competitive analysis, and technology evaluation pipeline

platform_health:
  current_metrics:
    design_system_adoption: 73%
    developer_satisfaction: 8.2/10
    platform_velocity_multiplier: 2.3x
    accessibility_compliance: 94%
    internationalization_coverage: 85%
    
  adoption_trends:
    - component: "Button Library"
      adoption: 95%
      trend: "stable"
      satisfaction: 9.1/10
    - component: "Form Components"
      adoption: 78%
      trend: "growing"
      satisfaction: 8.5/10
    - component: "Navigation Shell"
      adoption: 89%
      trend: "stable"
      satisfaction: 8.8/10
      
technology_evaluation:
  current_evaluations:
    - technology: "Next.js 15"
      status: "trial"
      impact: "high"
      timeline: "Q4 2025"
      owner: "Web Platform Team"
    - technology: "Figma Dev Mode"
      status: "assess"
      impact: "medium"
      timeline: "Q1 2026"
      owner: "Design System Team"
      
  investment_pipeline:
    - capability: "Component Testing Framework"
      investment: "$150K"
      roi_timeline: "6 months"
      business_value: "reduced QA overhead, faster release cycles"
    - capability: "Internationalization Automation"
      investment: "$200K"
      roi_timeline: "12 months"
      business_value: "market expansion enablement, compliance risk reduction"

competitive_intelligence:
  market_positioning:
    - competitor: "Industry Leader A"
      strength: "mature design system"
      gap: "accessibility compliance"
      opportunity: "international expansion"
    - competitor: "Industry Leader B"
      strength: "developer experience"
      gap: "cross-platform consistency"
      opportunity: "mobile-first approach"

# Update quarterly with current metrics and evaluations
last_updated: "2025-08-03"
next_review: "2025-11-03"
EOF

    log "  ✅ Stakeholder intelligence template created"
    log "  ✅ Technology radar template created"
    log "${GREEN}✅ Context intelligence system configured${NC}"
}

# Setup automated workflows
setup_workflows() {
    log "${BLUE}🔄 Setting up automated workflows...${NC}"
    
    # Check if sync script exists in the current project
    if [[ -f "${SCRIPT_DIR}/sync-claude-config.sh" ]]; then
        # Copy existing sync script to workflows as sync-context.sh
        cp "${SCRIPT_DIR}/sync-claude-config.sh" "${CLAUDE_GLOBAL_DIR}/workflows/sync-context.sh"
        chmod +x "${CLAUDE_GLOBAL_DIR}/workflows/sync-context.sh"
        log "  ✅ Configuration sync script installed"
    fi
    
    # Check if optimization and maintenance scripts exist globally
    if [[ -f "${CLAUDE_GLOBAL_DIR}/workflows/optimize-config.sh" ]]; then
        log "  ✅ Optimization script already available"
    else
        log "  ℹ️  Optimization script will be created during first maintenance run"
    fi
    
    if [[ -f "${CLAUDE_GLOBAL_DIR}/workflows/daily-maintenance.sh" ]]; then
        log "  ✅ Maintenance scripts already available"
    else
        log "  ℹ️  Maintenance scripts will be created during first setup"
    fi
    
    log "${GREEN}✅ Workflow automation configured${NC}"
}

# Setup local project configuration
setup_local_config() {
    log "${BLUE}📁 Setting up local project configuration...${NC}"
    
    # Create local .claude directory
    mkdir -p "${PROJECT_CLAUDE_DIR}"
    
    # Create .gitignore for .claude directory
    cat > "${SCRIPT_DIR}/.gitignore" << 'EOF'
# SuperClaude Configuration
.claude/context/STAKEHOLDERS.yaml
.claude/context/TECHNOLOGY_RADAR.yaml
.claude/logs/
.claude/backups/
*.log

# Environment variables
.env
.env.local

# Sensitive configuration
weekly-report-config.yaml
*-config.yaml
*-credentials.*

# Temporary files
*.tmp
*.temp
current-jira-data.json
EOF

    # Run initial sync if sync script is available
    if [[ -x "${CLAUDE_GLOBAL_DIR}/workflows/sync-context.sh" ]]; then
        log "  🔄 Running initial configuration sync..."
        cd "${SCRIPT_DIR}"
        "${CLAUDE_GLOBAL_DIR}/workflows/sync-context.sh" global-to-local || log "  ⚠️  Initial sync encountered issues (this is normal for first setup)"
    fi
    
    log "  ✅ Local project configuration created"
    log "  ✅ .gitignore configured for sensitive data protection"
    log "${GREEN}✅ Local configuration setup completed${NC}"
}

# Environment setup
setup_environment() {
    log "${BLUE}🌍 Setting up environment configuration...${NC}"
    
    # Create environment template
    cat > "${SCRIPT_DIR}/.env.template" << 'EOF'
# SuperClaude Environment Configuration Template
# Copy this to .env and configure for your organization

# Claude Code Configuration
CLAUDE_GLOBAL_DIR="$HOME/.claude"

# Jira Integration (Optional - for weekly reporting)
# JIRA_API_TOKEN="your-jira-api-token"
# JIRA_EMAIL="your-email@company.com"
# JIRA_BASE_URL="https://company.atlassian.net"

# Organization Context
# ORGANIZATION_NAME="Your Company"
# PLATFORM_TEAM_NAME="UI Foundation"
# VP_ENGINEERING_NAME="VP Engineering Name"

# Notification Settings (Optional)
# SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
# EMAIL_NOTIFICATIONS="your-email@company.com"
EOF

    # Add environment variables to shell profile (optional)
    local shell_profile=""
    if [[ -f "${HOME}/.zshrc" ]]; then
        shell_profile="${HOME}/.zshrc"
    elif [[ -f "${HOME}/.bashrc" ]]; then
        shell_profile="${HOME}/.bashrc"
    elif [[ -f "${HOME}/.bash_profile" ]]; then
        shell_profile="${HOME}/.bash_profile"
    fi
    
    if [[ -n "${shell_profile}" ]]; then
        if ! grep -q "CLAUDE_GLOBAL_DIR" "${shell_profile}" 2>/dev/null; then
            log "  📝 Adding environment variables to ${shell_profile}"
            echo "" >> "${shell_profile}"
            echo "# SuperClaude Configuration" >> "${shell_profile}"
            echo 'export CLAUDE_GLOBAL_DIR="$HOME/.claude"' >> "${shell_profile}"
            log "  ✅ Environment variables added to shell profile"
        else
            log "  ✅ Environment variables already configured"
        fi
    fi
    
    log "  ✅ Environment template created (.env.template)"
    log "${GREEN}✅ Environment configuration completed${NC}"
}

# Run initial tests
run_initial_tests() {
    log "${BLUE}🧪 Running initial system tests...${NC}"
    
    # Test file structure
    local required_files=(
        "${CLAUDE_GLOBAL_DIR}/CLAUDE.md"
        "${CLAUDE_GLOBAL_DIR}/PERSONAS.md"
        "${CLAUDE_GLOBAL_DIR}/COMMANDS.md"
    )
    
    local missing_files=0
    for file in "${required_files[@]}"; do
        if [[ -f "${file}" ]]; then
            log "  ✅ $(basename "${file}")"
        else
            log "  ❌ Missing: $(basename "${file}")"
            ((missing_files++))
        fi
    done
    
    # Test context intelligence
    if [[ -f "${CLAUDE_GLOBAL_DIR}/context/STAKEHOLDERS.yaml" ]]; then
        log "  ✅ Stakeholder intelligence"
    else
        log "  ❌ Missing stakeholder intelligence"
        ((missing_files++))
    fi
    
    if [[ -f "${CLAUDE_GLOBAL_DIR}/context/TECHNOLOGY_RADAR.yaml" ]]; then
        log "  ✅ Technology radar"
    else
        log "  ❌ Missing technology radar"
        ((missing_files++))
    fi
    
    # Test workflow scripts
    local workflow_count=0
    if [[ -d "${CLAUDE_GLOBAL_DIR}/workflows" ]]; then
        workflow_count=$(find "${CLAUDE_GLOBAL_DIR}/workflows" -name "*.sh" -type f | wc -l)
    fi
    
    if [[ ${workflow_count} -gt 0 ]]; then
        log "  ✅ Workflow automation (${workflow_count} scripts)"
    else
        log "  ⚠️  No workflow scripts found (will be created on first use)"
    fi
    
    # Test Claude Code integration
    if command -v claude &> /dev/null; then
        log "  ✅ Claude Code CLI integration"
    else
        log "  ❌ Claude Code CLI not accessible"
        ((missing_files++))
    fi
    
    if [[ ${missing_files} -gt 0 ]]; then
        log "${YELLOW}⚠️  ${missing_files} issues detected. Please review the setup log.${NC}"
    else
        log "${GREEN}✅ All tests passed successfully${NC}"
    fi
}

# Post-installation instructions
show_next_steps() {
    log ""
    log "${GREEN}🎉 SuperClaude Platform Leadership Configuration installed successfully!${NC}"
    log ""
    log "${BLUE}📋 Next Steps:${NC}"
    log ""
    log "${YELLOW}1. Customize Your Configuration:${NC}"
    log "   • Edit stakeholder profiles: ${CLAUDE_GLOBAL_DIR}/context/STAKEHOLDERS.yaml"
    log "   • Update technology radar: ${CLAUDE_GLOBAL_DIR}/context/TECHNOLOGY_RADAR.yaml"
    log "   • Configure environment: Copy .env.template to .env and customize"
    log ""
    log "${YELLOW}2. Test Strategic Commands:${NC}"
    log "   claude --help                                    # Verify Claude Code works"
    log "   /assess-platform-health adoption --platform-health   # Test platform assessment"
    log "   /analyze-stakeholder vp_engineering \"quarterly planning\"  # Test stakeholder analysis"
    log "   /prepare-slt \"Q4 Platform Strategy\" --executive-brief    # Test executive prep"
    log ""
    log "${YELLOW}3. Set Up Automation (Optional):${NC}"
    log "   cat ~/.claude/AUTOMATION_SETUP.md              # Review automation options"
    log "   ~/.claude/workflows/daily-maintenance.sh        # Test maintenance scripts"
    log ""
    log "${YELLOW}4. Advanced Configuration:${NC}"
    log "   • Configure Jira integration for weekly reporting"
    log "   • Set up automated maintenance scheduling"
    log "   • Customize personas for your organization"
    log ""
    log "${BLUE}📚 Documentation:${NC}"
    log "   • README.md: Complete usage guide and examples"
    log "   • .claude/: Local configuration (synchronized with global)"
    log "   • ~/.claude/: Global configuration and workflows"
    log ""
    log "${BLUE}🆘 Support:${NC}"
    log "   • Use --introspect flag to debug decision-making"
    log "   • Check ~/.claude/logs/ for maintenance reports"
    log "   • Review troubleshooting section in README.md"
    log ""
    log "${GREEN}🚀 Ready for strategic platform leadership!${NC}"
    log ""
    log "${PURPLE}Setup log saved to: ${LOG_FILE}${NC}"
}

# Main installation function
main() {
    print_header
    
    # Installation steps
    check_prerequisites
    backup_existing_config
    install_global_config
    setup_context_intelligence
    setup_workflows
    setup_local_config
    setup_environment
    run_initial_tests
    show_next_steps
    
    log ""
    log "${GREEN}✅ SuperClaude Platform Leadership Configuration setup completed successfully!${NC}"
}

# Handle interruption
trap 'echo -e "\n${RED}Setup interrupted. Partial installation may be present.${NC}"; exit 1' INT TERM

# Run main installation
main "$@"