"""Template engine for dynamic report generation."""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import structlog
from jinja2 import Environment, FileSystemLoader, Template

from ..models.report import ReportTemplate, TemplateContext, InitiativeHealthStatus

logger = structlog.get_logger(__name__)


class ReportTemplateEngine:
    """Template engine for generating strategic reports."""

    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize the template engine."""
        self.template_dir = template_dir or Path(__file__).parent.parent / "templates"
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

        # Add custom filters and functions
        self._setup_template_helpers()

    def _setup_template_helpers(self):
        """Set up custom Jinja2 filters and functions."""

        # Date formatting filters
        self.env.filters['format_date'] = lambda d, fmt='%B %d, %Y': d.strftime(fmt) if d else 'N/A'
        self.env.filters['format_datetime'] = lambda d, fmt='%Y-%m-%d %H:%M': d.strftime(fmt) if d else 'N/A'
        self.env.filters['days_ago'] = self._days_ago_filter
        self.env.filters['week_range'] = self._week_range_filter

        # Status and priority filters
        self.env.filters['health_emoji'] = self._health_emoji_filter
        self.env.filters['priority_emoji'] = self._priority_emoji_filter
        self.env.filters['status_color'] = self._status_color_filter

        # Data formatting filters
        self.env.filters['percentage'] = lambda x: f"{x:.1%}" if isinstance(x, (int, float)) else "N/A"
        self.env.filters['jira_link'] = self._jira_link_filter
        self.env.filters['truncate_smart'] = self._smart_truncate_filter

        # List and grouping filters
        self.env.filters['group_by'] = self._group_by_filter
        self.env.filters['sort_by'] = self._sort_by_filter
        self.env.filters['count_by'] = self._count_by_filter

        # Custom global functions
        self.env.globals['now'] = datetime.now
        self.env.globals['format_metric'] = self._format_metric
        self.env.globals['calculate_trend'] = self._calculate_trend

    def _days_ago_filter(self, date: datetime) -> str:
        """Calculate days ago from date."""
        if not date:
            return "Unknown"

        now = datetime.now(date.tzinfo) if date.tzinfo else datetime.now()
        days = (now - date).days

        if days == 0:
            return "Today"
        elif days == 1:
            return "Yesterday"
        elif days < 7:
            return f"{days} days ago"
        elif days < 30:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            months = days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"

    def _week_range_filter(self, date: datetime) -> str:
        """Generate week range string from date."""
        if not date:
            return "Unknown"

        # Find Monday of the week
        monday = date - timedelta(days=date.weekday())
        friday = monday + timedelta(days=4)

        if monday.month == friday.month:
            return f"{monday.strftime('%B %d')} - {friday.strftime('%d, %Y')}"
        else:
            return f"{monday.strftime('%B %d')} - {friday.strftime('%B %d, %Y')}"

    def _health_emoji_filter(self, status: Union[str, InitiativeHealthStatus]) -> str:
        """Convert health status to emoji."""
        status_str = status.value if isinstance(status, InitiativeHealthStatus) else str(status).lower()

        emoji_map = {
            'green': '🟢',
            'yellow': '🟡',
            'red': '🔴',
            'unknown': '⚪',
            'good': '🟢',
            'warning': '🟡',
            'critical': '🔴',
            'on_track': '🟢',
            'at_risk': '🟡',
            'blocked': '🔴'
        }

        return emoji_map.get(status_str, '⚪')

    def _priority_emoji_filter(self, priority: str) -> str:
        """Convert priority to emoji."""
        priority_lower = str(priority).lower()

        emoji_map = {
            'highest': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢',
            'lowest': '🔵',
            'critical': '🔴',
            'urgent': '🟠'
        }

        return emoji_map.get(priority_lower, '⚪')

    def _status_color_filter(self, status: str) -> str:
        """Get color for status display."""
        status_lower = str(status).lower()

        color_map = {
            'done': 'green',
            'completed': 'green',
            'closed': 'green',
            'in progress': 'blue',
            'in_progress': 'blue',
            'to do': 'gray',
            'todo': 'gray',
            'blocked': 'red',
            'at risk': 'orange',
            'at_risk': 'orange'
        }

        return color_map.get(status_lower, 'gray')

    def _jira_link_filter(self, key: str, base_url: str = "https://procoretech.atlassian.net") -> str:
        """Generate Jira issue link."""
        if not key:
            return ""
        return f"[{key}]({base_url}/browse/{key})"

    def _smart_truncate_filter(self, text: str, length: int = 100, suffix: str = "...") -> str:
        """Smart truncation that respects word boundaries."""
        if not text or len(text) <= length:
            return text

        # Try to truncate at word boundary
        truncated = text[:length]
        last_space = truncated.rfind(' ')

        if last_space > length * 0.8:  # If we can find a space in the last 20%
            return truncated[:last_space] + suffix
        else:
            return truncated + suffix

    def _group_by_filter(self, items: List[Dict], key: str) -> Dict[str, List[Dict]]:
        """Group items by a key."""
        grouped = {}
        for item in items:
            group_key = str(item.get(key, 'Unknown'))
            if group_key not in grouped:
                grouped[group_key] = []
            grouped[group_key].append(item)
        return grouped

    def _sort_by_filter(self, items: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
        """Sort items by a key."""
        return sorted(items, key=lambda x: x.get(key, ''), reverse=reverse)

    def _count_by_filter(self, items: List[Dict], key: str) -> Dict[str, int]:
        """Count items by a key."""
        counts = {}
        for item in items:
            count_key = str(item.get(key, 'Unknown'))
            counts[count_key] = counts.get(count_key, 0) + 1
        return counts

    def _format_metric(self, value: Any, metric_type: str = 'number') -> str:
        """Format metrics for display."""
        if value is None:
            return "N/A"

        if metric_type == 'percentage':
            return f"{value:.1%}"
        elif metric_type == 'currency':
            return f"${value:,.0f}"
        elif metric_type == 'number':
            if isinstance(value, float):
                return f"{value:,.1f}"
            else:
                return f"{value:,}"
        else:
            return str(value)

    def _calculate_trend(self, current: float, previous: float) -> Dict[str, Any]:
        """Calculate trend between two values."""
        if previous == 0:
            if current > 0:
                return {'direction': 'up', 'percentage': float('inf'), 'symbol': '↗️'}
            else:
                return {'direction': 'flat', 'percentage': 0, 'symbol': '➡️'}

        change = ((current - previous) / previous) * 100

        if change > 5:
            return {'direction': 'up', 'percentage': change, 'symbol': '↗️'}
        elif change < -5:
            return {'direction': 'down', 'percentage': abs(change), 'symbol': '↘️'}
        else:
            return {'direction': 'flat', 'percentage': abs(change), 'symbol': '➡️'}

    def load_template(self, template_name: str) -> Template:
        """Load a template by name."""
        try:
            return self.env.get_template(template_name)
        except Exception as e:
            logger.error("Failed to load template", template_name=template_name, error=str(e))
            raise

    def render_template(self, template_name: str, context: TemplateContext) -> str:
        """Render a template with context data."""
        try:
            template = self.load_template(template_name)

            # Prepare context for template
            template_context = {
                'report': context.report,
                'metadata': context.metadata,
                'data': context.data,
                **context.format_helpers
            }

            rendered = template.render(**template_context)
            logger.info("Template rendered successfully", template_name=template_name)
            return rendered

        except Exception as e:
            logger.error("Template rendering failed", template_name=template_name, error=str(e))
            raise

    def render_from_string(self, template_string: str, context: TemplateContext) -> str:
        """Render a template from string content."""
        try:
            template = self.env.from_string(template_string)

            template_context = {
                'report': context.report,
                'metadata': context.metadata,
                'data': context.data,
                **context.format_helpers
            }

            return template.render(**template_context)

        except Exception as e:
            logger.error("String template rendering failed", error=str(e))
            raise

    def create_default_templates(self):
        """Create default templates for common report types."""
        templates = {
            'weekly_slt_summary.md': self._get_weekly_template(),
            'monthly_pi_summary.md': self._get_monthly_template(),
            'executive_summary.md': self._get_executive_summary_template(),
            'team_breakdown.md': self._get_team_breakdown_template()
        }

        for filename, content in templates.items():
            template_path = self.template_dir / filename
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info("Created default template", template=filename)

    def _get_weekly_template(self) -> str:
        """Get default weekly report template."""
        return '''# {{ report.get_title() }}

**Generated**: {{ metadata.generation_date | format_date }}
**Reporting Period**: {{ metadata.report_period_start | format_date }} to {{ metadata.report_period_end | format_date }}
**Teams**: {{ metadata.teams_included | join(', ') }}

---

## 📊 Executive Summary

- **Total Active Initiatives**: {{ data.total_active_initiatives }}
- **Completed This Week**: {{ data.completed_this_week }}
- **At Risk**: {{ data.at_risk_count }} {{ health_emoji('red') if data.at_risk_count > 0 else health_emoji('green') }}
- **High Priority**: {{ data.high_priority_count }}

### Platform Health Overview

{% for area, status in data.platform_health.items() %}
- **{{ area }}**: {{ status | health_emoji }} {{ status.value | title }}
{% endfor %}

---

## 🎯 Key Highlights

### Major Completions
{% for completion in data.major_completions %}
- **{{ completion.title }}** ({{ completion.team }})
  - {{ completion.description }}
  - Impact: {{ completion.impact }}
{% endfor %}

### Escalations Required
{% for escalation in data.escalations %}
- **{{ escalation.title }}** {{ health_emoji('red') }}
  - Issue: {{ escalation.issue }}
  - Recommendation: {{ escalation.recommendation }}
{% endfor %}

---

## 👥 Team Performance

{% for team_name, team_data in data.team_summaries.items() %}
### {{ team_name }}

- **Active Initiatives**: {{ team_data.active_count }}
- **Completed This Week**: {{ team_data.completed_count }}
- **Health**: {{ team_data.health | health_emoji }} {{ team_data.health }}

{% if team_data.highlights %}
**Highlights**:
{% for highlight in team_data.highlights %}
- {{ highlight }}
{% endfor %}
{% endif %}

{% endfor %}

---

## 🔮 Looking Ahead

### Upcoming Milestones
{% for milestone in data.upcoming_milestones %}
- **{{ milestone.title }}** ({{ milestone.date | format_date }})
  - Team: {{ milestone.team }}
  - Risk Level: {{ milestone.risk | health_emoji }} {{ milestone.risk }}
{% endfor %}

---

*Report generated by Strategic Integration Service*
'''

    def _get_monthly_template(self) -> str:
        """Get default monthly report template."""
        return '''# {{ report.get_title() }}

**Generated**: {{ metadata.generation_date | format_date }}
**Reporting Period**: {{ metadata.report_period_start | format_date('%B %Y') }}
**Total Initiatives Analyzed**: {{ metadata.total_initiatives }}

---

## 📈 PI Initiative Overview

### Summary Metrics
- **Total PI Initiatives**: {{ data.total_pi_initiatives }}
- **L1 Initiatives**: {{ data.l1_initiatives }}
- **L2 Strategic Initiatives**: {{ data.l2_initiatives }}

### Status Distribution
{% for status, count in data.initiatives_by_status.items() %}
- **{{ status }}**: {{ count }} initiatives
{% endfor %}

### Health Assessment
{% for health, count in data.health_distribution.items() %}
- {{ health | health_emoji }} **{{ health.value | title }}**: {{ count }} initiatives
{% endfor %}

---

## 🎯 Strategic Analysis

### Key Themes
{% for theme in data.strategic_themes %}
#### {{ theme.name }}
- **Initiatives**: {{ theme.initiative_count }}
- **Progress**: {{ theme.progress | percentage }}
- **Health**: {{ theme.health | health_emoji }} {{ theme.health }}
- **Key Outcomes**: {{ theme.outcomes }}
{% endfor %}

---

## 📊 Detailed Initiative Breakdown

{% for initiative in data.initiative_details %}
### {{ initiative.key | jira_link }}: {{ initiative.summary | truncate_smart(80) }}

- **Status**: {{ initiative.status }}
- **Priority**: {{ initiative.priority | priority_emoji }} {{ initiative.priority }}
- **Health**: {{ initiative.health | health_emoji }} {{ initiative.health }}
- **Team**: {{ initiative.team }}
- **Last Updated**: {{ initiative.updated | days_ago }}

{% if initiative.blockers %}
**Blockers**: {{ initiative.blockers | join(', ') }}
{% endif %}

{% endfor %}

---

## 🔍 Risk Assessment

{{ data.risk_assessment.summary }}

### Top Risks
{% for risk in data.risk_assessment.top_risks %}
- **{{ risk.title }}** {{ health_emoji('red') }}
  - Impact: {{ risk.impact }}
  - Mitigation: {{ risk.mitigation }}
{% endfor %}

---

*Report generated by Strategic Integration Service*
'''

    def _get_executive_summary_template(self) -> str:
        """Get executive summary template."""
        return '''## Executive Summary

**Period**: {{ metadata.report_period_start | format_date }} to {{ metadata.report_period_end | format_date }}

### Key Metrics
- Total Initiatives: {{ metadata.total_initiatives }}
- Teams Covered: {{ metadata.teams_included | length }}
- Data Sources: {{ metadata.data_sources | join(', ') }}

### Recommendations
{% for recommendation in report.recommendations %}
{{ loop.index }}. {{ recommendation }}
{% endfor %}
'''

    def _get_team_breakdown_template(self) -> str:
        """Get team breakdown template."""
        return '''## Team Performance Breakdown

{% for team_name, team_data in data.team_summaries.items() %}
### {{ team_name }}

| Metric | Value |
|--------|-------|
| Active Initiatives | {{ team_data.active_count }} |
| Completed | {{ team_data.completed_count }} |
| Health | {{ team_data.health | health_emoji }} {{ team_data.health }} |

{% endfor %}
'''
