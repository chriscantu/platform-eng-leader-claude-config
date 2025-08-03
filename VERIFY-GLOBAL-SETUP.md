# Verify Global Weekly Report Setup

## Quick Test Commands

Test that `/generate-weekly-report` is available from any Claude Code session:

### 1. Test Command Recognition
```bash
# In any directory, open a new Claude Code session and ask:
"Can you show me the /generate-weekly-report command documentation?"
```

### 2. Test Configuration Access  
```bash
# Test that the config files are accessible:
"Read the weekly-report-config.yaml file and tell me what teams are configured"
```

### 3. Test Dry Run
```bash
# Test the actual command functionality:
"/generate-weekly-report --dry-run"
```

## Expected Results

✅ **Command Recognition**: Claude should recognize the command and show its documentation  
✅ **Configuration Access**: Should be able to read weekly-report-config.yaml from ~/.claude/  
✅ **Dry Run Success**: Should validate configuration and show team structure  

## If Tests Fail

### Missing Command Recognition
- Check that COMMANDS.md is synced: `./sync-claude-config.sh check`
- Restart Claude Code session to reload configuration

### Missing Configuration Files
- Run sync script: `./sync-claude-config.sh sync`
- Verify files exist: `ls -la ~/.claude/weekly-report*`

### Environment Variables Missing
- Ensure Jira environment variables are set globally:
  ```fish
  set -Ux JIRA_BASE_URL "https://company.atlassian.net"
  set -Ux JIRA_EMAIL "chris.cantu@procore.com"  
  set -Ux JIRA_API_TOKEN "your-token-here"
  ```

## Global Files Synchronized

The following files are now available globally in `~/.claude/`:

**Core Framework Files:**
- CLAUDE.md, COMMANDS.md, FLAGS.md, PRINCIPLES.md, RULES.md
- MCP.md, PERSONAS.md, ORCHESTRATOR.md, MODES.md

**Weekly Report Files:**
- weekly-report-config.yaml (Procore team configuration)
- weekly-report-template.md (Executive report template)  
- jira-integration-spec.md (Technical integration details)

## Usage from Any Session

Once synchronized, you can use the command from any Claude Code session:

```bash
# Generate current week report
/generate-weekly-report

# Generate for specific teams
/generate-weekly-report --teams web_platform,design_system

# Generate for specific stakeholder
/generate-weekly-report --stakeholder vp_engineering

# Test configuration
/generate-weekly-report --dry-run
```

## Troubleshooting

### New Claude Code Session Not Recognizing Command
1. Wait 30-60 seconds for configuration to load
2. Try asking: "What commands are available?"
3. If still not working, restart Claude Code completely

### Permission Issues
- Ensure ~/.claude/ directory is readable: `chmod 755 ~/.claude`
- Ensure config files are readable: `chmod 644 ~/.claude/weekly-report*`

### Environment Variables Not Available
- Fish shell variables: Use `set -Ux` for universal variables
- Bash/Zsh: Add to ~/.bashrc or ~/.zshrc and source the file
- System-wide: Add to /etc/environment (requires sudo)