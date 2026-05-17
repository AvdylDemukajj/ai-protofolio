-- Enable UUID extension for unique IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main Table: Support Tickets
CREATE TABLE IF NOT EXISTS support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_email TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    category TEXT, -- 'billing', 'technical', 'sales', 'other'
    priority TEXT CHECK (priority IN ('low', 'medium', 'high')),
    confidence_score NUMERIC(3, 2), -- AI Confidence (0.00 - 1.00)
    status TEXT DEFAULT 'new', -- 'new', 'in_progress', 'resolved', 'closed'
    ai_summary TEXT,
    assigned_to TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Table: AI Decisions & Workflow Steps
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID REFERENCES support_tickets(id) ON DELETE CASCADE,
    workflow_step TEXT NOT NULL, -- e.g., 'classification', 'drafting', 'routing'
    model_version TEXT,
    input_hash TEXT, -- Hash of input for privacy verification
    output_json JSONB, -- Full AI response
    execution_time_ms INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for Performance
CREATE INDEX idx_tickets_status ON support_tickets(status);
CREATE INDEX idx_tickets_email ON support_tickets(customer_email);
CREATE INDEX idx_tickets_created ON support_tickets(created_at DESC);
CREATE INDEX idx_audit_ticket ON audit_logs(ticket_id);

-- Trigger to auto-update 'updated_at'
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_support_tickets_updated_at BEFORE UPDATE ON support_tickets
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();