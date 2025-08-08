# ClaudeDirector: Strategic Leadership AI Framework

**Claude specialized for engineering directors** - Get strategic AI assistance with persistent memory and intelligent meeting tracking.

## 🚀 Quick Start (2 minutes)

### 1. Install ClaudeDirector
```bash
git clone https://github.com/chriscantu/claudedirector.git
cd claudedirector
```

### 2. Set Up Core Features
```bash
# Set up meeting intelligence and memory system
python setup_meeting_intelligence.py

# Optional: Set up smart git hooks (only if you plan to contribute/customize)
# python setup_smart_git.py
```

### 3. Start Using ClaudeDirector
```bash
# Start automatic meeting tracking
python memory/workspace_monitor.py &

# Create a new meeting directory and watch it get processed automatically
mkdir workspace/meeting-prep/team-sync-jan-2025
```

**That's it!** ClaudeDirector is now tracking your meetings and building strategic memory.

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

## 📁 Your Workspace Structure

```
workspace/
├── meeting-prep/           # Your meeting directories (auto-monitored)
│   ├── vp-1on1-weekly/    # 1-on-1s with your VP
│   ├── team-planning/     # Strategic planning sessions
│   └── stakeholder-sync/  # Cross-team coordination
├── reports/               # Generated strategic reports
└── strategic_memory.db    # Your persistent AI memory
```

## 🎮 Usage Examples

### Create Meeting Intelligence
```bash
# Create new meeting prep (automatically detected and processed)
mkdir workspace/meeting-prep/board-presentation-q1
echo "## Agenda: Platform ROI, Team Growth, Risk Assessment" > workspace/meeting-prep/board-presentation-q1/notes.md

# ClaudeDirector will:
# 1. Detect the new directory
# 2. Analyze the content
# 3. Store strategic intelligence
# 4. Recommend optimal AI personas (probably alvaro + camille)
```

### Query Your Strategic Memory
```bash
# Get meeting intelligence summary
python memory/meeting_intelligence.py --summary

# View all tracked meetings
python memory/meeting_intelligence.py --scan
```

### Use Strategic AI Personas
```bash
# In your Claude conversations, reference specific personas:
# @diego: How should we structure our platform team for Q2?
# @camille: What's the strategic value of this technical investment?
# @rachel: How do we align design system adoption across teams?
# @alvaro: How do we communicate this platform ROI to leadership?
```

## 🏗️ Architecture

ClaudeDirector is built on three pillars:

1. **Strategic AI Foundation**: 12 personas + VP/SLT communication protocols
2. **Meeting Intelligence Engine**: Automated tracking + strategic memory
3. **Persistent Memory System**: SQLite-based organizational intelligence

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
