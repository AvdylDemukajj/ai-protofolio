# Data Model

## Table: `leads`

Primary store for prospects and AI enrichment results.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `name` | VARCHAR(255) | Contact name |
| `email` | VARCHAR(255) | Unique email (dedup key) |
| `company` | VARCHAR(255) | Company name |
| `company_size` | INTEGER | Employee count for ICP filtering |
| `source` | VARCHAR(50) | `website`, `webhook`, `csv_demo`, etc. |
| `message` | TEXT | Free-text inquiry |
| `external_id` | TEXT | CRM correlation id |
| `lead_score` | INTEGER 0–100 | AI score |
| `intent_category` | VARCHAR(50) | `high_buying`, `medium_interest`, `low_info`, `spam` |
| `summary` | TEXT | AI one-line summary |
| `recommended_action` | TEXT | Next step for sales |
| `status` | VARCHAR(50) | `new`, `validated`, `rejected`, `qualified`, … |
| `requires_human_review` | BOOLEAN | Low-confidence flag |
| `review_reason` | TEXT | Validation rejection reason |
| `created_at` / `updated_at` | TIMESTAMPTZ | Audit timestamps |

## Table: `lead_audit_log`

Immutable trail of workflow and AI decisions.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `lead_id` | UUID FK | Nullable for global errors |
| `workflow_step` | VARCHAR(100) | `intake`, `validation`, `scoring`, `error` |
| `model_version` | VARCHAR(50) | e.g. `gpt-4o-mini` |
| `input_hash` | VARCHAR(64) | SHA-256 of key fields (no full PII in log) |
| `ai_output_json` | JSONB | Raw model or rule output |
| `execution_time_ms` | INTEGER | Optional timing |
| `execution_timestamp` | TIMESTAMPTZ | When recorded |

## Indexes

- `email`, `status`, `lead_score DESC`, `source`
- `lead_audit_log(lead_id)`

## Seed data

`database/seed_data.sql` inserts five sample leads with `status = new` for immediate validation testing.
