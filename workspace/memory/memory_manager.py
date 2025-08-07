#!/usr/bin/env python3
"""
SuperClaude Strategic Memory Manager
Director of Engineering: Cross-session strategic context persistence

This module provides persistent memory capabilities for strategic leadership,
VP/SLT preparation, initiative tracking, and organizational intelligence.
"""

import json
import logging
import os
import sqlite3
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExecutiveSession:
    """Executive meeting session data model"""

    session_type: str
    stakeholder_key: str
    meeting_date: str
    agenda_topics: List[str]
    decisions_made: List[Dict[str, Any]]
    action_items: List[Dict[str, Any]]
    business_impact: str
    next_session_prep: str
    persona_activated: str
    outcome_rating: int = 3
    follow_up_required: bool = True


@dataclass
class StrategicInitiative:
    """Strategic initiative tracking data model"""

    initiative_key: str
    initiative_name: str
    assignee: str
    status: str
    priority: str
    business_value: str
    risk_level: str = "green"
    parent_initiative: Optional[str] = None
    resource_allocation: List[Dict[str, Any]] = None
    completion_probability: float = 0.5
    budget_impact: Optional[float] = None


@dataclass
class StakeholderProfile:
    """Stakeholder relationship intelligence data model"""

    stakeholder_key: str
    display_name: str
    role_title: str
    department: str
    communication_style: str
    decision_criteria: List[str]
    preferred_personas: List[str]
    relationship_strength: int = 3


@dataclass
class PlatformIntelligence:
    """Platform metrics and operational intelligence"""

    intelligence_type: str
    category: str
    metric_name: str
    data_source: str
    measurement_date: str
    trend_direction: str = "stable"
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    unit: Optional[str] = None
    business_impact: Optional[str] = None
    confidence_level: str = "medium"


