#!/usr/bin/env python3
"""
Intelligent Task Detection Engine
Automatically detect tasks, assignments, and follow-ups from meeting content
"""

import json
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import structlog

logger = structlog.get_logger()


class IntelligentTaskDetector:
    """AI-powered task detection from meeting content and communications"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize with local-only task detection patterns"""
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path(__file__).parent / "strategic_memory.db"
        
        self.logger = logger.bind(component="intelligent_task_detector")
        
        # Local pattern libraries for task detection
        self.task_patterns = self._build_task_patterns()
        self.assignment_patterns = self._build_assignment_patterns()
        self.timeline_patterns = self._build_timeline_patterns()
        self.priority_indicators = self._build_priority_indicators()
        
        # Detection thresholds
        self.AUTO_CREATE_THRESHOLD = 0.8
        self.REVIEW_THRESHOLD = 0.6
        self.MINIMUM_CONFIDENCE = 0.4
    
    def _build_task_patterns(self) -> Dict:
        """Build task detection patterns"""
        return {
            'action_verbs': [
                # Direct assignments
                'will', 'should', 'need to', 'must', 'have to', 'required to',
                # Action items
                'action item', 'todo', 'task', 'deliverable', 'milestone',
                # Follow-ups
                'follow up', 'check in', 'circle back', 'touch base',
                # Platform-specific
                'implement', 'design', 'architect', 'deploy', 'migrate',
                'review', 'analyze', 'investigate', 'research', 'document'
            ],
            'task_indicators': [
                # Explicit task language
                r'\b(?:action item|todo|task|deliverable|milestone)\b',
                r'\b(?:will|should|need to|must|have to|required to)\s+\w+',
                r'\b(?:follow up|check in|circle back|touch base)\b',
                # Assignment patterns
                r'\b\w+\s+(?:will|should|needs? to|must|has to)\s+\w+',
                r'\b(?:assign|delegate|responsible for|owns?|leads?)\b',
                # Timeline indicators
                r'\b(?:by|before|due|deadline|target|deliver)\s+\w+',
                r'\b(?:next week|this week|tomorrow|friday|monday)\b'
            ],
            'exclusions': [
                # Avoid false positives
                'should we', 'could we', 'might we', 'would we',
                'we should consider', 'we could explore', 'we might want'
            ]
        }
    
    def _build_assignment_patterns(self) -> Dict:
        """Build assignment direction detection patterns"""
        return {
            'incoming_to_me': [
                # Direct assignments to me
                r'\byou\s+(?:will|should|need to|must|have to)\s+([^.!?]+)',
                r'\byou\s+(?:are|\'re)\s+(?:responsible for|assigned to|leading)\s+([^.!?]+)',
                r'\bcan you\s+([^.!?]+)',
                r'\byour\s+(?:action|task|responsibility)\s+(?:is|will be)\s+([^.!?]+)',
                # Action items for me
                r'\baction item:\s*you\s+([^.!?]+)',
                r'\btodo:\s*you\s+([^.!?]+)'
            ],
            'outgoing_from_me': [
                # Tasks I assign to others
                r'\bI\s+will\s+ask\s+(\w+)\s+to\s+([^.!?]+)',
                r'\b(\w+)\s+will\s+([^.!?]+)',
                r'\b(\w+)\s+should\s+([^.!?]+)',
                r'\b(\w+)\s+needs? to\s+([^.!?]+)',
                r'\baction item:\s*(\w+)\s+([^.!?]+)',
                r'\btodo:\s*(\w+)\s+([^.!?]+)',
                # Follow-up assignments
                r'\bI\s+will\s+follow up with\s+(\w+)\s+(?:on|about)\s+([^.!?]+)',
                r'\bneed to\s+check with\s+(\w+)\s+(?:on|about)\s+([^.!?]+)'
            ],
            'self_assigned': [
                # Tasks I assign to myself
                r'\bI\s+will\s+([^.!?]+)',
                r'\bI\s+need to\s+([^.!?]+)',
                r'\bI\s+should\s+([^.!?]+)',
                r'\bmy\s+action\s+(?:item|task):\s*([^.!?]+)',
                r'\bI\'ll\s+([^.!?]+)',
                r'\bI\s+have to\s+([^.!?]+)'
            ]
        }
    
    def _build_timeline_patterns(self) -> Dict:
        """Build timeline detection patterns"""
        return {
            'explicit_dates': [
                r'\b(?:by|before|due)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
                r'\b(?:by|before|due)\s+(\d{1,2}\/\d{1,2}\/?\d{0,4})\b',
                r'\b(?:by|before|due)\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b',
                r'\b(?:deadline|target|deliver)\s+(?:is|on|by)?\s*(\w+\s+\d{1,2})\b'
            ],
            'relative_dates': [
                r'\b(tomorrow)\b',
                r'\b(next week)\b',
                r'\b(this week)\b',
                r'\b(end of week)\b',
                r'\b(end of month)\b',
                r'\bin\s+(\d+)\s+(days?|weeks?|months?)\b',
                r'\b(asap|urgent|immediately)\b'
            ],
            'meeting_based': [
                r'\bbefore\s+(?:our|the)\s+next\s+(\w+\s+meeting)\b',
                r'\bby\s+(?:our|the)\s+(\w+\s+meeting)\b',
                r'\bbefore\s+we\s+meet\s+(?:again|next)\b'
            ]
        }
    
    def _build_priority_indicators(self) -> Dict:
        """Build priority detection patterns"""
        return {
            'critical': {
                'keywords': ['urgent', 'asap', 'critical', 'emergency', 'blocker', 'blocking'],
                'patterns': [
                    r'\b(?:urgent|asap|critical|emergency)\b',
                    r'\b(?:blocking|blocker|blocked)\b',
                    r'\bneeds? (?:immediate|urgent) attention\b'
                ],
                'weight': 10
            },
            'high': {
                'keywords': ['important', 'priority', 'key', 'essential', 'must'],
                'patterns': [
                    r'\b(?:important|priority|key|essential)\b',
                    r'\bmust\s+(?:be|get|have)\b',
                    r'\bhigh priority\b'
                ],
                'weight': 7
            },
            'medium': {
                'keywords': ['should', 'need', 'would be good', 'helpful'],
                'patterns': [
                    r'\bshould\s+(?:be|get|have)\b',
                    r'\bneed(?:s)?\s+to\b',
                    r'\bwould be (?:good|helpful|nice)\b'
                ],
                'weight': 5
            },
            'low': {
                'keywords': ['could', 'might', 'eventually', 'someday', 'nice to have'],
                'patterns': [
                    r'\bcould\s+(?:be|get|have)\b',
                    r'\bmight\s+(?:be|get|have)\b',
                    r'\beventually\b',
                    r'\bnice to have\b'
                ],
                'weight': 3
            }
        }
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def detect_tasks_in_content(self, content: str, context: Dict) -> List[Dict]:
        """Detect tasks from content using local AI patterns"""
        
        task_candidates = []
        
        try:
            # Clean and normalize content
            normalized_content = self._normalize_content(content)
            
            # Extract potential tasks using different patterns
            incoming_tasks = self._extract_incoming_tasks(normalized_content)
            outgoing_tasks = self._extract_outgoing_tasks(normalized_content)
            self_tasks = self._extract_self_assigned_tasks(normalized_content)
            
            # Process all detected tasks
            all_tasks = []
            all_tasks.extend([(task, 'incoming') for task in incoming_tasks])
            all_tasks.extend([(task, 'outgoing') for task in outgoing_tasks])
            all_tasks.extend([(task, 'self_assigned') for task in self_tasks])
            
            for task_text, assignment_direction in all_tasks:
                analysis = self._analyze_task_candidate(task_text, assignment_direction, normalized_content, context)
                
                if analysis['confidence_score'] >= self.MINIMUM_CONFIDENCE:
                    task_candidates.append(analysis)
            
            # Sort by confidence score
            task_candidates.sort(key=lambda x: x['confidence_score'], reverse=True)
            
            self.logger.info("Detected task candidates", 
                           count=len(task_candidates),
                           high_confidence=len([t for t in task_candidates if t['confidence_score'] >= self.AUTO_CREATE_THRESHOLD]))
            
            return task_candidates
            
        except Exception as e:
            self.logger.error("Failed to detect tasks in content", error=str(e))
            return []
    
    def _normalize_content(self, content: str) -> str:
        """Normalize content for better analysis"""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove markdown formatting but preserve structure
        content = re.sub(r'[*_`]', '', content)
        
        # Normalize bullet points
        content = re.sub(r'^[-*•]\s+', '• ', content, flags=re.MULTILINE)
        
        return content.strip()
    
    def _extract_incoming_tasks(self, content: str) -> List[str]:
        """Extract tasks assigned TO me"""
        tasks = []
        
        for pattern in self.assignment_patterns['incoming_to_me']:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if match.groups():
                    task_text = match.group(1).strip()
                    if self._is_valid_task(task_text):
                        tasks.append(task_text)
        
        return self._deduplicate_tasks(tasks)
    
    def _extract_outgoing_tasks(self, content: str) -> List[Tuple[str, str]]:
        """Extract tasks assigned BY me to others"""
        tasks = []
        
        for pattern in self.assignment_patterns['outgoing_from_me']:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.groups()) >= 2:
                    assignee = match.group(1).strip()
                    task_text = match.group(2).strip()
                    if self._is_valid_task(task_text) and self._is_valid_assignee(assignee):
                        tasks.append((task_text, assignee))
        
        return tasks
    
    def _extract_self_assigned_tasks(self, content: str) -> List[str]:
        """Extract tasks I assign to myself"""
        tasks = []
        
        for pattern in self.assignment_patterns['self_assigned']:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if match.groups():
                    task_text = match.group(1).strip()
                    if self._is_valid_task(task_text):
                        tasks.append(task_text)
        
        return self._deduplicate_tasks(tasks)
    
    def _is_valid_task(self, task_text: str) -> bool:
        """Validate if text represents a meaningful task"""
        # Minimum length
        if len(task_text) < 5 or len(task_text) > 200:
            return False
        
        # Check for exclusion patterns
        task_lower = task_text.lower()
        for exclusion in self.task_patterns['exclusions']:
            if exclusion in task_lower:
                return False
        
        # Must contain action-oriented language
        has_action = any(verb in task_lower for verb in self.task_patterns['action_verbs'])
        if not has_action:
            return False
        
        # Avoid questions and hypotheticals
        if task_text.strip().endswith('?'):
            return False
        
        return True
    
    def _is_valid_assignee(self, assignee: str) -> bool:
        """Validate if text represents a valid assignee"""
        # Length check
        if len(assignee) < 2 or len(assignee) > 50:
            return False
        
        # Should look like a name or role
        if re.match(r'^[A-Za-z][A-Za-z\s.-]+$', assignee):
            return True
        
        return False
    
    def _deduplicate_tasks(self, tasks: List[str]) -> List[str]:
        """Remove duplicate and very similar tasks"""
        if not tasks:
            return []
        
        unique_tasks = []
        for task in tasks:
            # Simple deduplication by similarity
            is_duplicate = False
            for existing in unique_tasks:
                if self._tasks_similar(task, existing):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_tasks.append(task)
        
        return unique_tasks
    
    def _tasks_similar(self, task1: str, task2: str, threshold: float = 0.8) -> bool:
        """Check if two tasks are similar enough to be considered duplicates"""
        # Simple word-based similarity
        words1 = set(task1.lower().split())
        words2 = set(task2.lower().split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = intersection / union if union > 0 else 0
        return similarity >= threshold
    
    def _analyze_task_candidate(self, task_text: str, assignment_direction: str, full_content: str, context: Dict) -> Dict:
        """Analyze a task candidate and extract metadata"""
        
        analysis = {
            'task_text': task_text,
            'assignment_direction': assignment_direction,
            'assignee': None,
            'priority': 'medium',
            'priority_score': 5,
            'due_date': None,
            'category': 'operational',
            'impact_scope': 'individual',
            'follow_up_required': False,
            'confidence_score': 0.0,
            'source_context': context,
            'detection_metadata': {}
        }
        
        # Extract assignee for outgoing tasks
        if assignment_direction == 'outgoing' and isinstance(task_text, tuple):
            analysis['task_text'] = task_text[0]
            analysis['assignee'] = task_text[1]
        
        # Analyze priority
        priority_analysis = self._analyze_priority(task_text, full_content)
        analysis['priority'] = priority_analysis['level']
        analysis['priority_score'] = priority_analysis['score']
        
        # Analyze timeline
        timeline_analysis = self._analyze_timeline(task_text, full_content)
        analysis['due_date'] = timeline_analysis.get('due_date')
        
        # Analyze category and scope
        category_analysis = self._analyze_category_and_scope(task_text, context)
        analysis['category'] = category_analysis['category']
        analysis['impact_scope'] = category_analysis['scope']
        
        # Determine if follow-up is required
        analysis['follow_up_required'] = self._requires_follow_up(task_text, assignment_direction)
        
        # Calculate confidence score
        analysis['confidence_score'] = self._calculate_task_confidence(analysis, full_content, context)
        
        return analysis
    
    def _analyze_priority(self, task_text: str, full_content: str) -> Dict:
        """Analyze task priority based on language patterns"""
        
        task_context = self._extract_task_context(task_text, full_content, window=100)
        combined_text = f"{task_text} {task_context}".lower()
        
        best_priority = 'medium'
        best_score = 5
        
        for priority_level, priority_data in self.priority_indicators.items():
            score = 0
            
            # Check keywords
            for keyword in priority_data['keywords']:
                if keyword in combined_text:
                    score += priority_data['weight']
            
            # Check patterns
            for pattern in priority_data['patterns']:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    score += priority_data['weight']
            
            if score > best_score:
                best_score = score
                best_priority = priority_level
        
        return {
            'level': best_priority,
            'score': best_score
        }
    
    def _analyze_timeline(self, task_text: str, full_content: str) -> Dict:
        """Analyze task timeline and due dates"""
        
        task_context = self._extract_task_context(task_text, full_content, window=150)
        combined_text = f"{task_text} {task_context}"
        
        timeline_info = {}
        
        # Look for explicit dates
        for pattern in self.timeline_patterns['explicit_dates']:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                date_text = match.group(1)
                parsed_date = self._parse_date_text(date_text)
                if parsed_date:
                    timeline_info['due_date'] = parsed_date
                    break
        
        # Look for relative dates if no explicit date found
        if 'due_date' not in timeline_info:
            for pattern in self.timeline_patterns['relative_dates']:
                match = re.search(pattern, combined_text, re.IGNORECASE)
                if match:
                    relative_text = match.group(1)
                    parsed_date = self._parse_relative_date(relative_text)
                    if parsed_date:
                        timeline_info['due_date'] = parsed_date
                        break
        
        return timeline_info
    
    def _analyze_category_and_scope(self, task_text: str, context: Dict) -> Dict:
        """Analyze task category and impact scope"""
        
        task_lower = task_text.lower()
        
        # Determine category
        category = 'operational'  # default
        
        if any(word in task_lower for word in ['platform', 'architecture', 'system', 'infrastructure']):
            category = 'platform_initiative'
        elif any(word in task_lower for word in ['follow up', 'check in', 'circle back', 'touch base']):
            category = 'stakeholder_followup'
        elif any(word in task_lower for word in ['strategic', 'roadmap', 'vision', 'planning']):
            category = 'strategic_project'
        
        # Determine scope
        scope = 'individual'  # default
        
        if any(word in task_lower for word in ['platform', 'all teams', 'organization', 'company']):
            scope = 'platform_wide'
        elif any(word in task_lower for word in ['cross-team', 'multiple teams', 'coordination']):
            scope = 'cross_team'
        elif any(word in task_lower for word in ['team', 'group', 'department']):
            scope = 'single_team'
        
        # Context-based adjustments
        if context.get('meeting_type') in ['vp_1on1', 'strategic_planning']:
            if category == 'operational':
                category = 'strategic_project'
            if scope == 'individual':
                scope = 'cross_team'
        
        return {
            'category': category,
            'scope': scope
        }
    
    def _requires_follow_up(self, task_text: str, assignment_direction: str) -> bool:
        """Determine if task requires follow-up"""
        
        task_lower = task_text.lower()
        
        # Explicit follow-up language
        follow_up_indicators = [
            'follow up', 'check in', 'circle back', 'touch base',
            'get back to', 'update on', 'report back'
        ]
        
        if any(indicator in task_lower for indicator in follow_up_indicators):
            return True
        
        # Outgoing tasks typically require follow-up
        if assignment_direction == 'outgoing':
            return True
        
        # High-impact tasks require follow-up
        if any(word in task_lower for word in ['platform', 'strategic', 'critical', 'important']):
            return True
        
        return False
    
    def _extract_task_context(self, task_text: str, full_content: str, window: int = 100) -> str:
        """Extract context around task mention"""
        
        # Find task in content
        task_pos = full_content.lower().find(task_text.lower())
        if task_pos == -1:
            return ""
        
        # Extract window around task
        start = max(0, task_pos - window)
        end = min(len(full_content), task_pos + len(task_text) + window)
        
        return full_content[start:end]
    
    def _parse_date_text(self, date_text: str) -> Optional[str]:
        """Parse date text into ISO format"""
        
        # Handle weekdays (relative to current week)
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        date_lower = date_text.lower()
        if date_lower in weekdays:
            today = datetime.now()
            target_weekday = weekdays[date_lower]
            current_weekday = today.weekday()
            
            days_ahead = target_weekday - current_weekday
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7  # Next week
            
            target_date = today + timedelta(days=days_ahead)
            return target_date.strftime('%Y-%m-%d')
        
        # Handle MM/DD or MM/DD/YY formats
        date_patterns = [
            r'(\d{1,2})\/(\d{1,2})\/(\d{2,4})',
            r'(\d{1,2})\/(\d{1,2})'
        ]
        
        for pattern in date_patterns:
            match = re.match(pattern, date_text)
            if match:
                try:
                    month = int(match.group(1))
                    day = int(match.group(2))
                    
                    if len(match.groups()) >= 3:
                        year = int(match.group(3))
                        if year < 100:
                            year += 2000
                    else:
                        year = datetime.now().year
                        # If date has passed this year, assume next year
                        test_date = datetime(year, month, day)
                        if test_date < datetime.now():
                            year += 1
                    
                    target_date = datetime(year, month, day)
                    return target_date.strftime('%Y-%m-%d')
                
                except ValueError:
                    continue
        
        return None
    
    def _parse_relative_date(self, relative_text: str) -> Optional[str]:
        """Parse relative date text into ISO format"""
        
        today = datetime.now()
        relative_lower = relative_text.lower()
        
        if relative_lower == 'tomorrow':
            target_date = today + timedelta(days=1)
        elif relative_lower == 'next week':
            # Next Monday
            days_ahead = 7 - today.weekday()
            target_date = today + timedelta(days=days_ahead)
        elif relative_lower == 'this week':
            # End of this week (Friday)
            days_ahead = 4 - today.weekday()
            if days_ahead < 0:
                days_ahead = 0  # Already past Friday
            target_date = today + timedelta(days=days_ahead)
        elif relative_lower == 'end of week':
            # Friday
            days_ahead = 4 - today.weekday()
            if days_ahead < 0:
                days_ahead += 7  # Next Friday
            target_date = today + timedelta(days=days_ahead)
        elif relative_lower == 'end of month':
            # Last day of current month
            next_month = today.replace(day=28) + timedelta(days=4)
            target_date = next_month - timedelta(days=next_month.day)
        elif relative_lower in ['asap', 'urgent', 'immediately']:
            # Today
            target_date = today
        else:
            # Try to parse "in X days/weeks/months"
            match = re.match(r'in\s+(\d+)\s+(days?|weeks?|months?)', relative_lower)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                
                if unit.startswith('day'):
                    target_date = today + timedelta(days=amount)
                elif unit.startswith('week'):
                    target_date = today + timedelta(weeks=amount)
                elif unit.startswith('month'):
                    target_date = today + timedelta(days=amount * 30)  # Approximate
                else:
                    return None
            else:
                return None
        
        return target_date.strftime('%Y-%m-%d')
    
    def _calculate_task_confidence(self, analysis: Dict, full_content: str, context: Dict) -> float:
        """Calculate confidence score for task detection"""
        
        score = 0.0
        
        # Base task clarity (40%)
        task_text = analysis['task_text']
        
        # Length and clarity
        if 10 <= len(task_text) <= 100:
            score += 0.2
        elif 5 <= len(task_text) <= 150:
            score += 0.1
        
        # Action-oriented language
        action_verbs = ['implement', 'design', 'review', 'update', 'create', 'build', 'fix', 'analyze']
        if any(verb in task_text.lower() for verb in action_verbs):
            score += 0.2
        
        # Assignment direction clarity (25%)
        if analysis['assignment_direction'] == 'incoming':
            score += 0.15  # Clear assignments to me
        elif analysis['assignment_direction'] == 'outgoing' and analysis['assignee']:
            score += 0.20  # Clear assignments to others
        elif analysis['assignment_direction'] == 'self_assigned':
            score += 0.10  # Self-assignments are less explicit
        
        # Context relevance (20%)
        if context.get('category') == 'meeting_prep':
            score += 0.1
        
        if context.get('meeting_type') in ['vp_1on1', 'strategic_planning']:
            score += 0.1
        
        # Priority and timeline indicators (15%)
        if analysis['priority'] != 'medium':
            score += 0.075
        
        if analysis['due_date']:
            score += 0.075
        
        return min(1.0, score)


def main():
    """CLI interface for intelligent task detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Intelligent Task Detection Engine")
    parser.add_argument("--analyze-content", help="Analyze content for tasks")
    parser.add_argument("--context", help="JSON context for analysis")
    
    args = parser.parse_args()
    
    detector = IntelligentTaskDetector()
    
    if args.analyze_content:
        context = json.loads(args.context) if args.context else {}
        
        try:
            with open(args.analyze_content, 'r') as f:
                content = f.read()
            
            tasks = detector.detect_tasks_in_content(content, context)
            
            print("🎯 Intelligent Task Detection Results:")
            print("=" * 45)
            
            if not tasks:
                print("No tasks detected in content.")
                return
            
            for i, task in enumerate(tasks, 1):
                confidence_emoji = "🟢" if task['confidence_score'] >= 0.8 else "🟡" if task['confidence_score'] >= 0.6 else "🔴"
                direction_emoji = {"incoming": "📥", "outgoing": "📤", "self_assigned": "📝"}[task['assignment_direction']]
                
                print(f"{confidence_emoji} {direction_emoji} Task {i}: {task['task_text']}")
                print(f"   Direction: {task['assignment_direction']}")
                print(f"   Priority: {task['priority']}")
                print(f"   Category: {task['category']}")
                print(f"   Scope: {task['impact_scope']}")
                print(f"   Confidence: {task['confidence_score']:.1%}")
                
                if task.get('assignee'):
                    print(f"   Assignee: {task['assignee']}")
                
                if task.get('due_date'):
                    print(f"   Due Date: {task['due_date']}")
                
                if task['follow_up_required']:
                    print(f"   Follow-up Required: Yes")
                
                print()
        
        except FileNotFoundError:
            print(f"❌ File not found: {args.analyze_content}")
        except Exception as e:
            print(f"❌ Error analyzing content: {e}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
