"""Data models for Jira initiatives and related objects."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class InitiativeStatus(str, Enum):
    """Enumeration of possible initiative statuses."""

    NEW = "New"
    COMMITTED = "Committed"
    IN_PROGRESS = "In Progress"
    AT_RISK = "At Risk"
    DONE = "Done"
    COMPLETED = "Completed"
    CLOSED = "Closed"
    CANCELED = "Canceled"
    RELEASED = "Released"


class InitiativePriority(str, Enum):
    """Enumeration of initiative priorities."""

    LOWEST = "Lowest"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    HIGHEST = "Highest"
    CRITICAL = "Critical"


class UIFoundationTeam(str, Enum):
    """UI Foundation team project mappings."""

    EXPERIENCE_SERVICES = "WES"
    GLOBALIZERS = "GLB"
    HUBS = "HUBS"
    ONBOARDING = "FSGD"
    UIF_SPECIAL_PROJECTS = "UISP"
    WEB_PLATFORM = "UIS"
    WEB_DESIGN_SYSTEMS = "UXI"
    PLATFORM_INITIATIVES = "PI"

    @property
    def team_name(self) -> str:
        """Get human-readable team name."""
        team_names = {
            "WES": "Experience Services",
            "GLB": "Globalizers",
            "HUBS": "Hubs",
            "FSGD": "Onboarding",
            "UISP": "UIF Special Projects",
            "UIS": "Web Platform",
            "UXI": "Web Design Systems",
            "PI": "Platform Initiatives",
        }
        return team_names.get(self.value, "Unknown Team")


class StrategicLabel(str, Enum):
    """Strategic initiative labels for filtering."""

    PLATFORM_FOUNDATION = "platform-foundation"
    DESIGN_SYSTEM = "design-system"
    QUALITY_MONITORING = "quality-monitoring"
    MFE_MIGRATION = "mfe-migration"
    BASELINE_STANDARDS = "baseline-standards"


class JiraUser(BaseModel):
    """Jira user information."""

    account_id: str = Field(..., description="Jira account ID")
    display_name: str = Field(..., description="User display name")
    email_address: Optional[str] = Field(None, description="User email address")
    active: bool = Field(True, description="Whether user is active")


class JiraProject(BaseModel):
    """Jira project information."""

    key: str = Field(..., description="Project key (e.g., 'PI')")
    name: str = Field(..., description="Project name")
    project_type: Optional[str] = Field(None, description="Project type")


class Initiative(BaseModel):
    """Base model for Jira initiatives."""

    key: str = Field(..., description="Jira issue key (e.g., 'PI-123')")
    summary: str = Field(..., description="Initiative summary/title")
    description: Optional[str] = Field(None, description="Initiative description")
    status: InitiativeStatus = Field(..., description="Current status")
    priority: Optional[InitiativePriority] = Field(None, description="Initiative priority")

    # People
    assignee: Optional[JiraUser] = Field(None, description="Assigned user")
    reporter: Optional[JiraUser] = Field(None, description="Reporter user")

    # Project and organization
    project: JiraProject = Field(..., description="Jira project")
    labels: List[str] = Field(default_factory=list, description="Initiative labels")
    components: List[str] = Field(default_factory=list, description="Initiative components")

    # Dates
    created: datetime = Field(..., description="Creation date")
    updated: datetime = Field(..., description="Last updated date")
    due_date: Optional[datetime] = Field(None, description="Due date")
    resolution_date: Optional[datetime] = Field(None, description="Resolution date")

    # Custom fields (stored as flexible dict)
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom field values")

    # Links and relationships
    parent_key: Optional[str] = Field(None, description="Parent issue key")
    epic_key: Optional[str] = Field(None, description="Epic issue key")

    # Raw Jira data for debugging/fallback
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw Jira response data")

    @classmethod
    def from_jira_issue(cls, jira_data: Dict[str, Any]) -> "Initiative":
        """Create Initiative from Jira API response data.

        Args:
            jira_data: Raw Jira issue data from API

        Returns:
            Initiative instance
        """
        fields = jira_data.get("fields", {})

        # Extract basic fields
        key = jira_data.get("key", "")
        summary = fields.get("summary", "")
        description = cls._extract_description(fields.get("description"))

        # Status and priority
        status_data = fields.get("status", {})
        status = InitiativeStatus(status_data.get("name", "New"))

        priority_data = fields.get("priority")
        priority = None
        if priority_data and priority_data.get("name"):
            try:
                priority = InitiativePriority(priority_data["name"])
            except ValueError:
                # Handle unknown priority values
                pass

        # Users
        assignee = None
        if fields.get("assignee"):
            assignee = JiraUser(
                account_id=fields["assignee"]["accountId"],
                display_name=fields["assignee"]["displayName"],
                email_address=fields["assignee"].get("emailAddress"),
                active=fields["assignee"].get("active", True),
            )

        reporter = None
        if fields.get("reporter"):
            reporter = JiraUser(
                account_id=fields["reporter"]["accountId"],
                display_name=fields["reporter"]["displayName"],
                email_address=fields["reporter"].get("emailAddress"),
                active=fields["reporter"].get("active", True),
            )

        # Project
        project_data = fields.get("project", {})
        project = JiraProject(
            key=project_data.get("key", ""),
            name=project_data.get("name", ""),
            project_type=project_data.get("projectTypeKey"),
        )

        # Labels and components
        labels = fields.get("labels", [])
        components = [comp["name"] for comp in fields.get("components", [])]

        # Dates
        created = datetime.fromisoformat(fields["created"].replace("Z", "+00:00"))
        updated = datetime.fromisoformat(fields["updated"].replace("Z", "+00:00"))

        due_date = None
        if fields.get("duedate"):
            due_date = datetime.fromisoformat(f"{fields['duedate']}T00:00:00+00:00")

        resolution_date = None
        if fields.get("resolutiondate"):
            resolution_date = datetime.fromisoformat(
                fields["resolutiondate"].replace("Z", "+00:00")
            )

        # Custom fields
        custom_fields = {}
        for field_key, field_value in fields.items():
            if field_key.startswith("customfield_") or field_key.startswith("cf["):
                custom_fields[field_key] = field_value

        # Parent and epic relationships
        parent_key = None
        if fields.get("parent"):
            parent_key = fields["parent"]["key"]

        epic_key = None
        # Check for epic link in various possible locations
        for epic_field in ["epic", "epicLink", "customfield_10014"]:
            if fields.get(epic_field):
                epic_data = fields[epic_field]
                if isinstance(epic_data, dict) and epic_data.get("key"):
                    epic_key = epic_data["key"]
                elif isinstance(epic_data, str):
                    epic_key = epic_data
                break

        return cls(
            key=key,
            summary=summary,
            description=description,
            status=status,
            priority=priority,
            assignee=assignee,
            reporter=reporter,
            project=project,
            labels=labels,
            components=components,
            created=created,
            updated=updated,
            due_date=due_date,
            resolution_date=resolution_date,
            custom_fields=custom_fields,
            parent_key=parent_key,
            epic_key=epic_key,
            raw_data=jira_data,
        )

    @staticmethod
    def _extract_description(description_data: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extract plain text description from Jira's Atlassian Document Format.

        Args:
            description_data: Jira description field data

        Returns:
            Plain text description or None
        """
        if not description_data:
            return None

        if isinstance(description_data, str):
            return description_data

        # Handle Atlassian Document Format (ADF)
        if isinstance(description_data, dict):
            content = description_data.get("content", [])
            if content and isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("content"):
                        for inline in block["content"]:
                            if isinstance(inline, dict) and inline.get("text"):
                                text_parts.append(inline["text"])

                if text_parts:
                    return " ".join(text_parts)

        return str(description_data) if description_data else None

    def is_active(self) -> bool:
        """Check if initiative is in an active state."""
        active_statuses = {
            InitiativeStatus.COMMITTED,
            InitiativeStatus.IN_PROGRESS,
            InitiativeStatus.AT_RISK,
        }
        return self.status in active_statuses

    def is_completed(self) -> bool:
        """Check if initiative is completed."""
        completed_statuses = {
            InitiativeStatus.DONE,
            InitiativeStatus.COMPLETED,
            InitiativeStatus.CLOSED,
            InitiativeStatus.RELEASED,
        }
        return self.status in completed_statuses

    def is_at_risk(self) -> bool:
        """Check if initiative is at risk."""
        return self.status == InitiativeStatus.AT_RISK

    def days_since_update(self) -> int:
        """Calculate days since last update."""
        now = datetime.now(self.updated.tzinfo)
        delta = now - self.updated
        return delta.days

    def get_jira_url(self, base_url: str) -> str:
        """Get the Jira URL for this initiative."""
        return f"{base_url.rstrip('/')}/browse/{self.key}"


