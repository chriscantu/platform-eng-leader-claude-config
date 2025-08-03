# SuperClaude Platform Leadership Configuration

**Strategic Claude Code configuration system for Directors of Engineering leading web platform organizations.**

Comprehensive framework for strategic platform leadership, executive communication, and organizational effectiveness with automated workflows and dynamic intelligence.

## 🎯 Strategic Overview

**For**: Directors of Engineering, Platform Leaders, Technical Executives
**Purpose**: Strategic platform leadership with VP/SLT communication optimization
**Scope**: Web platform organizations (Design System, i18n, UI Foundation, Developer Experience)

### Key Capabilities
- **Executive Communication**: VP-specific meeting prep, strategic presentations, business case development
- **Platform Intelligence**: Real-time adoption metrics, stakeholder analysis, competitive positioning
- **Organizational Leverage**: Cross-team coordination, resource optimization, strategic architecture
- **Automated Workflows**: Configuration sync, maintenance automation, context intelligence

## 🚀 Quick Start

### Prerequisites
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and configured
- macOS/Linux environment with bash
- Git repository access
- Optional: Jira API access for weekly reporting

### 1. Installation
```bash
# Clone this repository
git clone <your-repo-url>
cd platform-eng-leader-claude-config

# Run the automated setup
./setup.sh

# Verify installation
claude --version
```

### 2. Configuration Sync
```bash
# Sync global configuration to this project
~/.claude/workflows/sync-context.sh global-to-local

# Verify sync
ls .claude/
```

### 3. Test Strategic Commands
```bash
# Test platform health assessment
/assess-platform-health adoption --platform-health

# Test stakeholder analysis
/analyze-stakeholder vp_engineering "quarterly planning"

# Test executive communication prep
/prepare-slt "Q4 Platform Strategy" --executive-brief
```

## 📋 Configuration Architecture

### Global Configuration (`~/.claude/`)
```
~/.claude/
├── CLAUDE.md                 # Entry point with UI Foundation context
├── PERSONAS.md               # Strategic leadership persona system
├── COMMANDS.md               # Strategic command framework
├── FLAGS.md                  # Director-level flag system
├── PRINCIPLES.md             # Strategic leadership principles
├── RULES.md                  # Operational rules and quick reference
├── MCP.md                    # MCP server orchestration
├── ORCHESTRATOR.md           # Strategic routing intelligence
├── MODES.md                  # Task management and efficiency modes
├── context/
│   ├── STAKEHOLDERS.yaml     # Dynamic stakeholder intelligence
│   └── TECHNOLOGY_RADAR.yaml # Platform health and competitive intelligence
├── workflows/
│   ├── sync-context.sh       # Configuration synchronization
│   ├── optimize-config.sh    # Performance optimization
│   ├── daily-maintenance.sh  # Daily health checks
│   ├── weekly-maintenance.sh # Weekly optimization
│   └── monthly-maintenance.sh # Deep maintenance
└── logs/                     # Maintenance and optimization logs
```

### Local Project Configuration (`.claude/`)
- Synchronized copy of global configuration
- Project-specific context overlays
- Local workflow customizations
- Protected by .gitignore (sensitive data)

## 🎯 Strategic Commands

### Executive Communication
```bash
# VP-level meeting preparation
/prep-vp-engineering "technical strategy review" --vp-engineering-prep
/prep-vp-product "platform roadmap alignment" --vp-product-prep
/prep-vp-design "design system strategy" --vp-design-prep

# Strategic presentations
/prepare-slt "Q4 Platform Investment Strategy" --executive-brief

# Investment business cases
/justify-investment "design system evolution" --platform-health --executive-brief
```

### Platform Intelligence
```bash
# Real-time platform health
/assess-platform-health adoption --business-impact --executive-summary

# Stakeholder analysis with decision patterns
/analyze-stakeholder vp_engineering "budget planning" --meeting-prep

# Vendor strategy
/prep-vendor-negotiation figma --tco-analysis --competitive-alternatives
```

### Organizational Coordination
```bash
# Cross-team alignment
/align-stakeholders "design system adoption" --stakeholder-align

# Resource planning
/estimate platform-team-scaling --team-readiness --budget-optimization

# Weekly SLT reporting (with Jira integration)
/generate-weekly-report --config weekly-report-config.yaml --stakeholder vp
```

## 👥 Strategic Personas

