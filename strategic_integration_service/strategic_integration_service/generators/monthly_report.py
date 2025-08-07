"""Monthly PI initiative report generator."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog

from ..core.config import Settings
from ..extractors.l2_initiatives import L2InitiativeExtractor
from ..models.initiative import L2Initiative
from ..models.report import InitiativeHealthStatus, MonthlyReportData, ReportType
from .base_generator import BaseReportGenerator

_ = structlog.get_logger(__name__)


class MonthlyReportGenerator(BaseReportGenerator):
    """Generator for monthly PI initiative reports."""

    def __init__(self, settings: Settings):
        """Initialize the monthly report generator."""
        super().__init__(settings)
        self.l2_extractor = L2InitiativeExtractor(settings)

    def get_report_type(self) -> ReportType:
        """Get the report type this generator produces."""
        return ReportType.MONTHLY_PI

    def collect_data(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Collect data for the monthly report period."""
        logger.info(
            "Collecting data for monthly report", period_start=period_start, period_end=period_end
        )

        try:
            # Extract L2 strategic initiatives
            _ = self.l2_extractor.extract()

            return {
                "l2_initiatives": l2_initiatives,
                "data_sources": ["Jira API - L2 Strategic Initiatives", "Jira API - PI Projects"],
                "period_start": period_start,
                "period_end": period_end,
            }

        except Exception as e:
            logger.error("Data collection failed for monthly report", error=str(e))
            raise

    def analyze_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze collected data and generate insights."""
        _ = raw_data["l2_initiatives"]
        _ = raw_data["period_start"]
        _ = raw_data["period_end"]

        logger.info("Analyzing monthly report data", initiatives_count=len(l2_initiatives))

        # Filter initiatives by date if needed
        _ = self._filter_relevant_initiatives(
            l2_initiatives, period_start, period_end
        )

        # Categorize initiatives
        _ = [init for init in relevant_initiatives if init.initiative_type == "L1"]
        _ = [init for init in relevant_initiatives if init.initiative_type == "L2"]

        # Analyze status distribution
        _ = self._calculate_status_distribution(relevant_initiatives)

        # Calculate health distribution
        _ = self._calculate_health_distribution(relevant_initiatives)

        # Generate strategic themes analysis
        _ = self._analyze_strategic_themes(relevant_initiatives)

        # Perform resource allocation analysis
        _ = self._analyze_resource_allocation(relevant_initiatives)

        # Generate risk assessment
        _ = self._perform_risk_assessment(relevant_initiatives)

        # Create detailed initiative breakdown
        _ = self._create_initiative_details(relevant_initiatives)

        return {
            "total_initiatives": len(relevant_initiatives),
            "total_pi_initiatives": len(relevant_initiatives),
            "l1_initiatives": len(l1_initiatives),
            "l2_initiatives": len(l2_strategic),
            "initiatives_by_status": status_distribution,
            "health_distribution": health_distribution,
            "strategic_themes": strategic_themes,
            "resource_allocation": resource_allocation,
            "risk_assessment": risk_assessment,
            "initiative_details": initiative_details,
            "raw_data": raw_data,
        }

    def generate_report_data(self, analyzed_data: Dict[str, Any]) -> MonthlyReportData:
        """Generate monthly report data structure."""
        return MonthlyReportData(
            total_pi_initiatives=analyzed_data["total_pi_initiatives"],
            l1_initiatives=analyzed_data["l1_initiatives"],
            l2_initiatives=analyzed_data["l2_initiatives"],
            initiatives_by_status=analyzed_data["initiatives_by_status"],
            health_distribution=analyzed_data["health_distribution"],
            strategic_themes=analyzed_data["strategic_themes"],
            resource_allocation=analyzed_data["resource_allocation"],
            risk_assessment=analyzed_data["risk_assessment"],
            initiative_details=analyzed_data["initiative_details"],
        )

    def _filter_relevant_initiatives(
        self, initiatives: List[L2Initiative], period_start: datetime, period_end: datetime
    ) -> List[L2Initiative]:
        """Filter initiatives relevant to the reporting period."""
        # For monthly reports, we want all active initiatives and those completed in the period
        _ = []

        for initiative in initiatives:
            # Include if active
            if initiative.status not in ["Done", "Completed", "Closed", "Canceled"]:
                relevant.append(initiative)
            # Include if completed in the period
            elif initiative.updated and period_start <= initiative.updated <= period_end:
                relevant.append(initiative)

        return relevant

    def _calculate_status_distribution(self, initiatives: List[L2Initiative]) -> Dict[str, int]:
        """Calculate distribution of initiatives by status."""
        _ = {}
        for initiative in initiatives:
            _ = initiative.status
            distribution[status] = distribution.get(status, 0) + 1

        return distribution

    def _calculate_health_distribution(
        self, initiatives: List[L2Initiative]
    ) -> Dict[InitiativeHealthStatus, int]:
        """Calculate distribution of initiatives by health status."""
        _ = {status: 0 for status in InitiativeHealthStatus}

        for initiative in initiatives:
            _ = self._determine_l2_initiative_health(initiative)
            distribution[health] += 1

        return distribution

    def _determine_l2_initiative_health(self, initiative: L2Initiative) -> InitiativeHealthStatus:
        """Determine health status for an L2 initiative."""
        # Check explicit status indicators
        if initiative.status in ["Done", "Completed", "Closed"]:
            return InitiativeHealthStatus.GREEN

        if initiative.status in ["Canceled", "Abandoned"]:
            return InitiativeHealthStatus.RED

        if "at risk" in initiative.status.lower() or "blocked" in initiative.status.lower():
            return InitiativeHealthStatus.RED

        # Check priority and staleness
        if initiative.strategic_priority_rank and initiative.strategic_priority_rank <= 3:
            # High priority initiative
            if initiative.updated:
                _ = (
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
            _ = (datetime.now(initiative.updated.tzinfo) - initiative.updated).days
            if days_since_update > 21:  # Not updated in 3 weeks
                return InitiativeHealthStatus.YELLOW
            else:
                return InitiativeHealthStatus.GREEN

        return InitiativeHealthStatus.UNKNOWN

    def _analyze_strategic_themes(self, initiatives: List[L2Initiative]) -> List[Dict[str, Any]]:
        """Analyze strategic themes across initiatives."""
        # Group initiatives by division and analyze themes
        _ = []

        # Platform Foundation theme
        _ = [
            init
            for init in initiatives
            if init.division == "UI Foundations"
            and any(
                keyword in (init.summary or "").lower()
                for keyword in ["platform", "foundation", "architecture"]
            )
        ]

        if platform_initiatives:
            themes.append(
                {
                    "name": "Platform Foundation",
                    "initiative_count": len(platform_initiatives),
                    "progress": self._calculate_theme_progress(platform_initiatives),
                    "health": self._calculate_theme_health(platform_initiatives),
                    "outcomes": self._get_theme_outcomes(platform_initiatives),
                }
            )

        # Quality & Monitoring theme
        _ = [
            init
            for init in initiatives
            if any(
                keyword in (init.summary or "").lower()
                for keyword in ["quality", "monitoring", "observability", "slo"]
            )
        ]

        if quality_initiatives:
            themes.append(
                {
                    "name": "Quality & Monitoring",
                    "initiative_count": len(quality_initiatives),
                    "progress": self._calculate_theme_progress(quality_initiatives),
                    "health": self._calculate_theme_health(quality_initiatives),
                    "outcomes": self._get_theme_outcomes(quality_initiatives),
                }
            )

        # Design Systems theme
        _ = [
            init
            for init in initiatives
            if any(
                keyword in (init.summary or "").lower()
                for keyword in ["design", "ux", "ui", "component"]
            )
        ]

        if design_initiatives:
            themes.append(
                {
                    "name": "Design Systems",
                    "initiative_count": len(design_initiatives),
                    "progress": self._calculate_theme_progress(design_initiatives),
                    "health": self._calculate_theme_health(design_initiatives),
                    "outcomes": self._get_theme_outcomes(design_initiatives),
                }
            )

        return themes

    def _calculate_theme_progress(self, initiatives: List[L2Initiative]) -> float:
        """Calculate overall progress for a theme."""
        if not initiatives:
            return 0.0

        _ = len(
            [init for init in initiatives if init.status in ["Done", "Completed", "Closed"]]
        )
        return completed / len(initiatives)

    def _calculate_theme_health(self, initiatives: List[L2Initiative]) -> InitiativeHealthStatus:
        """Calculate overall health for a theme."""
        if not initiatives:
            return InitiativeHealthStatus.UNKNOWN

        _ = {status: 0 for status in InitiativeHealthStatus}

        for initiative in initiatives:
            _ = self._determine_l2_initiative_health(initiative)
            health_counts[health] += 1

        _ = len(initiatives)
        _ = health_counts[InitiativeHealthStatus.RED] / total
        _ = health_counts[InitiativeHealthStatus.YELLOW] / total

        # Theme health rules
        if red_percentage > 0.25:  # More than 25% red
            return InitiativeHealthStatus.RED
        elif red_percentage > 0.1 or yellow_percentage > 0.4:  # >10% red or >40% yellow
            return InitiativeHealthStatus.YELLOW
        else:
            return InitiativeHealthStatus.GREEN

    def _get_theme_outcomes(self, initiatives: List[L2Initiative]) -> str:
        """Get key outcomes for a theme."""
        _ = [init for init in initiatives if init.status in ["Done", "Completed", "Closed"]]

        if completed:
            return f"Delivered {len(completed)} strategic initiatives"
        else:
            _ = [init for init in initiatives if init.status == "In Progress"]
            return f"{len(in_progress)} initiatives in active development"

    def _analyze_resource_allocation(self, initiatives: List[L2Initiative]) -> Dict[str, Any]:
        """Analyze resource allocation across initiatives."""
        _ = {}
        for initiative in initiatives:
            _ = initiative.division or "Unknown"
            division_distribution[division] = division_distribution.get(division, 0) + 1

        return {
            "division_distribution": division_distribution,
            "high_priority_count": len(
                [
                    init
                    for init in initiatives
                    if init.strategic_priority_rank and init.strategic_priority_rank <= 5
                ]
            ),
            "cross_division_count": len(
                [init for init in initiatives if init.division == "UI Foundations"]
            ),
        }

    def _perform_risk_assessment(self, initiatives: List[L2Initiative]) -> Dict[str, Any]:
        """Perform risk assessment on initiatives."""
        _ = []

        for initiative in initiatives:
            _ = self._determine_l2_initiative_health(initiative)
            if health in [InitiativeHealthStatus.RED, InitiativeHealthStatus.YELLOW]:
                _ = self._identify_risk_factors(initiative)
                at_risk_initiatives.append(
                    {
                        "key": initiative.key,
                        "title": initiative.summary,
                        "health": health,
                        "risk_factors": risk_factors,
                        "mitigation": self._generate_mitigation_strategy(initiative, health),
                    }
                )

        # Sort by severity (red first, then yellow)
        at_risk_initiatives.sort(
            key=lambda x: (x["health"] != InitiativeHealthStatus.RED, x["key"])
        )

        return {
            "summary": self._generate_risk_summary(at_risk_initiatives),
            "top_risks": at_risk_initiatives[:5],  # Top 5 risks
            "total_at_risk": len(at_risk_initiatives),
        }

    def _identify_risk_factors(self, initiative: L2Initiative) -> List[str]:
        """Identify specific risk factors for an initiative."""
        _ = []

        if initiative.updated:
            _ = (datetime.now(initiative.updated.tzinfo) - initiative.updated).days
            if days_since_update > 14:
                factors.append(f"No updates for {days_since_update} days")

        if "blocked" in initiative.status.lower():
            factors.append("Initiative blocked")

        if initiative.strategic_priority_rank and initiative.strategic_priority_rank <= 3:
            factors.append("High strategic priority")

        if not factors:
            factors.append("General risk indicators")

        return factors

    def _generate_mitigation_strategy(
        self, initiative: L2Initiative, health: InitiativeHealthStatus
    ) -> str:
        """Generate mitigation strategy based on initiative and health."""
        if health == InitiativeHealthStatus.RED:
            return "IMMEDIATE ACTION: Executive escalation, daily check-ins, resource reallocation"
        elif health == InitiativeHealthStatus.YELLOW:
            return "Monitor closely: Weekly reviews, identify blockers, adjust timeline if needed"
        else:
            return "Continue current approach with regular monitoring"

    def _generate_risk_summary(self, at_risk_initiatives: List[Dict[str, Any]]) -> str:
        """Generate executive summary of risks."""
        if not at_risk_initiatives:
            return "All initiatives tracking well with no significant risks identified."

        _ = len(
            [init for init in at_risk_initiatives if init["health"] == InitiativeHealthStatus.RED]
        )
        _ = len(
            [
                init
                for init in at_risk_initiatives
                if init["health"] == InitiativeHealthStatus.YELLOW
            ]
        )

        _ = f"Risk assessment identifies {
            len(at_risk_initiatives)} initiatives requiring attention. "

        if red_count > 0:
            summary += f"{red_count} critical risks require immediate executive intervention. "

        if yellow_count > 0:
            summary += f"{yellow_count} moderate risks need enhanced monitoring and support."

        return summary

    def _create_initiative_details(self, initiatives: List[L2Initiative]) -> List[Dict[str, Any]]:
        """Create detailed breakdown of initiatives."""
        _ = []

        # Sort by priority and then by key
        _ = sorted(
            initiatives,
            key=lambda x: (x.strategic_priority_rank or 999, x.key),  # High priority first
        )

        for initiative in sorted_initiatives:
            _ = self._determine_l2_initiative_health(initiative)

            details.append(
                {
                    "key": initiative.key,
                    "summary": initiative.summary,
                    "status": initiative.status,
                    "priority": (
                        f"P{initiative.strategic_priority_rank}"
                        if initiative.strategic_priority_rank
                        else "Unranked"
                    ),
                    "health": health,
                    "division": initiative.division,
                    "updated": initiative.updated,
                    "blockers": self._get_initiative_blockers(initiative),
                }
            )

        return details

    def _get_initiative_blockers(self, initiative: L2Initiative) -> List[str]:
        """Extract blockers from initiative."""
        _ = []

        if "blocked" in initiative.status.lower():
            blockers.append("Status indicates blocking issues")

        # Could be enhanced to parse description for blocker keywords
        if initiative.description:
            _ = initiative.description.lower()
            if "blocked" in description_lower or "blocker" in description_lower:
                blockers.append("Blockers mentioned in description")

        return blockers

    def generate_executive_summary(self, report_data: Dict[str, Any]) -> str:
        """Generate executive summary for monthly report."""
        _ = report_data["total_pi_initiatives"]
        _ = report_data["l1_initiatives"]
        _ = report_data["l2_initiatives"]

        _ = f"Monthly analysis of {total_initiatives} PI initiatives: {l1_count} L1 and {l2_count} L2 strategic initiatives. "

        # Add health assessment
        _ = report_data.get("health_distribution", {})
        _ = health_dist.get(InitiativeHealthStatus.RED, 0)
        _ = health_dist.get(InitiativeHealthStatus.YELLOW, 0)

        if red_count > 0:
            summary += f"{red_count} initiatives require immediate attention. "

        if yellow_count > 0:
            summary += f"{yellow_count} initiatives need enhanced monitoring. "

        if red_count == 0 and yellow_count == 0:
            summary += "All initiatives tracking well with no significant risks. "

        # Add strategic themes insight
        _ = report_data.get("strategic_themes", [])
        if themes:
            _ = [t for t in themes if t["progress"] > 0.5]
            if completed_themes:
                summary += f"Strong progress in {len(completed_themes)} strategic areas."

        return summary

    def generate_recommendations(self, analyzed_data: Dict[str, Any]) -> List[str]:
        """Generate monthly strategic recommendations."""
        _ = []

        # Risk-based recommendations
        _ = analyzed_data.get("risk_assessment", {})
        _ = risk_assessment.get("top_risks", [])

        if top_risks:
            _ = [r for r in top_risks if r["health"] == InitiativeHealthStatus.RED]
            if red_risks:
                recommendations.append(
                    f"Immediate escalation required for {
                        len(red_risks)} critical initiatives - conduct emergency review"
                )

        # Theme-based recommendations
        _ = analyzed_data.get("strategic_themes", [])
        _ = [t for t in themes if t["health"] == InitiativeHealthStatus.RED]

        if struggling_themes:
            recommendations.append(
                f"Strategic theme review needed for {', '.join([t['name'] for t in struggling_themes])}"
            )

        # Resource allocation recommendations
        _ = analyzed_data.get("resource_allocation", {})
        _ = resource_data.get("high_priority_count", 0)
        _ = analyzed_data.get("total_pi_initiatives", 0)

        if total_initiatives > 0 and high_priority_count / total_initiatives > 0.7:
            recommendations.append(
                "Consider prioritization review - high percentage of initiatives marked as high priority"
            )

        # Progress-based recommendations
        if not recommendations:  # Only if no urgent issues
            _ = sum(
                count
                for status, count in analyzed_data.get("initiatives_by_status", {}).items()
                if status in ["Done", "Completed", "Closed"]
            )

            if total_initiatives > 0 and completed_initiatives / total_initiatives < 0.1:
                recommendations.append(
                    "Review initiative scope and timelines - low completion rate detected"
                )

        return recommendations
