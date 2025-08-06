-- SuperClaude Strategic Memory System Database Schema
-- Director of Engineering platform leadership memory infrastructure

-- Executive sessions tracking VP/SLT interactions and strategic meetings
CREATE TABLE executive_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_type TEXT NOT NULL,  -- 'vp_slt', 'board', 'strategic_planning'
    stakeholder_key TEXT NOT NULL,  -- 'vp_engineering', 'vp_product', 'vp_design'
    meeting_date DATE NOT NULL,
    agenda_topics TEXT,  -- JSON array
    decisions_made TEXT,  -- JSON structured decisions
    action_items TEXT,   -- JSON with owners and deadlines
    business_impact TEXT,  -- Quantified outcomes where available
    next_session_prep TEXT,  -- Context for next interaction
    persona_activated TEXT,  -- 'camille', 'alvaro', 'diego', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Strategic initiatives and PI tracking across sessions
CREATE TABLE strategic_initiatives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    initiative_key TEXT UNIQUE NOT NULL,  -- PI-14741, etc.
    initiative_name TEXT NOT NULL,
    parent_initiative TEXT,
    assignee TEXT,
    status TEXT,  -- 'new', 'in_progress', 'at_risk', 'completed', 'canceled'
    priority TEXT,  -- 'critical', 'high', 'medium', 'low'
    business_value TEXT,  -- Strategic business impact description
    risk_level TEXT,  -- 'green', 'yellow', 'red'
    resource_allocation TEXT,  -- JSON with team assignments
    milestone_history TEXT,  -- JSON timeline of key events
    roi_tracking TEXT,  -- JSON with cost/benefit analysis
    stakeholder_impact TEXT,  -- JSON with cross-functional implications
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stakeholder relationship and communication pattern intelligence
CREATE TABLE stakeholder_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stakeholder_key TEXT UNIQUE NOT NULL,  -- 'vp_engineering', 'design_director'
    display_name TEXT NOT NULL,
    role_title TEXT,
    communication_style TEXT,  -- 'data_driven', 'narrative_focused', 'visual'
    decision_criteria TEXT,  -- JSON with key factors they prioritize
    interaction_history TEXT,  -- JSON with meeting outcomes and patterns
    preferred_personas TEXT,  -- JSON array of effective SuperClaude personas
    escalation_threshold TEXT,  -- When they need involvement
    success_metrics TEXT,  -- What they measure for success
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Platform adoption metrics and competitive intelligence
CREATE TABLE platform_intelligence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intelligence_type TEXT NOT NULL,  -- 'adoption_metric', 'competitive', 'market'
    category TEXT NOT NULL,  -- 'design_system', 'internationalization', 'devex'
    metric_name TEXT,
    value_numeric REAL,
    value_text TEXT,
    data_source TEXT,  -- Always cite sources
    measurement_date DATE,
    trend_direction TEXT,  -- 'improving', 'stable', 'declining'
    business_impact TEXT,  -- How this relates to strategic outcomes
    action_required TEXT,  -- Strategic recommendations
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Budget cycle planning and ROI tracking intelligence
CREATE TABLE budget_intelligence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_cycle TEXT NOT NULL,  -- '2025_q3', '2025_annual'
    category TEXT NOT NULL,  -- 'headcount', 'tooling', 'vendors', 'infrastructure'
    subcategory TEXT,  -- 'design_tools', 'ci_cd', 'monitoring'
    allocated_budget REAL,
    actual_spend REAL,
    roi_measurement REAL,
    justification_history TEXT,  -- JSON with historical business cases
    approval_stakeholders TEXT,  -- JSON with decision makers
    variance_analysis TEXT,  -- Budget vs actual analysis
    next_cycle_implications TEXT,  -- Impact on future planning
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for optimal query performance
CREATE INDEX idx_executive_sessions_stakeholder ON executive_sessions(stakeholder_key);
CREATE INDEX idx_executive_sessions_date ON executive_sessions(meeting_date);
CREATE INDEX idx_strategic_initiatives_key ON strategic_initiatives(initiative_key);
CREATE INDEX idx_strategic_initiatives_status ON strategic_initiatives(status);
CREATE INDEX idx_strategic_initiatives_assignee ON strategic_initiatives(assignee);
CREATE INDEX idx_stakeholder_profiles_key ON stakeholder_profiles(stakeholder_key);
CREATE INDEX idx_platform_intelligence_category ON platform_intelligence(category);
CREATE INDEX idx_platform_intelligence_date ON platform_intelligence(measurement_date);
CREATE INDEX idx_budget_intelligence_cycle ON budget_intelligence(budget_cycle);
CREATE INDEX idx_budget_intelligence_category ON budget_intelligence(category);