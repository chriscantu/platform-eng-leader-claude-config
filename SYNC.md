# Claude Configuration Sync

Automated synchronization system for keeping your global Claude configuration aligned with this Director of Engineering configuration repository.

## Overview

This sync system ensures your global Claude configuration (`~/.claude/`) stays synchronized with your project-specific Director of Engineering configuration. Changes made to core framework files in this repository automatically propagate to your global Claude configuration.

## Core Files Synchronized

The following SuperClaude framework files are kept in sync:

- **CLAUDE.md** - Main entry point and UI Foundation context
- **COMMANDS.md** - Strategic command execution framework
- **FLAGS.md** - Director-level flag system and auto-activation
- **PRINCIPLES.md** - Strategic leadership principles and decision frameworks
- **RULES.md** - Director of Engineering operational rules
- **MCP.md** - MCP server integration for strategic workflows
- **PERSONAS.md** - Strategic leadership persona system
- **ORCHESTRATOR.md** - Strategic routing and decision intelligence
- **MODES.md** - Operational modes for strategic effectiveness

## Sync Methods

### 1. Automatic Sync (Recommended)

**Git Hook Integration**: Automatically syncs after every commit that modifies core framework files.

The post-commit hook (`/.git/hooks/post-commit`) automatically detects when strategic configuration files are modified and syncs them to your global Claude configuration.

**No action required** - sync happens automatically when you commit changes.

### 2. Manual Sync

**Sync Script**: `./sync-claude-config.sh`

```bash
# Sync all files from project to global config
./sync-claude-config.sh sync

# Check sync status without making changes  
./sync-claude-config.sh check

# Show help and available commands
./sync-claude-config.sh help
```

## Sync Process

1. **Detection**: Identifies files that differ between project and global config
2. **Backup**: Creates timestamped backups of existing global files before overwriting
3. **Copy**: Copies project files to global Claude configuration directory
4. **Validation**: Verifies all files are properly synchronized
5. **Reporting**: Provides detailed sync status and results

## Safety Features

- **Automatic Backups**: Existing global config files are backed up before sync
- **Validation**: Comprehensive validation ensures sync integrity
- **Error Handling**: Graceful error handling with detailed error messages
- **Status Checking**: Non-destructive status checking before sync

## Backup Management

Backups are automatically created in your global Claude directory with format:
```
~/.claude/FILENAME.backup.YYYYMMDD_HHMMSS
```

Example: `RULES.md.backup.20250801_143021`

## Usage Examples

### Check if sync is needed:
```bash
./sync-claude-config.sh check
```

### Force sync all files:
```bash
./sync-claude-config.sh sync
```

### View sync help:
```bash
./sync-claude-config.sh help
```

## Integration with Development Workflow

1. **Make changes** to any core framework file in this repository
2. **Test changes** in your local Claude Code sessions
3. **Commit changes** using `git commit` (automatic sync triggers)
4. **Push changes** to share with team: `git push`

The sync system ensures your global Claude configuration stays current with your Director of Engineering strategic framework while maintaining safety through backups and validation.

## Troubleshooting

**Sync fails**: Check file permissions and ensure both directories are accessible
**Validation errors**: Run `./sync-claude-config.sh check` to identify specific issues
**Backup issues**: Verify write permissions in `~/.claude/` directory

## Manual Recovery

If you need to restore from backup:
```bash
# List available backups
ls ~/.claude/*.backup.*

# Restore specific file (example)
cp ~/.claude/RULES.md.backup.20250801_143021 ~/.claude/RULES.md
```