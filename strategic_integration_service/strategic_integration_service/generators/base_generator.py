"""Base report generator class."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from ..core.config import Settings
from ..models.initiative import CurrentInitiative
from ..models.report import (
    InitiativeHealthStatus,
    ReportMetadata,
    ReportOutput,
    ReportType,
    TemplateContext,
)
from ..utils.template_engine import ReportTemplateEngine

logger = structlog.get_logger(__name__)


class BaseReportGenerator(ABC):
    """Base class for all report generators."""

    def __init__(self, settings: Settings):
        """Initialize the report generator."""
        self.settings = settings
        self.template_engine = ReportTemplateEngine()
        self.logger = structlog.get_logger(self.__class__.__name__)

    @abstractmethod
    def get_report_type(self) -> ReportType:
        """Get the report type this generator produces."""
        pass

    @abstractmethod
    def collect_data(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Collect data for the report period."""
        pass

    @abstractmethod
    def analyze_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze collected data and generate insights."""
        pass

    @abstractmethod
    def generate_report_data(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report-specific data structure."""
        pass

    def determine_initiative_health(self, initiative: CurrentInitiative) -> InitiativeHealthStatus:
        """Determine health status for an initiative."""
        # Check if explicitly at risk or blocked
        if initiative.is_at_risk():
            return InitiativeHealthStatus.RED

        # Check priority and age
        if initiative.is_high_priority():
            if initiative.updated:
                days_since_update = (
                    datetime.now(initiative.updated.tzinfo) - initiative.updated
                ).days
                if days_since_update > 7:  # High priority not updated in a week
                    return InitiativeHealthStatus.YELLOW
                else:
                    return InitiativeHealthStatus.GREEN
            else:
                return InitiativeHealthStatus.YELLOW

        # Regular initiatives
        if initiative.updated:
            days_since_update = (datetime.now(initiative.updated.tzinfo) - initiative.updated).days
            if days_since_update > 14:  # Not updated in 2 weeks
                return InitiativeHealthStatus.YELLOW
            else:
                return InitiativeHealthStatus.GREEN

        return InitiativeHealthStatus.UNKNOWN

    def calculate_team_health(
        self, team_initiatives: List[CurrentInitiative]
    ) -> InitiativeHealthStatus:
        """Calculate overall health for a team based on their initiatives."""
        if not team_initiatives:
            return InitiativeHealthStatus.UNKNOWN

        health_counts = {status: 0 for status in InitiativeHealthStatus}

        for initiative in team_initiatives:
            health = self.determine_initiative_health(initiative)
            health_counts[health] += 1

        total = len(team_initiatives)
        red_percentage = health_counts[InitiativeHealthStatus.RED] / total
        yellow_percentage = health_counts[InitiativeHealthStatus.YELLOW] / total

        # Team health rules
        if red_percentage > 0.3:  # More than 30% red
            return InitiativeHealthStatus.RED
        elif red_percentage > 0.1 or yellow_percentage > 0.5:  # >10% red or >50% yellow
            return InitiativeHealthStatus.YELLOW
        else:
            return InitiativeHealthStatus.GREEN

    def group_initiatives_by_team(
        self, initiatives: List[CurrentInitiative]
    ) -> Dict[str, List[CurrentInitiative]]:
        """Group initiatives by team."""
        teams = {}
        for initiative in initiatives:
            team_name = initiative.team_name
            if team_name not in teams:
                teams[team_name] = []
            teams[team_name].append(initiative)
        return teams

    def filter_by_date_range(
        self,
        initiatives: List[CurrentInitiative],
        start_date: datetime,
        end_date: datetime,
        date_field: str = "updated",
    ) -> List[CurrentInitiative]:
        """Filter initiatives by date range."""
        filtered = []
        for initiative in initiatives:
            date_value = getattr(initiative, date_field, None)
            if date_value and start_date <= date_value <= end_date:
                filtered.append(initiative)
        return filtered

    def generate_executive_summary(self, report_data: Dict[str, Any]) -> str:
        """Generate executive summary text."""
        # This is a base implementation - subclasses should override for specific insights
        total_initiatives = report_data.get("total_initiatives", 0)
        teams_count = len(report_data.get("teams_included", []))

        summary = f"Analysis of {total_initiatives} initiatives across {teams_count} UI Foundation teams. "

        # Add health assessment if available
        if "health_distribution" in report_data:
            health_dist = report_data["health_distribution"]
            red_count = health_dist.get(InitiativeHealthStatus.RED, 0)
            if red_count > 0:
                summary += f"{red_count} initiatives require immediate attention. "

        return summary

    def generate_recommendations(self, analyzed_data: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations based on data analysis."""
        recommendations = []

        # Analyze at-risk initiatives
        at_risk_count = analyzed_data.get("at_risk_count", 0)
        if at_risk_count > 0:
            recommendations.append(
                f"Address {at_risk_count} at-risk initiatives through resource reallocation or scope adjustment"
            )

        # Analyze team capacity
        team_summaries = analyzed_data.get("team_summaries", {})
        overloaded_teams = [
            team
            for team, data in team_summaries.items()
            if data.get("active_count", 0) > 10  # More than 10 active initiatives
        ]
        if overloaded_teams:
            recommendations.append(
                f"Review capacity for {', '.join(overloaded_teams)} - high initiative load detected"
            )

        # Analyze completion velocity
        completed_count = analyzed_data.get("completed_this_week", 0)
        if completed_count == 0:
            recommendations.append(
                "Review initiative progress - no completions detected this period"
            )

        return recommendations

    def create_report_metadata(
        self,
        period_start: datetime,
        period_end: datetime,
        data_sources: List[str],
        total_initiatives: int,
        teams_included: List[str],
    ) -> ReportMetadata:
        """Create report metadata."""
        return ReportMetadata(
            report_type=self.get_report_type(),
            generation_date=datetime.now(),
            report_period_start=period_start,
            report_period_end=period_end,
            data_sources=data_sources,
            total_initiatives=total_initiatives,
            teams_included=teams_included,
        )

    def render_report(self, report_data: Dict[str, Any], template_name: str) -> str:
        """Render report using template."""
        try:
            # Create template context
            context = TemplateContext(
                report=report_data.get("report"),
                metadata=report_data.get("metadata"),
                data=report_data.get("data"),
                format_helpers={},
            )

            # Render using template engine
            return self.template_engine.render_template(template_name, context)

        except Exception as e:
            self.logger.error("Report rendering failed", template=template_name, error=str(e))
            raise

    def save_report(self, report: ReportOutput, output_dir: Optional[Path] = None) -> Path:
        """Save report to file."""
        if output_dir is None:
            output_dir = self.settings.report_output_dir

        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        filename = report.get_filename()
        output_path = output_dir / filename

        # Write report content
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report.raw_markdown)

        self.logger.info("Report saved", output_path=output_path)
        return output_path

    async def generate(
        self,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        output_dir: Optional[Path] = None,
    ) -> ReportOutput:
        """Generate complete report for the specified period."""
        # Set default dates if not provided
        if period_end is None:
            period_end = datetime.now()
        if period_start is None:
            # Default to last week for weekly reports, last month for monthly
            if self.get_report_type() == ReportType.WEEKLY_SLT:
                period_start = period_end - timedelta(weeks=1)
            else:
                period_start = period_end - timedelta(days=30)

        self.logger.info(
            "Starting report generation",
            report_type=self.get_report_type().value,
            period_start=period_start,
            period_end=period_end,
        )

        try:
            # Collect and analyze data
            raw_data = self.collect_data(period_start, period_end)
            analyzed_data = self.analyze_data(raw_data)
            report_data = self.generate_report_data(analyzed_data)

            # Create metadata
            metadata = self.create_report_metadata(
                period_start=period_start,
                period_end=period_end,
                data_sources=raw_data.get("data_sources", []),
                total_initiatives=analyzed_data.get("total_initiatives", 0),
                teams_included=list(analyzed_data.get("team_summaries", {}).keys()),
            )

            # Generate content
            executive_summary = self.generate_executive_summary(analyzed_data)
            recommendations = self.generate_recommendations(analyzed_data)

            # Create report output
            report = ReportOutput(
                metadata=metadata,
                sections=[],  # Will be populated by template rendering
                data=report_data,
                raw_markdown="",  # Will be set after rendering
                executive_summary=executive_summary,
                recommendations=recommendations,
            )

            # Render template
            template_name = f"{self.get_report_type().value.replace('_', '-')}-template.md"
            rendered_content = self.render_report(
                {"report": report, "metadata": metadata, "data": report_data}, template_name
            )

            # Update report with rendered content
            report.raw_markdown = rendered_content

            # Save report if output directory specified
            if output_dir:
                self.save_report(report, output_dir)

            self.logger.info(
                "Report generation completed", report_type=self.get_report_type().value
            )
            return report

        except Exception as e:
            self.logger.error("Report generation failed", error=str(e))
            raise
