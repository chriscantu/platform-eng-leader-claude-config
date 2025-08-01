# Company Jira Integration Setup
# Director of Engineering - UI Foundation Platform

## Quick Setup for Procore

### 1. Generate Company Jira API Token

1. **Access Company Jira**: Navigate to https://company.atlassian.net
2. **Account Settings**: Click your profile → Account settings
3. **Security Tab**: Go to Security → API tokens
4. **Create Token**: 
   - Click "Create API token"
   - Name: "Claude Weekly Reports - UI Foundation"
   - Click "Create"
   - **COPY TOKEN IMMEDIATELY** (it won't be shown again)

### 2. Set Environment Variables

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Company Jira Integration for Weekly Reports
export JIRA_BASE_URL="https://company.atlassian.net"
export JIRA_EMAIL="chris.cantu@procore.com"  # Your Procore email
export JIRA_API_TOKEN="your-api-token-here"   # Token from step 1

# Reload your shell
source ~/.zshrc  # or source ~/.bashrc
```

### 3. Verify Jira Access

Test your access manually first:
```bash
curl -u chris.cantu@procore.com:$JIRA_API_TOKEN \
  -X GET \
  -H "Accept: application/json" \
  "https://company.atlassian.net/rest/api/3/myself"
```

Should return your user profile if authentication works.

### 4. Identify UI Foundation Project Keys

You'll need to find the actual Jira project keys for your teams. Common patterns at Procore might be:

**Likely Project Keys** (need verification):
- Web Platform: `WP`, `WEBPLAT`, `PLATFORM`, or `FE` 
- Design System: `DS`, `DESIGN`, `DESIGNSYS`, or `UI`
- Internationalization: `I18N`, `INTL`, or `LOCALE`
- UI Service Shell: `SHELL`, `CORE`, or `FOUNDATION`
- Header/Navigation: `NAV`, `HEADER`, or `CHROME`

**Find Your Project Keys**:
1. Go to https://company.atlassian.net/projects
2. Click on each project your teams use
3. Note the project key in the URL: `/projects/{KEY}/board`

### 5. Update Configuration File

Once you have the actual project keys, update `weekly-report-config.yaml`:

```yaml
teams:
  web_platform:
    name: "Web Platform"
    jira_project: "YOUR_ACTUAL_KEY"  # Replace with real key
    team_lead: "Your Team Lead Name"
    
  design_system:
    name: "Design System"
    jira_project: "YOUR_ACTUAL_KEY"  # Replace with real key
    team_lead: "Your Team Lead Name"
    
  # ... update all teams
```

### 6. Test Configuration

```bash
/generate-weekly-report --dry-run
```

This should now pass the authentication and show available projects.

## Procore-Specific Configuration

### Custom Fields Discovery

Procore likely has custom fields for business value tracking. To find them:

1. **Manual Discovery**: 
   - Go to any epic in Jira
   - View the "Configure Fields" or check epic details
   - Look for fields like "Business Value", "ROI", "Impact", etc.

2. **API Discovery**:
   ```bash
   curl -u chris.cantu@procore.com:$JIRA_API_TOKEN \
     -X GET \
     "https://company.atlassian.net/rest/api/3/field" | jq '.[] | select(.name | contains("value") or contains("impact") or contains("roi"))'
   ```

### Common Procore Field Mappings

Update in `weekly-report-config.yaml`:

```yaml
epics:
  # Update these with actual Procore custom field IDs
  business_value_field: "customfield_XXXXX"
  sprint_field: "customfield_XXXXX" 
  epic_link_field: "customfield_XXXXX"

report:
  metrics:
    platform_adoption: "customfield_XXXXX"
    developer_satisfaction: "customfield_XXXXX"
    support_tickets: "customfield_XXXXX"
```

### Sprint Board Configuration

If teams use different boards, find board IDs:

1. Go to team's board in Jira
2. Note board ID in URL: `/boards/{BOARD_ID}`
3. Add to config:

```yaml
teams:
  web_platform:
    name: "Web Platform"
    jira_project: "WEBPLAT"
    board_id: 123  # Add if using specific board
```

## Troubleshooting Procore Setup

### Authentication Issues

**Problem**: "401 Unauthorized"
- **Check**: Email matches your Procore login
- **Check**: API token is correct and not expired
- **Solution**: Regenerate API token if needed

### Project Access Issues

**Problem**: "403 Forbidden" or "Project not found"
- **Check**: You have browse permissions for the projects
- **Check**: Project keys are correct (case-sensitive)
- **Solution**: Verify permissions with Jira admin

### Sprint Detection Issues

**Problem**: "No active sprint found"
- **Check**: Teams are using Scrum boards (not Kanban)
- **Check**: Active sprints exist for your projects
- **Solution**: Specify sprint manually with `--sprint` flag

### Custom Field Issues

**Problem**: "Field not found" errors
- **Check**: Custom field IDs exist in your Jira instance
- **Solution**: Use field discovery API or set fallback to "description"

## Production Workflow

Once configured:

1. **Weekly Automation**: Add to calendar to run every Friday
2. **Command**: `/generate-weekly-report --format markdown`
3. **Review**: Quick review before sending to SLT
4. **Distribution**: Copy markdown to email/Slack/document system

## Next Steps

1. **Complete environment variables setup**
2. **Identify actual Procore project keys**
3. **Update configuration file with real values** 
4. **Test with `/generate-weekly-report --dry-run`**
5. **Generate first production report**
6. **Iterate on business value frameworks based on results**

## Support

For Procore-specific Jira questions:
- **Jira Admin**: Contact your Jira administrator for custom field IDs
- **Project Access**: Check with project leads for correct project keys
- **Permissions**: Verify with IT for Jira API access permissions