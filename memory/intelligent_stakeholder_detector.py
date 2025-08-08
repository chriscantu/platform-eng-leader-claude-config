#!/usr/bin/env python3
"""
Intelligent Stakeholder Detection Engine
Integrates local AI with existing stakeholder management system for automated discovery
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import structlog

from local_stakeholder_ai import LocalStakeholderAI
from stakeholder_engagement_engine import StakeholderEngagementEngine

logger = structlog.get_logger()


class IntelligentStakeholderDetector:
    """Intelligent stakeholder detection with local AI and adaptive profiling"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize with local AI and engagement engine"""
        self.ai_engine = LocalStakeholderAI(db_path)
        self.engagement_engine = StakeholderEngagementEngine(db_path)
        self.logger = logger.bind(component="intelligent_detector")
        
        # Detection settings
        self.auto_create_enabled = True
        self.profiling_enabled = True
        self.update_detection_enabled = True
    
    def process_content_for_stakeholders(self, content: str, context: Dict) -> Dict:
        """Process content for stakeholder detection and management"""
        
        result = {
            'candidates_detected': 0,
            'auto_created': 0,
            'profiling_needed': 0,
            'updates_suggested': 0,
            'actions_taken': []
        }
        
        try:
            self.logger.info("Processing content for stakeholder detection", 
                           content_length=len(content),
                           context_type=context.get('category', 'unknown'))
            
            # Detect stakeholder candidates using local AI
            candidates = self.ai_engine.detect_stakeholders_in_content(content, context)
            result['candidates_detected'] = len(candidates)
            
            for candidate in candidates:
                action = self._process_stakeholder_candidate(candidate)
                result['actions_taken'].append(action)
                
                if action['type'] == 'auto_created':
                    result['auto_created'] += 1
                elif action['type'] == 'profiling_initiated':
                    result['profiling_needed'] += 1
                elif action['type'] == 'update_suggested':
                    result['updates_suggested'] += 1
            
            self.logger.info("Stakeholder detection completed", **result)
            return result
            
        except Exception as e:
            self.logger.error("Failed to process content for stakeholders", error=str(e))
            return result
    
    def _process_stakeholder_candidate(self, candidate: Dict) -> Dict:
        """Process individual stakeholder candidate"""
        
        stakeholder_key = candidate['stakeholder_key']
        
        # Check if stakeholder already exists
        existing = self.ai_engine.check_existing_stakeholder(stakeholder_key)
        
        if existing:
            # Existing stakeholder - check for updates
            return self._handle_existing_stakeholder(stakeholder_key, candidate, existing)
        else:
            # New stakeholder - determine creation approach
            return self._handle_new_stakeholder(candidate)
    
    def _handle_existing_stakeholder(self, stakeholder_key: str, candidate: Dict, existing: Dict) -> Dict:
        """Handle updates to existing stakeholders"""
        
        if not self.update_detection_enabled:
            return {'type': 'no_action', 'reason': 'update_detection_disabled'}
        
        # Check for suggested updates
        suggestions = self.ai_engine.suggest_stakeholder_updates(stakeholder_key, candidate)
        
        if suggestions:
            # Store update suggestions for user review
            self._store_update_suggestions(stakeholder_key, suggestions)
            
            return {
                'type': 'update_suggested',
                'stakeholder_key': stakeholder_key,
                'suggestions': suggestions,
                'reason': f'Detected {len(suggestions)} potential updates'
            }
        
        return {
            'type': 'no_updates_needed',
            'stakeholder_key': stakeholder_key,
            'reason': 'No significant changes detected'
        }
    
    def _handle_new_stakeholder(self, candidate: Dict) -> Dict:
        """Handle new stakeholder discovery"""
        
        confidence = candidate['confidence_score']
        
        if confidence >= self.ai_engine.AUTO_CREATE_THRESHOLD and self.auto_create_enabled:
            # High confidence - auto-create
            return self._auto_create_stakeholder(candidate)
        
        elif confidence >= self.ai_engine.PROFILING_THRESHOLD and self.profiling_enabled:
            # Medium confidence - initiate smart profiling
            return self._initiate_smart_profiling(candidate)
        
        else:
            # Low confidence - log for potential manual review
            return {
                'type': 'low_confidence',
                'stakeholder_key': candidate['stakeholder_key'],
                'confidence': confidence,
                'reason': 'Confidence too low for automatic processing'
            }
    
    def _auto_create_stakeholder(self, candidate: Dict) -> Dict:
        """Automatically create stakeholder with high confidence"""
        
        try:
            # Map AI analysis to stakeholder profile
            profile = self._map_candidate_to_profile(candidate)
            
            # Create stakeholder using engagement engine
            success = self.engagement_engine.add_stakeholder(
                stakeholder_key=candidate['stakeholder_key'],
                display_name=candidate['name'],
                role_title=profile.get('role_title'),
                organization=profile.get('organization'),
                strategic_importance=candidate['strategic_importance']
            )
            
            if success:
                # Update detailed preferences
                self._update_stakeholder_preferences(candidate['stakeholder_key'], profile)
                
                # Generate initial recommendations
                self.engagement_engine.generate_engagement_recommendations()
                
                self.logger.info("Auto-created stakeholder", 
                               stakeholder_key=candidate['stakeholder_key'],
                               confidence=candidate['confidence_score'])
                
                return {
                    'type': 'auto_created',
                    'stakeholder_key': candidate['stakeholder_key'],
                    'name': candidate['name'],
                    'confidence': candidate['confidence_score'],
                    'profile': profile
                }
            else:
                return {
                    'type': 'creation_failed',
                    'stakeholder_key': candidate['stakeholder_key'],
                    'reason': 'Database creation failed'
                }
                
        except Exception as e:
            self.logger.error("Failed to auto-create stakeholder", 
                            stakeholder_key=candidate['stakeholder_key'], 
                            error=str(e))
            return {
                'type': 'creation_error',
                'stakeholder_key': candidate['stakeholder_key'],
                'error': str(e)
            }
    
    def _initiate_smart_profiling(self, candidate: Dict) -> Dict:
        """Initiate smart profiling for medium confidence candidates"""
        
        try:
            # Generate targeted questions based on what we know
            questions = self._generate_smart_questions(candidate)
            
            # Store profiling task for user interaction
            profiling_task = {
                'stakeholder_key': candidate['stakeholder_key'],
                'name': candidate['name'],
                'confidence': candidate['confidence_score'],
                'auto_detected_info': {
                    'role': candidate.get('detected_role'),
                    'importance': candidate['strategic_importance'],
                    'communication_prefs': candidate.get('communication_preferences', {})
                },
                'questions': questions,
                'created_at': datetime.now().isoformat()
            }
            
            self._store_profiling_task(profiling_task)
            
            return {
                'type': 'profiling_initiated',
                'stakeholder_key': candidate['stakeholder_key'],
                'name': candidate['name'],
                'questions': questions,
                'confidence': candidate['confidence_score']
            }
            
        except Exception as e:
            self.logger.error("Failed to initiate smart profiling", 
                            stakeholder_key=candidate['stakeholder_key'], 
                            error=str(e))
            return {
                'type': 'profiling_error',
                'stakeholder_key': candidate['stakeholder_key'],
                'error': str(e)
            }
    
    def _map_candidate_to_profile(self, candidate: Dict) -> Dict:
        """Map AI analysis to stakeholder profile format"""
        
        profile = {}
        
        # Map role
        if candidate.get('detected_role'):
            role_mapping = {
                'executive': candidate['detected_role'].title(),
                'director': 'Director',
                'manager': 'Manager',
                'principal': 'Principal',
                'senior': 'Senior',
                'external': 'External Partner'
            }
            profile['role_title'] = role_mapping.get(candidate['detected_role'], candidate['detected_role'].title())
        
        # Map communication preferences
        comm_prefs = candidate.get('communication_preferences', {})
        if comm_prefs.get('channels'):
            profile['preferred_channels'] = comm_prefs['channels']
        
        if comm_prefs.get('style'):
            profile['communication_style'] = comm_prefs['style']
        
        # Infer meeting frequency based on importance
        importance = candidate['strategic_importance']
        frequency_mapping = {
            'critical': 'weekly',
            'high': 'biweekly',
            'medium': 'monthly',
            'low': 'quarterly'
        }
        profile['meeting_frequency'] = frequency_mapping.get(importance, 'monthly')
        
        # Suggest personas based on role and style
        profile['suggested_personas'] = self._suggest_personas(candidate)
        
        return profile
    
    def _suggest_personas(self, candidate: Dict) -> List[str]:
        """Suggest SuperClaude personas based on stakeholder analysis"""
        
        personas = []
        
        role = candidate.get('detected_role')
        importance = candidate['strategic_importance']
        style = candidate.get('communication_preferences', {}).get('style')
        
        # Role-based persona suggestions
        if role == 'executive':
            personas.extend(['camille', 'alvaro'])
        elif role == 'director':
            personas.extend(['diego', 'alvaro'])
        elif role == 'manager':
            personas.extend(['diego', 'marcus'])
        elif role == 'principal':
            personas.extend(['martin', 'diego'])
        
        # Style-based adjustments
        if style == 'data_driven':
            personas.append('alvaro')
        elif style == 'visual':
            personas.append('rachel')
        elif style == 'collaborative':
            personas.append('diego')
        
        # Importance-based adjustments
        if importance == 'critical':
            personas.extend(['camille', 'alvaro'])
        
        # Remove duplicates and limit to top 3
        return list(dict.fromkeys(personas))[:3]
    
    def _generate_smart_questions(self, candidate: Dict) -> List[Dict]:
        """Generate targeted questions based on detected information"""
        
        questions = []
        
        # Role confirmation if detected with medium confidence
        if candidate.get('detected_role') and candidate.get('role_confidence', 0) < 0.8:
            questions.append({
                'type': 'role_confirmation',
                'question': f"Is {candidate['name']} a {candidate['detected_role'].title()}?",
                'options': ['yes', 'no', 'similar_role'],
                'pre_filled': candidate['detected_role']
            })
        
        # Strategic importance if unclear
        if candidate['importance_score'] < 3:
            questions.append({
                'type': 'importance_clarification',
                'question': f"How strategically important is {candidate['name']} to your platform objectives?",
                'options': ['critical', 'high', 'medium', 'low'],
                'pre_filled': candidate['strategic_importance']
            })
        
        # Communication preferences if not detected
        comm_prefs = candidate.get('communication_preferences', {})
        if not comm_prefs.get('channels'):
            questions.append({
                'type': 'communication_channels',
                'question': f"What's the best way to communicate with {candidate['name']}?",
                'options': ['slack', 'email', 'in_person', 'video'],
                'multiple_choice': True
            })
        
        # Meeting frequency based on importance
        questions.append({
            'type': 'meeting_frequency',
            'question': f"How often should you engage with {candidate['name']}?",
            'options': ['weekly', 'biweekly', 'monthly', 'quarterly', 'as_needed'],
            'pre_filled': self._suggest_frequency(candidate['strategic_importance'])
        })
        
        return questions
    
    def _suggest_frequency(self, importance: str) -> str:
        """Suggest meeting frequency based on importance"""
        mapping = {
            'critical': 'weekly',
            'high': 'biweekly', 
            'medium': 'monthly',
            'low': 'quarterly'
        }
        return mapping.get(importance, 'monthly')
    
    def _update_stakeholder_preferences(self, stakeholder_key: str, profile: Dict):
        """Update stakeholder preferences in database"""
        
        try:
            with self.engagement_engine.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE stakeholder_profiles_enhanced 
                    SET optimal_meeting_frequency = ?,
                        preferred_communication_channels = ?,
                        communication_style = ?,
                        most_effective_personas = ?
                    WHERE stakeholder_key = ?
                """, (
                    profile.get('meeting_frequency'),
                    json.dumps(profile.get('preferred_channels', [])),
                    profile.get('communication_style'),
                    json.dumps(profile.get('suggested_personas', [])),
                    stakeholder_key
                ))
                
        except Exception as e:
            self.logger.error("Failed to update stakeholder preferences", 
                            stakeholder_key=stakeholder_key, error=str(e))
    
    def _store_profiling_task(self, task: Dict):
        """Store profiling task for user interaction"""
        
        try:
            # Store in database for later retrieval
            with self.engagement_engine.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create profiling tasks table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stakeholder_profiling_tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stakeholder_key TEXT NOT NULL,
                        task_data TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO stakeholder_profiling_tasks 
                    (stakeholder_key, task_data)
                    VALUES (?, ?)
                """, (task['stakeholder_key'], json.dumps(task)))
                
        except Exception as e:
            self.logger.error("Failed to store profiling task", error=str(e))
    
    def _store_update_suggestions(self, stakeholder_key: str, suggestions: List[Dict]):
        """Store update suggestions for user review"""
        
        try:
            with self.engagement_engine.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create update suggestions table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stakeholder_update_suggestions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stakeholder_key TEXT NOT NULL,
                        suggestions TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO stakeholder_update_suggestions 
                    (stakeholder_key, suggestions)
                    VALUES (?, ?)
                """, (stakeholder_key, json.dumps(suggestions)))
                
        except Exception as e:
            self.logger.error("Failed to store update suggestions", error=str(e))
    
    def get_pending_profiling_tasks(self) -> List[Dict]:
        """Get pending profiling tasks for user interaction"""
        
        try:
            with self.engagement_engine.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, stakeholder_key, task_data, created_at
                    FROM stakeholder_profiling_tasks
                    WHERE status = 'pending'
                    ORDER BY created_at ASC
                """)
                
                tasks = []
                for row in cursor.fetchall():
                    task_data = json.loads(row[2])
                    task_data['task_id'] = row[0]
                    task_data['created_at'] = row[3]
                    tasks.append(task_data)
                
                return tasks
                
        except Exception as e:
            self.logger.error("Failed to get pending profiling tasks", error=str(e))
            return []
    
    def get_pending_update_suggestions(self) -> List[Dict]:
        """Get pending update suggestions for user review"""
        
        try:
            with self.engagement_engine.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT s.id, s.stakeholder_key, s.suggestions, s.created_at,
                           p.display_name
                    FROM stakeholder_update_suggestions s
                    JOIN stakeholder_profiles_enhanced p ON s.stakeholder_key = p.stakeholder_key
                    WHERE s.status = 'pending'
                    ORDER BY s.created_at ASC
                """)
                
                suggestions = []
                for row in cursor.fetchall():
                    suggestion_data = {
                        'suggestion_id': row[0],
                        'stakeholder_key': row[1],
                        'suggestions': json.loads(row[2]),
                        'created_at': row[3],
                        'stakeholder_name': row[4]
                    }
                    suggestions.append(suggestion_data)
                
                return suggestions
                
        except Exception as e:
            self.logger.error("Failed to get pending update suggestions", error=str(e))
            return []


def main():
    """CLI interface for intelligent stakeholder detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Intelligent Stakeholder Detection Engine")
    parser.add_argument("--process-file", help="Process file for stakeholder detection")
    parser.add_argument("--context", help="JSON context for processing")
    parser.add_argument("--show-profiling-tasks", action="store_true", help="Show pending profiling tasks")
    parser.add_argument("--show-update-suggestions", action="store_true", help="Show pending update suggestions")
    
    args = parser.parse_args()
    
    detector = IntelligentStakeholderDetector()
    
    if args.process_file:
        context = json.loads(args.context) if args.context else {}
        
        try:
            with open(args.process_file, 'r') as f:
                content = f.read()
            
            result = detector.process_content_for_stakeholders(content, context)
            
            print("🧠 Intelligent Stakeholder Detection Results:")
            print("=" * 50)
            print(f"📊 Candidates detected: {result['candidates_detected']}")
            print(f"✅ Auto-created: {result['auto_created']}")
            print(f"❓ Profiling needed: {result['profiling_needed']}")
            print(f"🔄 Updates suggested: {result['updates_suggested']}")
            
            if result['actions_taken']:
                print("\n📋 Actions taken:")
                for action in result['actions_taken']:
                    action_emoji = {
                        'auto_created': '✅',
                        'profiling_initiated': '❓',
                        'update_suggested': '🔄',
                        'no_action': 'ℹ️',
                        'low_confidence': '⚠️'
                    }.get(action['type'], '📝')
                    
                    print(f"  {action_emoji} {action['type']}: {action.get('stakeholder_key', 'N/A')}")
                    if action.get('reason'):
                        print(f"     Reason: {action['reason']}")
            
        except FileNotFoundError:
            print(f"❌ File not found: {args.process_file}")
        except Exception as e:
            print(f"❌ Error processing file: {e}")
    
    elif args.show_profiling_tasks:
        tasks = detector.get_pending_profiling_tasks()
        
        print("❓ Pending Stakeholder Profiling Tasks:")
        print("=" * 40)
        
        if not tasks:
            print("No pending profiling tasks.")
            return
        
        for task in tasks:
            print(f"👤 {task['name']} ({task['stakeholder_key']})")
            print(f"   Confidence: {task['confidence']:.1%}")
            print(f"   Questions: {len(task['questions'])}")
            for q in task['questions']:
                print(f"     • {q['question']}")
            print()
    
    elif args.show_update_suggestions:
        suggestions = detector.get_pending_update_suggestions()
        
        print("🔄 Pending Stakeholder Update Suggestions:")
        print("=" * 45)
        
        if not suggestions:
            print("No pending update suggestions.")
            return
        
        for suggestion in suggestions:
            print(f"👤 {suggestion['stakeholder_name']} ({suggestion['stakeholder_key']})")
            print(f"   Suggestions: {len(suggestion['suggestions'])}")
            for s in suggestion['suggestions']:
                print(f"     • {s['type']}: {s['current_value']} → {s['suggested_value']}")
                print(f"       Confidence: {s['confidence']:.1%} - {s['reason']}")
            print()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
