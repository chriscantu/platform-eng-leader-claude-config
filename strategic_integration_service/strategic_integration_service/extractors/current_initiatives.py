"""Current initiatives extractor for UI Foundation teams."""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import structlog

from ..core.config import Settings
from ..models.initiative import CurrentInitiative, StrategicEpic, StrategicLabel, TeamProject
from ..utils.jira_client import JiraClient
from ..utils.markdown_utils import MarkdownGenerator
from .base_extractor import BaseExtractor

logger = structlog.get_logger(__name__)


class CurrentInitiativesExtractor(BaseExtractor):
    """Extractor for current UI Foundation initiatives."""

    def __init__(self, settings: Settings):
        """Initialize the current initiatives extractor."""
        super().__init__(settings)
        self.team_projects = list(settings.team_projects)
        self.strategic_labels = [label.value for label in StrategicLabel]

    def extract(self) -> List[CurrentInitiative]:
        """Extract current initiatives (implementation of abstract method)."""
        import asyncio

        active_initiatives, _, _ = asyncio.run(self.extract_all())
        return active_initiatives

    def get_jql_query(self) -> str:
        """Get the primary JQL query (implementation of abstract method)."""
        return self.get_active_initiatives_jql()

    def get_active_initiatives_jql(self) -> str:
        """Generate JQL for active initiatives."""
        projects = ",".join(self.team_projects)
        return (
            f"project in ({projects}) AND "
            f"status not in (Done, Closed, Resolved) "
            f"ORDER BY priority DESC, project, updated DESC"
        )

    def get_strategic_epics_jql(self) -> str:
        """Generate JQL for strategic epics."""
        projects = ",".join(self.team_projects)
        labels = ",".join(self.strategic_labels)
        return (
            f"(project in ({projects}) OR labels in ({labels})) AND "
            f"issuetype = Epic AND "
            f"status not in (Done, Closed) "
            f"ORDER BY priority DESC, updated DESC"
        )

    def get_recent_completed_jql(self, days: int = 30) -> str:
        """Generate JQL for recently completed work."""
        projects = ",".join(self.team_projects)
        return (
            f"project in ({projects}) AND "
            f"status in (Done, Closed, Resolved) AND "
            f"updated >= -{days}d "
            f"ORDER BY updated DESC"
        )

    async def extract_active_initiatives(self) -> List[CurrentInitiative]:
        """Extract active initiatives from all UI Foundation teams."""
        logger.info("Extracting active initiatives", projects=self.team_projects)

        jql = self.get_active_initiatives_jql()
        logger.info("Active initiatives query", jql=jql)

        jira_client = JiraClient(self.settings)
        issues = await jira_client.search_issues(
            jql=jql,
            max_results=200,
            fields=[
                "summary",
                "status",
                "priority",
                "assignee",
                "project",
                "labels",
                "components",
                "fixVersions",
                "description",
                "updated",
                "created",
                "issuetype",
                "timeestimate",
                "timeoriginalestimate",
                "customfield_10014",
            ],
        )

        initiatives = []
        failed_count = 0

        for issue_data in issues:
            try:
                initiative = CurrentInitiative.from_jira_issue(issue_data)
                initiatives.append(initiative)
                logger.debug(
                    "Processed active initiative",
                    key=initiative.key,
                    project=initiative.project.key if initiative.project else None,
                    status=initiative.status,
                )
            except Exception as e:
                failed_count += 1
                logger.warning(
                    "Failed to process active initiative",
                    issue_key=issue_data.get("key", "unknown"),
                    error=str(e),
                )

        logger.info(
            "Active initiatives extraction completed",
            total_found=len(issues),
            successfully_processed=len(initiatives),
            failed=failed_count,
        )

        return initiatives

    async def extract_strategic_epics(self) -> List[StrategicEpic]:
        """Extract strategic epics and platform initiatives."""
        logger.info("Extracting strategic epics", labels=self.strategic_labels)

        jql = self.get_strategic_epics_jql()
        logger.info("Strategic epics query", jql=jql)

        jira_client = JiraClient(self.settings)
        issues = await jira_client.search_issues(
            jql=jql,
            max_results=100,
            fields=[
                "summary",
                "status",
                "priority",
                "assignee",
                "project",
                "labels",
                "components",
                "fixVersions",
                "description",
                "updated",
                "created",
                "timeestimate",
                "timeoriginalestimate",
                "customfield_10011",
                "customfield_10010",  # Epic Name and Epic Status
            ],
        )

        epics = []
        failed_count = 0

        for issue_data in issues:
            try:
                epic = StrategicEpic.from_jira_issue(issue_data)
                epics.append(epic)
                logger.debug(
                    "Processed strategic epic",
                    key=epic.key,
                    project=epic.project.key if epic.project else None,
                    epic_name=epic.epic_name,
                )
            except Exception as e:
                failed_count += 1
                logger.warning(
                    "Failed to process strategic epic",
                    issue_key=issue_data.get("key", "unknown"),
                    error=str(e),
                )

        logger.info(
            "Strategic epics extraction completed",
            total_found=len(issues),
            successfully_processed=len(epics),
            failed=failed_count,
        )

        return epics

    async def extract_recent_completed(self, days: int = 30) -> List[CurrentInitiative]:
        """Extract recently completed work for context."""
        logger.info("Extracting recent completed work", days=days)

        jql = self.get_recent_completed_jql(days)
        logger.info("Recent completed query", jql=jql)

        jira_client = JiraClient(self.settings)
        issues = await jira_client.search_issues(
            jql=jql,
            max_results=100,
            fields=[
                "summary",
                "status",
                "priority",
                "assignee",
                "project",
                "labels",
                "components",
                "resolutiondate",
                "updated",
                "issuetype",
            ],
        )

        completed = []
        failed_count = 0

        for issue_data in issues:
            try:
                initiative = CurrentInitiative.from_jira_issue(issue_data)
                completed.append(initiative)
                logger.debug(
                    "Processed completed initiative",
                    key=initiative.key,
                    project=initiative.project.key if initiative.project else None,
                    resolution_date=initiative.resolution_date,
                )
            except Exception as e:
                failed_count += 1
                logger.warning(
                    "Failed to process completed initiative",
                    issue_key=issue_data.get("key", "unknown"),
                    error=str(e),
                )

        logger.info(
            "Recent completed extraction completed",
            total_found=len(issues),
            successfully_processed=len(completed),
            failed=failed_count,
        )

        return completed

    async def extract_all(
        self,
    ) -> Tuple[List[CurrentInitiative], List[StrategicEpic], List[CurrentInitiative]]:
        """Extract all current initiatives data."""
        logger.info("Starting comprehensive current initiatives extraction")

        # Run extractions in parallel for better performance
        active_task = asyncio.create_task(self.extract_active_initiatives())
        epics_task = asyncio.create_task(self.extract_strategic_epics())
        completed_task = asyncio.create_task(self.extract_recent_completed())

        active_initiatives = await active_task
        strategic_epics = await epics_task
        recent_completed = await completed_task

        logger.info(
            "All extractions completed",
            active_count=len(active_initiatives),
            epics_count=len(strategic_epics),
            completed_count=len(recent_completed),
        )

        return active_initiatives, strategic_epics, recent_completed

    def generate_team_breakdown(
        self, initiatives: List[CurrentInitiative]
    ) -> Dict[str, List[CurrentInitiative]]:
        """Group initiatives by UI Foundation team."""
        teams = {}
        for initiative in initiatives:
            team_key = initiative.project.key if initiative.project else "Unknown"
            team_name = initiative.team_name

            if team_name not in teams:
                teams[team_name] = []
            teams[team_name].append(initiative)

        return teams

    def generate_priority_analysis(
        self, initiatives: List[CurrentInitiative]
    ) -> Dict[str, List[CurrentInitiative]]:
        """Analyze initiatives by priority and risk."""
        return {
            "high_priority": [init for init in initiatives if init.is_high_priority()],
            "at_risk": [init for init in initiatives if init.is_at_risk()],
            "strategic": [init for init in initiatives if init.has_strategic_labels()],
        }

    def generate_markdown_report(
        self,
        active_initiatives: List[CurrentInitiative],
        strategic_epics: List[StrategicEpic],
        recent_completed: List[CurrentInitiative],
        output_path: Path,
    ) -> str:
        """Generate comprehensive markdown analysis report."""
        extract_date = datetime.now().strftime("%Y-%m-%d")

        # Generate team breakdown
        team_breakdown = self.generate_team_breakdown(active_initiatives)
        priority_analysis = self.generate_priority_analysis(active_initiatives)

        # Categorize strategic epics
        platform_epics = [epic for epic in strategic_epics if epic.is_platform_related()]
        quality_epics = [epic for epic in strategic_epics if epic.is_quality_related()]
        other_epics = [
            epic
            for epic in strategic_epics
            if not epic.is_platform_related() and not epic.is_quality_related()
        ]

        markdown_gen = MarkdownGenerator()
        content = []

        # Header
        content.extend(
            [
                f"# UI Foundation Current Initiatives Analysis",
                f"**Generated**: {extract_date}",
                f"**Source**: Company Jira API across all UI Foundation teams",
                "",
                "---",
                "",
                "## Executive Summary",
                "",
                f"**Total Active Initiatives**: {len(active_initiatives)}",
                f"**Strategic Epics**: {len(strategic_epics)}",
                f"**Recent Completions (30d)**: {len(recent_completed)}",
                "",
                "---",
                "",
                "## Active Initiatives by Team",
                "",
            ]
        )

        # Team breakdown
        for team_name, team_initiatives in team_breakdown.items():
            content.extend([f"### {team_name}", ""])

            if team_initiatives:
                for initiative in team_initiatives:
                    jira_url = f"https://procoretech.atlassian.net/browse/{initiative.key}"
                    content.append(f"- [{initiative.key}]({jira_url}): {initiative.summary}")
            else:
                content.append("  *No active initiatives found*")

            content.append("")

        # Strategic epics analysis
        content.extend(
            [
                "---",
                "",
                "## Strategic Epics Analysis",
                "",
                "### Platform Foundation & Architecture",
                "",
            ]
        )

        if platform_epics:
            for epic in platform_epics:
                jira_url = f"https://procoretech.atlassian.net/browse/{epic.key}"
                priority = epic.priority or "No Priority"
                content.append(
                    f"- [{epic.key}]({jira_url}): {epic.summary} - {epic.status} - {priority}"
                )
        else:
            content.append("  *No platform-related epics found*")

        content.extend(["", "### Quality & Monitoring", ""])

        if quality_epics:
            for epic in quality_epics:
                jira_url = f"https://procoretech.atlassian.net/browse/{epic.key}"
                priority = epic.priority or "No Priority"
                content.append(
                    f"- [{epic.key}]({jira_url}): {epic.summary} - {epic.status} - {priority}"
                )
        else:
            content.append("  *No quality-related epics found*")

        content.extend(["", "### Other Strategic Initiatives", ""])

        if other_epics:
            for epic in other_epics:
                jira_url = f"https://procoretech.atlassian.net/browse/{epic.key}"
                priority = epic.priority or "No Priority"
                content.append(
                    f"- [{epic.key}]({jira_url}): {epic.summary} - {epic.status} - {priority}"
                )
        else:
            content.append("  *No other strategic epics found*")

        # Priority analysis
        content.extend(
            [
                "",
                "---",
                "",
                "## Priority Analysis for Strategic Planning",
                "",
                "### High Priority Initiatives",
                "",
            ]
        )

        if priority_analysis["high_priority"]:
            for initiative in priority_analysis["high_priority"]:
                jira_url = f"https://procoretech.atlassian.net/browse/{initiative.key}"
                project = initiative.project.key if initiative.project else "Unknown"
                content.append(
                    f"- [{initiative.key}]({jira_url}): {initiative.summary} - {project}"
                )
        else:
            content.append("  *No high priority initiatives found*")

        content.extend(["", "### At Risk / Blocked Initiatives", ""])

        if priority_analysis["at_risk"]:
            for initiative in priority_analysis["at_risk"]:
                jira_url = f"https://procoretech.atlassian.net/browse/{initiative.key}"
                content.append(
                    f"- [{initiative.key}]({jira_url}): {initiative.summary} - {initiative.status}"
                )
        else:
            content.append("  *No at-risk initiatives identified*")

        # Recommendations
        total_platform = len(platform_epics)
        total_quality = len(quality_epics)
        total_high_priority = len(priority_analysis["high_priority"])
        total_at_risk = len(priority_analysis["at_risk"])

        content.extend(
            [
                "",
                "---",
                "",
                "## Recommendations for Strategic Priority Ranking",
                "",
                "Based on this analysis:",
                "",
                f"1. **Platform Foundation Priority**: {total_platform} initiatives related to platform/foundation work",
                f"2. **Quality Infrastructure Priority**: {total_quality} initiatives related to monitoring/quality",
                f"3. **Team Capacity**: {len(active_initiatives)} total active initiatives across teams",
                f"4. **Resource Constraints**: {total_high_priority} high priority + {total_at_risk} at risk items need attention",
                "",
                "---",
                "",
                "## Data Sources",
                f"- **Company Jira API**: All team projects ({', '.join(self.team_projects)})",
                f"- **Strategic Labels**: {', '.join(self.strategic_labels)}",
                f"- **Query Date**: {extract_date}",
                f"- **Raw Data**: Available in output directory",
                "",
            ]
        )

        report_content = "\n".join(content)

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info("Markdown report generated", path=output_path)
        return report_content

    async def run(self, output_dir: Optional[Path] = None) -> Dict[str, any]:
        """Run the current initiatives extraction."""
        if output_dir is None:
            output_dir = self.settings.output_base_dir / "current-initiatives" / "jira-data"

        output_dir.mkdir(parents=True, exist_ok=True)
        extract_date = datetime.now().strftime("%Y-%m-%d")

        logger.info("Starting current initiatives extraction", output_dir=output_dir)

        # Extract all data
        active_initiatives, strategic_epics, recent_completed = await self.extract_all()

        # Save raw data
        active_file = output_dir / f"active-initiatives-{extract_date}.json"
        epics_file = output_dir / f"strategic-epics-{extract_date}.json"
        completed_file = output_dir / f"recent-completed-{extract_date}.json"
        analysis_file = output_dir / f"initiatives-analysis-{extract_date}.md"

        # Save JSON data
        self.save_json_data([init.model_dump() for init in active_initiatives], active_file)
        self.save_json_data([epic.model_dump() for epic in strategic_epics], epics_file)
        self.save_json_data([comp.model_dump() for comp in recent_completed], completed_file)

        # Generate analysis report
        self.generate_markdown_report(
            active_initiatives, strategic_epics, recent_completed, analysis_file
        )

        logger.info("Current initiatives extraction completed successfully")

        return {
            "active_initiatives": len(active_initiatives),
            "strategic_epics": len(strategic_epics),
            "recent_completed": len(recent_completed),
            "output_files": {
                "active_initiatives": str(active_file),
                "strategic_epics": str(epics_file),
                "recent_completed": str(completed_file),
                "analysis_report": str(analysis_file),
            },
        }
