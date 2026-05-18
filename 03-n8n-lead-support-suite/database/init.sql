-- Lead lifecycle schema (application tables in leads_db)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    company VARCHAR(255),
    company_size INTEGER,
    source VARCHAR(50) DEFAULT 'unknown',
    message TEXT,
    external_id TEXT,

    lead_score INTEGER CHECK (lead_score IS NULL OR lead_score BETWEEN 0 AND 100),
    intent_category VARCHAR(50),
    summary TEXT,
    recommended_action TEXT,

    status VARCHAR(50) DEFAULT 'new',
    requires_human_review BOOLEAN DEFAULT FALSE,
    review_reason TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lead_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    workflow_step VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    input_hash VARCHAR(64),
    ai_output_json JSONB,
    execution_time_ms INTEGER,
    execution_timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(lead_score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
CREATE INDEX IF NOT EXISTS idx_lead_audit ON lead_audit_log(lead_id);

CREATE OR REPLACE FUNCTION update_leads_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_leads_updated_at_trigger ON leads;
CREATE TRIGGER update_leads_updated_at_trigger
    BEFORE UPDATE ON leads
    FOR EACH ROW
    EXECUTE FUNCTION update_leads_updated_at();
