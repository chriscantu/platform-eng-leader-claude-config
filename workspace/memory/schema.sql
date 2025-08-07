-- SuperClaude Strategic Memory System Database Schema
-- Director of Engineering: Cross-session strategic context persistence
-- Created: 2025-08-06

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ===========================================
-- Strategic Context Tables
-- ===========================================

-- Executive meeting sessions and outcomes
CREATE TABLE executive_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_type TEXT NOT NULL CHECK (session_type IN ('vp_slt', 'board', 'strategic_planning', '1on1', 'cross_team')),
    stakeholder_key TEXT NOT NULL, -- 'vp_engineering', 'vp_product', 'vp_design'
    meeting_date DATE NOT NULL,
    agenda_topics TEXT, -- JSON array
    decisions_made TEXT, -- JSON structured decisions
    action_items TEXT, -- JSON with owners and deadlines
    business_impact TEXT, -- Quantified outcomes where available
    next_session_prep TEXT, -- Context for next interaction
    persona_activated TEXT, -- 'camille', 'alvaro', 'diego', etc.
    outcome_rating INTEGER CHECK (outcome_rating BETWEEN 1 AND 5), -- Meeting effectiveness
    follow_up_required BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Strategic initiatives and PI tracking
CREATE TABLE strategic_initiatives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    initiative_key TEXT UNIQUE NOT NULL, -- PI-14741, etc.
    initiative_name TEXT NOT NULL,
    parent_initiative TEXT,
    assignee TEXT,
    status TEXT NOT NULL CHECK (status IN ('new', 'committed', 'in_progress', 'at_risk', 'completed', 'canceled')),
    priority TEXT NOT NULL CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    business_value TEXT, -- Strategic business impact description
    risk_level TEXT CHECK (risk_level IN ('green', 'yellow', 'red')),
    resource_allocation TEXT, -- JSON with team assignments
    milestone_history TEXT, -- JSON timeline of key events
    roi_tracking TEXT, -- JSON with cost/benefit analysis
    stakeholder_impact TEXT, -- JSON with cross-functional implications
    completion_probability REAL CHECK (completion_probability BETWEEN 0.0 AND 1.0),
    budget_impact REAL, -- Dollar impact if known
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stakeholder profiles and relationship intelligence
CREATE TABLE stakeholder_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stakeholder_key TEXT UNIQUE NOT NULL, -- 'vp_engineering', 'design_director'
    display_name TEXT NOT NULL,
    role_title TEXT,
    department TEXT,
    communication_style TEXT CHECK (communication_style IN ('data_driven', 'narrative_focused', 'visual', 'technical', 'strategic')),
    decision_criteria TEXT, -- JSON with key factors they prioritize
    interaction_history TEXT, -- JSON with meeting outcomes and patterns
    preferred_personas TEXT, -- JSON array of effective SuperClaude personas
    escalation_threshold TEXT, -- When they need involvement
    success_metrics TEXT, -- What they measure for success
    relationship_strength INTEGER CHECK (relationship_strength BETWEEN 1 AND 5),
    last_interaction DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Platform metrics and operational intelligence
CREATE TABLE platform_intelligence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intelligence_type TEXT NOT NULL CHECK (intelligence_type IN ('adoption_metric', 'competitive', 'market', 'performance', 'quality')),
    category TEXT NOT NULL, -- 'design_system', 'internationalization', 'devex'
    metric_name TEXT NOT NULL,
    value_numeric REAL,
    value_text TEXT,
    unit TEXT, -- 'percentage', 'count', 'dollars', 'score'
    data_source TEXT NOT NULL, -- Always cite sources
    measurement_date DATE NOT NULL,
    trend_direction TEXT CHECK (trend_direction IN ('improving', 'stable', 'declining')),
    business_impact TEXT, -- How this relates to strategic outcomes
    action_required TEXT, -- Strategic recommendations
    confidence_level TEXT CHECK (confidence_level IN ('high', 'medium', 'low')),
    baseline_value REAL, -- For trend comparison
    target_value REAL, -- Strategic target if applicable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Budget and financial intelligence
