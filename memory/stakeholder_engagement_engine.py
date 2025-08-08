#!/usr/bin/env python3
"""
Stakeholder Engagement Management System
Intelligent recommendation engine for strategic relationship management
"""

import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import structlog

logger = structlog.get_logger()


class StakeholderEngagementEngine:
    """Intelligent stakeholder engagement management and recommendation system"""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the engagement engine"""
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Default to strategic memory database
            self.db_path = Path(__file__).parent / "strategic_memory.db"

        self.logger = logger.bind(component="stakeholder_engagement")

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def apply_engagement_schema(self):
        """Apply the stakeholder engagement schema to the database"""
        schema_path = Path(__file__).parent / "stakeholder_engagement_schema.sql"

        try:
            with open(schema_path, "r") as f:
                schema_sql = f.read()

            with self.get_connection() as conn:
                conn.executescript(schema_sql)
                self.logger.info("Stakeholder engagement schema applied successfully")
                return True

        except Exception as e:
            self.logger.error("Failed to apply engagement schema", error=str(e))
            return False

    def add_stakeholder(
        self,
        stakeholder_key: str,
        display_name: str,
        role_title: str = None,
        organization: str = None,
        strategic_importance: str = "medium",
        **kwargs,
    ) -> bool:
        """Add or update a stakeholder profile"""

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Check if stakeholder exists
                cursor.execute(
                    "SELECT id FROM stakeholder_profiles_enhanced WHERE stakeholder_key = ?",
                    (stakeholder_key,),
                )
                existing = cursor.fetchone()

                if existing:
                    # Update existing stakeholder
                    cursor.execute(
                        """
                        UPDATE stakeholder_profiles_enhanced
                        SET display_name = ?, role_title = ?, organization = ?,
                            strategic_importance = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE stakeholder_key = ?
                    """,
                        (
                            display_name,
                            role_title,
                            organization,
                            strategic_importance,
                            stakeholder_key,
                        ),
                    )

                    self.logger.info("Updated stakeholder profile", stakeholder=stakeholder_key)
                else:
                    # Insert new stakeholder
                    cursor.execute(
                        """
                        INSERT INTO stakeholder_profiles_enhanced
                        (stakeholder_key, display_name, role_title, organization, strategic_importance)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            stakeholder_key,
                            display_name,
                            role_title,
                            organization,
                            strategic_importance,
                        ),
                    )

                    self.logger.info("Created new stakeholder profile", stakeholder=stakeholder_key)

                return True

        except Exception as e:
            self.logger.error(
                "Failed to add/update stakeholder", stakeholder=stakeholder_key, error=str(e)
            )
            return False

    def record_engagement(
        self,
        stakeholder_key: str,
        engagement_type: str,
        engagement_date: str = None,
        engagement_quality: str = "good",
        topics_discussed: List[str] = None,
        action_items: List[Dict] = None,
        **kwargs,
    ) -> bool:
        """Record a stakeholder engagement"""

        if not engagement_date:
            engagement_date = datetime.now().strftime("%Y-%m-%d")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO stakeholder_engagements
                    (stakeholder_key, engagement_type, engagement_date, engagement_quality,
                     topics_discussed, action_items)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        stakeholder_key,
                        engagement_type,
                        engagement_date,
                        engagement_quality,
                        json.dumps(topics_discussed) if topics_discussed else None,
                        json.dumps(action_items) if action_items else None,
                    ),
                )

                self.logger.info(
                    "Recorded engagement",
                    stakeholder=stakeholder_key,
                    type=engagement_type,
                    quality=engagement_quality,
                )

                # Trigger recommendation update
                self._update_recommendations_for_stakeholder(stakeholder_key)

                return True

        except Exception as e:
            self.logger.error(
                "Failed to record engagement", stakeholder=stakeholder_key, error=str(e)
            )
            return False

    def generate_engagement_recommendations(self) -> List[Dict]:
        """Generate proactive engagement recommendations for all stakeholders"""

        recommendations = []

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get all stakeholders
                cursor.execute(
                    """
                    SELECT stakeholder_key, display_name, strategic_importance,
                           optimal_meeting_frequency
                    FROM stakeholder_profiles_enhanced
                """
                )

                stakeholders = cursor.fetchall()

                for stakeholder in stakeholders:
                    stakeholder_key, display_name, importance, frequency = stakeholder

                    # Generate recommendations for this stakeholder
                    stakeholder_recs = self._generate_stakeholder_recommendations(
                        stakeholder_key, importance, frequency
                    )

                    recommendations.extend(stakeholder_recs)

                # Store recommendations in database
                self._store_recommendations(recommendations)

                self.logger.info("Generated engagement recommendations", count=len(recommendations))

                return recommendations

        except Exception as e:
            self.logger.error("Failed to generate recommendations", error=str(e))
            return []

    def _generate_stakeholder_recommendations(
        self, stakeholder_key: str, importance: str, frequency: str
    ) -> List[Dict]:
        """Generate recommendations for a specific stakeholder"""

        recommendations = []

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get last engagement
                cursor.execute(
                    """
                    SELECT engagement_date, engagement_type, engagement_quality
                    FROM stakeholder_engagements
                    WHERE stakeholder_key = ?
                    ORDER BY engagement_date DESC
                    LIMIT 1
                """,
                    (stakeholder_key,),
                )

                last_engagement = cursor.fetchone()

                if not last_engagement:
                    # No previous engagement - recommend initial meeting
                    recommendations.append(
                        {
                            "stakeholder_key": stakeholder_key,
                            "recommendation_type": "initial_connection",
                            "urgency_level": "high" if importance == "critical" else "medium",
                            "trigger_reason": "No previous engagement recorded",
                            "suggested_approach": "Schedule initial strategic alignment meeting",
                            "confidence_score": 0.9,
                        }
                    )
                    return recommendations

                last_date_str = last_engagement[0]
                last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
                days_since = (datetime.now() - last_date).days

                # Determine if engagement is overdue based on frequency
                frequency_thresholds = {
                    "weekly": 10,  # Allow some buffer
                    "biweekly": 18,
                    "monthly": 35,
                    "quarterly": 100,
                    "as_needed": 180,  # Flag if no contact for 6 months
                }

                threshold = frequency_thresholds.get(frequency, 60)

                if days_since > threshold:
                    urgency = self._calculate_urgency(days_since, threshold, importance)

                    recommendations.append(
                        {
                            "stakeholder_key": stakeholder_key,
                            "recommendation_type": "overdue_check_in",
                            "urgency_level": urgency,
                            "trigger_reason": f"Last engagement {days_since} days ago (threshold: {threshold})",
                            "suggested_approach": self._suggest_engagement_approach(
                                stakeholder_key
                            ),
                            "confidence_score": min(0.9, 0.5 + (days_since / threshold) * 0.4),
                        }
                    )

                # Check for strategic opportunities
                strategic_recs = self._check_strategic_opportunities(stakeholder_key)
                recommendations.extend(strategic_recs)

                return recommendations

        except Exception as e:
            self.logger.error(
                "Failed to generate stakeholder recommendations",
                stakeholder=stakeholder_key,
                error=str(e),
            )
            return []

    def _calculate_urgency(self, days_since: int, threshold: int, importance: str) -> str:
        """Calculate urgency level based on various factors"""

        ratio = days_since / threshold

        if importance == "critical":
            if ratio > 2.0:
                return "urgent"
            elif ratio > 1.5:
                return "high"
            else:
                return "medium"
        elif importance == "high":
            if ratio > 2.5:
                return "urgent"
            elif ratio > 2.0:
                return "high"
            else:
                return "medium"
        else:
            if ratio > 3.0:
                return "high"
            elif ratio > 2.0:
                return "medium"
            else:
                return "low"

    def _suggest_engagement_approach(self, stakeholder_key: str) -> str:
        """Suggest the best engagement approach for a stakeholder"""

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get stakeholder preferences
                cursor.execute(
                    """
                    SELECT preferred_communication_channels, communication_style,
                           most_effective_personas
                    FROM stakeholder_profiles_enhanced
                    WHERE stakeholder_key = ?
                """,
                    (stakeholder_key,),
                )

                prefs = cursor.fetchone()

                if prefs:
                    channels = json.loads(prefs[0]) if prefs[0] else ["meeting"]
                    style = prefs[1] or "collaborative"
                    personas = json.loads(prefs[2]) if prefs[2] else ["diego"]

                    primary_channel = channels[0] if channels else "meeting"
                    primary_persona = personas[0] if personas else "diego"

                    return f"Reach out via {primary_channel} with {style} approach, use @{primary_persona} persona"
                else:
                    return "Schedule a brief check-in meeting to maintain relationship"

        except Exception as e:
            self.logger.error(
                "Failed to suggest engagement approach", stakeholder=stakeholder_key, error=str(e)
            )
            return "Schedule a check-in meeting"

    def _check_strategic_opportunities(self, stakeholder_key: str) -> List[Dict]:
        """Check for strategic opportunities requiring stakeholder engagement"""

        opportunities = []

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Check for projects they're interested in that might need updates
                cursor.execute(
                    """
                    SELECT project_initiative_key, interest_level, update_frequency_needed
                    FROM stakeholder_project_interests
                    WHERE stakeholder_key = ? AND active = 1
                """,
                    (stakeholder_key,),
                )

                projects = cursor.fetchall()

                for project in projects:
                    project_key, interest, frequency = project

                    if interest in ["critical", "high"] and frequency in ["weekly", "biweekly"]:
                        opportunities.append(
                            {
                                "stakeholder_key": stakeholder_key,
                                "recommendation_type": "project_update",
                                "urgency_level": "medium",
                                "trigger_reason": f"High interest in {project_key} requiring {frequency} updates",
                                "suggested_approach": f"Provide strategic update on {project_key}",
                                "strategic_context": json.dumps(
                                    {"project": project_key, "interest_level": interest}
                                ),
                                "confidence_score": 0.7,
                            }
                        )

                return opportunities

        except Exception as e:
            self.logger.error(
                "Failed to check strategic opportunities", stakeholder=stakeholder_key, error=str(e)
            )
            return []

    def _store_recommendations(self, recommendations: List[Dict]):
        """Store recommendations in the database"""

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                for rec in recommendations:
                    cursor.execute(
                        """
                        INSERT INTO engagement_recommendations
                        (stakeholder_key, recommendation_type, urgency_level,
                         trigger_reason, suggested_approach, confidence_score,
                         strategic_context, expires_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            rec["stakeholder_key"],
                            rec["recommendation_type"],
                            rec["urgency_level"],
                            rec["trigger_reason"],
                            rec["suggested_approach"],
                            rec["confidence_score"],
                            rec.get("strategic_context"),
                            (datetime.now() + timedelta(days=7)).isoformat(),  # Expire in 1 week
                        ),
                    )

                self.logger.info("Stored recommendations", count=len(recommendations))

        except Exception as e:
            self.logger.error("Failed to store recommendations", error=str(e))

    def _update_recommendations_for_stakeholder(self, stakeholder_key: str):
        """Update recommendations after a new engagement"""

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Mark overdue check-in recommendations as completed
                cursor.execute(
                    """
                    UPDATE engagement_recommendations
                    SET recommendation_status = 'completed', completed_date = CURRENT_DATE
                    WHERE stakeholder_key = ?
                    AND recommendation_type = 'overdue_check_in'
                    AND recommendation_status = 'pending'
                """,
                    (stakeholder_key,),
                )

                self.logger.info(
                    "Updated recommendations after engagement", stakeholder=stakeholder_key
                )

        except Exception as e:
            self.logger.error(
                "Failed to update recommendations", stakeholder=stakeholder_key, error=str(e)
            )

    def get_pending_recommendations(self, urgency_filter: str = None) -> List[Dict]:
        """Get pending engagement recommendations"""

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                query = """
                    SELECT r.stakeholder_key, s.display_name, r.recommendation_type,
                           r.urgency_level, r.trigger_reason, r.suggested_approach,
                           r.confidence_score, r.created_at
                    FROM engagement_recommendations r
                    JOIN stakeholder_profiles_enhanced s ON r.stakeholder_key = s.stakeholder_key
                    WHERE r.recommendation_status = 'pending'
                    AND (r.expires_at IS NULL OR r.expires_at > CURRENT_TIMESTAMP)
                """

                params = []
                if urgency_filter:
                    query += " AND r.urgency_level = ?"
                    params.append(urgency_filter)

                query += " ORDER BY r.urgency_level DESC, r.confidence_score DESC, r.created_at ASC"

                cursor.execute(query, params)
                recommendations = cursor.fetchall()

                return [
                    {
                        "stakeholder_key": row[0],
                        "display_name": row[1],
                        "recommendation_type": row[2],
                        "urgency_level": row[3],
                        "trigger_reason": row[4],
                        "suggested_approach": row[5],
                        "confidence_score": row[6],
                        "created_at": row[7],
                    }
                    for row in recommendations
                ]

        except Exception as e:
            self.logger.error("Failed to get pending recommendations", error=str(e))
            return []

    def get_stakeholder_summary(self, stakeholder_key: str) -> Dict:
        """Get comprehensive summary for a stakeholder"""

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get stakeholder profile
                cursor.execute(
                    """
                    SELECT display_name, role_title, organization, strategic_importance,
                           preferred_communication_channels, most_effective_personas
                    FROM stakeholder_profiles_enhanced
                    WHERE stakeholder_key = ?
                """,
                    (stakeholder_key,),
                )

                profile = cursor.fetchone()

                if not profile:
                    return {}

                # Get recent engagements
                cursor.execute(
                    """
                    SELECT engagement_date, engagement_type, engagement_quality,
                           topics_discussed
                    FROM stakeholder_engagements
                    WHERE stakeholder_key = ?
                    ORDER BY engagement_date DESC
                    LIMIT 5
                """,
                    (stakeholder_key,),
                )

                engagements = cursor.fetchall()

                # Get pending recommendations
                cursor.execute(
                    """
                    SELECT recommendation_type, urgency_level, trigger_reason,
                           suggested_approach
                    FROM engagement_recommendations
                    WHERE stakeholder_key = ?
                    AND recommendation_status = 'pending'
                    ORDER BY urgency_level DESC
                """,
                    (stakeholder_key,),
                )

                recommendations = cursor.fetchall()

                return {
                    "stakeholder_key": stakeholder_key,
                    "display_name": profile[0],
                    "role_title": profile[1],
                    "organization": profile[2],
                    "strategic_importance": profile[3],
                    "preferred_channels": json.loads(profile[4]) if profile[4] else [],
                    "effective_personas": json.loads(profile[5]) if profile[5] else [],
                    "recent_engagements": [
                        {
                            "date": eng[0],
                            "type": eng[1],
                            "quality": eng[2],
                            "topics": json.loads(eng[3]) if eng[3] else [],
                        }
                        for eng in engagements
                    ],
                    "pending_recommendations": [
                        {"type": rec[0], "urgency": rec[1], "reason": rec[2], "approach": rec[3]}
                        for rec in recommendations
                    ],
                }

        except Exception as e:
            self.logger.error(
                "Failed to get stakeholder summary", stakeholder=stakeholder_key, error=str(e)
            )
            return {}


def main():
    """CLI interface for stakeholder engagement management"""
    import argparse

    parser = argparse.ArgumentParser(description="Stakeholder Engagement Management System")
    parser.add_argument("--init", action="store_true", help="Initialize the engagement schema")
    parser.add_argument(
        "--generate-recommendations",
        action="store_true",
        help="Generate engagement recommendations",
    )
    parser.add_argument(
        "--show-recommendations", action="store_true", help="Show pending recommendations"
    )
    parser.add_argument(
        "--urgency", choices=["urgent", "high", "medium", "low"], help="Filter by urgency level"
    )
    parser.add_argument("--stakeholder", help="Show summary for specific stakeholder")

    args = parser.parse_args()

    engine = StakeholderEngagementEngine()

    if args.init:
        print("🔧 Initializing stakeholder engagement schema...")
        if engine.apply_engagement_schema():
            print("✅ Schema applied successfully")
        else:
            print("❌ Failed to apply schema")
            sys.exit(1)

    elif args.generate_recommendations:
        print("🧠 Generating engagement recommendations...")
        recommendations = engine.generate_engagement_recommendations()
        print(f"✅ Generated {len(recommendations)} recommendations")

    elif args.show_recommendations:
        print("📋 Pending Engagement Recommendations:")
        print("=" * 50)
        recommendations = engine.get_pending_recommendations(args.urgency)

        if not recommendations:
            print("No pending recommendations found.")
            return

        for rec in recommendations:
            urgency_emoji = {"urgent": "🔴", "high": "🟡", "medium": "🟢", "low": "🔵"}.get(
                rec["urgency_level"], "⚪"
            )

            print(f"{urgency_emoji} {rec['display_name']} ({rec['stakeholder_key']})")
            print(f"   Type: {rec['recommendation_type']}")
            print(f"   Reason: {rec['trigger_reason']}")
            print(f"   Approach: {rec['suggested_approach']}")
            print(f"   Confidence: {rec['confidence_score']:.1%}")
            print()

    elif args.stakeholder:
        print(f"📊 Stakeholder Summary: {args.stakeholder}")
        print("=" * 50)
        summary = engine.get_stakeholder_summary(args.stakeholder)

        if not summary:
            print("Stakeholder not found.")
            return

        print(f"Name: {summary['display_name']}")
        print(f"Role: {summary['role_title']}")
        print(f"Organization: {summary['organization']}")
        print(f"Strategic Importance: {summary['strategic_importance']}")
        print(f"Effective Personas: {', '.join(summary['effective_personas'])}")

        print(f"\nRecent Engagements ({len(summary['recent_engagements'])}):")
        for eng in summary["recent_engagements"]:
            print(f"  • {eng['date']} - {eng['type']} ({eng['quality']})")

        print(f"\nPending Recommendations ({len(summary['pending_recommendations'])}):")
        for rec in summary["pending_recommendations"]:
            urgency_emoji = {"urgent": "🔴", "high": "🟡", "medium": "🟢", "low": "🔵"}.get(
                rec["urgency"], "⚪"
            )
            print(f"  {urgency_emoji} {rec['type']}: {rec['reason']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
