# CI Integration

## GitHub Actions

Add to your repository (adjust paths as needed):

```yaml
name: n8n Workflow Security Scan

on:
  pull_request:
    paths:
      - "**/workflows/**/*.json"
      - "02-n8n-template-hardening-catalog/**"

jobs:
  hardening-scan:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: 02-n8n-template-hardening-catalog

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install scanner
        run: pip install -r requirements.txt

      - name: Run hardening scan
        run: |
          python -m scanner ../01-n8n-support-automation-pack/workflows \
            --format sarif \
            --output reports/scan.sarif \
            --fail-on HIGH \
            --quiet

      - name: Upload SARIF
        if: always()
        uses: github/upload-sarif@v3
        with:
          sarif_file: 02-n8n-template-hardening-catalog/reports/scan.sarif
```

## Azure Pipelines

```yaml
- script: |
    cd 02-n8n-template-hardening-catalog
    pip install -r requirements.txt
    python -m scanner ../01-n8n-support-automation-pack/workflows --fail-on HIGH
  displayName: n8n workflow hardening scan
```

## Pre-commit (optional)

```yaml
repos:
  - repo: local
    hooks:
      - id: n8n-hardening
        name: n8n workflow hardening
        entry: python -m scanner
        language: system
        files: workflows/.*\.json$
        args: [--fail-on, HIGH, --quiet]
```

## Environment variables

| Variable | Purpose |
|----------|---------|
| `LOG_LEVEL` | structlog level (default INFO) |
| `REPORT_OUTPUT_DIR` | Default directory for reports (optional) |

Copy [`.env.example`](../.env.example) for local tooling; the scanner does not require secrets to run.
