from flask import Flask, request, g, jsonify
from core.tenant_resolver import tenant_required
from billing_engine.usage_tracker import track_api_call
import json

app = Flask(__name__)

@app.route('/health')
def health():
    return {"status": "ok"}

@app.route('/api/v1/data', methods=['GET', 'POST'])
@tenant_required
def handle_data():
    tenant = g.tenant
    cursor = g.db_cursor
    
    if request.method == 'POST':
        data = request.json
        # Insert into Tenant's isolated schema
        cursor.execute("INSERT INTO data (content) VALUES (%s) RETURNING id", (json.dumps(data),))
        new_id = cursor.fetchone()[0]
        g.db_conn.commit()
        
        # Track Usage for Billing
        track_api_call(tenant['id'])
        
        return jsonify({"id": new_id, "tenant": tenant['subdomain'], "status": "created"}), 201
        
    else:
        # Select from Tenant's isolated schema
        cursor.execute("SELECT id, content FROM data")
        rows = cursor.fetchall()
        return jsonify([{"id": r[0], "content": r[1]} for r in rows])

@app.route('/api/v1/users', methods=['GET'])
@tenant_required
def get_users():
    cursor = g.db_cursor
    cursor.execute("SELECT email FROM users")
    rows = cursor.fetchall()
    return jsonify([r[0] for r in rows])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)