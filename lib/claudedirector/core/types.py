"""
Type definitions and interfaces for ClaudeDirector
Provides comprehensive type safety and API contracts
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, TypedDict, Union


# Configuration Types
class ConfigProtocol(Protocol):
    """Protocol for configuration objects"""

    database_path: str
    workspace_dir: str
    stakeholder_auto_create_threshold: float
    task_auto_create_threshold: float
    cache_ttl_seconds: int
    enable_caching: bool


# Stakeholder Types
class StakeholderProfile(TypedDict, total=False):
    """Type definition for stakeholder profile data"""

    stakeholder_key: str
    display_name: str
    role_title: Optional[str]
    organization: Optional[str]
    strategic_importance: str  # 'critical', 'high', 'medium', 'low'
    optimal_meeting_frequency: str  # 'weekly', 'biweekly', 'monthly', 'quarterly'
    communication_style: Optional[str]
    last_interaction: Optional[str]


class StakeholderCandidate(TypedDict, total=False):
    """Type definition for AI-detected stakeholder candidates"""

    name: str
    stakeholder_key: str
    detected_role: str
    role_confidence: float
    strategic_importance: str
    importance_score: float
    confidence_score: float
    communication_preferences: Dict[str, Any]


class StakeholderDetectionResult(TypedDict):
    """Result of stakeholder detection processing"""

    candidates_detected: int
    auto_created: int
    profiling_needed: int
    updates_suggested: int
    actions_taken: List[Dict[str, Any]]


# Task Types
class TaskItem(TypedDict, total=False):
    """Type definition for strategic task items"""

    id: int
    task_description: str
    status: str  # 'pending', 'in_progress', 'completed', 'blocked', 'cancelled'
    priority: str  # 'critical', 'high', 'medium', 'low'
    assigned_to: Optional[str]
    assigned_by: Optional[str]
    due_date: Optional[str]
    follow_up_date: Optional[str]
    created_at: str
    updated_at: str
    source_context: Optional[str]
    strategic_category: Optional[str]
    ai_confidence: float


class TaskCandidate(TypedDict, total=False):
    """Type definition for AI-detected task candidates"""

    description: str
    assigned_to: str
    assigned_by: Optional[str]
    due_date: Optional[str]
    priority: str
    strategic_category: str
    confidence: float
    source_indicators: List[str]


class TaskDetectionResult(TypedDict):
    """Result of task detection processing"""

    tasks_detected: int
    tasks_created: int
    review_needed: int
    processing_time: float


# Meeting Types
class MeetingSession(TypedDict, total=False):
    """Type definition for meeting session data"""

    id: int
    session_type: str
    title: str
    date: str
    attendees: List[str]
    agenda_items: List[str]
    action_items: List[str]
    meeting_notes: Optional[str]
    strategic_themes: List[str]
    recommended_personas: List[str]


class MeetingMetadata(TypedDict, total=False):
    """Extracted meeting metadata"""

    title: str
    date: Optional[str]
    attendees: List[str]
    meeting_type: str
    agenda_items: List[str]
    action_items: List[str]
    strategic_context: Optional[str]


class PersonaRecommendation(TypedDict):
    """AI persona recommendation for meeting context"""

    persona: str
    confidence: float
    reason: str


# AI Detection Types
class AIDetectionContext(TypedDict, total=False):
    """Context information for AI detection"""

    file_path: str
    relative_path: str
    category: str  # 'meeting_prep', 'current_initiatives', 'strategic_docs'
    meeting_type: Optional[str]
    source_type: str


class DetectionCandidate(TypedDict, total=False):
    """Base type for AI detection candidates"""

    confidence_score: float
    detection_method: str  # 'ai_auto', 'ai_review', 'manual'
    source_indicators: List[str]
    suggested_actions: List[str]


# Performance and Caching Types
class PerformanceMetrics(TypedDict, total=False):
    """Performance measurement data"""

    processing_time: float
    files_processed: int
    items_detected: int
    cache_hits: int
    cache_misses: int
    memory_usage_mb: float
    parallel_processing_used: bool
    efficiency_gain: float


class CacheEntry(TypedDict):
    """Cache entry metadata"""

    key: str
    value: Any
    ttl: int
    created_at: datetime
    access_count: int


# Database Types
class DatabaseQuery(TypedDict, total=False):
    """Database query specification"""

    sql: str
    parameters: tuple
    fetch_one: bool
    fetch_all: bool


class DatabaseResult(TypedDict, total=False):
    """Database operation result"""

    success: bool
    data: Any
    row_count: int
    execution_time: float
    error: Optional[str]


# System Types
class SystemStats(TypedDict, total=False):
    """System health and statistics"""

    total_stakeholders: int
    total_tasks: int
    total_meetings: int
    database_size_mb: float
    cache_efficiency: float
    ai_detection_accuracy: float
    last_updated: str


class ComponentHealth(TypedDict):
    """Component health status"""

    status: str  # 'healthy', 'warning', 'error'
    last_check: datetime
    details: Dict[str, Any]
    recommendations: List[str]


# API Response Types
class APIResponse(TypedDict, total=False):
    """Standard API response format"""

    success: bool
    data: Any
    message: str
    error_code: Optional[str]
    processing_time: float
    metadata: Dict[str, Any]


# Protocol Definitions for Duck Typing
class StakeholderAIProtocol(Protocol):
    """Protocol for stakeholder AI engines"""

    def detect_stakeholders_in_content(
        self, content: str, context: AIDetectionContext
    ) -> List[StakeholderCandidate]:
        """Detect stakeholders in content"""
        ...

    def analyze_stakeholder_candidate(self, candidate: StakeholderCandidate) -> StakeholderProfile:
        """Analyze and profile stakeholder candidate"""
        ...


class TaskAIProtocol(Protocol):
    """Protocol for task AI engines"""

    def detect_tasks_in_content(
        self, content: str, context: AIDetectionContext
    ) -> List[TaskCandidate]:
        """Detect tasks in content"""
        ...

    def analyze_task_candidate(self, candidate: TaskCandidate) -> TaskItem:
        """Analyze and structure task candidate"""
        ...


class MeetingAIProtocol(Protocol):
    """Protocol for meeting AI engines"""

    def extract_meeting_metadata(self, content: str) -> MeetingMetadata:
        """Extract structured metadata from meeting content"""
        ...

    def suggest_personas(self, context: AIDetectionContext) -> List[PersonaRecommendation]:
        """Suggest optimal AI personas for meeting context"""
        ...


class DatabaseManagerProtocol(Protocol):
    """Protocol for database managers"""

    def execute_query(
        self, sql: str, parameters: tuple = (), fetch_one: bool = False, fetch_all: bool = False
    ) -> Any:
        """Execute database query"""
        ...

    def get_connection(self):
        """Get database connection context manager"""
        ...

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        ...


# Union Types for Flexibility
DetectionResult = Union[StakeholderDetectionResult, TaskDetectionResult, Dict[str, Any]]
IntelligenceCandidate = Union[StakeholderCandidate, TaskCandidate, Dict[str, Any]]
ProfileData = Union[StakeholderProfile, TaskItem, MeetingSession, Dict[str, Any]]

# Type Aliases for Clarity
FilePath = Union[str, Path]
JSONData = Dict[str, Any]
Timestamp = Union[str, datetime]
ConfidenceScore = float  # 0.0 to 1.0
Priority = str  # 'critical', 'high', 'medium', 'low'
Status = str  # Varies by context
