#!/usr/bin/env python3
"""
Local Stakeholder Intelligence Engine
Privacy-first automated stakeholder detection and profiling with local-only processing
"""

import json
import re
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import structlog

logger = structlog.get_logger()


class LocalStakeholderAI:
    """Local-only AI engine for stakeholder detection and profiling"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize with local-only components"""
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path(__file__).parent / "strategic_memory.db"
        
        self.logger = logger.bind(component="local_stakeholder_ai")
        
        # Local pattern libraries - no external dependencies
        self.name_patterns = self._build_name_patterns()
        self.role_patterns = self._build_role_patterns()
        self.importance_indicators = self._build_importance_indicators()
        self.communication_patterns = self._build_communication_patterns()
        
        # Detection thresholds
        self.AUTO_CREATE_THRESHOLD = 0.85
        self.PROFILING_THRESHOLD = 0.65
        self.UPDATE_THRESHOLD = 0.75
    
    def _build_name_patterns(self) -> Dict:
        """Build local name detection patterns"""
        return {
            'name_prefixes': ['dr', 'dr.', 'professor', 'prof', 'mr', 'ms', 'mrs'],
            'name_indicators': [
                r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # FirstName LastName
                r'\b[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+\b',  # FirstName M. LastName
                r'\b[A-Z]\. [A-Z][a-z]+\b',  # F. LastName
            ],
            'email_patterns': [
                r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
            ],
            'exclusions': [
                'engineering', 'product', 'design', 'marketing', 'legal',
                'meeting', 'project', 'initiative', 'team', 'group'
            ]
        }
    
    def _build_role_patterns(self) -> Dict:
        """Build local role classification patterns"""
        return {
            'executive': {
                'titles': ['ceo', 'cto', 'cfo', 'coo', 'vp', 'vice president', 'svp', 'evp', 'chief'],
                'weight': 10,
                'importance': 'critical'
            },
            'director': {
                'titles': ['director', 'dir', 'head of', 'principal director'],
                'weight': 8,
                'importance': 'high'
            },
            'manager': {
                'titles': ['manager', 'mgr', 'team lead', 'engineering manager', 'product manager', 'program manager'],
                'weight': 6,
                'importance': 'high'
            },
            'principal': {
                'titles': ['principal', 'staff', 'senior staff', 'distinguished', 'architect'],
                'weight': 7,
                'importance': 'medium'
            },
            'senior': {
                'titles': ['senior', 'sr', 'lead'],
                'weight': 5,
                'importance': 'medium'
            },
            'external': {
                'titles': ['vendor', 'client', 'partner', 'contractor', 'consultant'],
                'weight': 4,
                'importance': 'medium'
            }
        }
    
    def _build_importance_indicators(self) -> Dict:
        """Build strategic importance detection patterns"""
        return {
            'high_impact_keywords': {
                'budget': 3, 'funding': 3, 'investment': 3, 'cost': 2,
                'decision': 2, 'approval': 2, 'sign-off': 2, 'authorize': 2,
                'strategy': 2, 'roadmap': 2, 'vision': 2, 'direction': 2,
                'escalation': 2, 'escalate': 2, 'emergency': 2, 'urgent': 1
            },
            'cross_functional_indicators': {
                'cross-team': 2, 'cross-functional': 2, 'coordination': 1,
                'alignment': 1, 'stakeholder': 1, 'dependency': 1
            },
            'meeting_frequency_boost': {
                'weekly': 2, 'daily': 3, 'regular': 1, 'recurring': 1,
                '1-on-1': 2, 'one-on-one': 2, 'sync': 1
            },
            'project_involvement': {
                'owner': 3, 'lead': 2, 'responsible': 2, 'accountable': 2,
                'sponsor': 3, 'champion': 2, 'driver': 2
            }
        }
    
    def _build_communication_patterns(self) -> Dict:
        """Build communication preference detection patterns"""
        return {
            'channel_indicators': {
                'slack': ['slack', 'dm', 'channel', 'ping'],
                'email': ['email', 'send', 'mail', 'inbox'],
                'meeting': ['meeting', 'call', 'zoom', 'video', 'conference'],
                'in_person': ['in-person', 'office', 'desk', 'face-to-face']
            },
            'style_indicators': {
                'data_driven': ['metrics', 'data', 'numbers', 'analytics', 'roi', 'kpi'],
                'visual': ['diagram', 'chart', 'visual', 'presentation', 'slide'],
                'narrative': ['story', 'context', 'background', 'explain', 'walkthrough'],
                'direct': ['brief', 'quick', 'summary', 'tldr', 'bottom-line'],
                'collaborative': ['discuss', 'brainstorm', 'workshop', 'session', 'together']
            }
        }
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def detect_stakeholders_in_content(self, content: str, context: Dict) -> List[Dict]:
        """Detect potential stakeholders in content using local NLP"""
        
        stakeholder_candidates = []
        
        try:
            # Clean and normalize content
            normalized_content = self._normalize_content(content)
            
            # Extract potential names
            potential_names = self._extract_names(normalized_content)
            
            # Analyze each potential stakeholder
            for name in potential_names:
                analysis = self._analyze_stakeholder_candidate(name, normalized_content, context)
                
                if analysis['confidence_score'] >= self.PROFILING_THRESHOLD:
                    stakeholder_candidates.append(analysis)
            
            # Sort by confidence score
            stakeholder_candidates.sort(key=lambda x: x['confidence_score'], reverse=True)
            
            self.logger.info("Detected stakeholder candidates", 
                           count=len(stakeholder_candidates),
                           high_confidence=len([s for s in stakeholder_candidates if s['confidence_score'] >= self.AUTO_CREATE_THRESHOLD]))
            
            return stakeholder_candidates
            
        except Exception as e:
            self.logger.error("Failed to detect stakeholders in content", error=str(e))
            return []
    
    def _normalize_content(self, content: str) -> str:
        """Normalize content for better analysis"""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove markdown formatting
        content = re.sub(r'[#*`_]', '', content)
        
        # Normalize case for analysis while preserving names
        return content.strip()
    
    def _extract_names(self, content: str) -> Set[str]:
        """Extract potential names using local regex patterns"""
        potential_names = set()
        
        # Extract from various name patterns
        for pattern in self.name_patterns['name_indicators']:
            matches = re.findall(pattern, content)
            potential_names.update(matches)
        
        # Extract from email addresses
        for email_pattern in self.name_patterns['email_patterns']:
            email_matches = re.findall(email_pattern, content)
            for email in email_matches:
                # Extract name part before @
                name_part = email.split('@')[0]
                # Convert dot/underscore separated to proper name
                if '.' in name_part:
                    name_parts = name_part.split('.')
                    if len(name_parts) == 2:
                        potential_name = f"{name_parts[0].title()} {name_parts[1].title()}"
                        potential_names.add(potential_name)
        
        # Filter out obvious non-names
        filtered_names = set()
        for name in potential_names:
            if not self._is_excluded_name(name.lower()):
                filtered_names.add(name)
        
        return filtered_names
    
    def _is_excluded_name(self, name: str) -> bool:
        """Check if name should be excluded"""
        name_lower = name.lower()
        
        # Check against exclusion list
        for exclusion in self.name_patterns['exclusions']:
            if exclusion in name_lower:
                return True
        
        # Must have at least one capital letter (proper name)
        if not any(c.isupper() for c in name):
            return True
        
        # Must be reasonable length
        if len(name) < 3 or len(name) > 50:
            return True
        
        return False
    
    def _analyze_stakeholder_candidate(self, name: str, content: str, context: Dict) -> Dict:
        """Analyze a potential stakeholder candidate"""
        
        analysis = {
            'name': name,
            'stakeholder_key': self._generate_stakeholder_key(name),
            'detected_role': None,
            'role_confidence': 0.0,
            'strategic_importance': 'medium',
            'importance_score': 0.0,
            'communication_preferences': {},
            'context_indicators': [],
            'confidence_score': 0.0,
            'source_context': context
        }
        
        # Analyze role indicators
        role_analysis = self._analyze_role_indicators(name, content)
        analysis['detected_role'] = role_analysis['role']
        analysis['role_confidence'] = role_analysis['confidence']
        
        # Analyze strategic importance
        importance_analysis = self._analyze_importance_indicators(name, content, context)
        analysis['strategic_importance'] = importance_analysis['level']
        analysis['importance_score'] = importance_analysis['score']
        
        # Analyze communication preferences
        comm_analysis = self._analyze_communication_patterns(name, content)
        analysis['communication_preferences'] = comm_analysis
        
        # Calculate overall confidence
        analysis['confidence_score'] = self._calculate_confidence_score(analysis)
        
        return analysis
    
    def _generate_stakeholder_key(self, name: str) -> str:
        """Generate a stakeholder key from name"""
        # Convert "John Smith" to "john_smith"
        key = name.lower().replace(' ', '_').replace('.', '').replace('-', '_')
        # Remove any special characters
        key = re.sub(r'[^a-z0-9_]', '', key)
        return key
    
    def _analyze_role_indicators(self, name: str, content: str) -> Dict:
        """Analyze role indicators around the name"""
        
        # Look for role indicators near the name
        name_context = self._extract_name_context(name, content, window=50)
        
        best_role = None
        best_score = 0.0
        
        for role_category, role_data in self.role_patterns.items():
            score = 0.0
            
            for title in role_data['titles']:
                # Case-insensitive search
                if title.lower() in name_context.lower():
                    score += role_data['weight']
            
            if score > best_score:
                best_score = score
                best_role = role_category
        
        # Normalize confidence
        max_possible_score = max(role_data['weight'] for role_data in self.role_patterns.values())
        confidence = min(1.0, best_score / max_possible_score) if best_score > 0 else 0.0
        
        return {
            'role': best_role,
            'confidence': confidence,
            'raw_score': best_score
        }
    
    def _analyze_importance_indicators(self, name: str, content: str, context: Dict) -> Dict:
        """Analyze strategic importance indicators"""
        
        name_context = self._extract_name_context(name, content, window=100)
        
        total_score = 0.0
        
        # Check various importance indicators
        for category, indicators in self.importance_indicators.items():
            for indicator, weight in indicators.items():
                if indicator.lower() in name_context.lower():
                    total_score += weight
        
        # Context-based scoring
        if context.get('file_type') == 'vp_meeting':
            total_score += 2
        elif context.get('file_type') == 'strategic_planning':
            total_score += 1
        
        # Determine importance level
        if total_score >= 8:
            level = 'critical'
        elif total_score >= 5:
            level = 'high'
        elif total_score >= 2:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'level': level,
            'score': total_score
        }
    
    def _analyze_communication_patterns(self, name: str, content: str) -> Dict:
        """Analyze communication preferences from content"""
        
        name_context = self._extract_name_context(name, content, window=150)
        
        preferences = {
            'channels': [],
            'style': None,
            'frequency_indicators': []
        }
        
        # Detect preferred channels
        for channel, indicators in self.communication_patterns['channel_indicators'].items():
            for indicator in indicators:
                if indicator.lower() in name_context.lower():
                    preferences['channels'].append(channel)
        
        # Detect communication style
        style_scores = {}
        for style, indicators in self.communication_patterns['style_indicators'].items():
            score = sum(1 for indicator in indicators if indicator.lower() in name_context.lower())
            if score > 0:
                style_scores[style] = score
        
        if style_scores:
            preferences['style'] = max(style_scores, key=style_scores.get)
        
        # Remove duplicates and limit
        preferences['channels'] = list(set(preferences['channels']))[:3]
        
        return preferences
    
    def _extract_name_context(self, name: str, content: str, window: int = 100) -> str:
        """Extract context around a name mention"""
        
        # Find all occurrences of the name
        contexts = []
        content_lower = content.lower()
        name_lower = name.lower()
        
        start = 0
        while True:
            pos = content_lower.find(name_lower, start)
            if pos == -1:
                break
            
            # Extract window around the name
            context_start = max(0, pos - window)
            context_end = min(len(content), pos + len(name) + window)
            context = content[context_start:context_end]
            contexts.append(context)
            
            start = pos + 1
        
        return ' '.join(contexts)
    
    def _calculate_confidence_score(self, analysis: Dict) -> float:
        """Calculate overall confidence score for stakeholder detection"""
        
        score = 0.0
        
        # Role confidence contributes 40%
        score += analysis['role_confidence'] * 0.4
        
        # Importance score contributes 30%
        importance_normalized = min(1.0, analysis['importance_score'] / 10.0)
        score += importance_normalized * 0.3
        
        # Communication preferences contribute 20%
        comm_score = 0.0
        if analysis['communication_preferences']['channels']:
            comm_score += 0.5
        if analysis['communication_preferences']['style']:
            comm_score += 0.5
        score += comm_score * 0.2
        
        # Context relevance contributes 10%
        context_score = 0.0
        if analysis['source_context'].get('category') == 'meeting_prep':
            context_score += 0.5
        if analysis['source_context'].get('meeting_type') in ['vp_1on1', 'strategic_planning']:
            context_score += 0.5
        score += context_score * 0.1
        
        return min(1.0, score)
    
    def check_existing_stakeholder(self, stakeholder_key: str) -> Optional[Dict]:
        """Check if stakeholder already exists"""
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT stakeholder_key, display_name, role_title, strategic_importance,
                           optimal_meeting_frequency, preferred_communication_channels,
                           communication_style, most_effective_personas
                    FROM stakeholder_profiles_enhanced
                    WHERE stakeholder_key = ?
                """, (stakeholder_key,))
                
                row = cursor.fetchone()
                
                if row:
                    return {
                        'stakeholder_key': row[0],
                        'display_name': row[1],
                        'role_title': row[2],
                        'strategic_importance': row[3],
                        'optimal_meeting_frequency': row[4],
                        'preferred_communication_channels': json.loads(row[5]) if row[5] else [],
                        'communication_style': row[6],
                        'most_effective_personas': json.loads(row[7]) if row[7] else []
                    }
                
                return None
                
        except Exception as e:
            self.logger.error("Failed to check existing stakeholder", 
                            stakeholder_key=stakeholder_key, error=str(e))
            return None
    
    def suggest_stakeholder_updates(self, stakeholder_key: str, new_analysis: Dict) -> List[Dict]:
        """Suggest updates to existing stakeholder based on new analysis"""
        
        existing = self.check_existing_stakeholder(stakeholder_key)
        if not existing:
            return []
        
        suggestions = []
        
        # Check for role changes
        if (new_analysis.get('detected_role') and 
            new_analysis['role_confidence'] > 0.7 and
            new_analysis['detected_role'] != existing.get('role_title')):
            
            suggestions.append({
                'type': 'role_update',
                'field': 'role_title',
                'current_value': existing.get('role_title'),
                'suggested_value': new_analysis['detected_role'],
                'confidence': new_analysis['role_confidence'],
                'reason': 'Role change detected in recent content'
            })
        
        # Check for importance changes
        if (new_analysis.get('strategic_importance') != existing.get('strategic_importance') and
            new_analysis.get('importance_score', 0) > 5):
            
            suggestions.append({
                'type': 'importance_update',
                'field': 'strategic_importance',
                'current_value': existing.get('strategic_importance'),
                'suggested_value': new_analysis['strategic_importance'],
                'confidence': new_analysis['importance_score'] / 10.0,
                'reason': 'Strategic importance indicators changed'
            })
        
        # Check for communication preference updates
        new_channels = new_analysis.get('communication_preferences', {}).get('channels', [])
        existing_channels = existing.get('preferred_communication_channels', [])
        
        if new_channels and set(new_channels) != set(existing_channels):
            suggestions.append({
                'type': 'communication_update',
                'field': 'preferred_communication_channels',
                'current_value': existing_channels,
                'suggested_value': list(set(existing_channels + new_channels)),
                'confidence': 0.6,
                'reason': 'New communication patterns detected'
            })
        
        return suggestions


def main():
    """CLI interface for local stakeholder AI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Local Stakeholder AI Engine")
    parser.add_argument("--analyze-content", help="Analyze content for stakeholders")
    parser.add_argument("--context", help="JSON context for analysis")
    parser.add_argument("--check-stakeholder", help="Check existing stakeholder")
    
    args = parser.parse_args()
    
    ai_engine = LocalStakeholderAI()
    
    if args.analyze_content:
        context = json.loads(args.context) if args.context else {}
        
        with open(args.analyze_content, 'r') as f:
            content = f.read()
        
        candidates = ai_engine.detect_stakeholders_in_content(content, context)
        
        print("🧠 Local Stakeholder Detection Results:")
        print("=" * 45)
        
        for candidate in candidates:
            confidence_emoji = "🟢" if candidate['confidence_score'] >= 0.8 else "🟡" if candidate['confidence_score'] >= 0.6 else "🔴"
            
            print(f"{confidence_emoji} {candidate['name']} ({candidate['stakeholder_key']})")
            print(f"   Role: {candidate['detected_role']} (confidence: {candidate['role_confidence']:.1%})")
            print(f"   Importance: {candidate['strategic_importance']} (score: {candidate['importance_score']:.1f})")
            print(f"   Overall Confidence: {candidate['confidence_score']:.1%}")
            
            if candidate['communication_preferences']['channels']:
                print(f"   Preferred Channels: {', '.join(candidate['communication_preferences']['channels'])}")
            
            if candidate['communication_preferences']['style']:
                print(f"   Communication Style: {candidate['communication_preferences']['style']}")
            
            print()
    
    elif args.check_stakeholder:
        stakeholder = ai_engine.check_existing_stakeholder(args.check_stakeholder)
        
        if stakeholder:
            print(f"✅ Found stakeholder: {stakeholder['display_name']}")
            print(f"   Role: {stakeholder['role_title']}")
            print(f"   Importance: {stakeholder['strategic_importance']}")
        else:
            print(f"❌ Stakeholder '{args.check_stakeholder}' not found")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
