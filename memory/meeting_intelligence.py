#!/usr/bin/env python3
"""
SuperClaude Meeting Intelligence System
Automated meeting preparation tracking and strategic memory integration
"""

import hashlib
import json
import os
import re
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class MeetingIntelligenceManager:
    """Manages meeting preparation tracking and strategic memory integration."""

    def __init__(self, db_path: str = "memory/strategic_memory.db"):
        self.db_path = db_path
        self.workspace_root = Path("workspace")
        self.meeting_prep_root = self.workspace_root / "meeting-prep"
        self.ensure_enhanced_schema()

    def ensure_enhanced_schema(self):
        """Apply enhanced schema for meeting tracking."""
        enhanced_schema_path = Path("memory/enhanced_schema.sql")
        if not enhanced_schema_path.exists():
            print("Enhanced schema not found - using basic schema")
            return

        try:
            with open(enhanced_schema_path, "r") as f:
                schema_sql = f.read()

            with sqlite3.connect(self.db_path) as conn:
                # Split and execute each statement
                statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]
                for statement in statements:
                    if statement and not statement.startswith("--"):
                        try:
                            conn.execute(statement)
                        except sqlite3.OperationalError as e:
                            if "already exists" not in str(e).lower():
                                print(f"Schema warning: {e}")

                conn.commit()
                print("✅ Enhanced meeting tracking schema applied")

        except Exception as e:
            print(f"Schema application error: {e}")

    def parse_meeting_prep_directory(self, dir_path: Path) -> Dict[str, Any]:
        """Parse a meeting prep directory and extract strategic intelligence."""
        meeting_data = {
            "meeting_key": self._generate_meeting_key(dir_path),
            "meeting_type": self._detect_meeting_type(dir_path),
            "stakeholder_primary": self._extract_primary_stakeholder(dir_path),
            "stakeholder_secondary": self._extract_secondary_stakeholders(dir_path),
            "prep_file_path": str(dir_path),
            "agenda_items": [],
            "preparation_notes": "",
            "strategic_themes": [],
            "persona_activated": self._suggest_personas(dir_path),
        }

        # Analyze content of files in the directory
        content_analysis = self._analyze_directory_content(dir_path)
        meeting_data.update(content_analysis)

        return meeting_data

    def _generate_meeting_key(self, dir_path: Path) -> str:
        """Generate unique meeting key from path and current date."""
        # Extract meaningful parts of the path
        path_parts = str(dir_path).lower().replace("workspace/meeting-prep/", "")
        path_hash = hashlib.md5(path_parts.encode()).hexdigest()[:8]
        date_str = date.today().strftime("%Y-%m-%d")

        # Create readable key
        if "raghu" in path_parts:
            return f"raghu-1on1-{date_str}"
        elif "vp" in path_parts:
            return f"vp-1on1-{date_str}"
        elif "slt" in path_parts or "leadership" in path_parts:
            return f"slt-review-{date_str}"
        else:
            return f"meeting-{path_hash}-{date_str}"

    def _detect_meeting_type(self, dir_path: Path) -> str:
        """Detect meeting type from directory path and structure."""
        path_str = str(dir_path).lower()

        if "vp" in path_str and "1on1" in path_str:
            return "vp_1on1"
        elif "reports" in path_str and "1on1" in path_str:
            return "1on1_reports"
        elif "slt" in path_str or "leadership" in path_str:
            return "slt_review"
        elif "vendor" in path_str:
            return "vendor"
        elif "cross-team" in path_str or "coordination" in path_str:
            return "cross_team"
        else:
            return "strategic_planning"

    def _extract_primary_stakeholder(self, dir_path: Path) -> Optional[str]:
        """Extract primary stakeholder from directory name and content."""
        path_str = str(dir_path).lower()

        # Common stakeholder patterns
        stakeholder_patterns = {
            r"raghu": "raghu_datta",
            r"vp[_-]?engineering": "vp_engineering",
            r"vp[_-]?product": "vp_product",
            r"vp[_-]?design": "vp_design",
            r"design[_-]?director": "design_director",
            r"platform[_-]?lead": "platform_lead",
        }

        for pattern, stakeholder_key in stakeholder_patterns.items():
            if re.search(pattern, path_str):
                return stakeholder_key

        return None

    def _extract_secondary_stakeholders(self, dir_path: Path) -> List[str]:
        """Extract additional stakeholders from content analysis."""
        # This would analyze file content for stakeholder mentions
        # For now, return empty list - can be enhanced with NLP
        return []

    def _suggest_personas(self, dir_path: Path) -> List[str]:
        """Suggest SuperClaude personas based on meeting type and context."""
        meeting_type = self._detect_meeting_type(dir_path)

        persona_mapping = {
            "vp_1on1": ["camille", "alvaro", "diego"],
            "1on1_reports": ["diego", "marcus"],
            "slt_review": ["camille", "david", "diego"],
            "vendor": ["sofia", "david", "elena"],
            "cross_team": ["diego", "marcus", "martin"],
            "strategic_planning": ["camille", "alvaro", "diego"],
        }

        return persona_mapping.get(meeting_type, ["diego"])

    def _analyze_directory_content(self, dir_path: Path) -> Dict[str, Any]:
        """Analyze content of files in directory for strategic intelligence."""
        analysis = {
            "agenda_items": [],
            "preparation_notes": "",
            "strategic_themes": [],
            "content_summary": "",
        }

        if not dir_path.exists():
            return analysis

        # Analyze markdown files for content
        md_files = list(dir_path.glob("*.md"))
        for md_file in md_files:
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract agenda items (lines starting with numbers or bullets)
                agenda_items = re.findall(r"^[\d\-\*]\s*(.+)$", content, re.MULTILINE)
                analysis["agenda_items"].extend(agenda_items[:10])  # Limit to 10 items

                # Extract strategic themes (headers and key phrases)
                themes = re.findall(r"^#+\s*(.+)$", content, re.MULTILINE)
                analysis["strategic_themes"].extend(themes[:5])  # Limit to 5 themes

                # Build preparation notes summary
                if "prep" in md_file.name.lower():
                    analysis["preparation_notes"] = (
                        content[:500] + "..." if len(content) > 500 else content
                    )

            except Exception as e:
                print(f"Error analyzing {md_file}: {e}")

        # Generate content summary
        analysis["content_summary"] = (
            f"Meeting prep with {len(md_files)} documents, "
            f"{len(analysis['agenda_items'])} agenda items, "
            f"{len(analysis['strategic_themes'])} strategic themes"
        )

        return analysis

    def store_meeting_session(self, meeting_data: Dict[str, Any]) -> int:
        """Store meeting session in strategic memory database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if meeting session already exists
            cursor.execute(
                "SELECT id FROM meeting_sessions WHERE meeting_key = ?",
                (meeting_data["meeting_key"],),
            )
            existing = cursor.fetchone()

            if existing:
                # Update existing session
                cursor.execute(
                    """
                    UPDATE meeting_sessions
                    SET meeting_type = ?, stakeholder_primary = ?, stakeholder_secondary = ?,
                        prep_file_path = ?, agenda_items = ?, preparation_notes = ?,
                        strategic_themes = ?, persona_activated = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE meeting_key = ?
                """,
                    (
                        meeting_data["meeting_type"],
                        meeting_data["stakeholder_primary"],
                        json.dumps(meeting_data["stakeholder_secondary"]),
                        meeting_data["prep_file_path"],
                        json.dumps(meeting_data["agenda_items"]),
                        meeting_data["preparation_notes"],
                        json.dumps(meeting_data["strategic_themes"]),
                        json.dumps(meeting_data["persona_activated"]),
                        meeting_data["meeting_key"],
                    ),
                )
                return existing[0]
            else:
                # Insert new session
                cursor.execute(
                    """
                    INSERT INTO meeting_sessions
                    (meeting_key, meeting_type, stakeholder_primary, stakeholder_secondary,
                     prep_file_path, agenda_items, preparation_notes, strategic_themes, persona_activated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        meeting_data["meeting_key"],
                        meeting_data["meeting_type"],
                        meeting_data["stakeholder_primary"],
                        json.dumps(meeting_data["stakeholder_secondary"]),
                        meeting_data["prep_file_path"],
                        json.dumps(meeting_data["agenda_items"]),
                        meeting_data["preparation_notes"],
                        json.dumps(meeting_data["strategic_themes"]),
                        json.dumps(meeting_data["persona_activated"]),
                    ),
                )
                return cursor.lastrowid

    def scan_and_process_meeting_prep(self) -> Dict[str, Any]:
        """Scan meeting-prep directory and process all meetings."""
        results = {"processed": 0, "new_meetings": 0, "updated_meetings": 0, "errors": []}

        if not self.meeting_prep_root.exists():
            results["errors"].append(f"Meeting prep directory not found: {self.meeting_prep_root}")
            return results

        # Process each subdirectory as a potential meeting
        for item in self.meeting_prep_root.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                try:
                    meeting_data = self.parse_meeting_prep_directory(item)

                    # Check if this is a new meeting
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT id FROM meeting_sessions WHERE meeting_key = ?",
                            (meeting_data["meeting_key"],),
                        )
                        exists = cursor.fetchone()

                    meeting_id = self.store_meeting_session(meeting_data)

                    if exists:
                        results["updated_meetings"] += 1
                    else:
                        results["new_meetings"] += 1

                    results["processed"] += 1

                    print(
                        f"✅ Processed meeting: {meeting_data['meeting_key']} "
                        f"({meeting_data['meeting_type']}) -> ID {meeting_id}"
                    )

                except Exception as e:
                    error_msg = f"Error processing {item.name}: {e}"
                    results["errors"].append(error_msg)
                    print(f"❌ {error_msg}")

        return results

    def get_meeting_intelligence_summary(self) -> Dict[str, Any]:
        """Get summary of all meeting intelligence in the system."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get meeting type distribution
            cursor.execute(
                """
                SELECT meeting_type, COUNT(*) as count
                FROM meeting_sessions
                GROUP BY meeting_type
                ORDER BY count DESC
            """
            )
            meeting_types = [dict(row) for row in cursor.fetchall()]

            # Get stakeholder meeting frequency
            cursor.execute(
                """
                SELECT stakeholder_primary, COUNT(*) as count
                FROM meeting_sessions
                WHERE stakeholder_primary IS NOT NULL
                GROUP BY stakeholder_primary
                ORDER BY count DESC
            """
            )
            stakeholder_frequency = [dict(row) for row in cursor.fetchall()]

            # Get recent meetings
            cursor.execute(
                """
                SELECT meeting_key, meeting_type, stakeholder_primary, created_at
                FROM meeting_sessions
                ORDER BY created_at DESC
                LIMIT 10
            """
            )
            recent_meetings = [dict(row) for row in cursor.fetchall()]

            return {
                "meeting_types": meeting_types,
                "stakeholder_frequency": stakeholder_frequency,
                "recent_meetings": recent_meetings,
                "total_meetings": sum(mt["count"] for mt in meeting_types),
            }


def main():
    """Main CLI interface for meeting intelligence management."""
    import argparse

    parser = argparse.ArgumentParser(description="SuperClaude Meeting Intelligence System")
    parser.add_argument(
        "--scan", action="store_true", help="Scan and process meeting-prep directory"
    )
    parser.add_argument("--summary", action="store_true", help="Show meeting intelligence summary")
    parser.add_argument("--db-path", default="memory/strategic_memory.db", help="Database path")

    args = parser.parse_args()

    manager = MeetingIntelligenceManager(args.db_path)

    if args.scan:
        print("🔍 Scanning meeting-prep directory for strategic intelligence...")
        results = manager.scan_and_process_meeting_prep()

        print(f"\n📊 Processing Results:")
        print(f"   Total processed: {results['processed']}")
        print(f"   New meetings: {results['new_meetings']}")
        print(f"   Updated meetings: {results['updated_meetings']}")

        if results["errors"]:
            print(f"   Errors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"      ❌ {error}")

    elif args.summary:
        print("📊 Meeting Intelligence Summary")
        print("=" * 40)

        summary = manager.get_meeting_intelligence_summary()

        print(f"Total meetings tracked: {summary['total_meetings']}")

        if summary["meeting_types"]:
            print(f"\nMeeting Types:")
            for mt in summary["meeting_types"]:
                print(f"   {mt['meeting_type']}: {mt['count']} meetings")

        if summary["stakeholder_frequency"]:
            print(f"\nStakeholder Frequency:")
            for sf in summary["stakeholder_frequency"]:
                print(f"   {sf['stakeholder_primary']}: {sf['count']} meetings")

        if summary["recent_meetings"]:
            print(f"\nRecent Meetings:")
            for rm in summary["recent_meetings"]:
                print(f"   {rm['meeting_key']} ({rm['meeting_type']}) - {rm['created_at']}")

    else:
        # Default: scan and show summary
        print("🔍 Scanning meeting-prep directory...")
        results = manager.scan_and_process_meeting_prep()
        print(f"Processed {results['processed']} meetings")

        print("\n📊 Current Intelligence Summary:")
        summary = manager.get_meeting_intelligence_summary()
        print(f"Total meetings: {summary['total_meetings']}")


if __name__ == "__main__":
    main()
