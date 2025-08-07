"""Markdown generation utilities for reports."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from ..models.initiative import Initiative, L2Initiative


class MarkdownGenerator:
    """Utility class for generating markdown content."""

    def __init__(self, jira_base_url: str) -> None:
        self.jira_base_url = jira_base_url.rstrip("/")

    def create_issue_link(self, issue_key: str, title: Optional[str] = None) -> str:
        """Create markdown link to Jira issue.

        Args:
            issue_key: Jira issue key
            title: Optional link title (defaults to issue key)

        Returns:
            Markdown link string
        """
        if not title:
            title = issue_key

        url = f"{self.jira_base_url}/browse/{quote(issue_key)}"
        return f"[{title}]({url})"

    def format_initiative_summary(self, initiative: Initiative) -> str:
        """Format initiative as summary line.

        Args:
            initiative: Initiative to format

        Returns:
            Formatted markdown line
        """
        link = self.create_issue_link(initiative.key, f"{initiative.key}: {initiative.summary}")
        status = initiative.status.value
        priority = initiative.priority.value if initiative.priority else "No Priority"
        assignee = initiative.assignee.display_name if initiative.assignee else "Unassigned"

        return f"- {link} - {status} - {priority} - {assignee}"

    def format_l2_initiative_detailed(self, initiative: L2Initiative) -> str:
        """Format L2 initiative with detailed information.

        Args:
            initiative: L2Initiative to format

        Returns:
            Formatted markdown section
        """
        link = self.create_issue_link(initiative.key, initiative.summary)

        content = f"""
### {link}
**Status**: {initiative.status.value}
**Priority**: {initiative.priority.value if initiative.priority else "No Priority"}
**Assignee**: {initiative.assignee.display_name if initiative.assignee else "Unassigned"}
**Updated**: {initiative.updated.strftime("%Y-%m-%d")}
"""

        if initiative.strategic_priority_rank:
            content += f"**Strategic Priority Rank**: {initiative.strategic_priority_rank}  \n"

        if initiative.division:
            content += f"**Division**: {initiative.division}  \n"

        description = initiative.description or "No description available"
        content += f"\n**Description**: {description}\n"

        return content

    def create_status_summary_table(self, initiatives: List[Initiative]) -> str:
        """Create status summary table.

        Args:
            initiatives: List of initiatives

        Returns:
            Markdown table with status summary
        """
        status_counts = {}
        for initiative in initiatives:
            status = initiative.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        if not status_counts:
            return "*No initiatives found*"

        table = "| Status | Count |\n|--------|-------|\n"
        for status, count in sorted(status_counts.items()):
            table += f"| {status} | {count} |\n"

        return table

    def create_priority_summary_table(self, initiatives: List[Initiative]) -> str:
        """Create priority summary table.

        Args:
            initiatives: List of initiatives

        Returns:
            Markdown table with priority summary
        """
        priority_counts = {}
        for initiative in initiatives:
            priority = initiative.priority.value if initiative.priority else "No Priority"
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        if not priority_counts:
            return "*No initiatives found*"

        table = "| Priority | Count |\n|----------|-------|\n"
        # Sort by priority order
        priority_order = ["Critical", "Highest", "High", "Medium", "Low", "Lowest", "No Priority"]
        for priority in priority_order:
            if priority in priority_counts:
                count = priority_counts[priority]
                table += f"| {priority} | {count} |\n"

        return table

    def create_team_summary_table(self, initiatives: List[Initiative]) -> str:
        """Create team/project summary table.

        Args:
            initiatives: List of initiatives

        Returns:
            Markdown table with team summary
        """
        team_counts = {}
        for initiative in initiatives:
            team = initiative.project.key
            team_counts[team] = team_counts.get(team, 0) + 1

        if not team_counts:
            return "*No initiatives found*"

        table = "| Team/Project | Count |\n|--------------|-------|\n"
        for team, count in sorted(team_counts.items()):
            table += f"| {team} | {count} |\n"

        return table

    def format_initiative_list(
        self,
        initiatives: List[Initiative],
        group_by: Optional[str] = None,
        show_details: bool = False,
    ) -> str:
        """Format list of initiatives with optional grouping.

        Args:
            initiatives: List of initiatives to format
            group_by: Optional field to group by ('status', 'priority', 'project')
            show_details: Whether to show detailed information

        Returns:
            Formatted markdown content
        """
        if not initiatives:
            return "*No initiatives found*"

        if not group_by:
            # Simple list
            content = ""
            for initiative in initiatives:
                if show_details and isinstance(initiative, L2Initiative):
                    content += self.format_l2_initiative_detailed(initiative)
                    content += "\n---\n"
                else:
                    content += self.format_initiative_summary(initiative) + "\n"
            return content

        # Grouped list
        groups = {}
        for initiative in initiatives:
            if group_by == "status":
                key = initiative.status.value
            elif group_by == "priority":
                key = initiative.priority.value if initiative.priority else "No Priority"
            elif group_by == "project":
                key = initiative.project.key
            else:
                key = "Other"

            if key not in groups:
                groups[key] = []
            groups[key].append(initiative)

        content = ""
        for group_name in sorted(groups.keys()):
            content += f"\n### {group_name}\n\n"
            group_initiatives = groups[group_name]

            for initiative in group_initiatives:
                if show_details and isinstance(initiative, L2Initiative):
                    content += self.format_l2_initiative_detailed(initiative)
                    content += "\n---\n"
                else:
                    content += self.format_initiative_summary(initiative) + "\n"

            content += "\n"

        return content

    def create_executive_summary(
        self, initiatives: List[Initiative], division: str = "UI Foundations"
    ) -> str:
        """Create executive summary section.

        Args:
            initiatives: List of initiatives
            division: Division name

        Returns:
            Executive summary markdown
        """
        total_count = len(initiatives)
        active_count = len([i for i in initiatives if i.is_active()])
        completed_count = len([i for i in initiatives if i.is_completed()])
        at_risk_count = len([i for i in initiatives if i.is_at_risk()])

        summary = f"""## Executive Summary

