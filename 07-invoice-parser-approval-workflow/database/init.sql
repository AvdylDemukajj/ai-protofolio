CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE invoice_status_enum AS ENUM ('uploaded', 'processed', 'needs_review', 'approved', 'rejected');

CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    vendor_name VARCHAR(255),
    invoice_number VARCHAR(100),
    invoice_date TIMESTAMPTZ,
    subtotal NUMERIC(12, 2),
    tax NUMERIC(12, 2),
    total NUMERIC(12, 2),
    currency VARCHAR(10) DEFAULT 'USD',
    extraction_confidence NUMERIC(3, 2),
    status invoice_status_enum DEFAULT 'uploaded',
    rejection_reason TEXT,
    reviewed_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS review_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    action VARCHAR(20) NOT NULL,
    comments TEXT,
    reviewer VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_date ON invoices(invoice_date);