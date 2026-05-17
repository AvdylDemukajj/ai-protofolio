CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id_str VARCHAR(20) UNIQUE NOT NULL,
    subject VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Open',
    priority VARCHAR(20) DEFAULT 'Medium',
    assigned_to VARCHAR(100),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action_type VARCHAR(100),
    target_resource VARCHAR(255),
    parameters TEXT,
    agent_decision TEXT,
    guardrail_triggered BOOLEAN DEFAULT FALSE,
    executed_by VARCHAR(50) DEFAULT 'AI_AGENT',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tickets_str ON support_tickets(ticket_id_str);
CREATE INDEX idx_audit_date ON audit_logs(created_at DESC);