# Audit Methodology

## 1. Static analysis only

Workflow JSON exports are parsed and inspected **without execution**. This guarantees:

- No accidental API calls during audit
- Fast feedback in CI (milliseconds per file)
- Safe use on untrusted third-party templates

## 2. Rule-driven engine

All checks are declared in `rules/security_rules.json`:

- Enable/disable individual rules
- Adjust severities per organization policy
- Extend `secret_patterns` for internal token formats

The engine (`scanner/engine.py`) loads rules at startup and applies them consistently across files.

## 3. Pattern matching

Regular expressions detect known secret formats:

- OpenAI `sk-...` keys
- Slack `xox*` tokens
- AWS `AKIA...` access keys
- Generic `api_key=` / `password=` assignments

False positives are minimized by scoping searches to **node parameters** (not workflow metadata).

## 4. Graph traversal

For webhook security, the scanner builds a directed graph from `connections` and walks up to **4 hops** from each Webhook node. It passes only if a downstream **Code** node references authentication markers such as:

- `x-webhook-secret`
- `WEBHOOK_SECRET`
- `authorized`
- `hmac` / `signature`

This mirrors real-world patterns used in production intake workflows.

## 5. Compliance mapping

| Policy | Scanner rule |
|--------|----------------|
| No plaintext credentials | `hardcoded_credentials`, `hardcoded_slack_webhook` |
| Authenticated webhooks | `public_webhooks` |
| TLS for external calls | `insecure_http` |
| Operational resilience | `missing_error_handling` |
| Least privilege execution | `shell_execution_nodes`, `dangerous_code_execution` |

## 6. Reporting

Outputs support:

- **text** — human review in terminal
- **json** — automation and dashboards
- **sarif** — GitHub Advanced Security, Azure DevOps, GitLab SAST viewers

## 7. Limitations

- Cannot detect runtime misconfigurations (e.g. weak n8n UI password)
- Cannot verify credential *values*, only binding patterns
- Error workflow links set only in the UI may not appear in exported JSON until re-exported

Document known gaps in your change request when exporting workflows for audit.
