CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Master Table: Lists all Tenants
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subdomain VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    plan_type VARCHAR(20) DEFAULT 'free',
    schema_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Global Usage Tracking Table (For Billing across all tenants)
CREATE TABLE IF NOT EXISTS global_usage_logs (
    id BIGSERIAL PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    quantity INT DEFAULT 1,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Function to Create a New Tenant Schema dynamically
CREATE OR REPLACE FUNCTION create_tenant_schema(tenant_uuid UUID, schema_name TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', schema_name);

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I.users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email TEXT UNIQUE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )',
        schema_name
    );

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I.data (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            content JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )',
        schema_name
    );

    EXECUTE format('GRANT ALL ON ALL TABLES IN SCHEMA %I TO saas_admin', schema_name);

    RAISE NOTICE 'Schema % created successfully for tenant %', schema_name, tenant_uuid;
END;
$$ LANGUAGE plpgsql;

CREATE INDEX IF NOT EXISTS idx_tenants_subdomain ON tenants(subdomain);
CREATE INDEX IF NOT EXISTS idx_usage_tenant ON global_usage_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON global_usage_logs(timestamp);
