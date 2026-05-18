# Security Audit Baseline

## Authentication

- Optional `X-API-Key` on all `/leads/*` mutating and listing endpoints
- `/health` remains public for load balancers
- n8n/UI: no default credentials in repo — configure via `.env`

## Secrets

- `.env` gitignored; never commit `OPENAI_API_KEY`, `DB_PASSWORD`, `API_KEY`
- Slack webhook via environment variable only

## Input validation

- Pydantic schemas on API (`LeadCreate` email, field lengths)
- `sanitize_input` utility available for free-text extensions

## Data protection

- `agent_audit_log` stores reasoning, not full duplicate PII
- Draft emails in `interactions` table until approved

## Agent safety

- All outreach drafts require `requires_human_review=true` by default
- No auto-send email in production path (simulation only)
- Reject path for low scores and spam-like profiles

## Infrastructure

- Postgres on internal Docker network
- CORS restricted via `CORS_ORIGINS`
- Non-root Python slim images

## Pre-deploy checklist

- [ ] `API_KEY` set in production
- [ ] Strong `DB_PASSWORD`
- [ ] HTTPS termination at proxy
- [ ] OpenAI usage limits / monitoring enabled
- [ ] Slack webhook scoped to ops channel
