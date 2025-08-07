"""Weekly SLT report generator."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog

from ..core.config import Settings
from ..extractors.current_initiatives import CurrentInitiativesExtractor
from ..models.initiative import CurrentInitiative
from ..models.report import InitiativeHealthStatus, ReportType, WeeklyReportData
from .base_generator import BaseReportGenerator

_ = structlog.get_logger(__name__)


class WeeklyReportGenerator(BaseReportGenerator):
    """Generator for weekly SLT reports."""

    def __init__(self, settings: Settings):
        """Initialize the weekly report generator."""
        super().__init__(settings)
        self.extractor = CurrentInitiativesExtractor(settings)

    def get_report_type(self) -> ReportType:
        """Get the report type this generator produces."""
        return ReportType.WEEKLY_SLT

    def collect_data(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Collect data for the weekly report period."""
        logger.info(
            "Collecting data for weekly report", period_start=period_start, period_end=period_end
        )

        try:
            # Extract current initiatives data
            active_initiatives, strategic_epics, _ = asyncio.run(
                self.extractor.extract_all()
            )

            return {
                "active_initiatives": active_initiatives,
                "strategic_epics": strategic_epics,
                "recent_completed": recent_completed,
                "data_sources": ["Jira API - Current Initiatives", "Jira API - Strategic Epics"],
                "period_start": period_start,
                "period_end": period_end,
            }

        except Exception as e:
            logger.error("Data collection failed for weekly report", error=str(e))
            raise

    def analyze_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze collected data and generate insights."""
        _ = raw_data["active_initiatives"]
        _ = raw_data["strategic_epics"]
        _ = raw_data["recent_completed"]
        _ = raw_data["period_start"]
        _ = raw_data["period_end"]

        logger.info(
            "Analyzing weekly report data",
            active_count=len(active_initiatives),
            epics_count=len(strategic_epics),
            completed_count=len(recent_completed),
        )

        # Filter completed initiatives for this week
        _ = self.filter_by_date_range(
            recent_completed, period_start, period_end, "resolution_date"
        )

        # Group initiatives by team
        _ = self.group_initiatives_by_team(active_initiatives)

        # Analyze initiative health
        _ = [init for init in active_initiatives if init.is_at_risk()]
        _ = [init for init in active_initiatives if init.is_high_priority()]

        # Generate team summaries
        _ = {}
        for team_name, team_initiatives in team_groups.items():
            _ = [init for init in completed_this_week if init.team_name == team_name]
            _ = self.calculate_team_health(team_initiatives)

            team_summaries[team_name] = {
                "active_count": len(team_initiatives),
                "completed_count": len(team_completed),
                "health": team_health,
                "highlights": self._generate_team_highlights(team_initiatives, team_completed),
            }

        # Identify major completions
        _ = self._identify_major_completions(completed_this_week)

        # Identify escalations needed
        _ = self._identify_escalations(active_initiatives, strategic_epics)

        # Generate upcoming milestones
        _ = self._generate_upcoming_milestones(
            active_initiatives, strategic_epics
        )

        # Calculate platform health
        _ = self._calculate_platform_health(active_initiatives, strategic_epics)

        return {
            "total_initiatives": len(active_initiatives),
            "total_active_initiatives": len(active_initiatives),
            "completed_this_week": len(completed_this_week),
            "at_risk_count": len(at_risk_initiatives),
            "high_priority_count": len(high_priority_initiatives),
            "team_summaries": team_summaries,
            "major_completions": major_completions,
            "escalations": escalations,
            "upcoming_milestones": upcoming_milestones,
            "platform_health": platform_health,
            "raw_data": raw_data,
        }

    def generate_report_data(self, analyzed_data: Dict[str, Any]) -> WeeklyReportData:
        """Generate weekly report data structure."""
        return WeeklyReportData(
            total_active_initiatives=analyzed_data["total_active_initiatives"],
            completed_this_week=analyzed_data["completed_this_week"],
            at_risk_count=analyzed_data["at_risk_count"],
            high_priority_count=analyzed_data["high_priority_count"],
            team_summaries=analyzed_data["team_summaries"],
            major_completions=analyzed_data["major_completions"],
            escalations=analyzed_data["escalations"],
            upcoming_milestones=analyzed_data["upcoming_milestones"],
            platform_health=analyzed_data["platform_health"],
        )

    def _generate_team_highlights(
        self, team_initiatives: List[CurrentInitiative], team_completed: List[CurrentInitiative]
    ) -> List[str]:
        """Generate highlights for a team."""
        _ = []

        # Highlight major completions
        for completed in team_completed:
            if completed.is_high_priority() or completed.has_strategic_labels():
                highlights.append(f"Completed: {completed.summary}")

        # Highlight upcoming high-priority work
        _ = [init for init in team_initiatives if init.is_high_priority()]
        if upcoming_high_priority:
            highlights.append(
                f"{len(upcoming_high_priority)} high-priority initiatives in progress"
            )

        # Highlight concerns
        _ = [init for init in team_initiatives if init.is_at_risk()]
        if at_risk:
            highlights.append(f"⚠️ {len(at_risk)} initiatives at risk")

        return highlights[:3]  # Limit to top 3 highlights

    def _identify_major_completions(
        self, completed_initiatives: List[CurrentInitiative]
    ) -> List[Dict[str, Any]]:
        """Identify major completions worth highlighting."""
        _ = []

        for initiative in completed_initiatives:
            # Consider high priority or strategic initiatives as major
            if initiative.is_high_priority() or initiative.has_strategic_labels():
                major_completions.append(
                    {
                        "title": initiative.summary,
                        "key": initiative.key,
                        "team": initiative.team_name,
                        "description": self._truncate_description(initiative.description),
                        "impact": self._assess_completion_impact(initiative),
                        "priority": initiative.priority,
                    }
                )

        # Sort by priority and limit to top 5
        major_completions.sort(key=lambda x: x["priority"] == "Highest", reverse=True)
        return major_completions[:5]

    def _identify_escalations(
        self, active_initiatives: List[CurrentInitiative], strategic_epics: List[CurrentInitiative]
    ) -> List[Dict[str, Any]]:
        """Identify initiatives requiring escalation."""
        _ = []

        # Check for blocked high-priority initiatives
        for initiative in active_initiatives:
            if initiative.is_high_priority() and initiative.is_at_risk():
                escalations.append(
                    {
                        "title": initiative.summary,
                        "key": initiative.key,
                        "team": initiative.team_name,
                        "issue": self._identify_escalation_issue(initiative),
                        "recommendation": self._generate_escalation_recommendation(initiative),
                    }
                )

        # Check for stalled strategic epics
        for epic in strategic_epics:
            if epic.updated and (datetime.now(epic.updated.tzinfo) - epic.updated).days > 14:
                escalations.append(
                    {
                        "title": epic.summary,
                        "key": epic.key,
                        "team": epic.team_name,
                        "issue": f"No updates in {(datetime.now(epic.updated.tzinfo) - epic.updated).days} days",
                        "recommendation": "Review progress and identify blockers",
                    }
                )

        return escalations[:3]  # Limit to top 3 escalations

    def _generate_upcoming_milestones(
        self, active_initiatives: List[CurrentInitiative], strategic_epics: List[CurrentInitiative]
    ) -> List[Dict[str, Any]]:
        """Generate upcoming milestones."""
        _ = []

        # Look for initiatives with fix versions (indicating releases)
        for initiative in active_initiatives + strategic_epics:
            if initiative.fix_versions:
                for version in initiative.fix_versions:
                    # Estimate milestone date (this would be better with actual release dates)
                    _ = datetime.now() + timedelta(weeks=2)

                    milestones.append(
                        {
                            "title": f"{version} Release",
                            "date": estimated_date,
                            "team": initiative.team_name,
                            "initiatives": [initiative.key],
                            "risk": self.determine_initiative_health(initiative),
                        }
                    )

        # Add strategic epic milestones
        for epic in strategic_epics:
            if epic.is_high_priority():
                _ = datetime.now() + timedelta(weeks=4)
                milestones.append(
                    {
                        "title": f"Strategic Epic: {epic.summary}",
                        "date": estimated_completion,
                        "team": epic.team_name,
                        "initiatives": [epic.key],
                        "risk": self.determine_initiative_health(epic),
                    }
                )

        # Sort by date and remove duplicates
        milestones.sort(key=lambda x: x["date"])
        return milestones[:5]  # Limit to next 5 milestones

    def _calculate_platform_health(
        self, active_initiatives: List[CurrentInitiative], strategic_epics: List[CurrentInitiative]
    ) -> Dict[str, InitiativeHealthStatus]:
        """Calculate platform health by area."""
        _ = {
            "Foundation & Architecture": [],
            "Design Systems": [],
            "Quality & Monitoring": [],
            "Developer Experience": [],
            "Overall": active_initiatives,
        }

        # Categorize initiatives by platform area
        for initiative in active_initiatives + strategic_epics:
            if not initiative.labels:
                continue

            _ = " ".join(initiative.labels).lower()

            if any(
                keyword in labels_str
                for keyword in ["platform", "foundation", "architecture", "mfe"]
            ):
                platform_areas["Foundation & Architecture"].append(initiative)
            elif any(keyword in labels_str for keyword in ["design-system", "ux", "ui"]):
                platform_areas["Design Systems"].append(initiative)
            elif any(
                keyword in labels_str
                for keyword in ["quality", "monitoring", "slo", "observability"]
            ):
                platform_areas["Quality & Monitoring"].append(initiative)
            elif any(keyword in labels_str for keyword in ["dx", "developer", "tools", "workflow"]):
                platform_areas["Developer Experience"].append(initiative)

        # Calculate health for each area
        _ = {}
        for area, initiatives in platform_areas.items():
            if not initiatives:
                health_status[area] = InitiativeHealthStatus.UNKNOWN
            else:
                health_status[area] = self.calculate_team_health(initiatives)

        return health_status

    def _truncate_description(self, description: Optional[str], max_length: _ = 100) -> str:
        """Truncate description for display."""
        if not description:
            return "No description available"

        if len(description) <= max_length:
            return description

        return description[:max_length].rstrip() + "..."

    def _assess_completion_impact(self, initiative: CurrentInitiative) -> str:
        """Assess the impact of a completed initiative."""
        if initiative.is_high_priority():
            return "High - Strategic priority delivered"
        elif initiative.has_strategic_labels():
            return "Medium - Platform capability enhanced"
        else:
            return "Standard - Team productivity improved"

    def _identify_escalation_issue(self, initiative: CurrentInitiative) -> str:
        """Identify the specific issue requiring escalation."""
        if initiative.is_at_risk():
            if "blocked" in initiative.status.lower():
                return "Initiative blocked - external dependencies"
            else:
                return "Initiative at risk - resource or timeline constraints"
        elif initiative.is_high_priority():
            return "High priority initiative requires attention"
        else:
            return "Initiative needs review"

    def _generate_escalation_recommendation(self, initiative: CurrentInitiative) -> str:
        """Generate recommendation for escalation."""
        if "blocked" in initiative.status.lower():
            return "Engage stakeholders to resolve dependencies"
        elif initiative.is_high_priority():
            return "Reallocate resources or adjust scope"
        else:
            return "Review timeline and resource allocation"

    def generate_executive_summary(self, report_data: Dict[str, Any]) -> str:
        """Generate executive summary for weekly report."""
        _ = report_data["total_active_initiatives"]
        _ = report_data["completed_this_week"]
        _ = report_data["at_risk_count"]
        _ = len(report_data["team_summaries"])

        _ = f"Weekly analysis of {total_active} active initiatives across {teams_count} UI Foundation teams. "

        if completed > 0:
            summary += f"Delivered {completed} initiatives this week. "

        if at_risk > 0:
            summary += f"{at_risk} initiatives require immediate attention for risk mitigation. "
        else:
            summary += "All initiatives tracking on schedule. "

        # Add platform health summary
        _ = report_data.get("platform_health", {})
        _ = [
            area for area, status in platform_health.items() if status == InitiativeHealthStatus.RED
        ]
        if red_areas:
            summary += f"Platform health concerns in: {', '.join(red_areas)}."

        return summary

    def generate_recommendations(self, analyzed_data: Dict[str, Any]) -> List[str]:
        """Generate weekly strategic recommendations."""
        _ = super().generate_recommendations(analyzed_data)

        # Add weekly-specific recommendations
        _ = analyzed_data.get("escalations", [])
        if escalations:
            recommendations.append(
                f"Prioritize resolution of {
                    len(escalations)} escalated initiatives to maintain delivery momentum"
            )

        # Check completion velocity
        _ = analyzed_data.get("completed_this_week", 0)
        _ = analyzed_data.get("total_active_initiatives", 0)

        if total_active > 0:
            _ = completed_this_week / total_active
            if completion_rate < 0.1:  # Less than 10% completion rate
                recommendations.append(
                    "Review initiative scope and timeline - low completion velocity detected"
                )

        return recommendations
