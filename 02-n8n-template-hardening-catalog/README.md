# Project 2: n8n Template Hardening Catalog

**Status:** Production-ready CLI | CI/SARIF support | Graph-aware security rules

Static security scanner for **exported n8n workflow JSON** files. Run it in CI or locally **before** importing workflows into production n8n.

## What it detects

| Rule | Severity | Description |
|------|----------|-------------|
| `hardcoded_credentials` | CRITICAL | API keys, passwords, tokens in node parameters |
| `hardcoded_slack_webhook` | CRITICAL | Static `hooks.slack.com` URLs |
| `missing_credential_binding` | HIGH | Postgres/OpenAI/HTTP nodes without Credentials |
| `public_webhooks` | HIGH | Webhook triggers without downstream auth validation |
| `insecure_http` | HIGH | Non-HTTPS external URLs |
| `dangerous_code_execution` | CRITICAL | `eval`, `child_process`, etc. in Code nodes |
| `shell_execution_nodes` | CRITICAL | Execute Command nodes |
| `missing_error_handling` | MEDIUM | No Error Trigger or `settings.errorWorkflow` |
| `placeholder_credentials` | INFO | `PLACEHOLDER` credential IDs after import |
| `execution_settings` | LOW | Missing `executionOrder` in settings |

Rules are configurable in [`rules/security_rules.json`](rules/security_rules.json).

## Quick start

```bash
cd 02-n8n-template-hardening-catalog
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
```

### Scan one workflow

```bash
python -m scanner ../01-n8n-support-automation-pack/workflows/01_support_webhook_intake.json
```

### Scan a directory (recursive)

```bash
python -m scanner ../01-n8n-support-automation-pack/workflows/
```

### CI mode (SARIF + non-zero exit)

```bash
python -m scanner ./workflows/ \
  --format sarif \
  --output reports/scan.sarif \
  --fail-on HIGH \
  --quiet
```

Exit codes:

| Code | Meaning |
|------|---------|
| `0` | No issues at or above `--fail-on` threshold |
| `1` | Security issues found |
| `2` | Scan error (missing file, invalid JSON) |

### Installed CLI (optional)

```bash
pip install -e .
n8n-hardening ../01-n8n-support-automation-pack/workflows/ --fail-on HIGH
```

## Portfolio integration

Scan Project 1 before every production import:

```bash
# Linux/macOS
./scripts/scan_directory.sh ../01-n8n-support-automation-pack/workflows

# Windows PowerShell
./scripts/scan_directory.ps1 -Target "..\01-n8n-support-automation-pack\workflows"
```

Expected INFO findings on template exports:

- `placeholder_credentials` until credentials are bound in the n8n UI
- `missing_error_handling` until **Error Workflow** is linked in workflow settings

## Development

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Project structure

```
02-n8n-template-hardening-catalog/
├── scanner/
│   ├── cli.py           # CLI entry
│   ├── engine.py        # Rule engine
│   ├── graph.py         # Connection graph analysis
│   ├── models.py        # Pydantic models
│   └── reporters.py     # text / JSON / SARIF
├── rules/
│   └── security_rules.json
├── tests/
│   ├── fixtures/        # Safe & insecure samples
│   └── test_scanner.py
├── scripts/
│   ├── scan_directory.sh
│   └── scan_directory.ps1
├── reports/             # gitignored scan output
└── docs/
    ├── audit-methodology.md
    ├── hardening-guide.md
    └── ci-integration.md
```

## Documentation

- [Audit methodology](docs/audit-methodology.md)
- [Hardening guide for developers](docs/hardening-guide.md)
- [CI integration (GitHub Actions)](docs/ci-integration.md)

## Design note

This scanner performs **static analysis only** — workflows are never executed. Secret patterns and graph rules are versioned in `rules/security_rules.json` for auditability.
