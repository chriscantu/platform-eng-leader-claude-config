"""Strategic Integration Service for UI Foundation Platform Leadership.

This service provides enterprise-grade reliability for strategic data extraction
and reporting, replacing bash scripts with Python-based solutions.

Capabilities:
- L2 strategic initiative extraction from Jira
- Current initiative analysis across UI Foundation teams
- Weekly and monthly executive report generation
- Secure credential management and PII protection
"""

__version__ = "1.0.0"
__author__ = "Chris Cantu"
__email__ = "chris.cantu@procore.com"

# Re-export commonly used classes and functions
from .core.config import Settings
from .core.exceptions import (
    AuthenticationError,
    DataValidationError,
    JiraAPIError,
    StrategicIntegrationError,
)

__all__ = [
    "Settings",
    "StrategicIntegrationError",
    "JiraAPIError",
    "DataValidationError",
    "AuthenticationError",
]
