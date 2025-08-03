# Weekly Report Automation Setup
# Monday 12:00 CST Automated Generation

## Quick Setup

### 1. Install the Cron Job

```bash
# Open crontab editor
crontab -e

# Add this line for Monday 12:00 CST (18:00 UTC during standard time, 17:00 UTC during daylight time)
# During CST (Standard Time - November to March)
0 18 * * 1 /Users/chris.cantu/repos/Leadership/weekly-report-automation.sh

# During CDT (Daylight Time - March to November) 
# 0 17 * * 1 /Users/chris.cantu/repos/Leadership/weekly-report-automation.sh

# Save and exit the editor
```

### 2. Set Up Environment Variables for Cron

Since cron runs with minimal environment, create a wrapper script:

```bash
# Create environment wrapper
cat > /Users/chris.cantu/repos/Leadership/cron-wrapper.sh << 'EOF'
#!/bin/bash

# Load environment variables for cron
source /Users/chris.cantu/.config/fish/config.fish 2>/dev/null || true

# Set Fish shell environment variables for cron
export JIRA_BASE_URL="https://company.atlassian.net"
export JIRA_EMAIL="chris.cantu@procore.com"
export JIRA_API_TOKEN="$JIRA_API_TOKEN"  # This should be set in your fish config

# Run the actual automation script
/Users/chris.cantu/repos/Leadership/weekly-report-automation.sh
EOF

chmod +x /Users/chris.cantu/repos/Leadership/cron-wrapper.sh
```

### 3. Update Crontab with Wrapper

```bash
crontab -e

# Replace the previous line with:
0 18 * * 1 /Users/chris.cantu/repos/Leadership/cron-wrapper.sh
```

## Alternative: Launchd (macOS Preferred)

For macOS, launchd is preferred over cron:

### 1. Create Launch Agent

```bash
# Create launch agent directory
mkdir -p ~/Library/LaunchAgents

# Create the plist file
cat > ~/Library/LaunchAgents/com.procore.weekly-report.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.procore.weekly-report</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/chris.cantu/repos/Leadership/cron-wrapper.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>1</integer>
        <key>Hour</key>
        <integer>12</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/chris.cantu/repos/Leadership/logs/launchd.out</string>
    <key>StandardErrorPath</key>
    <string>/Users/chris.cantu/repos/Leadership/logs/launchd.err</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>JIRA_BASE_URL</key>
        <string>https://company.atlassian.net</string>
        <key>JIRA_EMAIL</key>
        <string>chris.cantu@procore.com</string>
    </dict>
</dict>
</plist>
EOF
```

### 2. Load the Launch Agent

```bash
# Load the launch agent
launchctl load ~/Library/LaunchAgents/com.procore.weekly-report.plist

# Enable it to start automatically
launchctl enable gui/$(id -u)/com.procore.weekly-report
```

### 3. Test the Launch Agent

```bash
# Test run manually
launchctl start com.procore.weekly-report

# Check status
launchctl list | grep weekly-report

# View logs
tail -f ~/repos/Leadership/logs/launchd.out
```

## Configuration Options

### Customize Report Generation

Edit `weekly-report-automation.sh` to customize:

```bash
# Change report format
claude-code "/generate-weekly-report --format pdf"

# Generate for specific teams only
claude-code "/generate-weekly-report --teams web_platform,design_system"

# Generate for specific stakeholder
claude-code "/generate-weekly-report --stakeholder vp_engineering"
```

### Add Notifications

Uncomment and configure the notification functions in the script:

**Email Notification:**
```bash
# Install mail command if needed
brew install mailutils

# Configure in notify_completion function
echo "Subject: Weekly SLT Report - $(date)" | mail -s "Weekly Report Ready" your-supervisor@procore.com < "$report_file"
```

**Slack Notification:**
```bash
# Add Slack webhook URL to notify_completion function
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Weekly SLT Report generated for '"$REPORT_DATE"'"}' \
  YOUR_SLACK_WEBHOOK_URL
```

## Troubleshooting

### Check Cron Logs
```bash
# View system cron logs
tail -f /var/log/cron

# View script logs
tail -f ~/repos/Leadership/logs/weekly-report-*.log
```

### Test Manual Execution
```bash
# Test the automation script manually
~/repos/Leadership/weekly-report-automation.sh

# Test the cron wrapper
~/repos/Leadership/cron-wrapper.sh
```

### Verify Environment Variables
```bash
# Check if variables are set in cron environment
env | grep JIRA

# Test from cron-like environment
env -i bash -c 'source cron-wrapper.sh && env | grep JIRA'
```

### Common Issues

1. **Environment Variables Not Set**: Ensure JIRA variables are properly exported in cron-wrapper.sh
2. **Path Issues**: Use absolute paths in all scripts
3. **Permissions**: Ensure all scripts are executable (`chmod +x`)
4. **Claude Code Not Found**: Verify Claude Code CLI is in PATH or use absolute path

## Monitoring

### View Generated Reports
```bash
# List recent reports
ls -la ~/repos/Leadership/weekly-report-*.md

# View latest report
cat $(ls -t ~/repos/Leadership/weekly-report-*.md | head -n1)
```

### Check Automation Logs
```bash
# View automation logs
ls -la ~/repos/Leadership/logs/

# Tail latest log
tail -f $(ls -t ~/repos/Leadership/logs/weekly-report-*.log | head -n1)
```

## Schedule Summary

**When**: Every Monday at 12:00 PM CST  
**What**: Generates weekly SLT report with live Company Jira data  
**Where**: Saves to project directory with timestamp  
**Logs**: Detailed execution logs for troubleshooting  
**Notifications**: Optional email/Slack integration available