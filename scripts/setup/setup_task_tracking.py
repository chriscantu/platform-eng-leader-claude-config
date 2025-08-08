#!/usr/bin/env python3
"""
Task Tracking System Setup
Initialize the comprehensive strategic task management system
"""

import sqlite3
import sys
from pathlib import Path

import structlog

logger = structlog.get_logger()


class TaskTrackingSetup:
    """Setup and configuration for the Strategic Task Tracking System"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.db_path = self.project_root / "memory" / "strategic_memory.db"
        self.schema_path = self.project_root / "memory" / "task_tracking_schema.sql"
    
    def print_header(self):
        """Print setup header"""
        print("🎯 Strategic Task Tracking System Setup")
        print("=" * 45)
        print("Initializing comprehensive task management with AI detection...")
        print()
    
    def verify_dependencies(self) -> bool:
        """Verify required files and dependencies exist"""
        print("🔍 Verifying dependencies...")
        
        # Check if schema file exists
        if not self.schema_path.exists():
            print(f"❌ Schema file not found: {self.schema_path}")
            return False
        
        # Check if memory directory exists
        memory_dir = self.project_root / "memory"
        if not memory_dir.exists():
            print("📁 Creating memory directory...")
            memory_dir.mkdir(exist_ok=True)
        
        # Check if core files exist
        required_files = [
            "memory/intelligent_task_detector.py",
            "strategic_task_manager.py",
            "daily_task_alerts.py"
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                print(f"❌ Required file not found: {file_path}")
                return False
        
        print("✅ All dependencies verified")
        return True
    
    def setup_database_schema(self) -> bool:
        """Set up task tracking database schema"""
        print("🗄️  Setting up task tracking database schema...")
        
        try:
            # Read schema file
            with open(self.schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Apply schema
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema_sql)
                
                # Verify tables were created
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name LIKE '%task%'
                    ORDER BY name
                """)
                
                tables = cursor.fetchall()
                
                if tables:
                    print("✅ Task tracking schema installed successfully")
                    print("   Created tables:")
                    for table in tables:
                        print(f"     • {table[0]}")
                    return True
                else:
                    print("❌ No task tables found after schema installation")
                    return False
                    
        except Exception as e:
            print(f"❌ Failed to setup database schema: {e}")
            return False
    
    def test_ai_detection(self) -> bool:
        """Test AI task detection functionality"""
        print("🧠 Testing AI task detection...")
        
        try:
            from memory.intelligent_task_detector import IntelligentTaskDetector
            
            detector = IntelligentTaskDetector(str(self.db_path))
            
            # Test content
            test_content = """
            Meeting Notes - Q1 Planning
            
            Action items:
            - I need to review the platform architecture by Friday
            - Sarah will update the technical roadmap
            - Follow up with the design team about component library
            - John should prepare the budget analysis for next week
            """
            
            test_context = {
                'category': 'meeting_prep',
                'meeting_type': 'strategic_planning',
                'file_path': 'test_meeting.md'
            }
            
            tasks = detector.detect_tasks_in_content(test_content, test_context)
            
            if tasks:
                print(f"✅ AI detection working - found {len(tasks)} tasks")
                print("   Sample detected tasks:")
                for i, task in enumerate(tasks[:3], 1):
                    direction_emoji = {'incoming': '📥', 'outgoing': '📤', 'self_assigned': '📝'}[task['assignment_direction']]
                    print(f"     {i}. {direction_emoji} {task['task_text'][:50]}... (confidence: {task['confidence_score']:.1%})")
                return True
            else:
                print("⚠️  AI detection working but no tasks found in test content")
                return True
                
        except Exception as e:
            print(f"❌ AI detection test failed: {e}")
            return False
    
    def test_task_management(self) -> bool:
        """Test task management functionality"""
        print("📋 Testing task management system...")
        
        try:
            from strategic_task_manager import StrategicTaskManager
            
            manager = StrategicTaskManager(str(self.db_path))
            
            # Test database connection
            with manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM strategic_tasks")
                task_count = cursor.fetchone()[0]
            
            print(f"✅ Task management system working - {task_count} tasks in database")
            return True
            
        except Exception as e:
            print(f"❌ Task management test failed: {e}")
            return False
    
    def test_alert_system(self) -> bool:
        """Test daily alert system"""
        print("🚨 Testing daily alert system...")
        
        try:
            from daily_task_alerts import DailyTaskAlerts
            
            alert_system = DailyTaskAlerts(str(self.db_path))
            alerts = alert_system.generate_daily_alerts()
            
            if 'summary' in alerts:
                summary = alerts['summary']
                print(f"✅ Alert system working - {summary['total_alerts']} alerts generated")
                print(f"   Urgency level: {summary['urgency_level']}")
                return True
            else:
                print("❌ Alert system not generating proper summary")
                return False
                
        except Exception as e:
            print(f"❌ Alert system test failed: {e}")
            return False
    
    def create_demo_tasks(self) -> bool:
        """Create demo tasks for testing"""
        print("🎬 Creating demo tasks...")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                demo_tasks = [
                    {
                        'task_key': 'demo_platform_review',
                        'title': 'Review platform architecture documentation',
                        'description': 'Complete review of current platform architecture and identify technical debt',
                        'assignment_direction': 'self_assigned',
                        'category': 'platform_initiative',
                        'priority': 'high',
                        'impact_scope': 'platform_wide',
                        'due_date': '2025-01-10',
                        'source_type': 'demo'
                    },
                    {
                        'task_key': 'demo_stakeholder_followup',
                        'title': 'Follow up with product team on Q2 roadmap',
                        'description': 'Check status of product roadmap planning for Q2 initiatives',
                        'assignment_direction': 'self_assigned',
                        'category': 'stakeholder_followup',
                        'priority': 'medium',
                        'impact_scope': 'cross_team',
                        'follow_up_required': True,
                        'follow_up_date': '2025-01-08',
                        'source_type': 'demo'
                    }
                ]
                
                for task in demo_tasks:
                    cursor.execute("""
                        INSERT OR IGNORE INTO strategic_tasks (
                            task_key, title, description, assignment_direction,
                            category, priority, impact_scope, due_date,
                            follow_up_required, follow_up_date, source_type,
                            status, created_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', datetime('now'))
                    """, (
                        task['task_key'], task['title'], task['description'],
                        task['assignment_direction'], task['category'],
                        task['priority'], task['impact_scope'],
                        task.get('due_date'), task.get('follow_up_required', False),
                        task.get('follow_up_date'), task['source_type']
                    ))
                
                print("✅ Demo tasks created successfully")
                return True
                
        except Exception as e:
            print(f"❌ Failed to create demo tasks: {e}")
            return False
    
    def show_usage_examples(self):
        """Show usage examples"""
        print("\n🚀 Task Tracking System Ready!")
        print("-" * 35)
        
        print("📋 Basic Commands:")
        print("   python strategic_task_manager.py scan       # Scan workspace for tasks")
        print("   python strategic_task_manager.py list       # Show my tasks")
        print("   python strategic_task_manager.py assigned   # Show tasks I've assigned")
        print("   python strategic_task_manager.py overdue    # Show overdue tasks")
        print("   python strategic_task_manager.py followups  # Show follow-ups due")
        
        print("\n🚨 Daily Alerts:")
        print("   python daily_task_alerts.py                 # Show daily alert dashboard")
        print("   python daily_task_alerts.py --quiet         # Summary for automation")
        
        print("\n🧠 AI Detection:")
        print("   # AI automatically detects tasks when you:")
        print("   # 1. Create meeting prep files with action items")
        print("   # 2. Use workspace monitor (python memory/workspace_monitor.py)")
        print("   # 3. Run task scan manually")
        
        print("\n💡 Workflow Examples:")
        print("   # Morning routine:")
        print("   python daily_task_alerts.py                 # Check daily alerts")
        print("   python strategic_task_manager.py overdue    # Address overdue items")
        print("   python strategic_task_manager.py followups  # Complete follow-ups")
        
        print("\n🎯 Platform Leadership Focus:")
        print("   • Bidirectional task tracking (assigned TO you + BY you)")
        print("   • Stakeholder integration with follow-up automation")
        print("   • AI-powered detection from meeting content")
        print("   • Proactive escalation for platform-wide impact")
        print("   • Executive accountability with reminder system")
    
    def run_setup(self) -> bool:
        """Run the complete setup process"""
        self.print_header()
        
        # Step 1: Verify dependencies
        if not self.verify_dependencies():
            print("\n❌ Setup failed at dependency verification")
            return False
        
        # Step 2: Setup database schema
        if not self.setup_database_schema():
            print("\n❌ Setup failed at database schema installation")
            return False
        
        # Step 3: Test AI detection
        if not self.test_ai_detection():
            print("\n❌ Setup failed at AI detection test")
            return False
        
        # Step 4: Test task management
        if not self.test_task_management():
            print("\n❌ Setup failed at task management test")
            return False
        
        # Step 5: Test alert system
        if not self.test_alert_system():
            print("\n❌ Setup failed at alert system test")
            return False
        
        # Step 6: Create demo tasks
        if not self.create_demo_tasks():
            print("\n⚠️  Demo task creation failed, but system is functional")
        
        # Show usage examples
        self.show_usage_examples()
        
        return True


def main():
    """Main setup interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Strategic Task Tracking System Setup")
    parser.add_argument("--verify-only", action="store_true", help="Only verify installation")
    parser.add_argument("--demo-tasks", action="store_true", help="Only create demo tasks")
    
    args = parser.parse_args()
    
    setup = TaskTrackingSetup()
    
    try:
        if args.verify_only:
            setup.print_header()
            
            if setup.verify_dependencies() and setup.test_task_management():
                print("\n✅ Task tracking system is properly installed and functional")
            else:
                print("\n❌ Task tracking system has issues")
                sys.exit(1)
        
        elif args.demo_tasks:
            setup.print_header()
            
            if setup.create_demo_tasks():
                print("\n✅ Demo tasks created successfully")
            else:
                print("\n❌ Failed to create demo tasks")
                sys.exit(1)
        
        else:
            if setup.run_setup():
                print("\n🎉 Task tracking system setup completed successfully!")
            else:
                print("\n💥 Setup failed - please check errors above")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error during setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
