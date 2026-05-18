CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS deletion_audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL, -- success, failed, rolled_back
    steps_completed TEXT, -- JSON array of step names
    error_message TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON deletion_audit_logs(user_id);
CREATE INDEX idx_audit_status ON deletion_audit_logs(status);