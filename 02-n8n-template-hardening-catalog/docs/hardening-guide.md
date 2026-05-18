# Hardening Guide for n8n Developers

## DO

- Store secrets in **n8n Credentials** or `$env` variables injected by Docker/Kubernetes.
- Validate webhooks with a shared secret header or HMAC before any database write.
- Link an **Error Workflow** (or include an Error Trigger) on every production workflow.
- Use **HTTPS** for all external HTTP Request nodes and public webhook base URLs.
- Pin n8n Docker images to a specific version (never `latest` in production).
- Run `python -m scanner` on exports **before** every production import.
- Re-export workflows after linking error handlers so audits reflect UI configuration.

## DON'T

- Paste API keys, Slack webhooks, or passwords into node parameter fields.
- Commit `.env` files or credential exports to git.
- Expose webhooks without authentication on the first processing nodes.
- Use Execute Command nodes in production automation paths.
- Use `eval()`, `child_process`, or shell execution inside Code nodes.
- Ignore MEDIUM/LOW findings — they often indicate future CRITICAL failures.

## Secure credential pattern

**Incorrect** (flagged as CRITICAL):

```json
"parameters": {
  "headerParameters": {
    "parameters": [
      { "name": "Authorization", "value": "Bearer sk-abc123..." }
    ]
  }
}
```

**Correct**:

1. Create **Credentials → OpenAI** (or HTTP Header Auth) in n8n.
2. Select the credential from the node dropdown.
3. Export workflow — JSON should reference credential id/name, not the secret.

## Secure webhook pattern

```
Webhook → Code (verify X-Webhook-Secret) → IF authorized → business logic
                              └→ Respond 401
```

See Project 1 `01_support_webhook_intake.json` for a reference implementation.

## Slack notifications

Use environment injection:

```
url: ={{ $env.SLACK_WEBHOOK_URL }}
```

Not a hardcoded `https://hooks.slack.com/services/...` URL in parameters.

## CI gate example

```bash
python -m scanner ./workflows --fail-on HIGH --format sarif --output reports/scan.sarif
```

Pipeline should fail when exit code is `1`.

## Remediation priority

1. CRITICAL — block merge / import
2. HIGH — block merge unless risk accepted
3. MEDIUM — fix before production go-live
4. LOW / INFO — track in backlog or fix during import checklist
