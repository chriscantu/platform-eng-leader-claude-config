#!/usr/bin/env python3
"""
SuperClaude Workspace Monitor
Automated filesystem monitoring for strategic intelligence capture
"""

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from memory.meeting_intelligence import MeetingIntelligenceManager

# Import stakeholder detection if available
try:
    from memory.intelligent_stakeholder_detector import IntelligentStakeholderDetector
    STAKEHOLDER_DETECTION_AVAILABLE = True
except ImportError:
    STAKEHOLDER_DETECTION_AVAILABLE = False


class StrategicWorkspaceHandler(FileSystemEventHandler):
    """Handle workspace filesystem events for strategic intelligence capture."""

    def __init__(self, db_path: str = "memory/strategic_memory.db"):
        self.db_path = db_path
        self.meeting_manager = MeetingIntelligenceManager(db_path)
        
        # Initialize stakeholder detection if available
        if STAKEHOLDER_DETECTION_AVAILABLE:
            self.stakeholder_detector = IntelligentStakeholderDetector(db_path)
        else:
            self.stakeholder_detector = None
            
        self.workspace_root = Path("workspace")

    def on_created(self, event):
        """Handle file/directory creation events."""
        if event.is_directory:
            self._handle_directory_created(event.src_path)
        else:
            self._handle_file_created(event.src_path)

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            self._handle_file_modified(event.src_path)

    def _handle_directory_created(self, path: str):
        """Process new directory creation for strategic intelligence."""
        dir_path = Path(path)
        relative_path = self._get_relative_path(dir_path)

        print(f"📁 New directory detected: {relative_path}")

        # Categorize the directory
        category, subcategory = self._categorize_path(relative_path)

        # Extract intelligence from path
        intelligence = self._extract_path_intelligence(dir_path)

        # Store workspace change
        change_id = self._store_workspace_change(
            change_type="directory_created",
            path_full=str(dir_path),
            path_relative=relative_path,
            category=category,
            subcategory=subcategory,
            **intelligence,
        )

        print(f"✅ Workspace change stored: ID {change_id}")

        # Handle special cases
        if category == "meeting_prep":
            self._handle_meeting_prep_directory(dir_path)
        elif category == "current_initiatives":
            self._handle_initiative_directory(dir_path)

        # Apply automatic templates if applicable
        self._apply_directory_templates(dir_path, category, subcategory)

    def _handle_file_created(self, path: str):
        """Process new file creation for strategic intelligence."""
        file_path = Path(path)
        relative_path = self._get_relative_path(file_path)

        # Skip temporary files and hidden files
        if file_path.name.startswith(".") or file_path.name.endswith(".tmp"):
            return

        print(f"📄 New file detected: {relative_path}")

        category, subcategory = self._categorize_path(relative_path)
        intelligence = self._extract_file_intelligence(file_path)

        change_id = self._store_workspace_change(
            change_type="file_created",
            path_full=str(file_path),
            path_relative=relative_path,
            category=category,
            subcategory=subcategory,
            **intelligence,
        )

        # Trigger strategic memory updates if applicable
        if intelligence.get("memory_trigger"):
            self._trigger_memory_update(file_path, category, subcategory)

    def _handle_file_modified(self, path: str):
        """Process file modifications for strategic intelligence."""
        file_path = Path(path)
        relative_path = self._get_relative_path(file_path)

        # Only process certain file types
        if not file_path.suffix.lower() in [".md", ".txt", ".json", ".yaml", ".yml"]:
            return

        category, subcategory = self._categorize_path(relative_path)

        # Check if this modification should trigger memory updates
        if category in ["meeting_prep", "current_initiatives", "strategic_docs"]:
            print(f"📝 Strategic file modified: {relative_path}")
            self._trigger_memory_update(file_path, category, subcategory)

    def _get_relative_path(self, path: Path) -> str:
        """Get path relative to workspace root."""
        try:
            return str(path.relative_to(self.workspace_root))
        except ValueError:
            return str(path)

    def _categorize_path(self, relative_path: str) -> tuple[str, str]:
        """Categorize workspace path for strategic intelligence."""
        path_lower = relative_path.lower()

        if "meeting-prep" in path_lower or "meeting_prep" in path_lower:
            if "vp" in path_lower:
                return "meeting_prep", "vp_1on1s"
            elif "1on1" in path_lower or "reports" in path_lower:
                return "meeting_prep", "reports_1on1s"
            elif "slt" in path_lower or "leadership" in path_lower:
                return "meeting_prep", "slt_reviews"
            else:
                return "meeting_prep", "general"

        elif "current-initiatives" in path_lower:
            if "design-system" in path_lower:
                return "current_initiatives", "design_system"
            elif "platform" in path_lower:
                return "current_initiatives", "platform_modernization"
            elif "quality" in path_lower:
                return "current_initiatives", "quality_infrastructure"
            else:
                return "current_initiatives", "general"

        elif "strategic-docs" in path_lower:
            return "strategic_docs", "planning"

        elif "reference-materials" in path_lower:
            return "reference_materials", "knowledge_base"

        else:
            return "workspace", "general"

    def _extract_path_intelligence(self, path: Path) -> Dict[str, Any]:
        """Extract strategic intelligence from path structure."""
        intelligence = {
            "stakeholders_detected": [],
            "projects_detected": [],
            "meeting_type_detected": None,
            "content_summary": "",
            "strategic_value": "medium",
            "memory_trigger": False,
        }

        path_str = str(path).lower()

        # Detect stakeholders
        stakeholder_patterns = {
            r"raghu": "raghu_datta",
            r"vp": "vp_engineering",
            r"design": "design_director",
            r"platform": "platform_lead",
        }

        for pattern, stakeholder in stakeholder_patterns.items():
            if pattern in path_str:
                intelligence["stakeholders_detected"].append(stakeholder)

        # Detect meeting types
        if "1on1" in path_str:
            if "vp" in path_str:
                intelligence["meeting_type_detected"] = "vp_1on1"
                intelligence["strategic_value"] = "high"
                intelligence["memory_trigger"] = True
            else:
                intelligence["meeting_type_detected"] = "1on1_reports"
                intelligence["memory_trigger"] = True

        # Detect project/initiative references
        project_patterns = [
            r"design-system",
            r"platform",
            r"quality",
            r"infrastructure",
            r"pi-\d+",
            r"strategic",
            r"modernization",
        ]

        for pattern in project_patterns:
            if pattern in path_str:
                intelligence["projects_detected"].append(pattern)

        return intelligence

    def _extract_file_intelligence(self, file_path: Path) -> Dict[str, Any]:
        """Extract strategic intelligence from file content."""
        intelligence = {
            "stakeholders_detected": [],
            "projects_detected": [],
            "content_summary": "",
            "strategic_value": "medium",
            "memory_trigger": False,
        }

        try:
            # Read file content for analysis
            if file_path.suffix.lower() in [".md", ".txt"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()[:1000]  # First 1000 chars

                intelligence["content_summary"] = (
                    f"File: {file_path.name}, " f"Size: {len(content)} chars"
                )

                # Set memory trigger for strategic content
                strategic_keywords = ["strategic", "vp", "slt", "initiative", "roadmap", "1on1"]
                if any(keyword in content.lower() for keyword in strategic_keywords):
                    intelligence["memory_trigger"] = True
                    intelligence["strategic_value"] = "high"

        except Exception as e:
            intelligence["content_summary"] = f"Error reading file: {e}"

        return intelligence

    def _store_workspace_change(self, **kwargs) -> int:
        """Store workspace change in strategic memory database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Ensure workspace_changes table exists (handle gracefully if not)
            try:
                cursor.execute(
                    """
                    INSERT INTO workspace_changes
                    (change_type, path_full, path_relative, category, subcategory,
                     stakeholders_detected, projects_detected, meeting_type_detected,
                     content_summary, strategic_value, memory_trigger)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        kwargs["change_type"],
                        kwargs["path_full"],
                        kwargs["path_relative"],
                        kwargs["category"],
                        kwargs["subcategory"],
                        json.dumps(kwargs.get("stakeholders_detected", [])),
                        json.dumps(kwargs.get("projects_detected", [])),
                        kwargs.get("meeting_type_detected"),
                        kwargs.get("content_summary", ""),
                        kwargs.get("strategic_value", "medium"),
                        kwargs.get("memory_trigger", False),
                    ),
                )
                return cursor.lastrowid
            except sqlite3.OperationalError:
                # Table doesn't exist yet - return 0
                return 0

    def _handle_meeting_prep_directory(self, dir_path: Path):
        """Handle new meeting prep directory creation."""
        print(f"🎯 Processing new meeting prep directory: {dir_path.name}")

        # Wait a moment for any initial files to be created
        time.sleep(1)

        # Parse and store meeting intelligence
        try:
            meeting_data = self.meeting_manager.parse_meeting_prep_directory(dir_path)
            meeting_id = self.meeting_manager.store_meeting_session(meeting_data)

            print(f"✅ Meeting session created: {meeting_data['meeting_key']} -> ID {meeting_id}")

            # Update workspace change with memory storage info
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE workspace_changes
                    SET memory_stored_at = CURRENT_TIMESTAMP
                    WHERE path_full = ? AND memory_stored_at IS NULL
                """,
                    (str(dir_path),),
                )

        except Exception as e:
            print(f"❌ Error processing meeting directory {dir_path}: {e}")

    def _handle_initiative_directory(self, dir_path: Path):
        """Handle new initiative directory creation."""
        print(f"🚀 Processing new initiative directory: {dir_path.name}")

        # Extract initiative information and store in strategic_initiatives table
        # This could be enhanced to parse initiative details from directory structure
        pass

    def _apply_directory_templates(self, dir_path: Path, category: str, subcategory: str):
        """Apply automatic directory templates based on category."""
        # Query workspace_templates for matching templates
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    SELECT template_name, directory_structure, default_files
                    FROM workspace_templates
                    WHERE active = 1
                """
                )
                templates = cursor.fetchall()

                for template_name, dir_structure, default_files in templates:
                    # Check if template matches this directory
                    if self._template_matches(dir_path, template_name):
                        print(f"📋 Applying template: {template_name}")
                        self._create_template_structure(dir_path, dir_structure, default_files)
                        break

            except sqlite3.OperationalError:
                # Templates table doesn't exist yet
                pass

    def _template_matches(self, dir_path: Path, template_name: str) -> bool:
        """Check if directory matches template pattern."""
        path_str = str(dir_path).lower()

        if "1on1" in template_name and "1on1" in path_str:
            return True
        elif "vp" in template_name and "vp" in path_str:
            return True
        elif "initiative" in template_name and any(
            keyword in path_str for keyword in ["initiative", "project", "pi-"]
        ):
            return True

        return False

    def _create_template_structure(self, dir_path: Path, dir_structure: str, default_files: str):
        """Create directory structure and default files from template."""
        try:
            structure = json.loads(dir_structure) if dir_structure else {}
            files = json.loads(default_files) if default_files else []

            # Create subdirectories
            if "subdirs" in structure:
                for subdir in structure["subdirs"]:
                    subdir_path = dir_path / subdir
                    subdir_path.mkdir(exist_ok=True)
                    print(f"   📁 Created subdirectory: {subdir}")

            # Create default files
            for file_name in files:
                file_path = dir_path / file_name
                if not file_path.exists():
                    file_path.touch()
                    print(f"   📄 Created template file: {file_name}")

        except Exception as e:
            print(f"❌ Error applying template: {e}")

    def _trigger_memory_update(self, file_path: Path, category: str, subcategory: str):
        """Trigger strategic memory update based on file changes."""
        if category == "meeting_prep":
            # Re-process the parent directory for meeting intelligence
            if file_path.parent != self.workspace_root / "meeting-prep":
                self._handle_meeting_prep_directory(file_path.parent)