CREATE TABLE budget_intelligence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_cycle TEXT NOT NULL, -- '2025_q3', '2025_annual'
    category TEXT NOT NULL CHECK (category IN ('headcount', 'tooling', 'vendors', 'infrastructure', 'training')),
    subcategory TEXT, -- 'design_tools', 'ci_cd', 'monitoring'
    allocated_budget REAL,
    actual_spend REAL,
    roi_measurement REAL,
    justification_history TEXT, -- JSON with historical business cases
    approval_stakeholders TEXT, -- JSON with decision makers
    variance_analysis TEXT, -- Budget vs actual analysis
    next_cycle_implications TEXT, -- Impact on future planning
    cost_center TEXT, -- UI Foundation team attribution
    vendor_name TEXT, -- If applicable
    contract_end_date DATE, -- For vendor management
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Decision history and rationale tracking
CREATE TABLE strategic_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_key TEXT UNIQUE NOT NULL, -- Unique identifier for decision
    decision_title TEXT NOT NULL,
    decision_type TEXT CHECK (decision_type IN ('architecture', 'vendor', 'budget', 'organizational', 'process')),
    decision_maker TEXT NOT NULL, -- Who made the final decision
    decision_date DATE NOT NULL,
    context_summary TEXT NOT NULL, -- Background and situation
    options_considered TEXT, -- JSON with alternatives evaluated
    decision_rationale TEXT NOT NULL, -- Why this option was chosen
    expected_outcomes TEXT, -- JSON with predicted results
    actual_outcomes TEXT, -- JSON with measured results (updated over time)
    stakeholders_affected TEXT, -- JSON with impact assessment
    reversibility TEXT CHECK (reversibility IN ('reversible', 'irreversible', 'partially_reversible')),
    lesson_learned TEXT, -- Post-decision analysis
    related_initiatives TEXT, -- JSON array of PI keys
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================
-- Indexes for Performance
-- ===========================================

-- Executive sessions indexes
CREATE INDEX idx_executive_sessions_stakeholder ON executive_sessions(stakeholder_key);
CREATE INDEX idx_executive_sessions_date ON executive_sessions(meeting_date);
CREATE INDEX idx_executive_sessions_type ON executive_sessions(session_type);

-- Strategic initiatives indexes
CREATE INDEX idx_initiatives_status ON strategic_initiatives(status);
CREATE INDEX idx_initiatives_assignee ON strategic_initiatives(assignee);
CREATE INDEX idx_initiatives_risk ON strategic_initiatives(risk_level);
CREATE INDEX idx_initiatives_priority ON strategic_initiatives(priority);

-- Stakeholder profiles indexes
CREATE INDEX idx_stakeholders_key ON stakeholder_profiles(stakeholder_key);
CREATE INDEX idx_stakeholders_department ON stakeholder_profiles(department);

-- Platform intelligence indexes
CREATE INDEX idx_intelligence_type ON platform_intelligence(intelligence_type);
CREATE INDEX idx_intelligence_category ON platform_intelligence(category);
CREATE INDEX idx_intelligence_date ON platform_intelligence(measurement_date);
CREATE INDEX idx_intelligence_trend ON platform_intelligence(trend_direction);

-- Budget intelligence indexes
CREATE INDEX idx_budget_cycle ON budget_intelligence(budget_cycle);
CREATE INDEX idx_budget_category ON budget_intelligence(category);

-- Strategic decisions indexes
CREATE INDEX idx_decisions_maker ON strategic_decisions(decision_maker);
CREATE INDEX idx_decisions_type ON strategic_decisions(decision_type);
CREATE INDEX idx_decisions_date ON strategic_decisions(decision_date);

-- ===========================================
-- Views for Common Queries
-- ===========================================

-- Active initiatives requiring attention
CREATE VIEW active_initiatives_dashboard AS
SELECT
    initiative_key,
    initiative_name,
    assignee,
    status,
    risk_level,
    completion_probability,
    business_value,
    updated_at
