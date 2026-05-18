# Workflow Logic & Business Rules

## 1. Lead webhook intake (Workflow 01)

- **Trigger:** `POST /webhook/lead-intake`
- **Auth:** `X-Webhook-Secret` must match `WEBHOOK_SECRET`
- **Required fields:** `name`, `email`, `company_size` (integer ≥ 0)
- **Upsert:** `ON CONFLICT (email)` updates existing lead
- **Audit:** `lead_audit_log` step `intake`
- **Response:** `200` with `lead_id`, `email`, `status`

## 2. Validation schedule (Workflow 02)

- **Trigger:** Every 15 minutes
- **Input:** Leads with `status = 'new'` (max 50 per run)
- **Rules:**
  - Email matches standard regex
  - `company_size >= 10`
  - Spam hints in email/message → `rejected`
- **Output status:** `validated` or `rejected` with `review_reason`
- **Audit:** step `validation`

## 3. AI scoring & routing (Workflow 03)

- **Trigger:** Every 15 minutes
- **Input:** Leads with `status = 'validated'` (max 25 per run)
- **Model:** `gpt-4o-mini` via OpenAI credentials
- **JSON output:** `lead_score`, `intent_category`, `summary`, `recommended_action`, `confidence`
- **Post-processing:**
  - Parse failures → score 50, `low_info`, confidence 0
  - `intent_category = spam` → cap score at 20, flag human review
  - `confidence < 0.6` → `requires_human_review = true`
- **Status after scoring:** `qualified`
- **Slack alert when:**
  - `lead_score >= 80`
  - `confidence >= 0.6`
  - `intent_category != spam`
- **Audit:** step `scoring` with full AI JSON

## 4. Demo CSV batch (Workflow 04)

- Manual trigger only
- Inserts rows from `demo-data/leads_batch_import.csv` with `source = csv_demo`
- Does not bypass validation — run workflow 02 after import

## 5. Error handling (Workflow 05)

- Logs to `lead_audit_log` with `workflow_step = error`
- Optional Slack ops alert via `SLACK_WEBHOOK_URL`

## Lead status machine

```
new → validated → qualified
new → rejected
```

Hot leads are `qualified` with high `lead_score`; Slack is a side effect, not a separate status.