Auto-activated based on context with strategic leadership focus:

### Primary Strategic Leadership
- **diego**: Engineering leadership, platform strategy, multinational coordination
- **camille**: Strategic technology, organizational scaling, executive advisory
- **rachel**: Design systems strategy, cross-functional alignment, UX leadership
- **alvaro**: Platform investment ROI, business value, stakeholder communication

### Platform Operations
- **sofia**: Vendor relationships, tool evaluation, technology partnerships
- **elena**: Accessibility compliance, legal requirements, audit management
- **marcus**: Internal adoption, change management, platform marketing
- **david**: Platform investment allocation, cost optimization, financial planning

### Technical Architecture
- **martin**: Platform architecture, evolutionary design, technical debt strategy

## 🎛️ Strategic Flags

Director-level optimization flags with auto-activation:

### Executive Communication
- `--executive-brief`: VP-level focused output with business impact translation
- `--single-question`: Ask ONE focused question (auto-activates for VP/SLT contexts)
- `--stakeholder-align`: Cross-functional coordination planning + dependency mapping

### Platform Intelligence
- `--platform-health`: Comprehensive platform assessment with adoption metrics
- `--vendor-eval`: Third-party tool assessment with TCO analysis + risk evaluation
- `--team-readiness`: Organizational capability evaluation + scaling assessment

### VP-Specific Preparation
- `--vp-product-prep`: VP of Product meeting preparation with business value focus
- `--vp-engineering-prep`: VP of Engineering meeting preparation with technical leadership
- `--vp-design-prep`: VP of Design meeting preparation with design system strategy

## 🔄 Automated Workflows

### Configuration Synchronization
```bash
# Sync global → local
~/.claude/workflows/sync-context.sh global-to-local

# Sync local → global  
~/.claude/workflows/sync-context.sh local-to-global

# Bidirectional sync
~/.claude/workflows/sync-context.sh bidirectional
```

### Maintenance Automation
```bash
# Daily health check (lightweight)
~/.claude/workflows/daily-maintenance.sh

# Weekly optimization (comprehensive)
~/.claude/workflows/weekly-maintenance.sh

# Monthly deep maintenance (performance tuning)
~/.claude/workflows/monthly-maintenance.sh

# Full configuration optimization
~/.claude/workflows/optimize-config.sh
```

### Automated Scheduling
Set up automatic maintenance using macOS LaunchAgent or cron:
```bash
# Review automation options
cat ~/.claude/AUTOMATION_SETUP.md

# Set up automated daily/weekly/monthly maintenance
```

## 📊 Context Intelligence

### Dynamic Stakeholder Intelligence
**File**: `~/.claude/context/STAKEHOLDERS.yaml`

VP-level stakeholder profiles with:
- Communication styles and preferences
- Decision-making criteria and patterns
- Escalation thresholds and protocols
- Historical context and relationship dynamics

### Technology Radar
**File**: `~/.claude/context/TECHNOLOGY_RADAR.yaml`

Platform intelligence including:
- Current adoption metrics and health indicators
- Technology evaluation pipeline and investment tracking
- Competitive analysis and market positioning
- Innovation experiments and emerging technology bets

## 🎯 Use Cases

### Executive Meeting Preparation
```bash
# VP of Engineering 1-on-1 prep
/prep-vp-engineering "Q4 platform roadmap" --platform-health --team-readiness

# Design leadership alignment
/align-stakeholders "accessibility compliance initiative" --compliance-scan

# Budget planning session
/justify-investment "internationalization platform" --vendor-eval --executive-brief
```

### Strategic Platform Analysis
```bash
# Quarterly platform health assessment
/assess-platform-health comprehensive --adoption-analysis --business-impact

# Vendor evaluation for design tools
/prep-vendor-negotiation figma --tco-analysis --contract-strategy

# Cross-team dependency optimization
/analyze platform-dependencies --stakeholder-align --team-readiness
```

### Weekly Reporting Automation
```bash
# Generate automated SLT report with Jira integration
/generate-weekly-report --teams "web-platform,design-system,i18n" --format markdown

# Create executive summary for VP
/generate-weekly-report --stakeholder vp_engineering --executive-brief
```

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Weekly reporting (optional)
export JIRA_API_TOKEN="your-jira-token"
export JIRA_EMAIL="your-email@company.com"
export JIRA_BASE_URL="https://company.atlassian.net"

