#!/usr/bin/env python3
"""
Current Initiatives Extraction CLI

Extracts comprehensive current initiative data from UI Foundation teams for
strategic priority analysis and capacity planning.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
import structlog

from ..core.authentication import JiraAuthenticator
from ..core.config import Settings
from ..core.exceptions import AuthenticationError, ExtractionError
from ..extractors.current_initiatives import CurrentInitiativesExtractor

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
    help="Output directory for extracted data and reports",
)
@click.option(
    "--validate-only",
    is_flag=True,
    help="Only validate configuration and authentication, don't extract data",
)
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option(
    "--max-results",
    type=int,
    default=200,
    help="Maximum number of results per query (default: 200)",
)
@click.option(
    "--recent-days",
    type=int,
    default=30,
    help="Number of days back for recent completed work (default: 30)",
)
def main(
    config: Optional[Path],
    output_dir: Optional[Path],
    validate_only: bool,
    debug: bool,
    max_results: int,
    recent_days: int,
):
    """Extract current UI Foundation initiatives for strategic analysis.

    This tool extracts comprehensive initiative data from all UI Foundation teams:
    - Active initiatives across all teams (WES, GLB, HUBS, FSGD, UISP, UIS, UXI, PI)
    - Strategic epics with platform/quality focus
    - Recently completed work for context

    Generates detailed analysis reports for strategic planning and capacity management.
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

        # Override settings with command line options
        if max_results:
            settings.jira_max_results = max_results

        print("🎯 UI Foundation Current Initiatives Extractor")
        print("=" * 50)
        print("Teams: WES, GLB, HUBS, FSGD, UISP, UIS, UXI, PI")
        print(f"Max Results: {settings.jira_max_results}")
        print(f"Recent Days: {recent_days}")
        print()

        asyncio.run(_run_extraction(settings, output_dir, validate_only, recent_days))

    except KeyboardInterrupt:
        print("\n⚠️  Extraction cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Extraction failed", error=str(e), exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


async def _run_extraction(
    settings: Settings, output_dir: Optional[Path], validate_only: bool, recent_days: int
):
    """Run the current initiatives extraction process."""

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

    # Create extractor
    print("🚀 Initializing current initiatives extractor...")
    _ = CurrentInitiativesExtractor(settings)

    # Validate JQL queries
    print("🔍 Validating JQL queries...")
    _ = {
        "Active Initiatives": extractor.get_active_initiatives_jql(),
        "Strategic Epics": extractor.get_strategic_epics_jql(),
        "Recent Completed": extractor.get_recent_completed_jql(recent_days),
    }

    for query_type, jql in queries.items():
        print(f"✅ {query_type}: {jql}")

    # Run extraction
    print("\n📊 Starting data extraction...")
    try:
        _ = await extractor.run(output_dir)

        print("\n✅ Extraction completed successfully!")
        print("=" * 50)
        print("📈 Results:")
        print(f"  • Active Initiatives: {result['active_initiatives']}")
        print(f"  • Strategic Epics: {result['strategic_epics']}")
        print(f"  • Recent Completed: {result['recent_completed']}")
        print("\n📁 Output Files:")
        for file_type, file_path in result["output_files"].items():
            print(f"  • {file_type.replace('_', ' ').title()}: {file_path}")

        print("\n🔧 Next Steps:")
        print("  1. Review the analysis report for current initiative landscape")
        print("  2. Compare against strategic priority ranking")
        print("  3. Identify gaps or conflicts between current work and strategic priorities")
        print("  4. Use data for VP/SLT priority alignment discussions")

    except Exception as e:
        logger.error("Extraction failed", error=str(e))
        raise ExtractionError(f"Data extraction failed: {e}")


if __name__ == "__main__":
    main()