class WorkspaceMonitor:
    """Main workspace monitoring service."""

    def __init__(
        self, workspace_path: str = "workspace", db_path: str = "memory/strategic_memory.db"
    ):
        self.workspace_path = Path(workspace_path)
        self.db_path = db_path
        self.observer = Observer()
        self.handler = StrategicWorkspaceHandler(db_path)

    def start_monitoring(self):
        """Start filesystem monitoring."""
        if not self.workspace_path.exists():
            print(f"❌ Workspace directory not found: {self.workspace_path}")
            return

        print(f"🔍 Starting workspace monitoring: {self.workspace_path}")
        print(f"📊 Strategic memory database: {self.db_path}")

        self.observer.schedule(self.handler, str(self.workspace_path), recursive=True)
        self.observer.start()

        try:
            print("✅ Workspace monitor active - watching for strategic changes...")
            print("   Press Ctrl+C to stop monitoring")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping workspace monitor...")
            self.observer.stop()

        self.observer.join()
        print("✅ Workspace monitor stopped")


    def _process_stakeholder_detection(self, file_path: Path, category: str, subcategory: str):
        """Process file for intelligent stakeholder detection"""
        if not self.stakeholder_detector:
            return
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content.strip()) < 10:  # Skip very short files
                return
            
            # Build context for AI analysis
            context = {
                'category': category,
                'subcategory': subcategory,
                'file_path': str(file_path),
                'relative_path': str(self._get_relative_path(file_path)),
                'meeting_type': self._infer_meeting_type(file_path.parent.name) if category == 'meeting-prep' else None
            }
            
            # Process with intelligent stakeholder detector
            result = self.stakeholder_detector.process_content_for_stakeholders(content, context)
            
            if result['candidates_detected'] > 0:
                print(f"🧠 AI detected {result['candidates_detected']} stakeholder candidates in {file_path.name}")
                
                if result['auto_created'] > 0:
                    print(f"   ✅ Auto-created {result['auto_created']} stakeholder profiles")
                
                if result['profiling_needed'] > 0:
                    print(f"   ❓ {result['profiling_needed']} stakeholders need profiling")
                    print("   💡 Run 'python stakeholder_ai_manager.py profile' to complete")
                
                if result['updates_suggested'] > 0:
                    print(f"   🔄 {result['updates_suggested']} stakeholder updates suggested")
                    print("   💡 Run 'python stakeholder_ai_manager.py updates' to review")
        
        except Exception as e:
            print(f"⚠️  Error in stakeholder detection for {file_path.name}: {e}")
    
    def _infer_meeting_type(self, directory_name: str) -> str:
        """Infer meeting type from directory name"""
        name_lower = directory_name.lower()
        
        if 'vp' in name_lower or 'vice-president' in name_lower:
            return 'vp_1on1'
        elif '1on1' in name_lower or 'one-on-one' in name_lower:
            return '1on1_reports'
        elif 'strategic' in name_lower or 'planning' in name_lower:
            return 'strategic_planning'
        elif 'team' in name_lower or 'all-hands' in name_lower:
            return 'team_meeting'
        else:
            return 'general_meeting'


def main():
    """Main CLI interface for workspace monitoring."""
    import argparse

    parser = argparse.ArgumentParser(description="SuperClaude Workspace Monitor")
    parser.add_argument("--workspace", default="workspace", help="Workspace directory to monitor")
    parser.add_argument("--db-path", default="memory/strategic_memory.db", help="Database path")
    parser.add_argument("--test", action="store_true", help="Test handler without monitoring")

    args = parser.parse_args()

    if args.test:
        # Test the handler functionality
        handler = StrategicWorkspaceHandler(args.db_path)
        print("🧪 Testing workspace handler...")

        # Simulate directory creation
        test_path = Path(args.workspace) / "meeting-prep" / "test-vp-1on1"
        if test_path.exists():
            handler._handle_directory_created(str(test_path))
        else:
            print(f"Test directory not found: {test_path}")

    else:
        # Start monitoring service
        monitor = WorkspaceMonitor(args.workspace, args.db_path)
        monitor.start_monitoring()


if __name__ == "__main__":
    main()
