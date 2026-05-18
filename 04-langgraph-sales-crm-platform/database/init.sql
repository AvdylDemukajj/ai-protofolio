-- LangGraph Sales CRM schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(255) NOT NULL,
    website_url VARCHAR(255),
    contact_email VARCHAR(255),
    industry VARCHAR(100),
    employee_count INTEGER,
    pain_points TEXT[],
    lead_score INTEGER CHECK (lead_score IS NULL OR lead_score BETWEEN 0 AND 100),
    buying_intent VARCHAR(50),
    outreach_strategy TEXT,
    status VARCHAR(50) DEFAULT 'new',
    draft_subject TEXT,
    draft_body TEXT,
    requires_human_review BOOLEAN DEFAULT TRUE,
    agent_decision VARCHAR(100),
    confidence_score NUMERIC(3, 2),
    last_interaction_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    ai_generated BOOLEAN DEFAULT TRUE,
    human_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    action_taken VARCHAR(100) NOT NULL,
    reasoning TEXT,
    confidence_score NUMERIC(3, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(lead_score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_interactions_lead ON interactions(lead_id);
CREATE INDEX IF NOT EXISTS idx_audit_lead ON agent_audit_log(lead_id);
