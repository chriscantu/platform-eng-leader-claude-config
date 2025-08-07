# {{ report.get_title() }}

**Generated**: {{ metadata.generation_date | format_date }}
**Reporting Period**: {{ metadata.report_period_start | format_date('%B %Y') }}
**Total Initiatives Analyzed**: {{ metadata.total_initiatives }}

---

## 📈 Executive Summary

{{ report.executive_summary }}

### PI Initiative Overview

| Category | Count | Percentage |
|----------|-------|------------|
| **Total PI Initiatives** | {{ data.total_pi_initiatives }} | 100% |
| **L1 Initiatives** | {{ data.l1_initiatives }} | {{ (data.l1_initiatives / data.total_pi_initiatives * 100) | round(1) if data.total_pi_initiatives > 0 else 0 }}% |
| **L2 Strategic Initiatives** | {{ data.l2_initiatives }} | {{ (data.l2_initiatives / data.total_pi_initiatives * 100) | round(1) if data.total_pi_initiatives > 0 else 0 }}% |

### Status Distribution
{% for status, count in data.initiatives_by_status.items() %}
- **{{ status }}**: {{ count }} initiatives ({{ (count / data.total_pi_initiatives * 100) | round(1) if data.total_pi_initiatives > 0 else 0 }}%)
{% endfor %}

### Health Assessment
{% for health, count in data.health_distribution.items() %}
- {{ health | health_emoji }} **{{ health.value | title }}**: {{ count }} initiatives ({{ (count / data.total_pi_initiatives * 100) | round(1) if data.total_pi_initiatives > 0 else 0 }}%)
{% endfor %}

---

## 🎯 Strategic Analysis

{% if data.strategic_themes %}
### Key Strategic Themes

{% for theme in data.strategic_themes %}
#### {{ theme.name }} {{ theme.health | health_emoji }}

| Metric | Value |
|--------|-------|
| **Initiatives** | {{ theme.initiative_count }} |
| **Progress** | {{ theme.progress | percentage }} |
| **Health** | {{ theme.health | health_emoji }} {{ theme.health.value | title }} |
| **Key Outcomes** | {{ theme.outcomes }} |

{% endfor %}
{% else %}
### Strategic Themes

*No strategic themes identified for this reporting period*
{% endif %}

---

## 📊 Resource Allocation Analysis

{% if data.resource_allocation %}
### Division Distribution
{% for division, count in data.resource_allocation.division_distribution.items() %}
- **{{ division }}**: {{ count }} initiatives ({{ (count / data.total_pi_initiatives * 100) | round(1) if data.total_pi_initiatives > 0 else 0 }}%)
{% endfor %}

### Priority Analysis
- **High Priority Initiatives**: {{ data.resource_allocation.high_priority_count }}
- **Cross-Division Initiatives**: {{ data.resource_allocation.cross_division_count }}
- **Priority Density**: {{ (data.resource_allocation.high_priority_count / data.total_pi_initiatives * 100) | round(1) if data.total_pi_initiatives > 0 else 0 }}%

{% endif %}

---

## 🔍 Risk Assessment

{% if data.risk_assessment %}
### Executive Risk Summary

{{ data.risk_assessment.summary }}

**Total At-Risk Initiatives**: {{ data.risk_assessment.total_at_risk }}

{% if data.risk_assessment.top_risks %}
### Top Strategic Risks

{% for risk in data.risk_assessment.top_risks %}
#### {{ risk.key | jira_link }}: {{ risk.title | truncate_smart(60) }} {{ risk.health | health_emoji }}

- **Health Status**: {{ risk.health | health_emoji }} {{ risk.health.value | title }}
- **Risk Factors**: {{ risk.risk_factors | join(', ') }}
- **Mitigation Strategy**: {{ risk.mitigation }}

{% endfor %}
{% else %}
### Strategic Risks

*No significant risks identified for this reporting period* {{ health_emoji('green') }}
{% endif %}

{% else %}
### Risk Assessment

