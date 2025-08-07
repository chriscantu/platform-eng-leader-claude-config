"""Report data models for strategic integration service."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ReportType(str, Enum):
    """Types of reports that can be generated."""

    WEEKLY_SLT = "weekly_slt"
    MONTHLY_PI = "monthly_pi"
    QUARTERLY_REVIEW = "quarterly_review"
    STRATEGIC_ANALYSIS = "strategic_analysis"


class InitiativeHealthStatus(str, Enum):
    """Health status for initiatives in reports."""

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    UNKNOWN = "unknown"


class ReportSection(BaseModel):
    """Individual section within a report."""

    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    order: int = Field(..., description="Display order")
    template_name: Optional[str] = Field(None, description="Template name for this section")
    data: Dict[str, Any] = Field(default_factory=dict, description="Data for template rendering")


class ReportMetadata(BaseModel):
    """Metadata for generated reports."""

    report_type: ReportType = Field(..., description="Type of report")
    generation_date: datetime = Field(
        default_factory=datetime.now, description="When report was generated"
    )
    report_period_start: datetime = Field(..., description="Start of reporting period")
    report_period_end: datetime = Field(..., description="End of reporting period")
    author: str = Field(default="Strategic Integration Service", description="Report author")
    version: str = Field(default="1.0", description="Report version")
    data_sources: List[str] = Field(default_factory=list, description="Data sources used")
    total_initiatives: int = Field(default=0, description="Total initiatives analyzed")
    teams_included: List[str] = Field(default_factory=list, description="Teams included in report")


class WeeklyReportData(BaseModel):
    """Data structure for weekly SLT reports."""

    # Executive summary metrics
    total_active_initiatives: int = Field(default=0, description="Total active initiatives")
    completed_this_week: int = Field(default=0, description="Initiatives completed this week")
    at_risk_count: int = Field(default=0, description="Number of at-risk initiatives")
    high_priority_count: int = Field(default=0, description="Number of high priority initiatives")

    # Team performance
    team_summaries: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Summary by team"
    )

    # Key highlights
    major_completions: List[Dict[str, Any]] = Field(
        default_factory=list, description="Major completions this week"
    )
    escalations: List[Dict[str, Any]] = Field(
        default_factory=list, description="Items requiring escalation"
    )
    upcoming_milestones: List[Dict[str, Any]] = Field(
        default_factory=list, description="Upcoming milestones"
    )

    # Platform health indicators
    platform_health: Dict[str, InitiativeHealthStatus] = Field(
        default_factory=dict, description="Platform health by area"
    )


class MonthlyReportData(BaseModel):
    """Data structure for monthly PI initiative reports."""

    # PI-level metrics
    total_pi_initiatives: int = Field(default=0, description="Total PI initiatives")
    l1_initiatives: int = Field(default=0, description="L1 initiatives")
    l2_initiatives: int = Field(default=0, description="L2 strategic initiatives")

    # Progress tracking
    initiatives_by_status: Dict[str, int] = Field(
        default_factory=dict, description="Initiatives grouped by status"
    )
    health_distribution: Dict[InitiativeHealthStatus, int] = Field(
        default_factory=dict, description="Health status distribution"
    )

    # Strategic analysis
    strategic_themes: List[Dict[str, Any]] = Field(
        default_factory=list, description="Strategic themes analysis"
    )
    resource_allocation: Dict[str, Any] = Field(
        default_factory=dict, description="Resource allocation analysis"
    )
    risk_assessment: Dict[str, Any] = Field(
        default_factory=dict, description="Risk assessment summary"
    )

    # Detailed initiative breakdown
    initiative_details: List[Dict[str, Any]] = Field(
        default_factory=list, description="Detailed initiative information"
    )


class ReportOutput(BaseModel):
    """Generated report with all content and metadata."""

    metadata: ReportMetadata = Field(..., description="Report metadata")
    sections: List[ReportSection] = Field(..., description="Report sections")
    data: Union[WeeklyReportData, MonthlyReportData] = Field(
        ..., description="Report-specific data"
    )
    raw_markdown: str = Field(..., description="Generated markdown content")
    executive_summary: str = Field(..., description="Executive summary")
    recommendations: List[str] = Field(
        default_factory=list, description="Strategic recommendations"
    )

    def get_filename(self, extension: str = "md") -> str:
        """Generate appropriate filename for the report."""
        date_str = self.metadata.generation_date.strftime("%Y-%m-%d")
        report_type = self.metadata.report_type.value.replace("_", "-")
        return f"{report_type}-report-{date_str}.{extension}"

    def get_title(self) -> str:
        """Generate report title."""
        period_start = self.metadata.report_period_start.strftime("%B %d")
        period_end = self.metadata.report_period_end.strftime("%B %d, %Y")

        title_map = {
            ReportType.WEEKLY_SLT: f"Engineering Weekly SLT Report - {period_start} to {period_end}",
            ReportType.MONTHLY_PI: f"Engineering Monthly PI Initiative Report - {period_end}",
            ReportType.QUARTERLY_REVIEW: f"Engineering Quarterly Review - {period_end}",
            ReportType.STRATEGIC_ANALYSIS: f"Engineering Strategic Analysis - {period_end}",
        }

        return title_map.get(self.metadata.report_type, f"Engineering Report - {period_end}")


class TemplateContext(BaseModel):
    """Context data for template rendering."""

    report: ReportOutput = Field(..., description="Report data")
    metadata: ReportMetadata = Field(..., description="Report metadata")
    data: Union[WeeklyReportData, MonthlyReportData] = Field(
        ..., description="Report-specific data"
    )
    format_helpers: Dict[str, Any] = Field(
        default_factory=dict, description="Helper functions for formatting"
    )

    class Config:
        arbitrary_types_allowed = True


class ReportTemplate(BaseModel):
    """Template definition for report generation."""

    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    report_type: ReportType = Field(..., description="Compatible report type")
    template_content: str = Field(..., description="Template content (Jinja2 format)")
    required_data_fields: List[str] = Field(
        default_factory=list, description="Required data fields"
    )
    optional_data_fields: List[str] = Field(
        default_factory=list, description="Optional data fields"
    )
    output_format: str = Field(default="markdown", description="Output format")

    def validate_context(self, context: TemplateContext) -> List[str]:
        """Validate that context has required data fields."""
        missing_fields = []
        data_dict = context.data.model_dump() if hasattr(context.data, "model_dump") else {}

        for field in self.required_data_fields:
            if field not in data_dict or data_dict[field] is None:
                missing_fields.append(field)

        return missing_fields
