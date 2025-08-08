"""
ClaudeDirector: Strategic Leadership AI Framework
Enterprise-grade package for strategic AI assistance with persistent memory and intelligent task tracking.
"""

__version__ = "1.0.0"
__author__ = "ClaudeDirector Team"

# Core functionality imports for package users
from .core.config import ClaudeDirectorConfig
from .core.database import DatabaseManager
from .intelligence.stakeholder import StakeholderIntelligence
from .intelligence.task import TaskIntelligence
from .intelligence.meeting import MeetingIntelligence

# Backward compatibility with existing scripts
def ensure_backward_compatibility():
    """Ensure existing scripts continue to work during migration"""
    import sys
    from pathlib import Path
    
    # Add legacy paths to Python path for existing imports
    project_root = Path(__file__).parent.parent.parent
    legacy_paths = [
        str(project_root / "memory"),
        str(project_root / "bin"),
        str(project_root / "scripts" / "daily"),
        str(project_root / "scripts" / "setup")
    ]
    
    for path in legacy_paths:
        if path not in sys.path:
            sys.path.insert(0, path)

# Auto-setup backward compatibility when package is imported
ensure_backward_compatibility()

__all__ = [
    "ClaudeDirectorConfig",
    "DatabaseManager", 
    "StakeholderIntelligence",
    "TaskIntelligence",
    "MeetingIntelligence",
    "__version__"
]