class SuperClaudeMemoryManager:
    """Strategic memory manager for Director-level context persistence"""

    def __init__(self, db_path: str = None):
        """Initialize memory manager with SQLite database"""
        if db_path is None:
            # Default to SuperClaude memory directory
            memory_dir = Path.home() / ".superclaude" / "memory"
            memory_dir.mkdir(parents=True, exist_ok=True)
            db_path = memory_dir / "strategic_memory.db"

        self.db_path = str(db_path)
        self.conn = None
        self._initialize_database()

    def _initialize_database(self):
        """Initialize SQLite database with schema"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        # Load and execute schema if database is empty
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            # Check if database is already initialized
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_metadata'"
            )

            if not cursor.fetchone():
                logger.info("Initializing SuperClaude Strategic Memory database")
                with open(schema_path, "r") as f:
                    schema_sql = f.read()
                self.conn.executescript(schema_sql)
                self.conn.commit()
                logger.info(f"Database initialized at: {self.db_path}")
            else:
                logger.info(f"Using existing database at: {self.db_path}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    # ==========================================
    # Executive Session Management
    # ==========================================

    def store_executive_session(self, session: ExecutiveSession) -> int:
        """Store executive meeting session with outcomes"""
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO executive_sessions (
                session_type, stakeholder_key, meeting_date, agenda_topics,
                decisions_made, action_items, business_impact, next_session_prep,
                persona_activated, outcome_rating, follow_up_required
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                session.session_type,
                session.stakeholder_key,
                session.meeting_date,
                json.dumps(session.agenda_topics),
                json.dumps(session.decisions_made),
                json.dumps(session.action_items),
                session.business_impact,
                session.next_session_prep,
                session.persona_activated,
                session.outcome_rating,
                session.follow_up_required,
            ),
        )

        self.conn.commit()
        session_id = cursor.lastrowid
        logger.info(f"Stored executive session: {session.stakeholder_key} ({session_id})")
        return session_id

    def get_stakeholder_context(self, stakeholder_key: str, days: int = 90) -> Dict[str, Any]:
        """Retrieve strategic context for stakeholder interactions"""
        cursor = self.conn.cursor()

        # Get recent sessions
        cursor.execute(
            """
            SELECT * FROM executive_sessions
            WHERE stakeholder_key = ? AND meeting_date >= date('now', '-{} days')
            ORDER BY meeting_date DESC
        """.format(
                days
            ),
            (stakeholder_key,),
        )

        sessions = []
        for row in cursor.fetchall():
            sessions.append(
                {
                    "meeting_date": row["meeting_date"],
                    "session_type": row["session_type"],
                    "agenda_topics": json.loads(row["agenda_topics"])
                    if row["agenda_topics"]
                    else [],
                    "decisions_made": json.loads(row["decisions_made"])
                    if row["decisions_made"]
                    else [],
                    "action_items": json.loads(row["action_items"]) if row["action_items"] else [],
                    "business_impact": row["business_impact"],
                    "outcome_rating": row["outcome_rating"],
                    "persona_activated": row["persona_activated"],
                }
            )

        # Get stakeholder profile
        cursor.execute(
            "SELECT * FROM stakeholder_profiles WHERE stakeholder_key = ?", (stakeholder_key,)
        )
        profile_row = cursor.fetchone()

        profile = None
        if profile_row:
            profile = {
                "display_name": profile_row["display_name"],
                "role_title": profile_row["role_title"],
                "communication_style": profile_row["communication_style"],
                "preferred_personas": json.loads(profile_row["preferred_personas"])
                if profile_row["preferred_personas"]
                else [],
                "relationship_strength": profile_row["relationship_strength"],
            }

        return {
            "stakeholder_key": stakeholder_key,
            "profile": profile,
            "recent_sessions": sessions,
            "session_count": len(sessions),
        }

    # ==========================================
    # Strategic Initiative Tracking
    # ==========================================

    def store_initiative(self, initiative: StrategicInitiative) -> None:
        """Store or update strategic initiative"""
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO strategic_initiatives (
                initiative_key, initiative_name, parent_initiative, assignee,
                status, priority, business_value, risk_level, resource_allocation,
                completion_probability, budget_impact
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                initiative.initiative_key,
                initiative.initiative_name,
                initiative.parent_initiative,
                initiative.assignee,
                initiative.status,
                initiative.priority,
                initiative.business_value,
                initiative.risk_level,
                json.dumps(initiative.resource_allocation)
                if initiative.resource_allocation
                else None,
                initiative.completion_probability,
                initiative.budget_impact,
            ),
        )

        self.conn.commit()
        logger.info(f"Stored initiative: {initiative.initiative_key}")

    def get_initiatives_by_status(
        self, status: str = None, assignee: str = None
    ) -> List[Dict[str, Any]]:
        """Get initiatives filtered by status and/or assignee"""
        cursor = self.conn.cursor()

        query = "SELECT * FROM active_initiatives_dashboard"
        params = []
        conditions = []

        if status:
            conditions.append("status = ?")
            params.append(status)

        if assignee:
            conditions.append("assignee = ?")
            params.append(assignee)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)

        initiatives = []
        for row in cursor.fetchall():
            initiatives.append(dict(row))

        return initiatives

    def get_initiative_context(self, initiative_key: str) -> Dict[str, Any]:
        """Get comprehensive context for specific initiative"""
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT * FROM strategic_initiatives WHERE initiative_key = ?", (initiative_key,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        initiative = dict(row)
        if initiative["resource_allocation"]:
            initiative["resource_allocation"] = json.loads(initiative["resource_allocation"])

        return initiative

    # ==========================================
    # Platform Intelligence Management
    # ==========================================

    def store_platform_metric(self, intelligence: PlatformIntelligence) -> None:
        """Store platform metric or intelligence data"""
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO platform_intelligence (
                intelligence_type, category, metric_name, value_numeric,
                value_text, unit, data_source, measurement_date,
                trend_direction, business_impact, confidence_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                intelligence.intelligence_type,
                intelligence.category,
                intelligence.metric_name,
                intelligence.value_numeric,
                intelligence.value_text,
                intelligence.unit,
                intelligence.data_source,
                intelligence.measurement_date,
                intelligence.trend_direction,
                intelligence.business_impact,
                intelligence.confidence_level,
            ),
        )

        self.conn.commit()
        logger.info(f"Stored platform metric: {intelligence.category}/{intelligence.metric_name}")

    def get_platform_trends(self, category: str = None, days: int = 90) -> List[Dict[str, Any]]:
        """Get platform metrics trending over specified time period"""
        cursor = self.conn.cursor()

        query = """
            SELECT * FROM platform_metrics_trending
            WHERE measurement_date >= date('now', '-{} days')
        """.format(
            days
        )

        params = []
        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY category, metric_name, measurement_date DESC"

        cursor.execute(query, params)

        metrics = []
        for row in cursor.fetchall():
            metrics.append(dict(row))

        return metrics

    # ==========================================
    # Memory Query Interface
    # ==========================================

    def memory_recall(self, memory_type: str, **filters) -> Dict[str, Any]:
        """Unified memory recall interface for strategic context"""

        if memory_type == "executive_session":
            stakeholder = filters.get("stakeholder")
            days = filters.get("days", 90)
            if stakeholder:
                return self.get_stakeholder_context(stakeholder, days)

        elif memory_type == "strategic_initiative":
            status = filters.get("status")
            assignee = filters.get("assignee")
            initiative_key = filters.get("key")

            if initiative_key:
                return self.get_initiative_context(initiative_key)
            else:
                return {"initiatives": self.get_initiatives_by_status(status, assignee)}

        elif memory_type == "platform_intelligence":
            category = filters.get("category")
            days = filters.get("days", 90)
            return {"metrics": self.get_platform_trends(category, days)}

        return {"error": f"Unknown memory type: {memory_type}"}

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory database statistics"""
        cursor = self.conn.cursor()

        stats = {}

        # Count records in each table
        tables = [
            "executive_sessions",
            "strategic_initiatives",
            "stakeholder_profiles",
            "platform_intelligence",
            "budget_intelligence",
            "strategic_decisions",
        ]

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            stats[table] = cursor.fetchone()["count"]

        # Get recent activity
        cursor.execute(
            """
            SELECT COUNT(*) as recent_sessions FROM executive_sessions
            WHERE created_at >= date('now', '-7 days')
        """
        )
        stats["recent_sessions"] = cursor.fetchone()["recent_sessions"]

        cursor.execute(
            """
            SELECT COUNT(*) as active_initiatives FROM strategic_initiatives
            WHERE status IN ('in_progress', 'at_risk', 'committed')
        """
        )
        stats["active_initiatives"] = cursor.fetchone()["active_initiatives"]

        return stats

    def cleanup_memory(self, days: int = 365) -> Dict[str, int]:
        """Clean up old memory records beyond retention period"""
        cursor = self.conn.cursor()

        cleanup_stats = {}

        # Clean up old platform intelligence (keep recent trends)
        cursor.execute(
            """
            DELETE FROM platform_intelligence
            WHERE measurement_date < date('now', '-{} days')
        """.format(
                days
            )
        )
        cleanup_stats["platform_intelligence"] = cursor.rowcount

        # Clean up old executive sessions (but keep important ones)
        cursor.execute(
            """
            DELETE FROM executive_sessions
            WHERE meeting_date < date('now', '-{} days') AND outcome_rating < 4
        """.format(
                days
            )
        )
        cleanup_stats["executive_sessions"] = cursor.rowcount

        self.conn.commit()
        logger.info(f"Memory cleanup completed: {cleanup_stats}")

        return cleanup_stats


