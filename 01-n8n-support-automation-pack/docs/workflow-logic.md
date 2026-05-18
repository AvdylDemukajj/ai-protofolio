# Workflow Logic & Business Rules

## 1. Webhook Intake (Workflow 01)

- **Trigger:** `POST /webhook/support-intake`
- **Auth:** Header `X-Webhook-Secret` must match `WEBHOOK_SECRET` from the environment.
- **Validation:**
  - `customer_email`, `subject`, and `body` are required.
  - Email must match a basic RFC-like pattern.
- **On success:** Returns HTTP 200 with `ticket_id`, `priority`, `category`, and `status`.

## 2. AI Classification (Workflows 01 & 02)

- **Model:** `gpt-4o-mini` via n8n OpenAI credentials.
- **Output:** Strict JSON with `category`, `priority`, `confidence`, `summary`, `recommended_action`, `sentiment`.
- **Parse failure:** Defaults to `category=other`, `priority=medium`, `confidence=0`, `recommended_action=escalate_human`.

### Keyword escalation

If the subject or body contains any of these phrases, priority is raised to at least `high`:

- `refund`
- `charged twice`
- `down`
- `outage`
- `cancel immediately`

### Low-confidence handling

If `confidence < 0.6`:

- Set `assigned_to = ai_low_confidence`
- Do **not** send Slack, even when priority is `high`

## 3. Slack routing

Slack is called only when:

- `priority === high`
- **and** `confidence >= 0.6`
- **and** `SLACK_WEBHOOK_URL` is configured in the environment

## 4. Demo CSV batch (Workflow 02)

- **Trigger:** Manual (local demo only; keep inactive in production).
- Reads `demo-data/support_emails.csv` from the mounted volume.
- Uses the same classification and persistence rules as workflow 01.
- Sets `source = csv_demo` on inserted tickets.

## 5. Error handling (Workflow 03)

- **Trigger:** n8n Error Trigger (link from workflows 01 and 02 in the UI).
- Writes an `audit_logs` row with `workflow_step = error`.
- Sends an ops alert to Slack when `SLACK_WEBHOOK_URL` is set (non-blocking on failure).
