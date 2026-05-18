# Audited Workflows

Place **passed** workflow exports here after a clean scan for portfolio evidence.

Example:

```bash
python -m scanner ../01-n8n-support-automation-pack/workflows --fail-on HIGH
cp ../01-n8n-support-automation-pack/workflows/01_support_webhook_intake.json ./01_support_webhook_intake.audited.json
```

Include the SARIF or text report in `../reports/` for audit trail.