# ==========================================
# CLI Interface for Memory Management
# ==========================================


def main():
    """Command-line interface for memory operations"""
    import argparse

    parser = argparse.ArgumentParser(description="SuperClaude Strategic Memory Manager")
    parser.add_argument(
        "action", choices=["stats", "recall", "cleanup", "test"], help="Memory operation to perform"
    )
    parser.add_argument("--type", help="Memory type for recall")
    parser.add_argument("--stakeholder", help="Stakeholder key for executive sessions")
    parser.add_argument("--days", type=int, default=90, help="Time range in days")
    parser.add_argument("--db-path", help="Custom database path")

    args = parser.parse_args()

    with SuperClaudeMemoryManager(args.db_path) as memory:
        if args.action == "stats":
            stats = memory.get_memory_stats()
            print("SuperClaude Strategic Memory Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")

        elif args.action == "recall" and args.type:
            filters = {}
            if args.stakeholder:
                filters["stakeholder"] = args.stakeholder
            if args.days:
                filters["days"] = args.days

            context = memory.memory_recall(args.type, **filters)
            print(json.dumps(context, indent=2, default=str))

        elif args.action == "cleanup":
            cleanup_stats = memory.cleanup_memory(args.days)
            print(f"Memory cleanup completed: {cleanup_stats}")

        elif args.action == "test":
            # Test basic functionality
            print("Testing SuperClaude Memory System...")

            # Test stakeholder profile
            test_profile = StakeholderProfile(
                stakeholder_key="test_vp",
                display_name="Test VP",
                role_title="Test Vice President",
                department="Test",
                communication_style="data_driven",
                decision_criteria=["ROI", "Risk"],
                preferred_personas=["camille", "alvaro"],
            )

            cursor = memory.conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO stakeholder_profiles
                (stakeholder_key, display_name, role_title, department, communication_style,
                 decision_criteria, preferred_personas)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    test_profile.stakeholder_key,
                    test_profile.display_name,
                    test_profile.role_title,
                    test_profile.department,
                    test_profile.communication_style,
                    json.dumps(test_profile.decision_criteria),
                    json.dumps(test_profile.preferred_personas),
                ),
            )
            memory.conn.commit()

            print("✅ Memory system test completed successfully")


if __name__ == "__main__":
    main()
