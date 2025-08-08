"""
Intelligence modules for ClaudeDirector
AI-powered stakeholder detection, task extraction, and meeting intelligence
"""

from .stakeholder import StakeholderIntelligence
from .task import TaskIntelligence  
from .meeting import MeetingIntelligence

__all__ = [
    "StakeholderIntelligence",
    "TaskIntelligence", 
    "MeetingIntelligence"
]
