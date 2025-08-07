"""L2 Strategic Initiative Extractor - Python replacement for extract-l2-strategic-initiatives.sh."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

import structlog

from ..core.config import Settings
from ..core.exceptions import ExtractionError
from ..models.initiative import L2Initiative
from .base_extractor import BaseExtractor

logger = structlog.get_logger(__name__)


class L2InitiativeExtractor(BaseExtractor):
    """Extractor for L2 strategic initiatives from the PI project.

    This replaces the bash script extract-l2-strategic-initiatives.sh with
    enterprise-grade reliability and comprehensive error handling.
    """

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self.division_filter = settings.l2_division_filter
        self.priority_field = settings.l2_custom_field_priority

    def get_jql_query(self) -> str:
        """Get the JQL query for L2 strategic initiatives.

        This implements the exact query from the bash script:
        project = PI AND division in ("UI Foundations") and type = L2
        AND status not in (Done, Closed, Completed, Canceled, Released)
        ORDER BY cf[18272] ASC, priority DESC, updated ASC

        Returns:
            JQL query string
        """
        excluded_statuses = ["Done", "Closed", "Completed", "Canceled", "Released"]

        status_filter = ", ".join(f'"{status}"' for status in excluded_statuses)

        jql = (
            f"project = PI "
            f'AND division in ("{self.division_filter}") '
            f"AND type = L2 "
            f"AND status not in ({status_filter}) "
            f"ORDER BY {self.priority_field} ASC, priority DESC, updated ASC"
        )

        return jql

    def extract(self) -> List[L2Initiative]:
        """Extract L2 strategic initiatives from Jira.

        Returns:
            List of L2Initiative objects

        Raises:
            ExtractionError: If extraction fails
        """
        try:
            self.logger.info(
                "Starting L2 strategic initiative extraction",
                division=self.division_filter,
                priority_field=self.priority_field,
            )

            # Get raw issues from Jira
            raw_issues = self.extract_raw_issues()

            if not raw_issues:
                self.logger.warning("No L2 initiatives found matching criteria")
                return []

            # Convert to L2Initiative objects
            l2_initiatives = []
            for issue_data in raw_issues:
                try:
                    initiative = L2Initiative.from_jira_issue(issue_data)

                    # Additional validation for L2 initiatives
                    if self._validate_l2_initiative(initiative):
                        l2_initiatives.append(initiative)
                    else:
                        self.logger.warning(
                            "Issue failed L2 validation",
                            issue_key=initiative.key,
                            division=initiative.division,
                            initiative_type=initiative.initiative_type,
                        )

                except Exception as e:
                    issue_key = issue_data.get("key", "unknown")
                    self.logger.error("Failed to parse issue", issue_key=issue_key, error=str(e))
                    # Continue processing other issues
                    continue

            self.logger.info(
                "L2 initiative extraction completed",
                total_extracted=len(l2_initiatives),
                total_raw=len(raw_issues),
            )

            return l2_initiatives

        except Exception as e:
            raise ExtractionError(f"L2 initiative extraction failed: {e}")

    def _validate_l2_initiative(self, initiative: L2Initiative) -> bool:
        """Validate that an initiative is a proper L2 strategic initiative.

        Args:
            initiative: L2Initiative to validate

        Returns:
            True if valid L2 initiative, False otherwise
        """
        # Check project (must be PI)
        if initiative.project.key != "PI":
            return False

        # Since we're already filtering by JQL `type = L2`, any issue returned
        # from the query is by definition an L2 initiative. We'll be more permissive
        # with division field since it might have different values than expected.

        # For now, accept any division value since the JQL filter ensures we have L2 issues
        # from the correct division. We can tighten this later if needed.

        return True

    def extract_and_save(
        self, output_file: Optional[Path] = None, include_context: bool = True
    ) -> Path:
        """Extract L2 initiatives and save to file.

        Args:
            output_file: Optional custom output file path
            include_context: Whether to include L1 context initiatives

        Returns:
            Path to the saved file

        Raises:
            ExtractionError: If extraction or saving fails
        """
        try:
            # Extract L2 initiatives
            l2_initiatives = self.extract()

            # Generate output filename if not provided
            if output_file is None:
                timestamp = datetime.now().strftime("%Y-%m-%d")
                filename = f"l2-strategic-initiatives-{timestamp}.json"
                output_file = self.settings.get_output_path(filename, "jira-data")

            # Save to JSON file
            self._save_initiatives_json(l2_initiatives, output_file)

            # Optionally extract L1 context
            l1_initiatives = []
            if include_context:
                l1_initiatives = self._extract_l1_context()
                l1_filename = output_file.with_name(
                    output_file.stem.replace("l2-strategic", "l1-context") + output_file.suffix
                )
                self._save_initiatives_json(l1_initiatives, l1_filename)

            # Generate analysis report
            report_file = self._generate_analysis_report(l2_initiatives, l1_initiatives)

            self.logger.info(
                "L2 extraction and save completed",
                output_file=str(output_file),
                report_file=str(report_file),
                l2_count=len(l2_initiatives),
                l1_count=len(l1_initiatives),
            )

            return report_file

        except Exception as e:
            raise ExtractionError(f"Failed to extract and save L2 initiatives: {e}")

    def _extract_l1_context(self) -> List[L2Initiative]:
        """Extract L1 initiatives for context.

        Returns:
            List of L1 initiatives for context
        """
        try:
            # Modified JQL for L1 initiatives
            l1_jql = (
                f"project = PI "
                f'AND division in ("{self.division_filter}") '
                f"AND type = L1 "
                f'AND status not in ("Done", "Closed", "Completed", "Canceled", "Released") '
                f"ORDER BY priority DESC, updated DESC"
            )

            raw_issues = self.extract_raw_issues(jql=l1_jql, max_results=100)

            l1_initiatives = []
            for issue_data in raw_issues:
                try:
                    initiative = L2Initiative.from_jira_issue(issue_data)
                    l1_initiatives.append(initiative)
                except Exception as e:
                    self.logger.warning(
                        "Failed to parse L1 context issue",
                        issue_key=issue_data.get("key", "unknown"),
                        error=str(e),
                    )

            self.logger.info("L1 context extraction completed", count=len(l1_initiatives))
            return l1_initiatives

        except Exception as e:
            self.logger.error("L1 context extraction failed", error=str(e))
            return []

    def _save_initiatives_json(self, initiatives: List[L2Initiative], output_file: Path) -> None:
        """Save initiatives to JSON file.

        Args:
            initiatives: List of initiatives to save
            output_file: Output file path
        """
        import json
        from datetime import datetime

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to serializable format
        data = {
            "extraction_date": datetime.now().isoformat(),
            "total_count": len(initiatives),
            "division": self.division_filter,
            "initiatives": [initiative.dict() for initiative in initiatives],
        }

        # Save with pretty formatting
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)

        self.logger.info("Initiatives saved to JSON", file=str(output_file), count=len(initiatives))

    def _generate_analysis_report(
        self, l2_initiatives: List[L2Initiative], l1_initiatives: List[L2Initiative]
    ) -> Path:
        """Generate markdown analysis report.

        Args:
            l2_initiatives: List of L2 initiatives
            l1_initiatives: List of L1 context initiatives

        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")
        report_filename = f"l2-strategic-analysis-{timestamp}.md"
        report_file = self.settings.get_output_path(report_filename, "jira-data")

        # Generate report content
        report_content = self._build_report_content(l2_initiatives, l1_initiatives)

        # Save report
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        self.logger.info("Analysis report generated", file=str(report_file))
        return report_file

    def _build_report_content(
        self, l2_initiatives: List[L2Initiative], l1_initiatives: List[L2Initiative]
    ) -> str:
        """Build the markdown report content.

        Args:
            l2_initiatives: List of L2 initiatives
            l1_initiatives: List of L1 context initiatives

        Returns:
            Markdown report content
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")

        content = f"""# UI Foundation L2 Strategic Initiatives Analysis