class L2Initiative(Initiative):
    """Model for L2 (business-level) strategic initiatives."""

    division: Optional[str] = Field(None, description="Initiative division")
    initiative_type: Optional[str] = Field(None, description="Initiative type (L1, L2, etc.)")
    business_value: Optional[str] = Field(None, description="Business value description")
    strategic_priority_rank: Optional[int] = Field(None, description="Strategic priority ranking")

    @classmethod
    def from_jira_issue(cls, jira_data: Dict[str, Any]) -> "L2Initiative":
        """Create L2Initiative from Jira API response data.

        Args:
            jira_data: Raw Jira issue data from API

        Returns:
            L2Initiative instance
        """
        # First create base Initiative
        base_initiative = super().from_jira_issue(jira_data)

        # Extract L2-specific fields
        fields = jira_data.get("fields", {})
        custom_fields = base_initiative.custom_fields

        # Extract division (could be in various custom fields)
        division = None
        division_fields = ["division", "customfield_18270", "cf[18270]"]
        for field in division_fields:
            if field in fields and fields[field]:
                if isinstance(fields[field], dict):
                    division = fields[field].get("value") or fields[field].get("name")
                else:
                    division = str(fields[field])
                break

        # Extract initiative type
        initiative_type = None
        type_fields = ["type", "issuetype", "customfield_18271", "cf[18271]"]
        for field in type_fields:
            if field in fields and fields[field]:
                if isinstance(fields[field], dict):
                    initiative_type = fields[field].get("name") or fields[field].get("value")
                else:
                    initiative_type = str(fields[field])
                break

        # Extract strategic priority rank
        strategic_priority_rank = None
        priority_fields = ["customfield_18272", "cf[18272]"]
        for field in priority_fields:
            if field in custom_fields and custom_fields[field] is not None:
                try:
                    strategic_priority_rank = int(custom_fields[field])
                except (ValueError, TypeError):
                    pass
                break

        return cls(
            **base_initiative.model_dump(
                exclude={"raw_data", "division", "initiative_type", "strategic_priority_rank"}
            ),
            division=division,
            initiative_type=initiative_type,
            strategic_priority_rank=strategic_priority_rank,
            raw_data=jira_data,
        )

    def is_l2_strategic(self) -> bool:
        """Check if this is an L2 strategic initiative."""
        return (
            self.initiative_type
            and self.initiative_type.upper() == "L2"
            and self.division == "UI Foundations"
        )


