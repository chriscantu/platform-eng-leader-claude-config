# ClaudeDirector Python Package

This directory contains the new Python package structure for ClaudeDirector.

## Installation

```bash
# Development installation (editable)
pip install -e .

# With optional dependencies
pip install -e ".[dev,pydantic,performance]"
```

## Usage

```python
# New package-based API
from claudedirector import ClaudeDirectorConfig, StakeholderIntelligence, TaskIntelligence

# Initialize with configuration
config = ClaudeDirectorConfig()
stakeholder_ai = StakeholderIntelligence(config)

# Detect stakeholders in content
content = "Meeting with John Smith (VP Engineering) about Q2 roadmap"
context = {"category": "meeting_prep", "meeting_type": "vp_1on1"}
stakeholders = stakeholder_ai.detect_stakeholders_in_content(content, context)
```

## Backward Compatibility

The package maintains full backward compatibility with existing scripts:

- All existing imports continue to work
- Legacy CLI (`claudedirector`) is preserved
- Database and file paths remain unchanged
- Configuration is automatically migrated

## Architecture

```
claudedirector/
├── __init__.py           # Package interface
├── cli.py               # CLI entry point  
├── core/                # Core functionality
│   ├── config.py        # Configuration management
│   ├── database.py      # Database management
│   └── exceptions.py    # Error handling
└── intelligence/        # AI modules
    ├── stakeholder.py   # Stakeholder AI
    ├── task.py         # Task detection
    └── meeting.py      # Meeting intelligence
```

## Migration Strategy

This package implements a zero-downtime migration:

1. **Phase 1**: Package structure with backward compatibility wrappers
2. **Phase 2**: Performance optimizations and parallel processing
3. **Phase 3**: Test suite and quality improvements

All existing functionality continues to work during migration.
