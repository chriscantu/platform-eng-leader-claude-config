"""
Intelligence modules for ClaudeDirector
AI-powered stakeholder detection, task extraction, and meeting intelligence
"""

from .meeting import MeetingIntelligence
from .stakeholder import StakeholderIntelligence
from .task import TaskIntelligence

__all__ = ["StakeholderIntelligence", "TaskIntelligence", "MeetingIntelligence"]
