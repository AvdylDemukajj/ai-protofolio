import psycopg2
import os
import uuid

MASTER_DB_URL = os.getenv('MASTER_DB_URL')

def onboard_new_tenant(company_name: str, subdomain: str, plan: str = 'free'):
    conn = psycopg2.connect(MASTER_DB_URL)
    cur = conn.cursor()
    
    tenant_id = uuid.uuid4()
    schema_name = f"tenant_{tenant_id.hex[:8]}"
    
    try:
        # 1. Register in Master Table
        cur.execute("""
            INSERT INTO tenants (id, subdomain, company_name, plan_type, schema_name)
            VALUES (%s, %s, %s, %s, %s)
        """, (tenant_id, subdomain, company_name, plan, schema_name))
        
        # 2. Trigger Schema Creation Function (Atomic)
        cur.execute("SELECT create_tenant_schema(%s, %s)", (tenant_id, schema_name))
        
        conn.commit()
        print(f"✅ Tenant Onboarded: {company_name} ({subdomain}) with Schema: {schema_name}")
        return tenant_id
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Onboarding failed: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Demo Onboarding
    onboard_new_tenant("Acme Corp", "acme", "pro")
    onboard_new_tenant("Stark Industries", "stark", "enterprise")