# Claude Code optimization
export CLAUDE_GLOBAL_DIR="$HOME/.claude"
```

### Customization
- **Stakeholder Profiles**: Edit `~/.claude/context/STAKEHOLDERS.yaml`
- **Technology Radar**: Update `~/.claude/context/TECHNOLOGY_RADAR.yaml`
- **Maintenance Schedule**: Modify `~/.claude/workflows/*-maintenance.sh`
- **Command Behavior**: Customize `~/.claude/COMMANDS.md`

## 🔍 Monitoring & Optimization

### Health Checks
```bash
# View recent maintenance activity
tail -f ~/.claude/logs/maintenance.log

# Check optimization reports
ls ~/.claude/logs/optimization-report-*.md

# Configuration size monitoring
du -sh ~/.claude/
```

### Performance Optimization
- **Token Efficiency**: Automatic `--uc` compression for large contexts
- **MCP Server Caching**: Intelligent caching for Context7, Sequential, Magic
- **Strategic Routing**: Auto-activation based on executive context detection
- **Quality Gates**: Validation checkpoints for strategic decision-making

## 📚 Documentation

### Core Framework Files
- **[CLAUDE.md](.claude/CLAUDE.md)**: UI Foundation context and meeting workflows
- **[PERSONAS.md](.claude/PERSONAS.md)**: Strategic leadership persona system
- **[COMMANDS.md](.claude/COMMANDS.md)**: Strategic command framework and pipelines
- **[FLAGS.md](.claude/FLAGS.md)**: Director-level flags and auto-activation
- **[PRINCIPLES.md](.claude/PRINCIPLES.md)**: Strategic leadership principles and decision frameworks
- **[RULES.md](.claude/RULES.md)**: Operational rules and quick reference
- **[ORCHESTRATOR.md](.claude/ORCHESTRATOR.md)**: Strategic routing and intelligence system

### Setup and Maintenance
- **[AUTOMATION_SETUP.md](~/.claude/AUTOMATION_SETUP.md)**: Automated maintenance configuration
- **Weekly Report Config**: Example configuration for Jira integration and business value translation

## 🆘 Troubleshooting

### Common Issues

**Configuration Sync Issues**:
```bash
# Verify sync script permissions
chmod +x ~/.claude/workflows/sync-context.sh

# Manual sync check
~/.claude/workflows/sync-context.sh --dry-run
```

**Persona Auto-Activation Problems**:
```bash
# Check persona definitions
grep "^## \`--persona-" ~/.claude/PERSONAS.md

# Test persona activation
/analyze platform-strategy --persona-diego --introspect
```

**Performance Issues**:
```bash
# Run optimization
~/.claude/workflows/optimize-config.sh

# Check file sizes
wc -c ~/.claude/PERSONAS.md ~/.claude/COMMANDS.md
```

### Support

**Configuration Validation**:
- Use `--introspect` flag to debug decision-making
- Check `~/.claude/logs/` for maintenance and optimization reports
- Verify MCP server integration with strategic commands

**Best Practices**:
- Run weekly optimization to maintain performance
- Keep PERSONAS.md under 45KB for optimal Claude Code performance
- Use context-aware commands for strategic workflows
- Enable auto-maintenance for hands-off operation

## 🚀 Getting Started Checklist

- [ ] Install Claude Code CLI and verify access
- [ ] Run `./setup.sh` for automated configuration
- [ ] Test basic strategic commands (`/assess-platform-health`, `/analyze-stakeholder`)
- [ ] Configure stakeholder profiles in `STAKEHOLDERS.yaml`
- [ ] Set up automated maintenance schedule
- [ ] Test VP-specific meeting preparation commands
- [ ] Enable weekly reporting (optional: configure Jira integration)
- [ ] Review and customize persona behaviors for your organization

## 📞 Advanced Usage

For advanced configuration, custom persona development, or organizational-specific customizations, review the core framework files and consider:

- **Custom Stakeholder Profiles**: Tailor decision patterns for your organization
- **Strategic Command Extensions**: Add organization-specific strategic workflows
- **Integration Patterns**: Connect with your organization's tools and processes
- **Executive Communication Templates**: Customize for your leadership team's preferences

---

**SuperClaude Platform Leadership Configuration** - Strategic technology leadership through intelligent automation and executive-optimized communication.