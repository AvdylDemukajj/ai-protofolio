# Agent Behavior Policy

## Purpose

The sales agent assists SDRs by researching accounts and drafting outreach. It does **not** send email autonomously.

## Decision rules

| Lead score | Action |
|------------|--------|
| **≥ 70** | Generate email draft → `pending_review` |
| **40–69** | Up to 2 research iterations, then reject if still below 70 |
| **< 40** | Reject — no draft |

## Confidence handling

- Model returns `confidence` 0.0–1.0 in analysis
- Logged in `agent_audit_log.confidence_score`
- Future: flag `requires_human_review` when confidence < 0.6 (UI filter)

## Slack notifications

Sent when:

- Lead status is `pending_review`
- `lead_score >= 70`

## Human approval

Required before any external send:

- Reviewer uses Streamlit or `POST /leads/{id}/approve`
- Rejection logs `human_reject` in audit trail

## Prohibited behaviors

- Auto-send without approval
- Fabricating customer data not in `company_info`
- Bypassing API key in production

## Model configuration

- Default: `gpt-4o-mini`
- Temperature: 0.2 for consistent JSON
- Override via `OPENAI_MODEL` in `.env`
