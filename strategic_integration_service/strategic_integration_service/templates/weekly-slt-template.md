# {{ report.get_title() }}

**Generated**: {{ metadata.generation_date | format_date }}
**Reporting Period**: {{ metadata.report_period_start | format_date }} to {{ metadata.report_period_end | format_date }}
**Teams**: {{ metadata.teams_included | join(', ') }}

---

## 📊 Executive Summary

{{ report.executive_summary }}

### Key Metrics
- **Total Active Initiatives**: {{ data.total_active_initiatives }}
- **Completed This Week**: {{ data.completed_this_week }} {{ health_emoji('green') if data.completed_this_week > 0 else health_emoji('yellow') }}
- **At Risk**: {{ data.at_risk_count }} {{ health_emoji('red') if data.at_risk_count > 0 else health_emoji('green') }}
- **High Priority**: {{ data.high_priority_count }} {{ priority_emoji('high') }}

### Platform Health Overview

{% for area, status in data.platform_health.items() %}
- **{{ area }}**: {{ status | health_emoji }} {{ status.value | title }}
{% endfor %}

---

## 🎯 Strategic Highlights

{% if data.major_completions %}
### 🎉 Major Completions

{% for completion in data.major_completions %}
- **{{ completion.title | jira_link(completion.key) }}** ({{ completion.team }})
  - **Impact**: {{ completion.impact }}
  - **Priority**: {{ completion.priority | priority_emoji }} {{ completion.priority }}
{% endfor %}
{% else %}
### 🎉 Major Completions

*No major completions to highlight this week*
{% endif %}

{% if data.escalations %}
### 🚨 Escalations Required

{% for escalation in data.escalations %}
- **{{ escalation.title | jira_link(escalation.key) }}** {{ health_emoji('red') }}
  - **Team**: {{ escalation.team }}
  - **Issue**: {{ escalation.issue }}
  - **Recommendation**: {{ escalation.recommendation }}
{% endfor %}
{% else %}
### 🚨 Escalations Required

*No escalations required this week* {{ health_emoji('green') }}
{% endif %}

---

## 👥 Team Performance

{% for team_name, team_data in data.team_summaries.items() %}
### {{ team_name }}

| Metric | Value | Status |
|--------|-------|--------|
| Active Initiatives | {{ team_data.active_count }} | {{ health_emoji('green') if team_data.active_count < 10 else health_emoji('yellow') }} |
| Completed This Week | {{ team_data.completed_count }} | {{ health_emoji('green') if team_data.completed_count > 0 else health_emoji('gray') }} |
| Team Health | {{ team_data.health.value | title }} | {{ team_data.health | health_emoji }} |

{% if team_data.highlights %}
**Key Highlights**:
{% for highlight in team_data.highlights %}
- {{ highlight }}
{% endfor %}
{% endif %}

{% endfor %}

---

## 🔮 Looking Ahead

{% if data.upcoming_milestones %}
### 📅 Upcoming Milestones

{% for milestone in data.upcoming_milestones %}
- **{{ milestone.title }}** ({{ milestone.date | format_date }})
  - **Team**: {{ milestone.team }}
  - **Risk Level**: {{ milestone.risk | health_emoji }} {{ milestone.risk.value | title }}
  {% if milestone.initiatives %}
  - **Initiatives**: {{ milestone.initiatives | join(', ') }}
  {% endif %}
{% endfor %}
{% else %}
### 📅 Upcoming Milestones

*No major milestones identified for the next two weeks*
{% endif %}

{% if report.recommendations %}
### 🎯 Strategic Recommendations

{% for recommendation in report.recommendations %}
{{ loop.index }}. {{ recommendation }}
{% endfor %}
{% endif %}

---

## 📈 Metrics Dashboard

### Initiative Distribution
{% set total = data.total_active_initiatives %}
{% for team_name, team_data in data.team_summaries.items() %}
- **{{ team_name }}**: {{ team_data.active_count }} ({{ (team_data.active_count / total * 100) | round(1) }}%)
{% endfor %}

### Health Summary
{% set health_counts = {} %}
{% for team_name, team_data in data.team_summaries.items() %}
  {% set _ = health_counts.update({team_data.health.value: health_counts.get(team_data.health.value, 0) + 1}) %}
{% endfor %}

{% for health, count in health_counts.items() %}
- {{ health | health_emoji }} **{{ health | title }}**: {{ count }} teams
{% endfor %}

### Weekly Velocity
- **Completion Rate**: {{ (data.completed_this_week / data.total_active_initiatives * 100) | round(1) if data.total_active_initiatives > 0 else 0 }}%
- **Risk Percentage**: {{ (data.at_risk_count / data.total_active_initiatives * 100) | round(1) if data.total_active_initiatives > 0 else 0 }}%

---

## 🔍 Data Sources

- **{{ metadata.data_sources | join('**<br>- **') }}**
- **Report Generation**: {{ metadata.generation_date | format_datetime }}
- **Total Data Points**: {{ metadata.total_initiatives }} initiatives analyzed

---

*This report was generated automatically by the Strategic Integration Service. For questions or additional analysis, contact the UI Foundation Platform Engineering team.*

**Next Weekly Report**: {{ (metadata.report_period_end.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=7)) | format_date }}
