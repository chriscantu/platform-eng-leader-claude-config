-- Stakeholder Engagement Management System
-- Strategic relationship intelligence and proactive engagement management

-- Enhanced stakeholder profiles with engagement intelligence
CREATE TABLE stakeholder_profiles_enhanced (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stakeholder_key TEXT UNIQUE NOT NULL,  -- 'vp_engineering', 'design_director_rachel'

    -- Basic profile information
    display_name TEXT NOT NULL,
    role_title TEXT,
    organization TEXT,
    reporting_relationship TEXT,  -- 'direct_report', 'peer', 'senior_leader', 'cross_functional', 'external'

    -- Strategic relationship context
    strategic_importance TEXT,  -- 'critical', 'high', 'medium', 'low'
    influence_level TEXT,  -- 'high_influence', 'medium_influence', 'low_influence'
    decision_authority TEXT,  -- JSON: what they can decide on
    strategic_interests TEXT,  -- JSON: key areas they care about
    success_metrics TEXT,  -- JSON: what they measure for success

    -- Communication preferences
    preferred_communication_channels TEXT,  -- JSON: ['slack', 'email', 'in_person', 'video']
    optimal_meeting_frequency TEXT,  -- 'weekly', 'biweekly', 'monthly', 'quarterly', 'as_needed'
    preferred_meeting_duration INTEGER,  -- minutes
    preferred_time_slots TEXT,  -- JSON: preferred meeting times
    communication_style TEXT,  -- 'direct', 'collaborative', 'data_driven', 'narrative', 'visual'

    -- SuperClaude persona effectiveness
    most_effective_personas TEXT,  -- JSON: which personas work best with them
    communication_approach_notes TEXT,  -- Free text: what works/doesn't work

    -- Engagement context
    key_projects_interests TEXT,  -- JSON: current projects/initiatives they care about
    escalation_preferences TEXT,  -- How they like to handle escalations
    follow_up_preferences TEXT,  -- Preferred follow-up style and timing

    -- Contact information
    primary_contact_method TEXT,
    contact_details TEXT,  -- JSON: various contact methods

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Engagement tracking and relationship health monitoring
CREATE TABLE stakeholder_engagements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stakeholder_key TEXT NOT NULL,

    -- Engagement details
    engagement_type TEXT NOT NULL,  -- 'meeting', 'slack', 'email', 'informal', 'strategic_session'
    engagement_date DATE NOT NULL,
    engagement_duration INTEGER,  -- minutes

    -- Context and preparation
    engagement_purpose TEXT,  -- Why this engagement happened
    preparation_level TEXT,  -- 'extensive', 'standard', 'minimal', 'spontaneous'
    strategic_context TEXT,  -- JSON: projects/initiatives discussed

    -- Outcomes and assessment
    engagement_quality TEXT,  -- 'excellent', 'good', 'adequate', 'poor'
    stakeholder_satisfaction TEXT,  -- 'very_positive', 'positive', 'neutral', 'negative'
    strategic_value TEXT,  -- 'high', 'medium', 'low'
    relationship_impact TEXT,  -- 'strengthened', 'maintained', 'neutral', 'weakened'

    -- Content and outcomes
    topics_discussed TEXT,  -- JSON: key topics covered
    decisions_made TEXT,  -- JSON: any decisions or agreements
    action_items TEXT,  -- JSON: follow-up actions with owners and dates
    next_engagement_context TEXT,  -- Context for future interactions

    -- SuperClaude integration
    personas_used TEXT,  -- JSON: which personas were activated
    communication_effectiveness TEXT,  -- How well the approach worked

    -- Follow-up tracking
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    follow_up_completed BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (stakeholder_key) REFERENCES stakeholder_profiles_enhanced(stakeholder_key)
);

-- Proactive engagement recommendations and alerts
CREATE TABLE engagement_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stakeholder_key TEXT NOT NULL,

    -- Recommendation details
    recommendation_type TEXT NOT NULL,  -- 'overdue_check_in', 'strategic_opportunity', 'relationship_maintenance', 'project_update', 'escalation_needed'
    urgency_level TEXT,  -- 'urgent', 'high', 'medium', 'low'
    confidence_score REAL,  -- 0.0-1.0: how confident the system is in this recommendation

    -- Context and reasoning
    trigger_reason TEXT,  -- Why this recommendation was generated
    strategic_context TEXT,  -- JSON: relevant projects/initiatives
    suggested_approach TEXT,  -- Recommended engagement approach
    suggested_timing TEXT,  -- When to engage
    suggested_duration INTEGER,  -- Recommended meeting length

    -- Preparation assistance
    talking_points TEXT,  -- JSON: suggested discussion topics
    relevant_history TEXT,  -- JSON: recent relevant interactions
    strategic_prep_notes TEXT,  -- Context and preparation suggestions
    recommended_personas TEXT,  -- JSON: which SuperClaude personas to use

    -- Status tracking
    recommendation_status TEXT DEFAULT 'pending',  -- 'pending', 'accepted', 'scheduled', 'completed', 'dismissed'
    scheduled_date DATE,
    completed_date DATE,
    dismissal_reason TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,  -- When this recommendation becomes stale

    FOREIGN KEY (stakeholder_key) REFERENCES stakeholder_profiles_enhanced(stakeholder_key)
);

