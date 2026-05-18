CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Master Table: Lists all Tenants
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subdomain VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    plan_type VARCHAR(20) DEFAULT 'free', -- free, pro, enterprise
    schema_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Global Usage Tracking Table (For Billing across all tenants)
CREATE TABLE IF NOT EXISTS global_usage_logs (
    id BIGSERIAL PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- 'api_call', 'storage_mb', 'user_login'
    quantity INT DEFAULT 1,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Function to Create a New Tenant Schema dynamically
-- This ensures atomic creation of schema + tables
CREATE OR REPLACE FUNCTION create_tenant_schema(tenant_uuid UUID, schema_name TEXT)
RETURNS VOID AS $$
BEGIN
    -- 1. Create Schema
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', schema_name);
    
    -- 2. Create Standard Tables in the new schema
    EXECUTE format('CREATE TABLE %I.users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
        email TEXT UNIQUE, 
        created_at TIMESTAMPTZ DEFAULT NOW()
    )', schema_name);
    
    EXECUTE format('CREATE TABLE %I.data (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
        content JSONB, 
        created_at TIMESTAMPTZ DEFAULT NOW()
    )', schema_name);
    
    -- 3. Grant Permissions (Simplified for demo)
    EXECUTE format('GRANT ALL ON ALL TABLES IN SCHEMA %I TO saas_admin', schema_name);
    
    RAISE NOTICE 'Schema % created successfully for tenant %', schema_name, tenant_uuid;
END;
$$ LANGUAGE plpgsql;

-- Indexes for performance
CREATE INDEX idx_tenants_subdomain ON tenants(subdomain);
CREATE INDEX idx_usage_tenant ON global_usage_logs(tenant_id);
CREATE INDEX idx_usage_timestamp ON global_usage_logs(timestamp);