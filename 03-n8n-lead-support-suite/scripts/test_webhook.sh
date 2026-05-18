#!/usr/bin/env bash
# Test lead webhook intake (activate workflow 01 first).
set -euo pipefail

WEBHOOK_URL="${WEBHOOK_URL:-http://localhost:5679/webhook/lead-intake}"
WEBHOOK_SECRET="${WEBHOOK_SECRET:?Set WEBHOOK_SECRET}"

curl -sS -X POST "${WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: ${WEBHOOK_SECRET}" \
  -d '{
    "name": "Jane CTO",
    "email": "jane.cto@enterprise.io",
    "company": "Enterprise IO",
    "company_size": 250,
    "message": "We need AI lead routing for our sales team this quarter.",
    "source": "website",
    "external_id": "test-lead-001"
  }'

echo ""
echo "Run: python scripts/validate_leads.py"
