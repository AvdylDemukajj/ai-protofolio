CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100),
    initial_query TEXT NOT NULL,
    routed_agent VARCHAR(50),
    final_response TEXT,
    risk_level VARCHAR(20),
    requires_human_review BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id),
    agent_name VARCHAR(50) NOT NULL,
    action_type VARCHAR(50),
    input_summary TEXT,
    output_summary TEXT,
    confidence_score INT,
    policy_checks_passed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_audit_agent ON audit_logs(agent_name);