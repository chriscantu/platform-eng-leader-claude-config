#!/usr/bin/env python3
"""
Weekly SLT Report Generation CLI

Generates comprehensive weekly reports for Senior Leadership Team (SLT)
covering UI Foundation platform initiatives, team performance, and strategic insights.
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
from ..generators.weekly_report import WeeklyReportGenerator

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
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

_ = structlog.get_logger(__name__)


@click.command()
@click.option(
    "-c", "--config", type=click.Path(exists=True, path_type=Path), help="Configuration file path"
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    help="Output directory for generated reports",
)
@click.option(
    "--week-start",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Start date for reporting week (YYYY-MM-DD). Defaults to last Monday.",
)
@click.option(
    "--week-end",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="End date for reporting week (YYYY-MM-DD). Defaults to last Friday.",
)
@click.option(
    "--validate-only",
    is_flag=True,
    help="Only validate configuration and authentication, don't generate report",
)
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(
    config: Optional[Path],
    output_dir: Optional[Path],
    week_start: Optional[datetime],
    week_end: Optional[datetime],
    validate_only: bool,
    debug: bool,
):
    """Generate weekly SLT report for UI Foundation platform.

    This tool generates comprehensive weekly reports for the Senior Leadership Team,
    covering:
    - Active initiatives across all UI Foundation teams
    - Weekly completions and progress tracking
    - Team performance and health assessment
    - Strategic escalations and upcoming milestones
    - Platform health indicators by area

    The report provides executive-level insights for strategic decision-making
    and resource allocation across the UI Foundation organization.
    """

    # Configure logging level
    if debug:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer(),
            ]
        )
        logger.info("Debug logging enabled")

    try:
        # Load configuration
        if config:
            _ = Settings.from_yaml(config)
        else:
            _ = Settings()

        # Set default week range if not provided
        if week_end is None:
            _ = datetime.now()
        if week_start is None:
            # Default to last Monday
            _ = week_end.weekday()
            _ = week_end - timedelta(days=days_since_monday + 7)  # Previous Monday
            _ = week_start + timedelta(days=4)  # Friday of that week

        print("📊 UI Foundation Weekly SLT Report Generator")
        print("=" * 55)
        print(f"Report Period: {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}")
        print("Teams: WES, GLB, HUBS, FSGD, UISP, UIS, UXI, PI")
        print()

        asyncio.run(_run_generation(settings, output_dir, week_start, week_end, validate_only))

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
    week_start: datetime,
    week_end: datetime,
    validate_only: bool,
):
    """Run the weekly report generation process."""

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
        _ = JiraAuthenticator(settings)
        if authenticator.validate_credentials():
            _ = authenticator.get_user_info()
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
    print("📈 Initializing weekly report generator...")
    _ = WeeklyReportGenerator(settings)

    # Set output directory
    if output_dir is None:
        _ = settings.report_output_dir / "weekly"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate report
    print("\n📊 Generating weekly SLT report...")
    print(f"   Period: {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}")

    try:
        _ = await generator.generate(
            period_start=week_start, period_end=week_end, output_dir=output_dir
        )

        print("\n✅ Weekly SLT report generated successfully!")
        print("=" * 55)

        # Display report summary
        print("📈 Report Summary:")
        if hasattr(report.data, "total_active_initiatives"):
            print(f"  • Total Active Initiatives: {report.data.total_active_initiatives}")
            print(f"  • Completed This Week: {report.data.completed_this_week}")
            print(f"  • At Risk: {report.data.at_risk_count}")
            print(f"  • High Priority: {report.data.high_priority_count}")

        print("\n📁 Report Details:")
        print(f"  • Report File: {report.get_filename()}")
        print(f"  • Output Directory: {output_dir}")
        print(f"  • Generation Date: {report.metadata.generation_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"  • Teams Covered: {len(report.metadata.teams_included)}")

        # Display executive summary
        print("\n💼 Executive Summary:")
        print(f"  {report.executive_summary}")

        # Display recommendations
        if report.recommendations:
            print("\n🎯 Key Recommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")

        print("\n🔧 Next Steps:")
        print("  1. Review report for strategic insights and team performance")
        print("  2. Address escalations and at-risk initiatives")
        print("  3. Share with SLT for strategic planning discussions")
        print("  4. Follow up on upcoming milestones and resource allocation")

    except Exception as e:
        logger.error("Report generation failed", error=str(e))
        raise ExtractionError(f"Weekly report generation failed: {e}")


if __name__ == "__main__":
    main()
