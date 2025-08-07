#!/usr/bin/env python3
"""L2 Strategic Initiative Extraction CLI - Python replacement for extract-l2-strategic-initiatives.sh.

This script provides enterprise-grade reliability for extracting L2 strategic initiatives
from Jira with comprehensive error handling and validation.
"""

import sys
from pathlib import Path
from typing import Optional

import click
import structlog

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from strategic_integration_service.core.config import Settings
from strategic_integration_service.core.exceptions import (
    AuthenticationError,
    ConfigurationError,
    StrategicIntegrationError,
)
from strategic_integration_service.extractors.l2_initiatives import L2InitiativeExtractor

# Configure structured logging
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

logger = structlog.get_logger(__name__)


@click.command()
@click.option(
    "--output-file",
    "-o",
    type=click.Path(path_type=Path),
    help="Custom output file path for the analysis report",
)
@click.option(
    "--include-l1-context/--no-l1-context",
    default=True,
    help="Include L1 initiatives for context (default: True)",
)
@click.option(
    "--config-file",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Custom configuration file path",
)
@click.option("--jira-token", help="Jira API token (overrides environment variable)")
@click.option(
    "--division",
    default="UI Foundations",
    help="Division filter for L2 initiatives (default: UI Foundations)",
)
@click.option(
    "--max-results", default=100, help="Maximum number of initiatives to extract (default: 100)"
)
@click.option(
    "--validate-only", is_flag=True, help="Only validate configuration and JQL, don't extract data"
)
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--quiet", is_flag=True, help="Suppress progress output (except errors)")
def main(
    output_file: Optional[Path],
    include_l1_context: bool,
    config_file: Optional[Path],
    jira_token: Optional[str],
    division: str,
    max_results: int,
    validate_only: bool,
    debug: bool,
    quiet: bool,
) -> None:
    """Extract L2 strategic initiatives from Jira PI project.

    This is the Python replacement for extract-l2-strategic-initiatives.sh,
    providing enterprise-grade reliability and comprehensive error handling.

    Examples:

        # Basic extraction
        sis-extract-l2

        # Custom output file
        sis-extract-l2 -o my-l2-analysis.md

        # Validate configuration only
        sis-extract-l2 --validate-only

        # Debug mode with custom division
        sis-extract-l2 --debug --division "Platform Engineering"
    """
    try:
        # Configure logging level
        if debug:
            import logging

            logging.basicConfig(level=logging.DEBUG)
        elif quiet:
            import logging

            logging.basicConfig(level=logging.ERROR)

        if not quiet:
            click.echo("🎯 UI Foundation L2 Strategic Initiatives Extractor")
            click.echo("=" * 60)
            click.echo(f"Division: {division}")
            click.echo(f"Max Results: {max_results}")
            click.echo("")

        # Load configuration
        if config_file:
            settings = Settings.load_from_file(config_file)
        else:
            settings = Settings()

        # Override settings from command line
        if jira_token:
            settings.jira_api_token = jira_token
        if division != "UI Foundations":
            settings.l2_division_filter = division

        # Validate configuration
        if not quiet:
            click.echo("🔍 Validating configuration...")

        try:
            settings.validate_configuration()
        except ConfigurationError as e:
            click.echo(f"❌ Configuration error: {e}", err=True)
            sys.exit(1)

        # Create extractor
        extractor = L2InitiativeExtractor(settings)

        # Test authentication
        if not quiet:
            click.echo("🔐 Testing Jira authentication...")

        try:
            user_info = extractor.jira_client.get_user_info()
            if not quiet:
                click.echo(f"✅ Authenticated as: {user_info['displayName']}")
        except AuthenticationError as e:
            click.echo(f"❌ Authentication failed: {e}", err=True)
            click.echo("   Please check your JIRA_API_TOKEN environment variable", err=True)
            sys.exit(1)

        # Validate JQL query
        if not quiet:
            click.echo("🔍 Validating JQL query...")

        jql = extractor.get_jql_query()
        if not extractor.validate_jql(jql):
            click.echo(f"❌ Invalid JQL query: {jql}", err=True)
            sys.exit(1)

        if not quiet:
            click.echo(f"✅ JQL validated: {jql}")

        # If validate-only mode, exit here
        if validate_only:
            click.echo("✅ Validation completed successfully!")
            return

        # Extract initiatives
        if not quiet:
            click.echo("📊 Extracting L2 strategic initiatives...")

        report_file = extractor.extract_and_save(
            output_file=output_file, include_context=include_l1_context
        )

        # Success output
        if not quiet:
            click.echo("")
            click.echo("✅ L2 Strategic Extraction Complete!")
            click.echo(f"📊 Analysis Report: {report_file}")
            click.echo(f"📁 Raw Data Directory: {report_file.parent}")
            click.echo("")
            click.echo("🔧 Next Steps:")
            click.echo("   1. Review L2 strategic initiatives to validate priority ranking")
            click.echo("   2. Map L2 initiatives to our three strategic priorities")
            click.echo("   3. Identify resource gaps or priority conflicts")
            click.echo("   4. Prepare VP/SLT briefing with L2-level strategic recommendations")
        else:
            # Minimal output for quiet mode
            click.echo(str(report_file))

    except StrategicIntegrationError as e:
        click.echo(f"❌ Strategic Integration Error: {e}", err=True)
        if hasattr(e, "details") and e.details:
            click.echo(f"   Details: {e.details}", err=True)
        sys.exit(1)

    except KeyboardInterrupt:
        click.echo("\n❌ Extraction interrupted by user", err=True)
        sys.exit(1)

    except Exception as e:
        logger.exception("Unexpected error during L2 extraction")
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)

    finally:
        # Clean up resources
        try:
            if "extractor" in locals():
                extractor.close()
        except:
            pass


if __name__ == "__main__":
    main()