-- Strategic project and stakeholder relationship mapping
CREATE TABLE stakeholder_project_interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stakeholder_key TEXT NOT NULL,
    project_initiative_key TEXT NOT NULL,

    -- Interest and involvement level
    interest_level TEXT,  -- 'critical', 'high', 'medium', 'low', 'not_interested'
    involvement_type TEXT,  -- 'owner', 'sponsor', 'contributor', 'stakeholder', 'informed', 'blocker'
    decision_authority TEXT,  -- What decisions they can make on this project

    -- Strategic context
    strategic_importance_to_them TEXT,  -- Why this matters to them specifically
    success_criteria TEXT,  -- What success looks like from their perspective
    potential_concerns TEXT,  -- What might worry them about this project

    -- Engagement strategy
    update_frequency_needed TEXT,  -- How often they want updates
    preferred_update_format TEXT,  -- 'detailed_report', 'summary', 'metrics_only', 'verbal_update'
    escalation_threshold TEXT,  -- When to escalate issues to them

    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (stakeholder_key) REFERENCES stakeholder_profiles_enhanced(stakeholder_key)
);

-- Relationship health and momentum tracking
CREATE TABLE relationship_health_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stakeholder_key TEXT NOT NULL,
    assessment_date DATE NOT NULL,

    -- Health indicators
    engagement_frequency_score REAL,  -- How well we're maintaining regular contact
    engagement_quality_score REAL,  -- Quality of recent interactions
    responsiveness_score REAL,  -- How responsive they are to outreach
    strategic_alignment_score REAL,  -- How well we're addressing their interests

    -- Momentum indicators
    relationship_momentum TEXT,  -- 'strengthening', 'stable', 'weakening', 'at_risk'
    trust_level TEXT,  -- 'high', 'medium', 'low', 'building'
    influence_trajectory TEXT,  -- 'increasing', 'stable', 'decreasing'

    -- Risk factors
    risk_factors TEXT,  -- JSON: potential relationship risks
    risk_level TEXT,  -- 'low', 'medium', 'high', 'critical'
    mitigation_recommendations TEXT,  -- JSON: suggested actions to improve relationship

    -- Overall assessment
    overall_health_score REAL,  -- 0.0-1.0: overall relationship health
    strategic_priority_adjustment TEXT,  -- Whether priority should be adjusted

    assessment_notes TEXT,  -- Free text assessment
    auto_generated BOOLEAN DEFAULT TRUE,  -- Whether this was automatically generated

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (stakeholder_key) REFERENCES stakeholder_profiles_enhanced(stakeholder_key)
);

-- Indexes for performance optimization
CREATE INDEX idx_stakeholder_engagements_key ON stakeholder_engagements(stakeholder_key);
CREATE INDEX idx_stakeholder_engagements_date ON stakeholder_engagements(engagement_date);
CREATE INDEX idx_stakeholder_engagements_type ON stakeholder_engagements(engagement_type);

CREATE INDEX idx_engagement_recommendations_key ON engagement_recommendations(stakeholder_key);
CREATE INDEX idx_engagement_recommendations_status ON engagement_recommendations(recommendation_status);
CREATE INDEX idx_engagement_recommendations_urgency ON engagement_recommendations(urgency_level);
CREATE INDEX idx_engagement_recommendations_created ON engagement_recommendations(created_at);

CREATE INDEX idx_stakeholder_projects_key ON stakeholder_project_interests(stakeholder_key);
CREATE INDEX idx_stakeholder_projects_project ON stakeholder_project_interests(project_initiative_key);
CREATE INDEX idx_stakeholder_projects_active ON stakeholder_project_interests(active);

CREATE INDEX idx_relationship_health_key ON relationship_health_metrics(stakeholder_key);
CREATE INDEX idx_relationship_health_date ON relationship_health_metrics(assessment_date);
CREATE INDEX idx_relationship_health_score ON relationship_health_metrics(overall_health_score);
