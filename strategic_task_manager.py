#!/usr/bin/env python3
"""
Strategic Task Manager
Comprehensive task management CLI with AI detection and stakeholder integration
"""

import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import structlog

from memory.intelligent_task_detector import IntelligentTaskDetector

logger = structlog.get_logger()


class StrategicTaskManager:
    """Comprehensive task management with AI detection and stakeholder integration"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize task manager with AI detection"""
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path("memory/strategic_memory.db")
        
        self.task_detector = IntelligentTaskDetector(str(self.db_path))
        self.logger = logger.bind(component="strategic_task_manager")
        
        # Initialize database if needed
        self._ensure_database_setup()
    
    def _ensure_database_setup(self):
        """Ensure task tracking tables exist"""
        try:
            schema_path = Path(__file__).parent / "memory" / "task_tracking_schema.sql"
            
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                
                with self.get_connection() as conn:
                    conn.executescript(schema_sql)
                    
        except Exception as e:
            self.logger.error("Failed to setup task database", error=str(e))
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def scan_workspace_for_tasks(self):
        """Scan workspace for tasks using AI detection"""
        print("🎯 AI-Powered Task Detection")
        print("=" * 35)
        
        workspace_dir = Path.cwd() / "workspace"
        
        if not workspace_dir.exists():
            print("❌ Workspace directory not found")
            print("   Create workspace with: mkdir workspace")
            return
        
        total_processed = 0
        total_tasks = 0
        
        # Scan all relevant files
        file_patterns = ["*.md", "*.txt"]
        
        for pattern in file_patterns:
            for file_path in workspace_dir.rglob(pattern):
                try:
                    if file_path.stat().st_size < 10:  # Skip very small files
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if len(content.strip()) < 20:  # Skip empty files
                        continue
                    
                    # Build context
                    context = self._build_file_context(file_path)
                    
                    # Detect tasks
                    detected_tasks = self.task_detector.detect_tasks_in_content(content, context)
                    
                    if detected_tasks:
                        print(f"\n📁 {file_path.relative_to(workspace_dir)}")
                        print(f"   🎯 Detected {len(detected_tasks)} potential tasks")
                        
                        for task in detected_tasks:
                            result = self._process_detected_task(task, file_path)
                            
                            if result['action'] == 'created':
                                print(f"   ✅ Created: {task['task_text'][:60]}...")
                            elif result['action'] == 'needs_review':
                                print(f"   ❓ Review needed: {task['task_text'][:60]}...")
                            else:
                                print(f"   ⏭️  Skipped: {task['task_text'][:60]}...")
                        
                        total_tasks += len(detected_tasks)
                    
                    total_processed += 1
                    
                except Exception as e:
                    self.logger.error("Failed to process file", file_path=str(file_path), error=str(e))
        
        print(f"\n🎉 Task Detection Complete!")
        print(f"   📁 Files processed: {total_processed}")
        print(f"   🎯 Tasks detected: {total_tasks}")
        
        # Show next steps
        self._show_task_summary()
    
    def _build_file_context(self, file_path: Path) -> Dict:
        """Build context for file analysis"""
        relative_path = file_path.relative_to(Path.cwd())
        
        context = {
            'file_path': str(file_path),
            'relative_path': str(relative_path),
            'category': 'general',
            'meeting_type': None,
        }
        
        # Determine category from path
        path_parts = relative_path.parts
        
        if 'meeting-prep' in path_parts:
            context['category'] = 'meeting_prep'
            # Infer meeting type from directory name
            for part in path_parts:
                if 'vp' in part.lower():
                    context['meeting_type'] = 'vp_1on1'
                    break
                elif '1on1' in part.lower():
                    context['meeting_type'] = '1on1'
                    break
                elif 'strategic' in part.lower() or 'planning' in part.lower():
                    context['meeting_type'] = 'strategic_planning'
                    break
        
        elif 'initiatives' in path_parts or 'projects' in path_parts:
            context['category'] = 'current_initiatives'
        
        elif 'strategic' in path_parts or 'planning' in path_parts:
            context['category'] = 'strategic_docs'
        
        return context
    
    def _process_detected_task(self, task_data: Dict, source_file: Path) -> Dict:
        """Process a detected task and decide what to do with it"""
        
        confidence = task_data['confidence_score']
        
        if confidence >= self.task_detector.AUTO_CREATE_THRESHOLD:
            # High confidence - auto-create
            task_id = self._create_task_from_detection(task_data, source_file)
            return {'action': 'created', 'task_id': task_id}
        
        elif confidence >= self.task_detector.REVIEW_THRESHOLD:
            # Medium confidence - store for review
            self._store_task_for_review(task_data, source_file)
            return {'action': 'needs_review', 'confidence': confidence}
        
        else:
            # Low confidence - log but don't create
            return {'action': 'skipped', 'confidence': confidence}
    
    def _create_task_from_detection(self, task_data: Dict, source_file: Path) -> Optional[int]:
        """Create task from AI detection"""
        
        try:
            task_key = self._generate_task_key(task_data['task_text'])
            
            # Check if task already exists
            if self._task_exists(task_key):
                return None
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO strategic_tasks (
                        task_key, title, description, assignment_direction,
                        category, priority, impact_scope, status,
                        due_date, follow_up_required, source_type, source_reference,
                        detection_confidence, created_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_key,
                    task_data['task_text'][:200],  # Truncate if too long
                    task_data['task_text'],
                    task_data['assignment_direction'],
                    task_data['category'],
                    task_data['priority'],
                    task_data['impact_scope'],
                    'active',
                    task_data.get('due_date'),
                    task_data['follow_up_required'],
                    'auto_detected',
                    str(source_file),
                    task_data['confidence_score'],
                    datetime.now().isoformat()
                ))
                
                task_id = cursor.lastrowid
                
                # Log activity
                cursor.execute("""
                    INSERT INTO task_activity_log (
                        task_id, activity_type, comment, created_at
                    ) VALUES (?, ?, ?, ?)
                """, (
                    task_id,
                    'created',
                    f"Auto-detected from {source_file.name} with {task_data['confidence_score']:.1%} confidence",
                    datetime.now().isoformat()
                ))
                
                return task_id
                
        except Exception as e:
            self.logger.error("Failed to create task from detection", error=str(e))
            return None
    
    def _store_task_for_review(self, task_data: Dict, source_file: Path):
        """Store task candidate for manual review"""
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create review tasks table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS task_review_queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_data TEXT NOT NULL,
                        source_file TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO task_review_queue (task_data, source_file, confidence)
                    VALUES (?, ?, ?)
                """, (
                    json.dumps(task_data),
                    str(source_file),
                    task_data['confidence_score']
                ))
                
        except Exception as e:
            self.logger.error("Failed to store task for review", error=str(e))
    
    def _generate_task_key(self, task_text: str) -> str:
        """Generate unique task key"""
        import hashlib
        
        # Create hash from task text
        task_hash = hashlib.md5(task_text.lower().encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d")
        
        return f"task_{timestamp}_{task_hash}"
    
    def _task_exists(self, task_key: str) -> bool:
        """Check if task already exists"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM strategic_tasks WHERE task_key = ?", (task_key,))
                return cursor.fetchone() is not None
        except:
            return False
    
    def show_my_tasks(self, status_filter: Optional[str] = None):
        """Show tasks assigned to me"""
        print("📋 My Tasks")
        print("=" * 20)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                where_clause = "WHERE (assigned_to = 'self' OR assignment_direction = 'incoming' OR assignment_direction = 'self_assigned')"
                if status_filter:
                    where_clause += f" AND status = '{status_filter}'"
                
                cursor.execute(f"""
                    SELECT id, title, priority, due_date, status, category, assignment_direction
                    FROM strategic_tasks 
                    {where_clause}
                    ORDER BY 
                        CASE priority 
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2  
                            WHEN 'medium' THEN 3
                            WHEN 'low' THEN 4
                        END,
                        due_date ASC
                """)
                
                tasks = cursor.fetchall()
                
                if not tasks:
                    print("No tasks found.")
                    return
                
                for task in tasks:
                    task_id, title, priority, due_date, status, category, direction = task
                    
                    priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[priority]
                    status_emoji = {'active': '⚡', 'blocked': '🚫', 'completed': '✅', 'deferred': '⏸️'}[status]
                    
                    print(f"{priority_emoji} {status_emoji} [{task_id}] {title[:60]}")
                    print(f"   Priority: {priority.title()} | Category: {category}")
                    
                    if due_date:
                        due_obj = datetime.fromisoformat(due_date.replace('Z', ''))
                        days_until = (due_obj - datetime.now()).days
                        
                        if days_until < 0:
                            print(f"   ⚠️  OVERDUE by {abs(days_until)} days")
                        elif days_until == 0:
                            print(f"   ⏰ DUE TODAY")
                        elif days_until <= 7:
                            print(f"   📅 Due in {days_until} days ({due_date})")
                        else:
                            print(f"   📅 Due: {due_date}")
                    
                    print()
                
        except Exception as e:
            print(f"❌ Error retrieving tasks: {e}")
    
    def show_assigned_tasks(self):
        """Show tasks I've assigned to others"""
        print("📤 Tasks I've Assigned")
        print("=" * 25)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT t.id, t.title, t.assigned_to, t.priority, t.due_date, t.status,
                           s.display_name
                    FROM strategic_tasks t
                    LEFT JOIN stakeholder_profiles_enhanced s ON t.assigned_to = s.stakeholder_key
                    WHERE t.assignment_direction = 'outgoing'
                    ORDER BY 
                        CASE t.priority 
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2  
                            WHEN 'medium' THEN 3
                            WHEN 'low' THEN 4
                        END,
                        t.due_date ASC
                """)
                
                tasks = cursor.fetchall()
                
                if not tasks:
                    print("No assigned tasks found.")
                    return
                
                for task in tasks:
                    task_id, title, assigned_to, priority, due_date, status, assignee_name = task
                    
                    priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[priority]
                    status_emoji = {'active': '⚡', 'blocked': '🚫', 'completed': '✅', 'deferred': '⏸️'}[status]
                    
                    assignee_display = assignee_name if assignee_name else assigned_to
                    
                    print(f"{priority_emoji} {status_emoji} [{task_id}] {title[:50]}")
                    print(f"   Assigned to: {assignee_display}")
                    
                    if due_date:
                        print(f"   Due: {due_date}")
                    
                    print()
                
        except Exception as e:
            print(f"❌ Error retrieving assigned tasks: {e}")
    
    def show_overdue_tasks(self):
        """Show overdue tasks requiring attention"""
        print("⚠️  Overdue Tasks Requiring Action")
        print("=" * 35)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, title, priority, due_date, assignment_direction, assigned_to,
                           (julianday('now') - julianday(due_date)) as days_overdue
                    FROM strategic_tasks 
                    WHERE status = 'active' 
                        AND due_date < date('now')
                    ORDER BY days_overdue DESC
                """)
                
                tasks = cursor.fetchall()
                
                if not tasks:
                    print("🎉 No overdue tasks!")
                    return
                
                for task in tasks:
                    task_id, title, priority, due_date, direction, assigned_to, days_overdue = task
                    
                    priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[priority]
                    direction_emoji = {'incoming': '📥', 'outgoing': '📤', 'self_assigned': '📝'}[direction]
                    
                    print(f"{priority_emoji} {direction_emoji} [{task_id}] {title[:50]}")
                    print(f"   OVERDUE by {int(days_overdue)} days (due: {due_date})")
                    
                    if direction == 'outgoing':
                        print(f"   Assigned to: {assigned_to} - FOLLOW UP NEEDED")
                    
                    print()
                
        except Exception as e:
            print(f"❌ Error retrieving overdue tasks: {e}")
    
    def show_follow_ups_due(self):
        """Show follow-ups that are due"""
        print("🔄 Follow-ups Due")
        print("=" * 20)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT t.id, t.title, t.follow_up_date, t.follow_up_stakeholder,
                           s.display_name,
                           (julianday('now') - julianday(t.follow_up_date)) as days_since_due
                    FROM strategic_tasks t
                    LEFT JOIN stakeholder_profiles_enhanced s ON t.follow_up_stakeholder = s.stakeholder_key
                    WHERE t.follow_up_required = TRUE
                        AND t.follow_up_date <= date('now')
                        AND t.status = 'active'
                    ORDER BY days_since_due DESC
                """)
                
                follow_ups = cursor.fetchall()
                
                if not follow_ups:
                    print("🎉 No follow-ups due!")
                    return
                
                for follow_up in follow_ups:
                    task_id, title, follow_up_date, stakeholder_key, stakeholder_name, days_since = follow_up
                    
                    stakeholder_display = stakeholder_name if stakeholder_name else stakeholder_key
                    
                    if days_since < 1:
                        urgency = "🟡 DUE TODAY"
                    elif days_since < 3:
                        urgency = f"🟠 {int(days_since)} days overdue"
                    else:
                        urgency = f"🔴 {int(days_since)} days overdue"
                    
                    print(f"{urgency} [{task_id}] {title[:50]}")
                    print(f"   Follow up with: {stakeholder_display}")
                    print(f"   Due date: {follow_up_date}")
                    print()
                
        except Exception as e:
            print(f"❌ Error retrieving follow-ups: {e}")
    
    def show_review_queue(self):
        """Show tasks needing manual review"""
        print("❓ Tasks Needing Review")
        print("=" * 25)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, task_data, source_file, confidence, created_at
                    FROM task_review_queue
                    WHERE status = 'pending'
                    ORDER BY confidence DESC, created_at ASC
                """)
                
                reviews = cursor.fetchall()
                
                if not reviews:
                    print("🎉 No tasks pending review!")
                    return
                
                for review in reviews:
                    review_id, task_data_json, source_file, confidence, created_at = review
                    task_data = json.loads(task_data_json)
                    
                    confidence_emoji = "🟡" if confidence >= 0.6 else "🔴"
                    direction_emoji = {'incoming': '📥', 'outgoing': '📤', 'self_assigned': '📝'}[task_data['assignment_direction']]
                    
                    print(f"{confidence_emoji} {direction_emoji} [{review_id}] {task_data['task_text'][:60]}")
                    print(f"   Confidence: {confidence:.1%}")
                    print(f"   Source: {Path(source_file).name}")
                    print(f"   Direction: {task_data['assignment_direction']}")
                    print(f"   Priority: {task_data['priority']}")
                    
                    if task_data.get('assignee'):
                        print(f"   Assignee: {task_data['assignee']}")
                    
                    print()
                
        except Exception as e:
            print(f"❌ Error retrieving review queue: {e}")
    
    def _show_task_summary(self):
        """Show task summary and next actions"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get counts
                cursor.execute("SELECT COUNT(*) FROM strategic_tasks WHERE status = 'active'")
                active_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM strategic_tasks WHERE status = 'active' AND due_date < date('now')")
                overdue_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM strategic_tasks WHERE follow_up_required = TRUE AND follow_up_date <= date('now') AND status = 'active'")
                followup_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM task_review_queue WHERE status = 'pending'")
                review_count = cursor.fetchone()[0]
                
                print(f"\n📊 Task System Status:")
                print(f"   ⚡ Active tasks: {active_count}")
                print(f"   ⚠️  Overdue tasks: {overdue_count}")
                print(f"   🔄 Follow-ups due: {followup_count}")
                print(f"   ❓ Tasks needing review: {review_count}")
                
                print(f"\n💡 Next actions:")
                if overdue_count > 0:
                    print("   1. Review overdue tasks: python strategic_task_manager.py overdue")
                if followup_count > 0:
                    print("   2. Complete follow-ups: python strategic_task_manager.py followups")
                if review_count > 0:
                    print("   3. Review detected tasks: python strategic_task_manager.py review")
                
                print("   4. View all my tasks: python strategic_task_manager.py list")
                print("   5. View assigned tasks: python strategic_task_manager.py assigned")
                
        except Exception as e:
            print(f"❌ Error getting task summary: {e}")


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ClaudeDirector Strategic Task Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python strategic_task_manager.py scan        # Scan workspace for tasks
  python strategic_task_manager.py list        # Show my tasks
  python strategic_task_manager.py assigned    # Show tasks I've assigned
  python strategic_task_manager.py overdue     # Show overdue tasks
  python strategic_task_manager.py followups   # Show follow-ups due
  python strategic_task_manager.py review      # Show tasks needing review
        """
    )
    
    parser.add_argument("command", 
                       choices=['scan', 'list', 'assigned', 'overdue', 'followups', 'review'],
                       help="Command to execute")
    
    parser.add_argument("--status", 
                       choices=['active', 'blocked', 'completed', 'deferred'],
                       help="Filter tasks by status")
    
    args = parser.parse_args()
    
    manager = StrategicTaskManager()
    
    try:
        if args.command == 'scan':
            manager.scan_workspace_for_tasks()
        
        elif args.command == 'list':
            manager.show_my_tasks(args.status)
        
        elif args.command == 'assigned':
            manager.show_assigned_tasks()
        
        elif args.command == 'overdue':
            manager.show_overdue_tasks()
        
        elif args.command == 'followups':
            manager.show_follow_ups_due()
        
        elif args.command == 'review':
            manager.show_review_queue()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
