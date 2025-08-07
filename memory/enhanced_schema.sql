-- Enhanced SuperClaude Strategic Memory System Database Schema
-- Extended for comprehensive meeting tracking and workspace monitoring

-- Meeting tracking for all types: 1-on-1s, VP meetings, strategic sessions
CREATE TABLE meeting_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_key TEXT UNIQUE NOT NULL,  -- Generated: 'raghu-1on1-2025-01-08', 'vp-1on1-2025-01-08'
    meeting_type TEXT NOT NULL,  -- '1on1_reports', 'vp_1on1', 'slt_review', 'cross_team', 'vendor', 'strategic_planning'
    stakeholder_primary TEXT,  -- Primary attendee: 'raghu_datta', 'vp_engineering'
    stakeholder_secondary TEXT,  -- Additional attendees (JSON array for multi-person meetings)
    meeting_date DATE,
    meeting_status TEXT DEFAULT 'scheduled',  -- 'scheduled', 'completed', 'cancelled', 'rescheduled'

    -- Meeting preparation intelligence
    prep_file_path TEXT,  -- Path to preparation document
    agenda_items TEXT,  -- JSON array of agenda topics
    preparation_notes TEXT,  -- Key prep insights and context

    -- Meeting outcomes and follow-up
    meeting_outcomes TEXT,  -- JSON structured outcomes
    action_items TEXT,  -- JSON with owners, deadlines, status
    next_meeting_prep TEXT,  -- Context for future meetings
    business_impact TEXT,  -- Quantified outcomes where available

    -- SuperClaude integration context
    persona_activated TEXT,  -- Which personas were most effective
    communication_style_used TEXT,  -- Adapted communication approach
    strategic_themes TEXT,  -- JSON array of strategic topics discussed

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workspace directory monitoring and automatic capture
CREATE TABLE workspace_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    change_type TEXT NOT NULL,  -- 'directory_created', 'file_created', 'file_modified', 'file_deleted'
    path_full TEXT NOT NULL,  -- Full file/directory path
    path_relative TEXT NOT NULL,  -- Relative to workspace root

    -- Automatic categorization
    category TEXT,  -- 'meeting_prep', 'current_initiatives', 'strategic_docs', 'reference_materials'
    subcategory TEXT,  -- '1on1s', 'vp_meetings', 'design_system', 'platform_modernization'

    -- Strategic context extraction
    stakeholders_detected TEXT,  -- JSON array of stakeholders mentioned
    projects_detected TEXT,  -- JSON array of project/initiative references
    meeting_type_detected TEXT,  -- Detected meeting type from path/content

    -- Content intelligence
    content_summary TEXT,  -- AI-generated summary of content/purpose
    strategic_value TEXT,  -- Assessment of strategic importance
    memory_trigger TEXT,  -- Whether this should trigger memory storage

    processed_at TIMESTAMP,  -- When strategic analysis was completed
    memory_stored_at TIMESTAMP,  -- When data was stored in strategic memory
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meeting participant relationship tracking
CREATE TABLE meeting_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_session_id INTEGER,
    stakeholder_key TEXT NOT NULL,
    participation_role TEXT,  -- 'organizer', 'primary_participant', 'attendee', 'optional'
    preparation_level TEXT,  -- 'extensive', 'standard', 'minimal', 'none'
    engagement_level TEXT,  -- Post-meeting assessment
    follow_up_required BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (meeting_session_id) REFERENCES meeting_sessions(id)
);

-- Enhanced stakeholder profiles with meeting history intelligence
CREATE TABLE stakeholder_meeting_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stakeholder_key TEXT NOT NULL,

    -- Meeting frequency and patterns
    meeting_frequency_preference TEXT,  -- 'weekly', 'biweekly', 'monthly', 'quarterly', 'ad_hoc'
    optimal_meeting_length INTEGER,  -- Minutes
    preferred_time_slots TEXT,  -- JSON array of preferred meeting times

    -- Communication effectiveness tracking
    most_effective_personas TEXT,  -- JSON array of SuperClaude personas that work best
    communication_preferences TEXT,  -- JSON with style preferences
    decision_making_pattern TEXT,  -- How they make decisions
    follow_up_preferences TEXT,  -- Preferred follow-up methods and timing

    -- Strategic relationship intelligence
    key_strategic_themes TEXT,  -- JSON array of recurring strategic interests
    escalation_patterns TEXT,  -- When and how they escalate issues
    business_impact_focus TEXT,  -- What business outcomes they prioritize
    cross_functional_relationships TEXT,  -- JSON mapping of their key relationships

    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Directory structure templates and automatic setup
CREATE TABLE workspace_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name TEXT UNIQUE NOT NULL,
    trigger_pattern TEXT NOT NULL,  -- Regex pattern for automatic activation
    directory_structure TEXT,  -- JSON template for directory creation
    default_files TEXT,  -- JSON array of template files to create
    memory_integration TEXT,  -- JSON config for automatic memory capture
    persona_activation TEXT,  -- JSON array of personas to auto-activate

    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX idx_meeting_sessions_stakeholder ON meeting_sessions(stakeholder_primary);
CREATE INDEX idx_meeting_sessions_type ON meeting_sessions(meeting_type);
CREATE INDEX idx_meeting_sessions_date ON meeting_sessions(meeting_date);
CREATE INDEX idx_meeting_sessions_status ON meeting_sessions(meeting_status);

CREATE INDEX idx_workspace_changes_category ON workspace_changes(category);
CREATE INDEX idx_workspace_changes_path ON workspace_changes(path_relative);
CREATE INDEX idx_workspace_changes_created ON workspace_changes(created_at);

CREATE INDEX idx_meeting_participants_stakeholder ON meeting_participants(stakeholder_key);
CREATE INDEX idx_meeting_participants_session ON meeting_participants(meeting_session_id);

CREATE INDEX idx_stakeholder_patterns_key ON stakeholder_meeting_patterns(stakeholder_key);

-- Insert default workspace templates
INSERT INTO workspace_templates (template_name, trigger_pattern, directory_structure, default_files, memory_integration, persona_activation) VALUES
('1on1_reports_template',
 '.*1on1.*|.*one-on-one.*|.*direct-report.*',
 '{"subdirs": ["prep-notes", "outcomes", "action-items"]}',
 '["prep-template.md", "outcomes-template.md", "action-items.md"]',
 '{"auto_capture": true, "meeting_type": "1on1_reports", "extract_stakeholders": true}',
 '["diego", "marcus"]'
),
('vp_1on1_template',
 '.*vp.*1on1.*|.*vp.*one-on-one.*|.*leadership.*1on1.*',
 '{"subdirs": ["prep-materials", "strategic-context", "follow-up"]}',
 '["vp-prep-template.md", "strategic-talking-points.md", "action-items.md"]',
 '{"auto_capture": true, "meeting_type": "vp_1on1", "extract_stakeholders": true, "high_priority": true}',
 '["camille", "alvaro", "diego"]'
),
('strategic_initiative_template',
 '.*(initiative|project|pi-[0-9]+).*',
 '{"subdirs": ["planning", "execution", "analysis", "stakeholder-comms"]}',
 '["initiative-overview.md", "roadmap.md", "stakeholder-analysis.md", "roi-tracking.md"]',
 '{"auto_capture": true, "extract_initiatives": true, "extract_stakeholders": true}',
 '["diego", "alvaro", "martin"]'
);
