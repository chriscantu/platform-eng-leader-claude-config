#!/usr/bin/env python3
"""
SuperClaude Strategic Memory Manager
Director of Engineering platform leadership memory operations
"""

import argparse
import json
import os
import sqlite3
from datetime import date, datetime
from typing import Any, Dict, List, Optional


class StrategicMemoryManager:
    """Manages strategic memory database operations for SuperClaude framework"""

    def __init__(self, db_path: str = "memory/strategic_memory.db"):
        self.db_path = db_path
        self.ensure_db_exists()

    def ensure_db_exists(self):
        """Ensure database and directory exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Check if database file exists, if not, it will be created on first connection
        if not os.path.exists(self.db_path):
            print(f"Database {self.db_path} will be created on first use")

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with JSON support"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def store_executive_session(
        self,
        session_type: str,
        stakeholder_key: str,
        meeting_date: str,
        agenda_topics: List[str] = None,
        decisions_made: Dict = None,
        action_items: List[Dict] = None,
        business_impact: str = None,
        next_session_prep: str = None,
        persona_activated: str = None,
    ) -> int:
        """Store executive session context"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO executive_sessions
                (session_type, stakeholder_key, meeting_date, agenda_topics,
                 decisions_made, action_items, business_impact, next_session_prep, persona_activated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    session_type,
                    stakeholder_key,
                    meeting_date,
                    json.dumps(agenda_topics) if agenda_topics else None,
                    json.dumps(decisions_made) if decisions_made else None,
                    json.dumps(action_items) if action_items else None,
                    business_impact,
                    next_session_prep,
                    persona_activated,
                ),
            )
            return cursor.lastrowid

    def store_strategic_initiative(
        self,
        initiative_key: str,
        initiative_name: str,
        assignee: str = None,
        status: str = "new",
        priority: str = "medium",
        business_value: str = None,
        risk_level: str = "green",
        **kwargs,
    ) -> int:
        """Store or update strategic initiative"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if initiative exists
            cursor.execute(
                "SELECT id FROM strategic_initiatives WHERE initiative_key = ?", (initiative_key,)
            )
            existing = cursor.fetchone()

            if existing:
                # Update existing
                cursor.execute(
                    """
                    UPDATE strategic_initiatives
                    SET initiative_name = ?, assignee = ?, status = ?, priority = ?,
                        business_value = ?, risk_level = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE initiative_key = ?
                """,
                    (
                        initiative_name,
                        assignee,
                        status,
                        priority,
                        business_value,
                        risk_level,
                        initiative_key,
                    ),
                )
                return existing[0]
            else:
                # Insert new
                cursor.execute(
                    """
                    INSERT INTO strategic_initiatives
                    (initiative_key, initiative_name, assignee, status, priority, business_value, risk_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        initiative_key,
                        initiative_name,
                        assignee,
                        status,
                        priority,
                        business_value,
                        risk_level,
                    ),
                )
                return cursor.lastrowid

    def store_stakeholder_profile(
        self,
        stakeholder_key: str,
        display_name: str,
        role_title: str = None,
        communication_style: str = None,
        **kwargs,
    ) -> int:
        """Store or update stakeholder profile"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM stakeholder_profiles WHERE stakeholder_key = ?", (stakeholder_key,)
            )
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    """
                    UPDATE stakeholder_profiles
                    SET display_name = ?, role_title = ?, communication_style = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE stakeholder_key = ?
                """,
                    (display_name, role_title, communication_style, stakeholder_key),
                )
                return existing[0]
            else:
                cursor.execute(
                    """
                    INSERT INTO stakeholder_profiles
                    (stakeholder_key, display_name, role_title, communication_style)
                    VALUES (?, ?, ?, ?)
                """,
                    (stakeholder_key, display_name, role_title, communication_style),
                )
                return cursor.lastrowid

    def store_platform_intelligence(
        self,
        intelligence_type: str,
        category: str,
        metric_name: str = None,
        value_numeric: float = None,
        value_text: str = None,
        data_source: str = None,
        measurement_date: str = None,
        **kwargs,
    ) -> int:
        """Store platform intelligence metric"""
        if not measurement_date:
            measurement_date = date.today().isoformat()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO platform_intelligence
                (intelligence_type, category, metric_name, value_numeric, value_text,
                 data_source, measurement_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    intelligence_type,
                    category,
                    metric_name,
                    value_numeric,
                    value_text,
                    data_source,
                    measurement_date,
                ),
            )
            return cursor.lastrowid

    def recall_executive_sessions(self, stakeholder_key: str = None, days: int = 90) -> List[Dict]:
        """Recall recent executive sessions for stakeholder preparation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT * FROM executive_sessions
                WHERE meeting_date >= date('now', '-{} days')
            """.format(
                days
            )

            if stakeholder_key:
                query += " AND stakeholder_key = ?"
                cursor.execute(query, (stakeholder_key,))
            else:
                cursor.execute(query)

            return [dict(row) for row in cursor.fetchall()]

    def recall_strategic_initiatives(self, status: str = None, assignee: str = None) -> List[Dict]:
        """Recall strategic initiatives by status or assignee"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM strategic_initiatives WHERE 1=1"
            params = []

            if status:
                query += " AND status = ?"
                params.append(status)
            if assignee:
                query += " AND assignee = ?"
                params.append(assignee)

            query += " ORDER BY updated_at DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def recall_platform_intelligence(
        self, category: str = None, intelligence_type: str = None, days: int = 90
    ) -> List[Dict]:
        """Recall platform intelligence metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT * FROM platform_intelligence
                WHERE measurement_date >= date('now', '-{} days')
            """.format(
                days
            )
            params = []

            if category:
                query += " AND category = ?"
                params.append(category)
            if intelligence_type:
                query += " AND intelligence_type = ?"
                params.append(intelligence_type)

            query += " ORDER BY measurement_date DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_database_status(self) -> Dict[str, Any]:
        """Get database status and table counts"""
        status = {
            "database_path": self.db_path,
            "database_exists": os.path.exists(self.db_path),
            "tables": {},
        }

        if not status["database_exists"]:
            return status

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get table counts
                tables = [
                    "executive_sessions",
                    "strategic_initiatives",
                    "stakeholder_profiles",
                    "platform_intelligence",
                    "budget_intelligence",
                ]

                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        status["tables"][table] = count
                    except sqlite3.OperationalError:
                        status["tables"][table] = "Table not found"

                status["status"] = "operational"
        except Exception as e:
            status["status"] = f"error: {str(e)}"

        return status

    def print_status(self):
        """Print formatted database status"""
        status = self.get_database_status()

        print("SuperClaude Strategic Memory System Status")
        print("=" * 45)
        print(f"Database: {status['database_path']}")
        print(f"Exists: {status['database_exists']}")

        if "status" in status:
            print(f"Status: {status['status']}")

        if status["tables"]:
            print("\nTable Status:")
            for table, count in status["tables"].items():
                print(f"  {table}: {count} records")

        print()