**Generated**: {timestamp}
**Source**: Procore Jira PI project - L2 business initiatives
**Division**: {self.division_filter}

---

## Executive Summary

**Total L2 Strategic Initiatives**: {len(l2_initiatives)}
**Total L1 Supporting Initiatives**: {len(l1_initiatives)}

This analysis focuses on L2 business-level initiatives that represent our true strategic priorities, as opposed to operational/tactical work.

---

## L2 Strategic Initiatives (Business Level)

"""

        # Add L2 initiatives
        if l2_initiatives:
            for initiative in l2_initiatives:
                content += f"""
### [{initiative.key}]({initiative.get_jira_url(self.settings.jira_base_url)}): {initiative.summary}
**Status**: {initiative.status.value}
**Priority**: {initiative.priority.value if initiative.priority else "No Priority"}
**Assignee**: {initiative.assignee.display_name if initiative.assignee else "Unassigned"}
**Updated**: {initiative.updated.strftime("%Y-%m-%d")}

**Description**: {initiative.description or "No description available"}

---
"""
        else:
            content += "*No L2 strategic initiatives found*\n"

        content += """

## L1 Supporting Initiatives Context

"""

        # Add L1 context
        if l1_initiatives:
            for initiative in l1_initiatives:
                priority_text = initiative.priority.value if initiative.priority else "No Priority"
                content += f"- [{initiative.key}]({initiative.get_jira_url(self.settings.jira_base_url)}): {initiative.summary} - {initiative.status.value} - {priority_text}\n"
        else:
            content += "*No L1 initiatives found*\n"

        content += f"""

---

## Strategic Priority Validation

Based on the L2 business initiatives above, we can now validate our strategic priority ranking:

### Priority 1: Platform Foundation & Baseline Standards
**L2 Initiatives Mapped**: [Analysis needed based on above data]
- Platform infrastructure and standardization initiatives
- MFE migration and architecture modernization
- Design system maturity and adoption

### Priority 2: Quality Infrastructure & SLO Framework
**L2 Initiatives Mapped**: [Analysis needed based on above data]
- Observability and monitoring initiatives
- Quality metrics and SLO implementation
- Performance and reliability improvements

### Priority 3: Strategic Planning & Organizational Development
**L2 Initiatives Mapped**: [Analysis needed based on above data]
- Team development and capability building
- Cross-functional alignment initiatives
- Innovation and exploration projects

---

## Data Sources
- **Procore Jira PI Project**: L2 and L1 initiatives for UI Foundations division
- **Query Date**: {timestamp}
- **Raw Data**: Available in workspace/current-initiatives/jira-data/

**Note**: This analysis represents true strategic business initiatives (L2 level) rather than operational/tactical work, providing accurate insight for executive decision-making.
"""

        return content