**Total Initiatives**: {total_count}
**Active Initiatives**: {active_count}
**Completed Initiatives**: {completed_count}
**At Risk Initiatives**: {at_risk_count}

**Division**: {division}
**Report Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

        return summary

    def create_recommendations_section(self, initiatives: List[Initiative]) -> str:
        """Create recommendations section based on initiative analysis.

        Args:
            initiatives: List of initiatives to analyze

        Returns:
            Recommendations markdown section
        """
        at_risk = [i for i in initiatives if i.is_at_risk()]
        high_priority = [
            i
            for i in initiatives
            if i.priority and i.priority.value in ["High", "Highest", "Critical"]
        ]
        stale = [i for i in initiatives if i.days_since_update() > 14]

        content = """## Recommendations for Strategic Priority Ranking

Based on this analysis:

"""

        if at_risk:
            content += f"1. **Immediate Attention Required**: {
                len(at_risk)} initiatives at risk need escalation\n"

        if high_priority and not all(i.is_active() for i in high_priority):
            inactive_high = [i for i in high_priority if not i.is_active()]
            content += f"2. **High Priority Activation**: {
                len(inactive_high)} high-priority initiatives not yet active\n"

        if stale:
            content += f"3. **Stale Initiative Review**: {
                len(stale)} initiatives not updated in 14+ days\n"

        content += """
### Next Steps:
- Review at-risk initiatives for blockers and resource needs
- Validate priority alignment with strategic objectives
- Identify resource constraints and capacity planning needs
- Prepare executive briefing with recommended actions

"""

        return content

    def escape_markdown(self, text: str) -> str:
        """Escape special markdown characters in text.

        Args:
            text: Text to escape

        Returns:
            Escaped text
        """
        if not text:
            return ""

        # Escape markdown special characters
        special_chars = [
            "\\",
            "`",
            "*",
            "_",
            "{",
            "}",
            "[",
            "]",
            "(",
            ")",
            "#",
            "+",
            "-",
            ".",
            "!",
            "|",
        ]
        for char in special_chars:
            text = text.replace(char, f"\\{char}")

        return text
