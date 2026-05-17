-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main Leads Table
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    company VARCHAR(255),
    company_size INTEGER,
    source VARCHAR(50) DEFAULT 'unknown', -- 'website', 'linkedin', 'referral'
    message TEXT,
    
    -- AI Enrichment Fields
    lead_score INTEGER CHECK (lead_score BETWEEN 0 AND 100),
    intent_category VARCHAR(50), -- 'high_buying', 'medium_interest', 'low_info', 'spam'
    summary TEXT,
    recommended_action TEXT, -- 'Call immediately', 'Send email', 'Nurture'
    
    -- Workflow State
    status VARCHAR(50) DEFAULT 'new', -- new, validated, qualified, contacted, converted, rejected
    requires_human_review BOOLEAN DEFAULT FALSE,
    review_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit Log Table for AI Decisions
CREATE TABLE IF NOT EXISTS lead_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    workflow_step VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    input_hash VARCHAR(64),
    ai_output_json JSONB,
    execution_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for Performance
CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_score ON leads(lead_score DESC);
CREATE INDEX idx_lead_audit ON lead_audit_log(lead_id);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_leads_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_leads_updated_at_trigger BEFORE UPDATE ON leads
FOR EACH ROW EXECUTE FUNCTION update_leads_updated_at();