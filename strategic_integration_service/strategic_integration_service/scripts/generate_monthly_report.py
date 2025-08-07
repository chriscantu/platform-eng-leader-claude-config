#!/usr/bin/env python3
"""
Monthly PI Initiative Report Generation CLI

Generates comprehensive monthly reports for PI initiatives covering L1 and L2 strategic
initiatives with red/yellow/green status assessment, strategic themes analysis, and
executive risk assessment.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click
import structlog

from ..core.authentication import JiraAuthenticator
from ..core.config import Settings
from ..core.exceptions import AuthenticationError, ExtractionError
from ..generators.monthly_report import MonthlyReportGenerator

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@click.command()
@click.option(
    "-c", "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path"
)
@click.option(
    "-o", "--output-dir",
    type=click.Path(path_type=Path),
    help="Output directory for generated reports"
)
@click.option(
    "--month",
    type=click.DateTime(formats=["%Y-%m"]),
    help="Month for reporting (YYYY-MM). Defaults to current month."
)
@click.option(
    "--month-start",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Start date for reporting month (YYYY-MM-DD). Defaults to first day of month."
)
@click.option(
    "--month-end",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="End date for reporting month (YYYY-MM-DD). Defaults to last day of month."
)
@click.option(
    "--validate-only",
    is_flag=True,
    help="Only validate configuration and authentication, don't generate report"
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging"
)
def main(
    config: Optional[Path],
    output_dir: Optional[Path],
    month: Optional[datetime],
    month_start: Optional[datetime],
    month_end: Optional[datetime],
    validate_only: bool,
    debug: bool
):
    """Generate monthly PI initiative report for UI Foundation platform.

    This tool generates comprehensive monthly reports covering L1 and L2 strategic
    initiatives with:
    - Red/Yellow/Green status assessment for all PI initiatives
    - Strategic themes analysis (Platform Foundation, Quality, Design Systems)
    - Resource allocation and division distribution analysis
    - Executive risk assessment with mitigation strategies
    - Detailed initiative breakdown with priority ranking

    The report provides VP/SLT-level insights for strategic PI planning and
    resource allocation decisions across the UI Foundation organization.
    """

    # Configure logging level
    if debug:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer()
            ]
        )
        logger.info("Debug logging enabled")

    try:
        # Load configuration
        if config:
            settings = Settings.from_yaml(config)
        else:
            settings = Settings()

        # Set default month range if not provided
        if month_end is None:
            if month:
                # Use provided month
                month_start = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                # Calculate last day of month
                if month.month == 12:
                    next_month = month.replace(year=month.year + 1, month=1)
                else:
                    next_month = month.replace(month=month.month + 1)
                month_end = next_month - timedelta(days=1)
            else:
                # Use current month
                now = datetime.now()
                month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                # Calculate last day of current month
                if now.month == 12:
                    next_month = now.replace(year=now.year + 1, month=1)
                else:
                    next_month = now.replace(month=now.month + 1)
                month_end = next_month - timedelta(days=1)

        if month_start is None:
            month_start = month_end.replace(day=1)

        print("📊 UI Foundation Monthly PI Initiative Report Generator")
        print("=" * 65)
        print(f"Report Period: {month_start.strftime('%B %Y')}")
        print(f"Date Range: {month_start.strftime('%B %d')} - {month_end.strftime('%B %d, %Y')}")
        print(f"Focus: L1 & L2 Strategic Initiative Tracking")
        print()

        asyncio.run(_run_generation(settings, output_dir, month_start, month_end, validate_only))

    except KeyboardInterrupt:
        print("\n⚠️  Report generation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Report generation failed", error=str(e), exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


async def _run_generation(
    settings: Settings,
    output_dir: Optional[Path],
    month_start: datetime,
    month_end: datetime,
    validate_only: bool
):
    """Run the monthly report generation process."""

    # Validate configuration
    print("🔍 Validating configuration...")
    try:
        settings.validate_configuration()
        print("✅ Configuration validated")
    except Exception as e:
        raise ExtractionError(f"Configuration validation failed: {e}")

    # Test authentication
    print("🔐 Testing Jira authentication...")
    try:
        authenticator = JiraAuthenticator(settings)
        if authenticator.validate_credentials():
            user_info = authenticator.get_user_info()
            if user_info:
                print(f"✅ Authenticated as: {user_info['displayName']}")
            else:
                raise ExtractionError("Failed to get user information")
        else:
            raise ExtractionError("Authentication validation failed")
    except AuthenticationError as e:
        raise ExtractionError(f"Authentication failed: {e}")

    if validate_only:
        print("✅ Validation completed successfully!")
        return

    # Create report generator
    print("📈 Initializing monthly PI initiative report generator...")
    generator = MonthlyReportGenerator(settings)

    # Set output directory
    if output_dir is None:
        output_dir = settings.report_output_dir / "monthly"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate report
    print(f"\n📊 Generating monthly PI initiative report...")
    print(f"   Period: {month_start.strftime('%B %Y')}")
    print(f"   Scope: L1 & L2 Strategic Initiatives")

    try:
        report = await generator.generate(
            period_start=month_start,
            period_end=month_end,
            output_dir=output_dir
        )

        print("\n✅ Monthly PI initiative report generated successfully!")
        print("=" * 65)

        # Display report summary
        print(f"📈 Report Summary:")
        if hasattr(report.data, 'total_pi_initiatives'):
            print(f"  • Total PI Initiatives: {report.data.total_pi_initiatives}")
            print(f"  • L1 Initiatives: {report.data.l1_initiatives}")
            print(f"  • L2 Strategic Initiatives: {report.data.l2_initiatives}")

            # Health distribution
            if hasattr(report.data, 'health_distribution'):
                health_dist = report.data.health_distribution
                print(f"  • Health Status:")
                for status, count in health_dist.items():
                    emoji = "🟢" if status.value == "green" else "🟡" if status.value == "yellow" else "🔴" if status.value == "red" else "⚪"
                    print(f"    - {emoji} {status.value.title()}: {count}")

        print(f"\n📁 Report Details:")
        print(f"  • Report File: {report.get_filename()}")
        print(f"  • Output Directory: {output_dir}")
        print(f"  • Generation Date: {report.metadata.generation_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"  • Strategic Themes: {len(report.data.strategic_themes) if hasattr(report.data, 'strategic_themes') else 0}")

        # Display executive summary
        print(f"\n💼 Executive Summary:")
        print(f"  {report.executive_summary}")

        # Display recommendations
        if report.recommendations:
            print(f"\n🎯 Strategic Recommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")

        # Display risk assessment if available
        if hasattr(report.data, 'risk_assessment') and report.data.risk_assessment:
            risk_data = report.data.risk_assessment
            total_risks = risk_data.get('total_at_risk', 0)
            if total_risks > 0:
                print(f"\n⚠️  Risk Assessment:")
                print(f"  • Total At-Risk Initiatives: {total_risks}")
                print(f"  • Risk Summary: {risk_data.get('summary', 'See detailed report')}")

        print(f"\n🔧 Next Steps:")
        print(f"  1. Review strategic themes and resource allocation")
        print(f"  2. Address high-risk initiatives and implement mitigations")
        print(f"  3. Share with VP/SLT for PI planning discussions")
        print(f"  4. Track progress on L2 strategic initiatives")
        print(f"  5. Adjust priorities based on health assessment")

    except Exception as e:
        logger.error("Report generation failed", error=str(e))
        raise ExtractionError(f"Monthly report generation failed: {e}")


if __name__ == "__main__":
    main()