FROM strategic_initiatives
WHERE status IN ('in_progress', 'at_risk', 'committed')
ORDER BY
    CASE risk_level
        WHEN 'red' THEN 1
        WHEN 'yellow' THEN 2
        WHEN 'green' THEN 3
        ELSE 4
    END,
    CASE priority
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END;

-- Recent executive session summary
CREATE VIEW recent_executive_sessions AS
SELECT
    session_type,
    stakeholder_key,
    meeting_date,
    outcome_rating,
    follow_up_required,
    persona_activated
FROM executive_sessions
WHERE meeting_date >= date('now', '-30 days')
ORDER BY meeting_date DESC;

-- Platform metrics trending
CREATE VIEW platform_metrics_trending AS
SELECT
    category,
    metric_name,
    value_numeric,
    unit,
    measurement_date,
    trend_direction,
    data_source
FROM platform_intelligence
WHERE measurement_date >= date('now', '-90 days')
ORDER BY category, metric_name, measurement_date DESC;

-- Budget variance analysis
CREATE VIEW budget_variance_current AS
SELECT
    category,
    subcategory,
    allocated_budget,
    actual_spend,
    (actual_spend - allocated_budget) as variance,
    ROUND((actual_spend - allocated_budget) / allocated_budget * 100, 2) as variance_percent,
    roi_measurement
FROM budget_intelligence
WHERE budget_cycle LIKE '%2025%'
ORDER BY variance_percent DESC;

-- ===========================================
-- Triggers for Data Integrity
-- ===========================================

-- Update timestamp trigger for executive_sessions
CREATE TRIGGER update_executive_sessions_timestamp
    AFTER UPDATE ON executive_sessions
BEGIN
    UPDATE executive_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update timestamp trigger for strategic_initiatives
CREATE TRIGGER update_strategic_initiatives_timestamp
    AFTER UPDATE ON strategic_initiatives
BEGIN
    UPDATE strategic_initiatives SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update timestamp trigger for stakeholder_profiles
CREATE TRIGGER update_stakeholder_profiles_timestamp
    AFTER UPDATE ON stakeholder_profiles
BEGIN
    UPDATE stakeholder_profiles SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update timestamp trigger for platform_intelligence
CREATE TRIGGER update_platform_intelligence_timestamp
    AFTER UPDATE ON platform_intelligence
BEGIN
    UPDATE platform_intelligence SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update timestamp trigger for budget_intelligence
CREATE TRIGGER update_budget_intelligence_timestamp
    AFTER UPDATE ON budget_intelligence
BEGIN
    UPDATE budget_intelligence SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update timestamp trigger for strategic_decisions
CREATE TRIGGER update_strategic_decisions_timestamp
    AFTER UPDATE ON strategic_decisions
BEGIN
    UPDATE strategic_decisions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ===========================================
-- Initial Data Population
-- ===========================================

-- Insert initial stakeholder profiles
INSERT INTO stakeholder_profiles (stakeholder_key, display_name, role_title, department, communication_style) VALUES
('vp_engineering', 'VP Engineering', 'Vice President of Engineering', 'Engineering', 'data_driven'),
('vp_product', 'VP Product', 'Vice President of Product', 'Product', 'strategic'),
('vp_design', 'VP Design', 'Vice President of Design', 'Design', 'visual'),
('design_director', 'Design Director', 'Director of Design', 'Design', 'visual'),
('product_director', 'Product Director', 'Director of Product Management', 'Product', 'narrative_focused');

