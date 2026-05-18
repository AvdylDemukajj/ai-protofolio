# Tenant Architecture Details

## Strategy: Schema-per-Tenant
We chose Schema isolation over Column isolation (`tenant_id` column) for the following reasons:
1. **Security**: Physical separation reduces risk of data leakage.
2. **Compliance**: Easier to export/delete data for GDPR per tenant.
3. **Performance**: Smaller indexes per schema.
4. **Customization**: Allows enterprise clients to have custom table structures if needed.

## Connection Flow
1. Request arrives with `Host: clientA.api.com`.
2. `TenantResolver` extracts `clientA`.
3. Checks Redis Cache. If miss, queries Master DB `tenants` table.
4. Establishes DB connection and executes `SET search_path TO tenant_clientA`.
5. All subsequent SQL queries in that request context automatically target the correct schema.