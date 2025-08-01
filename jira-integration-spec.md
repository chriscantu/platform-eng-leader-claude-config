# Jira Integration Specification
# `/generate-weekly-report` Command

## Integration Architecture

```
Claude Code Command → Jira REST API → Epic Data Extraction → Business Value Translation → Executive Report
```

## Jira API Integration

### Authentication Methods

**Method 1: API Token (Recommended for Jira Cloud)**
```bash
# Set environment variables
export JIRA_API_TOKEN="your-api-token-here"
export JIRA_EMAIL="your.email@company.com"
export JIRA_BASE_URL="https://your-company.atlassian.net"
```

**Method 2: Personal Access Token (Jira Data Center)**
```bash
export JIRA_PAT_TOKEN="your-pat-token-here"
export JIRA_BASE_URL="https://your-jira-datacenter.com"
```

### API Endpoints Used

**1. Sprint Data Collection**
```
GET /rest/api/3/board/{boardId}/sprint?state=active
GET /rest/api/3/sprint/{sprintId}/issue
```

**2. Epic Data Extraction**
```
GET /rest/api/3/search?jql=project IN (WEBPLAT,DSGNSYS,I18N,UISHELL,NAVHEAD) AND issuetype = Epic AND sprint = {sprintId}
GET /rest/api/3/issue/{epicKey}?expand=changelog,transitions
```

**3. Issue Hierarchy**
```
GET /rest/api/3/search?jql="Epic Link" = {epicKey}
```

### JQL Queries Generated

**Current Sprint Epics (All Teams)**
```sql
project IN (WEBPLAT, DSGNSYS, I18N, UISHELL, NAVHEAD) 
AND issuetype = Epic 
AND sprint IN openSprints() 
AND status IN ("In Progress", "In Review", "Ready for Release", "Done")
ORDER BY priority DESC, updated DESC
```

**Epic Completion Analysis**
```sql
"Epic Link" = {epicKey} 
AND status IN ("To Do", "In Progress", "Done") 
AND sprint IN openSprints()
```

## Command Implementation

### Usage Examples

**Basic Usage**
```bash
/generate-weekly-report
# Uses default config, auto-detects current sprint, all teams
```

**Specific Configuration**
```bash
/generate-weekly-report --config weekly-report-config.yaml --format markdown
```

**Team-Specific Report**
```bash
/generate-weekly-report --teams design_system,web_platform --format email
```

**Historical Report**
```bash
/generate-weekly-report --sprint "2024-W30" --format pdf
```

**VP-Specific Format**
```bash
/generate-weekly-report --stakeholder vp_engineering --format email
```

### Command Processing Flow

1. **Configuration Loading**
   - Load `weekly-report-config.yaml`
   - Validate Jira credentials
   - Parse team mappings and project keys

2. **Sprint Detection**
   - Auto-detect current active sprint OR use specified sprint
   - Validate sprint exists and is accessible

3. **Multi-Team Data Collection**
   ```python
   for team in config.teams:
       epics = jira_client.get_epics(
           project=team.jira_project,
           sprint=current_sprint
       )
       team_data[team.name] = analyze_epic_completion(epics)
   ```

4. **Epic Analysis Per Team**
   - Extract epic metadata (summary, description, status, assignee)
   - Calculate completion probability based on story points and remaining work
   - Identify blockers and dependencies
   - Extract business value from custom fields or description

5. **Business Value Translation**
   - Apply team-specific business impact frameworks
   - Map technical work to organizational outcomes
   - Calculate ROI and competitive advantage metrics

6. **Executive Report Generation**
   - Aggregate cross-team insights
   - Apply VP/SLT communication protocols
   - Generate risk assessment and resource implications
   - Format according to stakeholder preferences

## Data Extraction Logic

### Epic Completion Forecasting

```python
def calculate_completion_probability(epic):
    # Factors considered:
    total_story_points = sum(story.story_points for story in epic.stories)
    completed_story_points = sum(story.story_points for story in epic.stories if story.status == "Done")
    remaining_days = (sprint.end_date - today).days
    team_velocity = calculate_team_velocity(epic.team, last_3_sprints)
    
    # Risk factors:
    blocker_count = count_blockers(epic)
    dependency_count = count_external_dependencies(epic)
    
    # Confidence calculation:
    progress_ratio = completed_story_points / total_story_points
    velocity_feasibility = (total_story_points - completed_story_points) <= (team_velocity * remaining_days / 10)
    risk_adjustment = max(0.1, 1.0 - (blocker_count * 0.2) - (dependency_count * 0.1))
    
    confidence = progress_ratio * 0.4 + velocity_feasibility * 0.4 + risk_adjustment * 0.2
    
    return {
        "probability": confidence,
        "level": "High" if confidence > 0.8 else "Medium" if confidence > 0.5 else "Low",
        "rationale": generate_rationale(progress_ratio, velocity_feasibility, blocker_count)
    }
```

### Business Value Extraction

```python
def extract_business_value(epic, team_config):
    # Priority sources:
    1. Custom business value field (customfield_10030)
    2. Epic description parsing
    3. Team-specific business impact framework
    4. Standard template based on epic type
    
    business_value = extract_from_custom_field(epic) or \
                    parse_from_description(epic) or \
                    apply_team_framework(epic, team_config) or \
                    generate_default_value(epic)
    
    # Apply business impact translation
    return translate_to_business_impact(business_value, team_config.business_impact_category)
```

## Error Handling & Fallbacks

### Authentication Failures
- Validate credentials on startup
- Provide clear error messages for invalid tokens
- Fallback to cached data if available

### API Rate Limiting
- Implement exponential backoff
- Batch API calls efficiently
- Cache responses for repeated requests

### Missing Data Handling
- Graceful degradation when custom fields are missing
- Fallback to description parsing for business value
- Default estimates when story points are missing

### Network Issues
- Retry failed requests with exponential backoff
- Cache previous report data for comparison
- Generate partial reports when some teams are inaccessible

## Security Considerations

### Credential Management
- Store API tokens in environment variables only
- Never log or cache authentication credentials
- Use least-privilege Jira permissions

### Data Handling
- Don't store sensitive epic content locally
- Sanitize data before generating reports
- Respect Jira project permissions

## Setup Instructions

### 1. Jira API Token Setup
1. Go to Jira → Account Settings → Security → API Tokens
2. Create new token with name "Claude Weekly Reports"
3. Copy token and set environment variable

### 2. Jira Permissions Required
- Browse Projects (for all UI Foundation projects)
- View Issues (for epics and stories)
- View Development Tools (for sprint data)

### 3. Custom Field Configuration
Ensure these custom fields exist in your Jira instance:
- Business Value (customfield_10030)
- Platform Adoption Metrics (customfield_10040)
- Developer Satisfaction (customfield_10041)
- Support Ticket References (customfield_10042)

### 4. Configuration File Setup
1. Copy `weekly-report-config.yaml` to your preferred location
2. Update team mappings and Jira project keys
3. Configure business value frameworks for your organization
4. Set environment variables for Jira authentication

### 5. Test Command
```bash
/generate-weekly-report --dry-run --config weekly-report-config.yaml
```

This will validate configuration and API connectivity without generating a full report.