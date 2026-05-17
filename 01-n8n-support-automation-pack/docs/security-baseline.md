# Security Baseline

## 1. Credential Management
- All secrets stored in `.env` (gitignored).
- n8n Encryption Key set via env var.
- No hardcoded passwords in workflows.

## 2. Access Control
- Basic Auth enabled on n8n UI.
- Database accessible only from n8n container.

## 3. Data Protection
- PII (emails) stored in DB. In production, consider column-level encryption.
- Audit logs store input hashes instead of raw data where possible.

## 4. Infrastructure
- Containers run as non-root user (default in official images).
- Read-only root filesystem recommended for production (advanced).