def main():
    parser = argparse.ArgumentParser(description="SuperClaude Strategic Memory Manager")
    parser.add_argument("--status", action="store_true", help="Show database status")
    parser.add_argument("--db-path", default="memory/strategic_memory.db", help="Database path")

    # Storage commands
    parser.add_argument("--store-executive", action="store_true", help="Store executive session")
    parser.add_argument(
        "--store-initiative", action="store_true", help="Store strategic initiative"
    )
    parser.add_argument(
        "--store-stakeholder", action="store_true", help="Store stakeholder profile"
    )

    # Recall commands
    parser.add_argument("--recall-sessions", action="store_true", help="Recall executive sessions")
    parser.add_argument(
        "--recall-initiatives", action="store_true", help="Recall strategic initiatives"
    )

    # Parameters
    parser.add_argument("--stakeholder", help="Stakeholder key")
    parser.add_argument("--days", type=int, default=90, help="Days to look back")
    parser.add_argument("--status-filter", help="Filter by status")
    parser.add_argument("--assignee", help="Filter by assignee")

    args = parser.parse_args()

    manager = StrategicMemoryManager(args.db_path)

    if args.status:
        manager.print_status()
    elif args.recall_sessions:
        sessions = manager.recall_executive_sessions(args.stakeholder, args.days)
        print(f"Found {len(sessions)} executive sessions:")
        for session in sessions:
            print(
                f"  {session['meeting_date']} - {session['stakeholder_key']} ({session['session_type']})"
            )
    elif args.recall_initiatives:
        initiatives = manager.recall_strategic_initiatives(args.status_filter, args.assignee)
        print(f"Found {len(initiatives)} strategic initiatives:")
        for init in initiatives:
            print(f"  {init['initiative_key']} - {init['initiative_name']} ({init['status']})")
    else:
        manager.print_status()


if __name__ == "__main__":
    main()
