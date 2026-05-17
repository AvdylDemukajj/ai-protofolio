CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE document_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'dead_letter');

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    s3_path TEXT NOT NULL,
    status document_status DEFAULT 'pending',
    extracted_data JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created ON documents(created_at DESC);