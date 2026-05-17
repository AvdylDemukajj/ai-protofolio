CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- High-volume transactions table (Partition by date in real prod)
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    merchant_category_code VARCHAR(10),
    location_lat FLOAT,
    location_lon FLOAT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, flagged
    risk_score NUMERIC(5, 4) DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alerts for human review
CREATE TABLE IF NOT EXISTS fraud_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID REFERENCES transactions(id),
    reason_code VARCHAR(50) NOT NULL, -- e.g., 'VELOCITY_CHECK', 'ML_HIGH_RISK'
    details JSONB,
    status VARCHAR(20) DEFAULT 'open', -- open, resolved, false_positive
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp DESC);
CREATE INDEX idx_alerts_status ON fraud_alerts(status);
CREATE INDEX idx_alerts_transaction ON fraud_alerts(transaction_id);