class CurrentInitiative(Initiative):
    """Current initiative model for active work tracking."""

    issue_type: Optional[str] = Field(None, description="Jira issue type")
    epic_link: Optional[str] = Field(None, description="Epic link if this is a story")
    components: List[str] = Field(default_factory=list, description="Project components")
    fix_versions: List[str] = Field(default_factory=list, description="Fix versions")
    time_estimate: Optional[int] = Field(None, description="Time estimate in seconds")
    time_original_estimate: Optional[int] = Field(None, description="Original time estimate")
    resolution_date: Optional[datetime] = Field(None, description="Resolution date if completed")

    @classmethod
    def from_jira_issue(cls, jira_data: Dict[str, Any]) -> "CurrentInitiative":
        """Create CurrentInitiative from Jira API response."""
        # Start with base initiative
        base_initiative = super().from_jira_issue(jira_data)
        fields = jira_data.get("fields", {})

        # Extract additional fields specific to current initiatives
        issue_type = None
        if "issuetype" in fields and fields["issuetype"]:
            issue_type = fields["issuetype"].get("name")

        epic_link = fields.get("customfield_10014")  # Epic Link field

        # Extract components
        components = []
        if "components" in fields and fields["components"]:
            components = [comp.get("name", "") for comp in fields["components"]]

        # Extract fix versions
        fix_versions = []
        if "fixVersions" in fields and fields["fixVersions"]:
            fix_versions = [version.get("name", "") for version in fields["fixVersions"]]

        # Extract time estimates
        time_estimate = fields.get("timeestimate")
        time_original_estimate = fields.get("timeoriginalestimate")

        # Extract resolution date
        resolution_date = None
        if "resolutiondate" in fields and fields["resolutiondate"]:
            try:
                resolution_date = datetime.fromisoformat(
                    fields["resolutiondate"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        return cls(
            **base_initiative.model_dump(exclude={"raw_data"}),
            issue_type=issue_type,
            epic_link=epic_link,
            components=components,
            fix_versions=fix_versions,
            time_estimate=time_estimate,
            time_original_estimate=time_original_estimate,
            resolution_date=resolution_date,
            raw_data=jira_data,
        )

    @property
    def ui_foundation_team(self) -> Optional[UIFoundationTeam]:
        """Get UI Foundation team if this initiative belongs to one."""
        if self.project:
            try:
                return UIFoundationTeam(self.project.key)
            except ValueError:
                return None
        return None

    @property
    def team_name(self) -> str:
        """Get human-readable team name."""
        team = self.ui_foundation_team
        return (
            team.team_name
            if team
            else f"External ({self.project.key if self.project else 'Unknown'})"
        )

    def has_strategic_labels(self) -> bool:
        """Check if initiative has strategic labels."""
        if not self.labels:
            return False
        strategic_label_values = [label.value for label in StrategicLabel]
        return any(label in strategic_label_values for label in self.labels)

    def is_high_priority(self) -> bool:
        """Check if initiative is high or highest priority."""
        return self.priority in [InitiativePriority.HIGH, InitiativePriority.HIGHEST]

    def is_at_risk(self) -> bool:
        """Check if initiative appears to be at risk or blocked."""
        if not self.status:
            return False
        status_lower = self.status.lower()
        return any(keyword in status_lower for keyword in ["blocked", "risk", "impediment"])

    def is_recently_completed(self, days: int = 30) -> bool:
        """Check if initiative was completed recently."""
        if not self.resolution_date:
            return False
        now = datetime.now(self.resolution_date.tzinfo)
        days_ago = (now - self.resolution_date).days
        return days_ago <= days


class StrategicEpic(CurrentInitiative):
    """Strategic epic model for high-level platform initiatives."""

    epic_name: Optional[str] = Field(None, description="Epic name")
    epic_status: Optional[str] = Field(None, description="Epic status")
    epic_progress: Optional[float] = Field(None, description="Epic completion progress (0-1)")

    @classmethod
    def from_jira_issue(cls, jira_data: Dict[str, Any]) -> "StrategicEpic":
        """Create StrategicEpic from Jira API response."""
        # Start with current initiative
        base_initiative = super().from_jira_issue(jira_data)
        fields = jira_data.get("fields", {})

        # Extract epic-specific fields
        epic_name = fields.get("customfield_10011")  # Epic Name field
        epic_status = (
            fields.get("customfield_10010", {}).get("value")
            if fields.get("customfield_10010")
            else None
        )

        # Epic progress calculation (would need additional API call in practice)
        epic_progress = None

        return cls(
            **base_initiative.model_dump(exclude={"raw_data"}),
            epic_name=epic_name,
            epic_status=epic_status,
            epic_progress=epic_progress,
            raw_data=jira_data,
        )

    def is_platform_related(self) -> bool:
        """Check if epic is platform/foundation related."""
        if not self.labels:
            return False
        platform_keywords = ["platform", "foundation", "architecture", "mfe", "design-system"]
        return any(
            any(keyword in label.lower() for keyword in platform_keywords) for label in self.labels
        )

    def is_quality_related(self) -> bool:
        """Check if epic is quality/monitoring related."""
        if not self.labels:
            return False
        quality_keywords = ["quality", "monitoring", "slo", "observability"]
        return any(
            any(keyword in label.lower() for keyword in quality_keywords) for label in self.labels
        )
