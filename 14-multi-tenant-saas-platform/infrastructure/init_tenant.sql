-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Master Tenants Table
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subdomain VARCHAR(63) UNIQUE NOT NULL, -- Max length for DB identifier
    company_name VARCHAR(255) NOT NULL,
    plan_type VARCHAR(20) DEFAULT 'free', -- free, pro, enterprise
    schema_name VARCHAR(63) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Global Usage Logs for Billing (Across all tenants)
CREATE TABLE IF NOT EXISTS global_usage_logs (
    id BIGSERIAL PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    quantity INT DEFAULT 1,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Function to safely create a tenant schema and tables
CREATE OR REPLACE FUNCTION create_tenant_schema(t_uuid UUID, t_schema TEXT)
RETURNS VOID AS $$
BEGIN
    -- Validate schema name to prevent SQL Injection (only allow alphanumeric and underscore)
    IF NOT (t_schema ~ '^[a-zA-Z_][a-zA-Z0-9_]*$') THEN
        RAISE EXCEPTION 'Invalid schema name';
    END IF;

    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', t_schema);
    
    -- Create standard tables within the new schema
    EXECUTE format('CREATE TABLE %I.users (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), email TEXT UNIQUE, created_at TIMESTAMPTZ DEFAULT NOW())', t_schema);
    EXECUTE format('CREATE TABLE %I.data (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), content JSONB, created_at TIMESTAMPTZ DEFAULT NOW())', t_schema);
    
    -- Set permissions (Best practice: grant to specific role, here using admin for demo)
    EXECUTE format('GRANT ALL ON ALL TABLES IN SCHEMA %I TO saas_admin', t_schema);
    EXECUTE format('GRANT ALL ON ALL SEQUENCES IN SCHEMA %I TO saas_admin', t_schema);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Indexes
CREATE INDEX idx_tenants_subdomain ON tenants(subdomain);
CREATE INDEX idx_usage_tenant_time ON global_usage_logs(tenant_id, timestamp);