-- Strategic tool outputs and intelligence tracking
CREATE TABLE strategic_tool_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT NOT NULL,
    command_context TEXT NOT NULL,
    persona_activated TEXT,
    tool_inputs TEXT, -- JSON with input parameters
    tool_outputs TEXT, -- JSON with tool results
    strategic_insights TEXT, -- Extracted strategic value
    business_impact TEXT, -- Quantified business impact
    follow_up_actions TEXT, -- JSON with recommended actions
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 5),
    cost_token_usage INTEGER, -- Track token consumption
    execution_time_ms INTEGER,
    session_id TEXT, -- Link to session for context
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tool activation and cost optimization tracking
CREATE TABLE tool_activation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_name TEXT NOT NULL,
    activation_context TEXT, -- JSON with context triggers
    tools_activated TEXT, -- JSON array of activated tools
    cost_benefit_score REAL, -- Cost-benefit analysis score
    activation_decision TEXT CHECK (activation_decision IN ('activated', 'skipped', 'cached')),
    token_usage_actual INTEGER,
    token_usage_saved INTEGER, -- From caching or optimization
    execution_outcome TEXT,
    user_satisfaction INTEGER CHECK (user_satisfaction BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cross-session tool intelligence patterns
CREATE TABLE tool_intelligence_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL, -- 'performance_trend', 'coordination_success', 'cost_optimization'
    pattern_data TEXT NOT NULL, -- JSON with pattern details
    confidence_level REAL CHECK (confidence_level BETWEEN 0.0 AND 1.0),
    usage_count INTEGER DEFAULT 1,
    success_rate REAL,
    business_impact_correlation TEXT,
    last_validated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for strategic tool performance
CREATE INDEX idx_tool_outputs_tool_command ON strategic_tool_outputs(tool_name, command_context);
CREATE INDEX idx_tool_outputs_date ON strategic_tool_outputs(created_at);
CREATE INDEX idx_tool_outputs_session ON strategic_tool_outputs(session_id);
CREATE INDEX idx_tool_activation_command ON tool_activation_log(command_name);
CREATE INDEX idx_tool_activation_date ON tool_activation_log(created_at);
CREATE INDEX idx_intelligence_patterns_type ON tool_intelligence_patterns(pattern_type);

-- Enhanced views for strategic tool analytics
CREATE VIEW tool_effectiveness_dashboard AS
SELECT
    tool_name,
    command_context,
    AVG(effectiveness_rating) as avg_effectiveness,
    COUNT(*) as usage_count,
    AVG(cost_token_usage) as avg_cost,
    AVG(execution_time_ms) as avg_execution_time,
    MAX(created_at) as last_used
FROM strategic_tool_outputs
GROUP BY tool_name, command_context
ORDER BY avg_effectiveness DESC, usage_count DESC;

CREATE VIEW cost_optimization_summary AS
SELECT
    command_name,
    COUNT(*) as total_executions,
    SUM(CASE WHEN activation_decision = 'activated' THEN 1 ELSE 0 END) as activations,
    SUM(CASE WHEN activation_decision = 'cached' THEN 1 ELSE 0 END) as cache_hits,
    AVG(cost_benefit_score) as avg_cost_benefit,
    SUM(token_usage_actual) as total_tokens_used,
    SUM(token_usage_saved) as total_tokens_saved,
    AVG(user_satisfaction) as avg_satisfaction
FROM tool_activation_log
GROUP BY command_name
ORDER BY avg_cost_benefit DESC;

-- Update timestamp triggers for new tables
CREATE TRIGGER update_tool_outputs_timestamp
    AFTER UPDATE ON strategic_tool_outputs
BEGIN
    UPDATE strategic_tool_outputs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_intelligence_patterns_timestamp
    AFTER UPDATE ON tool_intelligence_patterns
BEGIN
    UPDATE tool_intelligence_patterns SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Create database metadata table for version tracking
CREATE TABLE schema_metadata (
    version TEXT PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_metadata (version, description) VALUES
('1.0.0', 'Initial SuperClaude Strategic Memory System schema deployment'),
('2.0.0', 'Claude Flow MCP tool integration and strategic intelligence enhancement');

-- ===========================================
-- Schema Summary
-- ===========================================

-- Total tables: 6 core + 1 metadata
-- Views: 4 strategic dashboards
-- Indexes: 15 performance optimizations
-- Triggers: 6 automatic timestamp updates
-- Constraints: Comprehensive data validation
-- Initial data: 5 stakeholder profiles
