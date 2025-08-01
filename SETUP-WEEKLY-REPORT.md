# Weekly Report Setup Guide
# `/generate-weekly-report` Command Configuration

## Quick Start

### 1. Set Environment Variables
```bash
# Add to your ~/.bashrc or ~/.zshrc
export JIRA_API_TOKEN="your-jira-api-token"
export JIRA_EMAIL="your.email@company.com"  
export JIRA_BASE_URL="https://your-company.atlassian.net"
```

### 2. Get Jira API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Create token named "Claude Weekly Reports"
3. Copy token to environment variable above

### 3. Update Configuration
Edit `weekly-report-config.yaml`:

```yaml
teams:
  # Update with your actual team structure
  web_platform:
    name: "Web Platform"
    jira_project: "YOUR_PROJECT_KEY"  # ← Change this
    team_lead: "Your Team Lead"       # ← Change this
    
  design_system:
    name: "Design System" 
    jira_project: "YOUR_PROJECT_KEY"  # ← Change this
    team_lead: "Your Team Lead"       # ← Change this
```

### 4. Test Configuration
```bash
/generate-weekly-report --dry-run
```

## Usage Examples

**Basic Weekly Report (All Teams)**
```bash
/generate-weekly-report
```

**Specific Teams Only**
```bash
/generate-weekly-report --teams web_platform,design_system
```

**VP Engineering Format**
```bash
/generate-weekly-report --stakeholder vp_engineering --format email
```

**Historical Report**
```bash
/generate-weekly-report --sprint "2024-W30" --format pdf
```

## Customization

### Team Configuration
For each team under your reporting structure, configure:

```yaml
your_team_name:
  name: "Display Name"
  jira_project: "PROJECT_KEY"      # Jira project abbreviation
  team_lead: "Lead Name"
  focus_areas: ["Area1", "Area2"]  # What this team works on
  business_impact_category: "Primary Business Value"
```

### Business Value Frameworks
Customize how technical work translates to business impact:

```yaml
business_value_frameworks:
  your_domain:
    keywords: ["technical", "terms"]
    translation: "Business impact statement"
    impact_metrics: ["metric1", "metric2"]
```

### Custom Fields
If you have custom Jira fields for business value:

```yaml
epics:
  business_value_field: "customfield_XXXXX"  # Your custom field ID
  priority_mapping:
    "Critical": "Critical Path Delivery"
    "High": "Strategic Priority"
```

## Common Issues & Solutions

### Authentication Errors
- **Error**: "401 Unauthorized"
- **Solution**: Verify API token and email are correct
- **Check**: Token has permissions to view your projects

### Missing Epic Data
- **Error**: "No epics found"
- **Solution**: Verify project keys are correct in config
- **Check**: Epics exist in current active sprint

### Custom Field Issues
- **Error**: "Field not found"
- **Solution**: Update field IDs in config to match your Jira instance
- **Check**: Fields exist and are accessible to your account

### Sprint Detection Problems
- **Error**: "No active sprint"
- **Solution**: Either specify sprint manually or check sprint configuration
- **Check**: Active sprints exist for your projects

## Advanced Configuration

### Multiple Sprint Boards
If teams use different boards:

```yaml
teams:
  web_platform:
    name: "Web Platform"
    jira_project: "WEBPLAT"
    board_id: 123  # Specific board ID
```

### Custom JQL Filters
For complex epic filtering:

```yaml
teams:
  design_system:
    name: "Design System"
    jira_project: "DESIGN"
    custom_jql: 'project = DESIGN AND issuetype = Epic AND labels = "ui-foundation"'
```

### VP-Specific Templates
Customize output for different stakeholders:

```yaml
executive:
  stakeholders:
    vp_engineering:
      focus: ["team velocity", "technical debt", "platform adoption"]
      template: "vp-engineering-template.md"
      metrics: ["development velocity", "incident rate"]
```

## Security Notes

- **Never commit API tokens** to version control
- **Use environment variables** for all credentials  
- **Limit Jira permissions** to minimum required (browse projects, view issues)
- **Rotate API tokens** regularly (quarterly recommended)

## Support

If you encounter issues:

1. **Test with dry-run**: `/generate-weekly-report --dry-run`
2. **Check logs**: Look for specific error messages
3. **Validate config**: Ensure YAML syntax is correct
4. **Test Jira access**: Try accessing projects manually in Jira

## Next Steps

Once configured:

1. **Automate weekly**: Set up calendar reminder to run command
2. **Template customization**: Modify report template for your organization
3. **Integration**: Connect to email/Slack for automated distribution
4. **Metrics tracking**: Monitor report effectiveness and iterate