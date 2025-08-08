-- Strategic Task Tracking Database Schema
-- Comprehensive task management integrated with stakeholder intelligence

-- Task definitions with rich context
CREATE TABLE strategic_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_key TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    
    -- Assignment tracking
    assigned_by TEXT, -- stakeholder_key if assigned by someone else
    assigned_to TEXT, -- stakeholder_key if assigned to someone else, 'self' if self-assigned
    assignment_direction TEXT NOT NULL, -- 'incoming', 'outgoing', 'self_assigned'
    
    -- Context and categorization
    category TEXT NOT NULL, -- 'platform_initiative', 'stakeholder_followup', 'strategic_project', 'operational'
    priority TEXT NOT NULL DEFAULT 'medium', -- 'critical', 'high', 'medium', 'low'
    impact_scope TEXT, -- 'platform_wide', 'cross_team', 'single_team', 'individual'
    strategic_theme TEXT, -- 'architecture', 'technical_debt', 'scalability', 'coordination'
    
    -- Timeline and status
    status TEXT NOT NULL DEFAULT 'active', -- 'active', 'blocked', 'completed', 'cancelled', 'deferred'
    due_date DATE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_date TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Source tracking
    source_type TEXT, -- 'meeting', 'email', 'manual', 'auto_detected'
    source_reference TEXT, -- meeting_id, file_path, etc.
    detection_confidence REAL, -- if auto-detected, confidence score
    
    -- Follow-up and accountability
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    follow_up_stakeholder TEXT, -- stakeholder_key for who to follow up with
    escalation_date DATE,
    escalation_stakeholder TEXT, -- stakeholder_key for escalation
    
    -- Progress tracking
    progress_percentage INTEGER DEFAULT 0,
    blockers TEXT, -- JSON array of blocking issues
    dependencies TEXT, -- JSON array of dependent task IDs
    
    -- Platform context
    affected_systems TEXT, -- JSON array of affected platform components
    architecture_impact TEXT, -- 'breaking_change', 'enhancement', 'maintenance', 'none'
    cross_team_coordination BOOLEAN DEFAULT FALSE,
    
    -- Rich metadata
    tags TEXT, -- JSON array of tags for flexible categorization
    notes TEXT, -- Free-form notes and updates
    effort_estimate TEXT, -- 'hours', 'days', 'weeks', 'months'
    business_justification TEXT
);

-- Task updates and activity log
CREATE TABLE task_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL, -- 'created', 'updated', 'status_changed', 'commented', 'assigned', 'completed'
    old_value TEXT,
    new_value TEXT,
    comment TEXT,
    created_by TEXT, -- stakeholder_key
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES strategic_tasks (id)
);

-- Task reminders and alerts
CREATE TABLE task_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    reminder_type TEXT NOT NULL, -- 'due_date', 'follow_up', 'check_in', 'escalation'
    scheduled_for TIMESTAMP NOT NULL,
    message TEXT,
    delivery_method TEXT DEFAULT 'console', -- 'console', 'notification', 'email'
    status TEXT DEFAULT 'pending', -- 'pending', 'sent', 'dismissed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES strategic_tasks (id)
);

-- Task-stakeholder relationships (many-to-many)
CREATE TABLE task_stakeholder_involvement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    stakeholder_key TEXT NOT NULL,
    involvement_type TEXT NOT NULL, -- 'assignee', 'assigner', 'collaborator', 'reviewer', 'blocker', 'escalation_path'
    involvement_level TEXT, -- 'primary', 'secondary', 'fyi'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES strategic_tasks (id),
    FOREIGN KEY (stakeholder_key) REFERENCES stakeholder_profiles_enhanced (stakeholder_key)
);

-- Task-meeting relationships
CREATE TABLE task_meeting_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    meeting_session_id INTEGER,
    context_type TEXT NOT NULL, -- 'created_in', 'discussed_in', 'assigned_in', 'updated_in'
    meeting_date DATE,
    meeting_type TEXT,
    agenda_item TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES strategic_tasks (id),
    FOREIGN KEY (meeting_session_id) REFERENCES meeting_sessions (id)
);

-- Recurring tasks and templates
CREATE TABLE task_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name TEXT UNIQUE NOT NULL,
    template_description TEXT,
    category TEXT NOT NULL,
    priority TEXT NOT NULL,
    default_assignee TEXT,
    default_duration TEXT,
    recurrence_pattern TEXT, -- 'weekly', 'monthly', 'quarterly', 'none'
    template_data TEXT NOT NULL, -- JSON with default task fields
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Platform-specific task views and indexes
CREATE INDEX idx_tasks_status ON strategic_tasks(status);
CREATE INDEX idx_tasks_priority ON strategic_tasks(priority);
CREATE INDEX idx_tasks_due_date ON strategic_tasks(due_date);
CREATE INDEX idx_tasks_assigned_to ON strategic_tasks(assigned_to);
CREATE INDEX idx_tasks_assigned_by ON strategic_tasks(assigned_by);
CREATE INDEX idx_tasks_category ON strategic_tasks(category);
CREATE INDEX idx_tasks_follow_up ON strategic_tasks(follow_up_date);
CREATE INDEX idx_task_activity_task_id ON task_activity_log(task_id);
CREATE INDEX idx_task_stakeholder_task_id ON task_stakeholder_involvement(task_id);
CREATE INDEX idx_task_stakeholder_key ON task_stakeholder_involvement(stakeholder_key);

-- Strategic task analysis views
CREATE VIEW active_tasks_by_priority AS
SELECT 
    t.*,
    s.display_name as assigned_to_name,
    s2.display_name as assigned_by_name
FROM strategic_tasks t
LEFT JOIN stakeholder_profiles_enhanced s ON t.assigned_to = s.stakeholder_key
LEFT JOIN stakeholder_profiles_enhanced s2 ON t.assigned_by = s2.stakeholder_key
WHERE t.status = 'active'
ORDER BY 
    CASE t.priority 
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2  
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    t.due_date ASC;

CREATE VIEW overdue_tasks AS
SELECT 
    t.*,
    s.display_name as assigned_to_name,
    (julianday('now') - julianday(t.due_date)) as days_overdue
FROM strategic_tasks t
LEFT JOIN stakeholder_profiles_enhanced s ON t.assigned_to = s.stakeholder_key
WHERE t.status = 'active' 
    AND t.due_date < date('now')
ORDER BY days_overdue DESC;

CREATE VIEW follow_up_due AS
SELECT 
    t.*,
    s.display_name as follow_up_with_name,
    (julianday('now') - julianday(t.follow_up_date)) as days_since_due
FROM strategic_tasks t
LEFT JOIN stakeholder_profiles_enhanced s ON t.follow_up_stakeholder = s.stakeholder_key
WHERE t.follow_up_required = TRUE
    AND t.follow_up_date <= date('now')
    AND t.status = 'active'
ORDER BY days_since_due DESC;

CREATE VIEW platform_impact_tasks AS
SELECT 
    t.*,
    COUNT(tsi.stakeholder_key) as stakeholder_count
FROM strategic_tasks t
LEFT JOIN task_stakeholder_involvement tsi ON t.id = tsi.task_id
WHERE t.impact_scope IN ('platform_wide', 'cross_team')
    AND t.status = 'active'
GROUP BY t.id
ORDER BY 
    CASE t.priority 
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2  
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    stakeholder_count DESC;
