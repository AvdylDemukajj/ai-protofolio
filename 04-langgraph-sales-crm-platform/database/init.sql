CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Leads Table
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(255) NOT NULL,
    website_url VARCHAR(255),
    contact_email VARCHAR(255),
    industry VARCHAR(100),
    employee_count INTEGER,
    
    -- AI Enrichment
    pain_points TEXT[],
    lead_score INTEGER CHECK (lead_score BETWEEN 0 AND 100),
    buying_intent VARCHAR(50), -- 'cold', 'warm', 'hot'
    outreach_strategy TEXT,
    
    -- Workflow State
    status VARCHAR(50) DEFAULT 'new', -- new, researching, drafted, pending_review, sent
    last_interaction_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Interactions Log
CREATE TABLE IF NOT EXISTS interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL, -- 'email_draft', 'call_note', 'meeting'
    content TEXT NOT NULL,
    ai_generated BOOLEAN DEFAULT TRUE,
    human_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent Audit Log
CREATE TABLE IF NOT EXISTS agent_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id),
    action_taken VARCHAR(100) NOT NULL,
    reasoning TEXT,
    confidence_score NUMERIC(3, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_score ON leads(lead_score DESC);