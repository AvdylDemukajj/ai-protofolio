-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create Knowledge Documents Table
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create Interaction Logs Table
CREATE TABLE IF NOT EXISTS interaction_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    response TEXT,
    sources_used TEXT,
    confidence_score INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for Vector Search
CREATE INDEX ON knowledge_documents USING ivfflat (embedding vector_cosine_ops);

-- Seed Data (Mock Knowledge Base)
INSERT INTO knowledge_documents (category, title, content, embedding) 
VALUES 
('shipping', 'Standard Shipping Policy', 'We ship all orders within 24 hours via DHL Express. Delivery takes 2-3 business days.', '[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]'),
('returns', 'Return Policy', 'Returns are accepted within 14 days of delivery. Items must be unused and in original packaging.', '[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1]'),
('refunds', 'Refund Process', 'Refunds are processed within 5 business days after we receive the returned item.', '[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2]');