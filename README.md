# ClaudeDirector: Strategic Leadership AI Framework

**Claude specialized for engineering directors** - Get strategic AI assistance with persistent memory and intelligent task tracking.

## 🚀 Quick Start (1 minute)

### 1. Install ClaudeDirector
```bash
git clone https://github.com/chriscantu/claudedirector.git
cd claudedirector
```

### 2. One-Command Setup
```bash
# Single command sets up everything
./claudedirector setup
```

### 3. Start Using ClaudeDirector
```bash
# Daily executive dashboard
./claudedirector alerts

# Scan workspace for stakeholders and tasks  
./claudedirector stakeholders scan
./claudedirector tasks scan

# View your strategic intelligence
./claudedirector status
```

**That's it!** ClaudeDirector is now your strategic leadership assistant.

## ✨ What You Get

### 🧠 **Strategic AI Personas**
12 specialized personas for different leadership contexts:
- **diego**: Engineering leadership, platform strategy
- **camille**: Strategic technology, organizational scaling
- **rachel**: Design systems, cross-functional alignment
- **alvaro**: Platform ROI, business value communication

### 🎯 **Intelligent Meeting Tracking**
- Automatically detects new meeting prep directories
- Extracts strategic intelligence from meeting notes
- Builds persistent memory across leadership sessions
- Suggests optimal AI personas for different meeting types

### 🗄️ **Persistent Strategic Memory**
- SQLite database stores organizational intelligence
- Executive sessions, stakeholder relationships, platform insights
- Context persists across Claude conversations
- No more re-explaining your org structure every session

## 🎯 **Unified Command Interface**

All ClaudeDirector features accessible through single `claudedirector` command:

### **📊 Executive Dashboard**
```bash
./claudedirector alerts              # Daily executive alerts
./claudedirector status              # System health overview
```

### **🧠 Meeting Intelligence**
```bash
./claudedirector meetings scan       # Process meeting files
./claudedirector meetings demo       # See demo
```

### **👥 Stakeholder Management**
```bash
./claudedirector stakeholders scan   # AI detect stakeholders
./claudedirector stakeholders list   # View all stakeholders
./claudedirector stakeholders alerts # Daily engagement alerts
```

### **🎯 Task Management**
```bash
./claudedirector tasks scan          # AI detect tasks
./claudedirector tasks list          # View my tasks
./claudedirector tasks overdue       # Critical overdue items
./claudedirector tasks followups     # Stakeholder follow-ups
```

### **⚡ Smart Development**
```bash
./claudedirector git setup          # Intelligent git hooks
./claudedirector git commit -m "msg" # Optimized commits
```

## 🏗️ Architecture

ClaudeDirector provides **unified strategic leadership AI** through:

1. **🎭 Strategic AI Foundation**: 12 specialized personas for different leadership contexts
2. **🧠 Intelligent Automation**: AI-powered stakeholder detection and task extraction
3. **📊 Executive Intelligence**: Proactive alerts and accountability tracking
4. **💾 Persistent Memory**: SQLite-based organizational intelligence that persists across sessions

## 📚 Advanced Features (Optional)

### Jira Integration for Strategic Reporting

<details>
<summary>🔧 Enterprise Jira Integration Setup (Click to expand)</summary>

If you want automated strategic initiative tracking and executive reporting:

```bash
# Set up the Python service
cd strategic_integration_service
python -m venv venv
source venv/bin/activate
pip install -e .

# Configure environment
cp env.example .env
# Edit .env with your Jira credentials

# Extract strategic initiatives
sis-extract-l2 --output workspace/l2-initiatives.json
sis-weekly-report --output workspace/weekly-slt-report.md
```

**Features:**
- Automated L2 strategic initiative extraction
- Weekly SLT executive reports
- Monthly PI initiative analysis
- Performance optimization with multi-tier caching

**Requirements:**
- Jira API access
- Strategic initiative structure in your Jira instance
- Organizational buy-in for automated reporting

</details>

### Custom Persona Development

<details>
<summary>🎭 Creating Custom Strategic Personas (Click to expand)</summary>

You can extend ClaudeDirector with your own strategic personas:

1. Add to `claude_config.yaml`:
```yaml
personas:
  your_persona:
    description: "Your custom leadership context"
    context: "Specific domain expertise and communication style"
```

2. Reference in conversations:
```
@your_persona: How should we approach this technical decision?
```

</details>

### Development Workflow Optimization

<details>
<summary>⚡ Smart Git Hooks for Contributors (Click to expand)</summary>

If you're contributing to ClaudeDirector or customizing the codebase:

```bash
# Smart commit that skips irrelevant checks
git sc -m "Update meeting notes"  # Saves ~45s for documentation

# Traditional commit for code changes (full validation)
git commit -m "Fix critical bug"  # Full security + quality checks

# Analyze what would be optimized
git analyze-commit  # Preview optimization strategy
```

**Features:**
- File-type-aware git hooks that save 10-45 seconds per commit
- Skips Python tests for documentation changes
- Maintains quality with security scanning where critical
- Intelligent hook filtering based on changed file types

**When useful:**
- Contributing to the ClaudeDirector codebase
- Customizing strategic integration scripts
- Frequent documentation updates
- Development workflow optimization

</details>

### Performance Monitoring

<details>
<summary>📊 System Health and Performance (Click to expand)</summary>

Monitor ClaudeDirector's performance and strategic intelligence:

```bash
# Meeting intelligence health
python memory/meeting_intelligence.py --summary

# Database integrity
sqlite3 memory/strategic_memory.db "PRAGMA integrity_check;"

# Git optimization stats
git sc --analyze-only  # See what would be optimized
```

</details>

## 🚀 Next Steps

### Immediate Value (Day 1)
1. ✅ **Set up meeting tracking** - Let ClaudeDirector learn your meeting patterns
2. ✅ **Try strategic personas** - Use `@diego` for platform decisions, `@camille` for scaling
3. ✅ **Create first meeting prep** - `mkdir workspace/meeting-prep/weekly-1on1`

### Strategic Value (Week 1)
1. **Build meeting intelligence** - Create 3-5 meeting prep directories
2. **Leverage persistent memory** - Reference past strategic decisions in Claude conversations
3. **Optimize persona usage** - Use appropriate personas for different meeting contexts

### Enterprise Value (Month 1)
1. **Consider Jira integration** - Automate strategic reporting
2. **Customize personas** - Add org-specific strategic contexts
3. **Scale team adoption** - Share meeting intelligence patterns across leadership team

## 🆘 Getting Help

### Quick Troubleshooting
   ```bash
# Check system health
python setup_meeting_intelligence.py --verify-only

# Reset if needed
python setup_meeting_intelligence.py --scan-only
```

### Common Issues
- **Import errors**: Run from project root directory
- **Database issues**: Re-run `python setup_meeting_intelligence.py`
- **Meeting tracking not working**: Check that `workspace/meeting-prep/` directory exists

---

**ClaudeDirector**: From AI assistant to strategic platform engineering partner.

*Built for engineering directors who want strategic AI that remembers, learns, and optimizes for leadership effectiveness.*
