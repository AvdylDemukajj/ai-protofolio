# Data Model

## `leads`

| Column | Description |
|--------|-------------|
| `id` | UUID primary key |
| `company_name` | Required company name |
| `website_url`, `contact_email`, `industry` | Optional enrichment |
| `employee_count` | Used in scoring heuristics |
| `pain_points` | TEXT[] from agent research |
| `lead_score` | 0–100 AI score |
| `buying_intent` | cold / warm / hot |
| `outreach_strategy` | Agent recommendation |
| `status` | new, processing, pending_review, approved, rejected, qualified |
| `draft_subject`, `draft_body` | Outreach draft |
| `requires_human_review` | Default true until approved |
| `agent_decision` | Last agent action |
| `confidence_score` | Model confidence |

## `interactions`

Email drafts and future touchpoints (`email_draft`, `call_note`, etc.).

## `agent_audit_log`

Immutable log of agent actions with `reasoning` and `confidence_score`.
