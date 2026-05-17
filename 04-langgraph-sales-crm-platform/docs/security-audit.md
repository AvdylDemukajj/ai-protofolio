# Security Audit

## Measures
- **API Key Management**: Keys stored in env vars, never in code.
- **Input Validation**: Pydantic models enforce strict types.
- **DB Security**: Parameterized queries via SQLAlchemy prevent SQL injection.
- **Network**: Services isolated in Docker network `sales-network`.