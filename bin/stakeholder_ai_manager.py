#!/usr/bin/env python3
"""
Stakeholder AI Manager
User-friendly interface for intelligent stakeholder management with local AI
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from memory.intelligent_stakeholder_detector import IntelligentStakeholderDetector


class StakeholderAIManager:
    """User-friendly interface for AI-powered stakeholder management"""
    
    def __init__(self):
        self.detector = IntelligentStakeholderDetector()
    
    def process_workspace_automatically(self):
        """Process workspace for automatic stakeholder detection"""
        print("🧠 AI-Powered Workspace Analysis")
        print("=" * 40)
        
        workspace_dir = Path.cwd() / "workspace" / "meeting-prep"
        
        if not workspace_dir.exists():
            print("❌ Meeting prep directory not found")
            print("   Create meetings with: mkdir workspace/meeting-prep/meeting-name")
            return
        
        total_processed = 0
        total_candidates = 0
        
        # Process all meeting prep directories
        for meeting_dir in workspace_dir.iterdir():
            if meeting_dir.is_dir():
                print(f"\n📁 Processing: {meeting_dir.name}")
                
                # Look for content files
                content_files = list(meeting_dir.glob("*.md")) + list(meeting_dir.glob("*.txt"))
                
                for content_file in content_files:
                    try:
                        with open(content_file, 'r') as f:
                            content = f.read()
                        
                        if len(content.strip()) < 10:  # Skip empty files
                            continue
                        
                        context = {
                            'category': 'meeting_prep',
                            'meeting_name': meeting_dir.name,
                            'file_path': str(content_file),
                            'meeting_type': self._infer_meeting_type(meeting_dir.name)
                        }
                        
                        result = self.detector.process_content_for_stakeholders(content, context)
                        
                        if result['candidates_detected'] > 0:
                            print(f"   📊 Detected {result['candidates_detected']} stakeholder candidates")
                            print(f"   ✅ Auto-created: {result['auto_created']}")
                            print(f"   ❓ Profiling needed: {result['profiling_needed']}")
                            print(f"   🔄 Updates suggested: {result['updates_suggested']}")
                            
                            total_candidates += result['candidates_detected']
                        
                        total_processed += 1
                        
                    except Exception as e:
                        print(f"   ⚠️  Error processing {content_file.name}: {e}")
        
        print(f"\n🎉 Analysis Complete!")
        print(f"   📁 Files processed: {total_processed}")
        print(f"   👤 Stakeholders detected: {total_candidates}")
        
        # Show next steps
        self._show_next_steps()
    
    def _infer_meeting_type(self, meeting_name: str) -> str:
        """Infer meeting type from directory name"""
        name_lower = meeting_name.lower()
        
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
    
    def handle_profiling_tasks(self):
        """Handle pending profiling tasks interactively"""
        tasks = self.detector.get_pending_profiling_tasks()
        
        if not tasks:
            print("🎉 No pending profiling tasks!")
            print("All detected stakeholders have been processed.")
            return
        
        print("❓ Stakeholder Profiling Assistant")
        print("=" * 40)
        print(f"Found {len(tasks)} stakeholders that need your input:\n")
        
        for i, task in enumerate(tasks, 1):
            print(f"👤 {i}. {task['name']} ({task['stakeholder_key']})")
            print(f"   Confidence: {task['confidence']:.1%}")
            print(f"   Auto-detected: {task['auto_detected_info']}")
            
            if self._ask_yes_no(f"\nProfile {task['name']} now?"):
                self._conduct_interactive_profiling(task)
            else:
                print("   ⏭️  Skipped for now\n")
    
    def _conduct_interactive_profiling(self, task: Dict):
        """Conduct interactive profiling for a stakeholder"""
        print(f"\n🎯 Profiling: {task['name']}")
        print("-" * 30)
        
        responses = {}
        
        for question in task['questions']:
            response = self._ask_question(question)
            responses[question['type']] = response
        
        # Create stakeholder profile from responses
        profile = self._build_profile_from_responses(task, responses)
        
        if self._ask_yes_no("Create this stakeholder profile?"):
            success = self._create_stakeholder_from_profile(task, profile)
            
            if success:
                print(f"✅ Successfully created profile for {task['name']}")
                self._mark_profiling_task_complete(task['task_id'])
            else:
                print(f"❌ Failed to create profile for {task['name']}")
        else:
            print("❌ Profile creation cancelled")
    
    def _ask_question(self, question: Dict) -> str:
        """Ask a profiling question and get user response"""
        print(f"\n❓ {question['question']}")
        
        if question.get('options'):
            for i, option in enumerate(question['options'], 1):
                marker = " (suggested)" if option == question.get('pre_filled') else ""
                print(f"   {i}. {option}{marker}")
            
            if question.get('multiple_choice'):
                response = input("Select options (comma-separated numbers): ").strip()
                try:
                    indices = [int(x.strip()) - 1 for x in response.split(',')]
                    selected = [question['options'][i] for i in indices if 0 <= i < len(question['options'])]
                    return selected
                except (ValueError, IndexError):
                    print("Invalid selection, using suggested default")
                    return [question.get('pre_filled')] if question.get('pre_filled') else []
            else:
                while True:
                    try:
                        choice = int(input("Select option: ").strip())
                        if 1 <= choice <= len(question['options']):
                            return question['options'][choice - 1]
                        else:
                            print("Invalid choice, please try again")
                    except ValueError:
                        print("Please enter a number")
        else:
            return input("Response: ").strip()
    
    def _ask_yes_no(self, question: str) -> bool:
        """Ask a yes/no question"""
        while True:
            response = input(f"{question} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def _build_profile_from_responses(self, task: Dict, responses: Dict) -> Dict:
        """Build stakeholder profile from user responses"""
        profile = {
            'stakeholder_key': task['stakeholder_key'],
            'display_name': task['name'],
            'role_title': None,
            'strategic_importance': task['auto_detected_info'].get('importance', 'medium'),
            'meeting_frequency': 'monthly',
            'communication_channels': [],
            'communication_style': None
        }
        
        # Process responses
        if 'role_confirmation' in responses:
            if responses['role_confirmation'] == 'yes':
                profile['role_title'] = task['auto_detected_info'].get('role', '').title()
            elif responses['role_confirmation'] == 'similar_role':
                profile['role_title'] = input("What is their actual role? ").strip()
        
        if 'importance_clarification' in responses:
            profile['strategic_importance'] = responses['importance_clarification']
        
        if 'communication_channels' in responses:
            profile['communication_channels'] = responses['communication_channels']
        
        if 'meeting_frequency' in responses:
            profile['meeting_frequency'] = responses['meeting_frequency']
        
        return profile
    
    def _create_stakeholder_from_profile(self, task: Dict, profile: Dict) -> bool:
        """Create stakeholder from completed profile"""
        try:
            # Create basic stakeholder
            success = self.detector.engagement_engine.add_stakeholder(
                stakeholder_key=profile['stakeholder_key'],
                display_name=profile['display_name'],
                role_title=profile['role_title'],
                strategic_importance=profile['strategic_importance']
            )
            
            if success:
                # Update preferences
                with self.detector.engagement_engine.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE stakeholder_profiles_enhanced 
                        SET optimal_meeting_frequency = ?,
                            preferred_communication_channels = ?,
                            communication_style = ?
                        WHERE stakeholder_key = ?
                    """, (
                        profile['meeting_frequency'],
                        json.dumps(profile['communication_channels']),
                        profile.get('communication_style'),
                        profile['stakeholder_key']
                    ))
                
                # Generate initial recommendations
                self.detector.engagement_engine.generate_engagement_recommendations()
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error creating stakeholder: {e}")
            return False
    
    def _mark_profiling_task_complete(self, task_id: int):
        """Mark profiling task as complete"""
        try:
            with self.detector.engagement_engine.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE stakeholder_profiling_tasks 
                    SET status = 'completed'
                    WHERE id = ?
                """, (task_id,))
        except Exception as e:
            print(f"Error marking task complete: {e}")
    
    def handle_update_suggestions(self):
        """Handle pending update suggestions interactively"""
        suggestions = self.detector.get_pending_update_suggestions()
        
        if not suggestions:
            print("🎉 No pending update suggestions!")
            print("All stakeholder profiles are current.")
            return
        
        print("🔄 Stakeholder Update Assistant")
        print("=" * 35)
        print(f"Found {len(suggestions)} stakeholders with suggested updates:\n")
        
        for suggestion in suggestions:
            print(f"👤 {suggestion['stakeholder_name']} ({suggestion['stakeholder_key']})")
            
            for update in suggestion['suggestions']:
                print(f"\n   🔄 {update['type'].replace('_', ' ').title()}:")
                print(f"      Current: {update['current_value']}")
                print(f"      Suggested: {update['suggested_value']}")
                print(f"      Confidence: {update['confidence']:.1%}")
                print(f"      Reason: {update['reason']}")
                
                if self._ask_yes_no("Apply this update?"):
                    self._apply_update(suggestion['stakeholder_key'], update)
                    print("   ✅ Update applied")
                else:
                    print("   ❌ Update skipped")
            
            # Mark suggestion as processed
            self._mark_suggestion_processed(suggestion['suggestion_id'])
            print()
    
    def _apply_update(self, stakeholder_key: str, update: Dict):
        """Apply an update to a stakeholder"""
        try:
            with self.detector.engagement_engine.get_connection() as conn:
                cursor = conn.cursor()
                
                field_mapping = {
                    'role_update': 'role_title',
                    'importance_update': 'strategic_importance',
                    'communication_update': 'preferred_communication_channels'
                }
                
                field = field_mapping.get(update['type'])
                if field:
                    value = update['suggested_value']
                    if field == 'preferred_communication_channels':
                        value = json.dumps(value)
                    
                    cursor.execute(f"""
                        UPDATE stakeholder_profiles_enhanced 
                        SET {field} = ?
                        WHERE stakeholder_key = ?
                    """, (value, stakeholder_key))
                    
        except Exception as e:
            print(f"Error applying update: {e}")
    
    def _mark_suggestion_processed(self, suggestion_id: int):
        """Mark update suggestion as processed"""
        try:
            with self.detector.engagement_engine.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE stakeholder_update_suggestions 
                    SET status = 'processed'
                    WHERE id = ?
                """, (suggestion_id,))
        except Exception as e:
            print(f"Error marking suggestion processed: {e}")
    
    def show_ai_summary(self):
        """Show AI detection summary and system status"""
        print("🧠 AI Stakeholder Management Summary")
        print("=" * 40)
        
        # Get pending tasks
        profiling_tasks = self.detector.get_pending_profiling_tasks()
        update_suggestions = self.detector.get_pending_update_suggestions()
        
        # Get total stakeholders
        try:
            with self.detector.engagement_engine.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM stakeholder_profiles_enhanced")
                total_stakeholders = cursor.fetchone()[0]
        except:
            total_stakeholders = 0
        
        print(f"📊 System Status:")
        print(f"   👥 Total stakeholders: {total_stakeholders}")
        print(f"   ❓ Pending profiling: {len(profiling_tasks)}")
        print(f"   🔄 Pending updates: {len(update_suggestions)}")
        
        if profiling_tasks:
            print(f"\n❓ Stakeholders needing profiling:")
            for task in profiling_tasks[:5]:  # Show first 5
                print(f"   • {task['name']} (confidence: {task['confidence']:.1%})")
            if len(profiling_tasks) > 5:
                print(f"   ... and {len(profiling_tasks) - 5} more")
        
        if update_suggestions:
            print(f"\n🔄 Stakeholders with suggested updates:")
            for suggestion in update_suggestions[:5]:  # Show first 5
                update_count = len(suggestion['suggestions'])
                print(f"   • {suggestion['stakeholder_name']} ({update_count} updates)")
            if len(update_suggestions) > 5:
                print(f"   ... and {len(update_suggestions) - 5} more")
        
        print(f"\n💡 Next actions:")
        if profiling_tasks:
            print("   1. Run 'python stakeholder_ai_manager.py profile' to complete profiling")
        if update_suggestions:
            print("   2. Run 'python stakeholder_ai_manager.py updates' to review updates")
        if not profiling_tasks and not update_suggestions:
            print("   ✅ All AI tasks complete! System is up to date.")
    
    def _show_next_steps(self):
        """Show recommended next steps after processing"""
        profiling_tasks = self.detector.get_pending_profiling_tasks()
        update_suggestions = self.detector.get_pending_update_suggestions()
        
        print(f"\n💡 Recommended next steps:")
        
        if profiling_tasks:
            print(f"   1. Complete profiling for {len(profiling_tasks)} stakeholders:")
            print(f"      python stakeholder_ai_manager.py profile")
        
        if update_suggestions:
            print(f"   2. Review {len(update_suggestions)} stakeholder updates:")
            print(f"      python stakeholder_ai_manager.py updates")
        
        print(f"   3. Check engagement recommendations:")
        print(f"      python stakeholder_manager.py recommendations")
        
        if not profiling_tasks and not update_suggestions:
            print("   ✅ AI processing complete! All stakeholders are current.")


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ClaudeDirector AI-Powered Stakeholder Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python stakeholder_ai_manager.py scan       # Analyze workspace for stakeholders
  python stakeholder_ai_manager.py profile    # Complete pending profiling tasks
  python stakeholder_ai_manager.py updates    # Review suggested updates
  python stakeholder_ai_manager.py status     # Show AI system status
        """
    )
    
    parser.add_argument("command", 
                       choices=['scan', 'profile', 'updates', 'status'],
                       help="Command to execute")
    
    args = parser.parse_args()
    
    manager = StakeholderAIManager()
    
    try:
        if args.command == 'scan':
            manager.process_workspace_automatically()
        
        elif args.command == 'profile':
            manager.handle_profiling_tasks()
        
        elif args.command == 'updates':
            manager.handle_update_suggestions()
        
        elif args.command == 'status':
            manager.show_ai_summary()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
