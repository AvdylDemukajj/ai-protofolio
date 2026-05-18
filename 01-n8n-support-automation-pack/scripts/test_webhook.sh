#!/usr/bin/env bash
# Test the support-intake webhook (activate workflow 01 in n8n first).
set -euo pipefail

WEBHOOK_URL="${WEBHOOK_URL:-http://localhost:5678/webhook/support-intake}"
WEBHOOK_SECRET="${WEBHOOK_SECRET:?Set WEBHOOK_SECRET in your environment or .env}"

curl -sS -X POST "${WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: ${WEBHOOK_SECRET}" \
  -d '{
    "customer_email": "test.user@example.com",
    "subject": "Urgent refund - charged twice",
    "body": "I was charged twice for invoice #999. Please refund immediately.",
    "external_id": "test-webhook-001"
  }' | jq .

echo ""
echo "Run: python scripts/validate_tickets.py"
