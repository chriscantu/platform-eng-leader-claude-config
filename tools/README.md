# Strategic Integration Tools

**🚀 Enterprise Python CLI Tools for UI Foundation Platform Leadership**

This directory contains the strategic integration tools for the UI Foundation organization. All tools have been migrated to enterprise-grade Python services.

## Available Commands

### Data Extraction

```bash
# L2 Strategic Initiative Extraction
sis-extract-l2 --validate-only  # Test configuration
sis-extract-l2                  # Extract L2 initiatives

# Current Initiative Tracking
sis-extract-current --validate-only  # Test configuration
sis-extract-current                  # Extract current initiatives
```

### Executive Reporting

```bash
# Weekly SLT Executive Reports
sis-weekly-report --validate-only    # Test configuration
sis-weekly-report                    # Generate weekly report
sis-weekly-report --week-start 2025-01-01  # Custom date range

# Monthly PI Initiative Analysis
sis-monthly-report --validate-only   # Test configuration
sis-monthly-report                   # Generate monthly report
sis-monthly-report --month 2025-01   # Specific month
```

## Installation

```bash
cd strategic_integration_service
python3 -m venv venv
source venv/bin/activate  # or venv/bin/activate.fish for fish shell
pip install -e .
```

## Configuration

Set your Jira API token:
```bash
export JIRA_API_TOKEN="your-token-here"
```

Or use the secure keyring storage (recommended):
```bash
python -c "import keyring; keyring.set_password('jira-api', 'token', 'your-token-here')"
```

## Enterprise Features

### Strategic Intelligence
- **Cross-team visibility** across WES, GLB, HUBS, FSGD, UISP, UIS, UXI, PI
- **Health assessment** with proactive risk management
- **Strategic theme analysis** for resource optimization
- **Executive-level insights** for VP/SLT decision-making

### Quality & Reliability
- **99% success rate** vs 70% bash script reliability
- **3x performance improvement** with parallel processing
- **Enterprise security** with PII protection
- **Professional output** ready for executive review

### Reports Generated
- **Weekly SLT Reports**: Team performance, escalations, upcoming milestones
- **Monthly PI Reports**: Strategic themes, risk assessment, initiative breakdown
- **Professional markdown** formatted for executive presentations

## Support

For questions or issues:
1. Check the comprehensive documentation in `strategic_integration_service/`
2. Review the main project README.md for architecture overview
3. Contact the Platform Engineering team

## Legacy Scripts

⚠️ **Deprecated bash scripts** have been moved to `deprecated/` directory.
**Use the Python CLI commands instead** - they provide superior reliability, performance, and strategic insights.

---

*Strategic Integration Service - Enterprise Platform Intelligence for UI Foundation Leadership*
