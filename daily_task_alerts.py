#!/usr/bin/env python3
"""
Daily Task Alerts System
Proactive reminder system for strategic task management and accountability
"""

import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import structlog

logger = structlog.get_logger()


class DailyTaskAlerts:
    """Proactive task reminder and escalation system"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize alert system"""
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path("memory/strategic_memory.db")
        
        self.logger = logger.bind(component="daily_task_alerts")
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def generate_daily_alerts(self) -> Dict:
        """Generate comprehensive daily task alerts"""
        
        alerts = {
            'critical_overdue': [],
            'due_today': [],
            'follow_ups_urgent': [],
            'assigned_task_updates': [],
            'escalation_needed': [],
            'summary': {}
        }
        
        try:
            # Critical overdue tasks
            alerts['critical_overdue'] = self._get_critical_overdue_tasks()
            
            # Tasks due today
            alerts['due_today'] = self._get_tasks_due_today()
            
            # Urgent follow-ups
            alerts['follow_ups_urgent'] = self._get_urgent_follow_ups()
            
            # Tasks assigned to others needing updates
            alerts['assigned_task_updates'] = self._get_assigned_tasks_needing_updates()
            
            # Tasks needing escalation
            alerts['escalation_needed'] = self._get_tasks_needing_escalation()
            
            # Generate summary
            alerts['summary'] = self._generate_alert_summary(alerts)
            
            self.logger.info("Generated daily task alerts", 
                           critical_count=len(alerts['critical_overdue']),
                           due_today_count=len(alerts['due_today']),
                           follow_up_count=len(alerts['follow_ups_urgent']))
            
            return alerts
            
        except Exception as e:
            self.logger.error("Failed to generate daily alerts", error=str(e))
            return alerts
    
    def _get_critical_overdue_tasks(self) -> List[Dict]:
        """Get critically overdue tasks"""
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT t.id, t.title, t.priority, t.due_date, t.assignment_direction,
                           t.assigned_to, s.display_name,
                           (julianday('now') - julianday(t.due_date)) as days_overdue
                    FROM strategic_tasks t
                    LEFT JOIN stakeholder_profiles_enhanced s ON t.assigned_to = s.stakeholder_key
                    WHERE t.status = 'active' 
                        AND t.due_date < date('now')
                        AND t.priority IN ('critical', 'high')
                    ORDER BY 
                        CASE t.priority 
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2
                        END,
                        days_overdue DESC
                """)
                
                tasks = []
                for row in cursor.fetchall():
                    task_id, title, priority, due_date, direction, assigned_to, assignee_name, days_overdue = row
                    
                    tasks.append({
                        'task_id': task_id,
                        'title': title,
                        'priority': priority,
                        'due_date': due_date,
                        'assignment_direction': direction,
                        'assigned_to': assigned_to,
                        'assignee_name': assignee_name or assigned_to,
                        'days_overdue': int(days_overdue),
                        'urgency_level': 'critical' if days_overdue > 7 else 'high'
                    })
                
                return tasks
                
        except Exception as e:
            self.logger.error("Failed to get critical overdue tasks", error=str(e))
            return []
    
    def _get_tasks_due_today(self) -> List[Dict]:
        """Get tasks due today"""
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT t.id, t.title, t.priority, t.assignment_direction,
                           t.assigned_to, s.display_name, t.category
                    FROM strategic_tasks t
                    LEFT JOIN stakeholder_profiles_enhanced s ON t.assigned_to = s.stakeholder_key
                    WHERE t.status = 'active' 
                        AND date(t.due_date) = date('now')
                    ORDER BY 
                        CASE t.priority 
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2  
                            WHEN 'medium' THEN 3
                            WHEN 'low' THEN 4
                        END
                """)
                
                tasks = []
                for row in cursor.fetchall():
                    task_id, title, priority, direction, assigned_to, assignee_name, category = row
                    
                    tasks.append({
                        'task_id': task_id,
                        'title': title,
                        'priority': priority,
                        'assignment_direction': direction,
                        'assigned_to': assigned_to,
                        'assignee_name': assignee_name or assigned_to,
                        'category': category
                    })
                
                return tasks
                
        except Exception as e:
            self.logger.error("Failed to get tasks due today", error=str(e))
            return []
    
    def _get_urgent_follow_ups(self) -> List[Dict]:
        """Get urgent follow-ups that are due or overdue"""
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT t.id, t.title, t.follow_up_date, t.follow_up_stakeholder,
                           s.display_name, t.priority,
                           (julianday('now') - julianday(t.follow_up_date)) as days_since_due
                    FROM strategic_tasks t
                    LEFT JOIN stakeholder_profiles_enhanced s ON t.follow_up_stakeholder = s.stakeholder_key
                    WHERE t.follow_up_required = TRUE
                        AND t.follow_up_date <= date('now', '+1 day')  -- Due today or tomorrow
                        AND t.status = 'active'
                    ORDER BY days_since_due DESC
                """)
                
                follow_ups = []
                for row in cursor.fetchall():
                    task_id, title, follow_up_date, stakeholder_key, stakeholder_name, priority, days_since = row
                    
                    # Determine urgency
                    if days_since >= 0:
                        urgency = 'overdue'
                    elif days_since >= -1:
                        urgency = 'due_today'
                    else:
                        urgency = 'due_soon'
                    
                    follow_ups.append({
                        'task_id': task_id,
                        'title': title,
                        'follow_up_date': follow_up_date,
                        'stakeholder_key': stakeholder_key,
                        'stakeholder_name': stakeholder_name or stakeholder_key,
                        'priority': priority,
                        'days_since_due': int(days_since) if days_since else 0,
                        'urgency': urgency
                    })
                
                return follow_ups
                
        except Exception as e:
            self.logger.error("Failed to get urgent follow-ups", error=str(e))
            return []
    
    def _get_assigned_tasks_needing_updates(self) -> List[Dict]:
        """Get tasks assigned to others that may need status updates"""
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT t.id, t.title, t.assigned_to, s.display_name,
                           t.due_date, t.priority, t.created_date,
                           julianday('now') - julianday(t.created_date) as days_since_assigned
                    FROM strategic_tasks t
                    LEFT JOIN stakeholder_profiles_enhanced s ON t.assigned_to = s.stakeholder_key
                    WHERE t.assignment_direction = 'outgoing'
                        AND t.status = 'active'
                        AND (
                            -- Tasks assigned more than 3 days ago without recent updates
                            julianday('now') - julianday(t.created_date) > 3
                            OR
                            -- High priority tasks assigned more than 1 day ago
                            (t.priority IN ('critical', 'high') AND julianday('now') - julianday(t.created_date) > 1)
                            OR
                            -- Tasks approaching due date
                            (t.due_date IS NOT NULL AND julianday(t.due_date) - julianday('now') <= 2)
                        )
                    ORDER BY 
                        CASE t.priority 
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2  
                            WHEN 'medium' THEN 3
                            WHEN 'low' THEN 4
                        END,
                        days_since_assigned DESC
                """)
                
                updates = []
                for row in cursor.fetchall():
                    task_id, title, assigned_to, assignee_name, due_date, priority, created_date, days_since = row
                    
                    # Determine update reason
                    if due_date and (datetime.fromisoformat(due_date.replace('Z', '')) - datetime.now()).days <= 2:
                        update_reason = 'approaching_due_date'
                    elif priority in ['critical', 'high'] and days_since > 1:
                        update_reason = 'high_priority_check_in'
                    else:
                        update_reason = 'regular_status_update'
                    
                    updates.append({
                        'task_id': task_id,
                        'title': title,
                        'assigned_to': assigned_to,
                        'assignee_name': assignee_name or assigned_to,
                        'due_date': due_date,
                        'priority': priority,
                        'days_since_assigned': int(days_since),
                        'update_reason': update_reason
                    })
                
                return updates
                
        except Exception as e:
            self.logger.error("Failed to get assigned tasks needing updates", error=str(e))
            return []
    
    def _get_tasks_needing_escalation(self) -> List[Dict]:
        """Get tasks that may need escalation"""
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT t.id, t.title, t.priority, t.due_date, t.assigned_to,
                           s.display_name, t.escalation_date,
                           (julianday('now') - julianday(t.due_date)) as days_overdue
                    FROM strategic_tasks t
                    LEFT JOIN stakeholder_profiles_enhanced s ON t.assigned_to = s.stakeholder_key
                    WHERE t.status = 'active'
                        AND (
                            -- Tasks overdue by more than 5 days
                            (t.due_date < date('now') AND julianday('now') - julianday(t.due_date) > 5)
                            OR
                            -- Critical tasks overdue by more than 2 days
                            (t.priority = 'critical' AND t.due_date < date('now') AND julianday('now') - julianday(t.due_date) > 2)
                            OR
                            -- Escalation date has passed
                            (t.escalation_date IS NOT NULL AND t.escalation_date <= date('now'))
                        )
                    ORDER BY 
                        CASE t.priority 
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2  
                            WHEN 'medium' THEN 3
                            WHEN 'low' THEN 4
                        END,
                        days_overdue DESC
                """)
                
                escalations = []
                for row in cursor.fetchall():
                    task_id, title, priority, due_date, assigned_to, assignee_name, escalation_date, days_overdue = row
                    
                    # Determine escalation reason
                    if escalation_date and escalation_date <= datetime.now().strftime('%Y-%m-%d'):
                        escalation_reason = 'scheduled_escalation'
                    elif priority == 'critical' and days_overdue > 2:
                        escalation_reason = 'critical_overdue'
                    else:
                        escalation_reason = 'extended_overdue'
                    
                    escalations.append({
                        'task_id': task_id,
                        'title': title,
                        'priority': priority,
                        'due_date': due_date,
                        'assigned_to': assigned_to,
                        'assignee_name': assignee_name or assigned_to,
                        'days_overdue': int(days_overdue) if days_overdue else 0,
                        'escalation_reason': escalation_reason
                    })
                
                return escalations
                
        except Exception as e:
            self.logger.error("Failed to get tasks needing escalation", error=str(e))
            return []
    
    def _generate_alert_summary(self, alerts: Dict) -> Dict:
        """Generate summary of alert priorities"""
        
        total_alerts = sum(len(alerts[key]) for key in alerts if key != 'summary')
        
        # Priority scoring
        priority_score = 0
        priority_score += len(alerts['critical_overdue']) * 10
        priority_score += len(alerts['escalation_needed']) * 8
        priority_score += len(alerts['follow_ups_urgent']) * 6
        priority_score += len(alerts['due_today']) * 4
        priority_score += len(alerts['assigned_task_updates']) * 2
        
        # Determine overall urgency
        if priority_score >= 20:
            urgency_level = 'critical'
        elif priority_score >= 10:
            urgency_level = 'high'
        elif priority_score >= 5:
            urgency_level = 'medium'
        else:
            urgency_level = 'low'
        
        return {
            'total_alerts': total_alerts,
            'priority_score': priority_score,
            'urgency_level': urgency_level,
            'needs_immediate_attention': len(alerts['critical_overdue']) > 0 or len(alerts['escalation_needed']) > 0,
            'generated_at': datetime.now().isoformat()
        }
    
    def display_daily_alerts(self):
        """Display formatted daily alerts"""
        
        alerts = self.generate_daily_alerts()
        
        print("🚨 Daily Task Alerts")
        print("=" * 25)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Summary
        summary = alerts['summary']
        urgency_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[summary['urgency_level']]
        
        print(f"\n{urgency_emoji} Overall Urgency: {summary['urgency_level'].title()}")
        print(f"📊 Total Alerts: {summary['total_alerts']}")
        
        if summary['needs_immediate_attention']:
            print("⚠️  IMMEDIATE ATTENTION REQUIRED")
        
        # Critical overdue tasks
        if alerts['critical_overdue']:
            print(f"\n🔴 CRITICAL OVERDUE TASKS ({len(alerts['critical_overdue'])})")
            print("-" * 35)
            
            for task in alerts['critical_overdue']:
                direction_emoji = {'incoming': '📥', 'outgoing': '📤', 'self_assigned': '📝'}[task['assignment_direction']]
                
                print(f"{direction_emoji} [{task['task_id']}] {task['title'][:50]}")
                print(f"   ⚠️  {task['days_overdue']} days overdue | Priority: {task['priority'].upper()}")
                
                if task['assignment_direction'] == 'outgoing':
                    print(f"   👤 Assigned to: {task['assignee_name']} - ESCALATE NOW")
                else:
                    print(f"   🎯 YOUR RESPONSIBILITY - ACT TODAY")
                
                print()
        
        # Tasks due today
        if alerts['due_today']:
            print(f"\n⏰ DUE TODAY ({len(alerts['due_today'])})")
            print("-" * 20)
            
            for task in alerts['due_today']:
                direction_emoji = {'incoming': '📥', 'outgoing': '📤', 'self_assigned': '📝'}[task['assignment_direction']]
                priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[task['priority']]
                
                print(f"{direction_emoji} {priority_emoji} [{task['task_id']}] {task['title'][:50]}")
                
                if task['assignment_direction'] == 'outgoing':
                    print(f"   👤 Check with: {task['assignee_name']}")
                else:
                    print(f"   🎯 Complete today")
                
                print()
        
        # Urgent follow-ups
        if alerts['follow_ups_urgent']:
            print(f"\n🔄 URGENT FOLLOW-UPS ({len(alerts['follow_ups_urgent'])})")
            print("-" * 25)
            
            for follow_up in alerts['follow_ups_urgent']:
                urgency_emoji = {'overdue': '🔴', 'due_today': '🟡', 'due_soon': '🟢'}[follow_up['urgency']]
                
                print(f"{urgency_emoji} [{follow_up['task_id']}] {follow_up['title'][:50]}")
                print(f"   👤 Follow up with: {follow_up['stakeholder_name']}")
                
                if follow_up['urgency'] == 'overdue':
                    print(f"   ⚠️  {follow_up['days_since_due']} days overdue")
                else:
                    print(f"   📅 Due: {follow_up['follow_up_date']}")
                
                print()
        
        # Tasks needing escalation
        if alerts['escalation_needed']:
            print(f"\n📈 ESCALATION NEEDED ({len(alerts['escalation_needed'])})")
            print("-" * 25)
            
            for escalation in alerts['escalation_needed']:
                print(f"🔴 [{escalation['task_id']}] {escalation['title'][:50]}")
                print(f"   👤 Assigned to: {escalation['assignee_name']}")
                print(f"   ⚠️  {escalation['days_overdue']} days overdue | Reason: {escalation['escalation_reason']}")
                print(f"   🚀 ESCALATE TO LEADERSHIP")
                print()
        
        # Assigned tasks needing updates
        if alerts['assigned_task_updates']:
            print(f"\n📋 CHECK-IN NEEDED ({len(alerts['assigned_task_updates'])})")
            print("-" * 25)
            
            for update in alerts['assigned_task_updates'][:5]:  # Limit to top 5
                priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[update['priority']]
                
                print(f"{priority_emoji} [{update['task_id']}] {update['title'][:50]}")
                print(f"   👤 Check with: {update['assignee_name']}")
                print(f"   📅 Assigned {update['days_since_assigned']} days ago")
                
                if update['update_reason'] == 'approaching_due_date':
                    print(f"   ⏰ Due soon: {update['due_date']}")
                
                print()
            
            if len(alerts['assigned_task_updates']) > 5:
                print(f"   ... and {len(alerts['assigned_task_updates']) - 5} more")
        
        # Next actions
        print("\n💡 RECOMMENDED ACTIONS:")
        
        if alerts['critical_overdue']:
            print("   1. 🔴 Address critical overdue tasks IMMEDIATELY")
        
        if alerts['escalation_needed']:
            print("   2. 📈 Escalate blocked tasks to leadership")
        
        if alerts['follow_ups_urgent']:
            print("   3. 🔄 Complete urgent stakeholder follow-ups")
        
        if alerts['due_today']:
            print("   4. ⏰ Focus on today's due tasks")
        
        if alerts['assigned_task_updates']:
            print("   5. 📋 Check in with assignees for status updates")
        
        print("\n📱 Task Management Commands:")
        print("   python strategic_task_manager.py overdue    # View all overdue")
        print("   python strategic_task_manager.py followups  # View all follow-ups")
        print("   python strategic_task_manager.py assigned   # View assigned tasks")


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily Task Alert System")
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed output")
    
    args = parser.parse_args()
    
    alert_system = DailyTaskAlerts()
    
    try:
        if args.quiet:
            # Just generate summary for automation
            alerts = alert_system.generate_daily_alerts()
            summary = alerts['summary']
            
            print(f"Urgency: {summary['urgency_level']}")
            print(f"Total alerts: {summary['total_alerts']}")
            print(f"Immediate attention: {summary['needs_immediate_attention']}")
        else:
            # Full interactive display
            alert_system.display_daily_alerts()
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