*Risk assessment data not available*
{% endif %}

---

## 📋 Detailed Initiative Breakdown

{% if data.initiative_details %}
{% for initiative in data.initiative_details %}
### {{ initiative.key | jira_link }}: {{ initiative.summary | truncate_smart(80) }}

| Field | Value |
|-------|-------|
| **Status** | {{ initiative.status }} |
| **Priority** | {{ initiative.priority | priority_emoji }} {{ initiative.priority }} |
| **Health** | {{ initiative.health | health_emoji }} {{ initiative.health.value | title }} |
| **Division** | {{ initiative.division or "Unknown" }} |
| **Last Updated** | {{ initiative.updated | days_ago if initiative.updated else "Unknown" }} |

{% if initiative.blockers %}
**Blockers**: {{ initiative.blockers | join(', ') }}
{% endif %}

{% endfor %}
{% else %}
### Initiative Details

*No initiative details available for this reporting period*
{% endif %}

---

{% if report.recommendations %}
## 🎯 Strategic Recommendations

{% for recommendation in report.recommendations %}
{{ loop.index }}. {{ recommendation }}
{% endfor %}

---
{% endif %}

## 📊 Metrics Dashboard

### Initiative Health Trends
{% set total = data.total_pi_initiatives %}
{% set green_count = data.health_distribution.get('green', 0) %}
{% set yellow_count = data.health_distribution.get('yellow', 0) %}
{% set red_count = data.health_distribution.get('red', 0) %}

- **Healthy Initiatives**: {{ (green_count / total * 100) | round(1) if total > 0 else 0 }}%
- **Initiatives Needing Attention**: {{ (yellow_count / total * 100) | round(1) if total > 0 else 0 }}%
- **Critical Risk Initiatives**: {{ (red_count / total * 100) | round(1) if total > 0 else 0 }}%

### Strategic Impact
{% if data.strategic_themes %}
{% set completed_themes = data.strategic_themes | selectattr('progress', '>', 0.5) | list %}
- **Themes with Strong Progress**: {{ completed_themes | length }} / {{ data.strategic_themes | length }}
- **Overall Theme Health**: {{ (data.strategic_themes | selectattr('health.value', 'equalto', 'green') | list | length / data.strategic_themes | length * 100) | round(1) if data.strategic_themes else 0 }}% Green
{% endif %}

### Executive KPIs
- **L2 Strategic Initiative Ratio**: {{ (data.l2_initiatives / data.total_pi_initiatives * 100) | round(1) if data.total_pi_initiatives > 0 else 0 }}%
- **Completion Rate**: {{ (data.initiatives_by_status.get('Done', 0) + data.initiatives_by_status.get('Completed', 0) + data.initiatives_by_status.get('Closed', 0)) / data.total_pi_initiatives * 100 | round(1) if data.total_pi_initiatives > 0 else 0 }}%
- **Risk Exposure**: {{ (data.risk_assessment.total_at_risk / data.total_pi_initiatives * 100) | round(1) if data.total_pi_initiatives > 0 and data.risk_assessment else 0 }}%

---

## 🔍 Data Sources & Methodology

- **{{ metadata.data_sources | join('**<br>- **') }}**
- **Report Generation**: {{ metadata.generation_date | format_datetime }}
- **Analysis Period**: {{ metadata.report_period_start | format_date('%B %d') }} - {{ metadata.report_period_end | format_date('%B %d, %Y') }}
- **Health Assessment**: Multi-factor analysis including status, priority, staleness, and blockers
- **Strategic Themes**: Automated categorization based on initiative content and division
- **Risk Scoring**: Priority-weighted assessment with mitigation strategy recommendations

---

*This report was generated automatically by the Strategic Integration Service. For detailed analysis or follow-up questions, contact the Platform Engineering team.*

**Next Monthly Report**: {{ (metadata.report_period_end.replace(day=1) + timedelta(days=32)).replace(day=1) | format_date('%B %Y') }}
