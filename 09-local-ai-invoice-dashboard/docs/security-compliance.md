# Security & Compliance

## Data Privacy
- **Local Execution**: LLM runs locally via Ollama. No data leaves the container network.
- **Encryption**: Data at rest in Postgres; TLS recommended for transit in production.

## Financial Integrity
- **Deterministic Checks**: Math validation is code-based, not AI-based, ensuring 100% accuracy on sums.
- **Human Oversight**: No payment is authorized without explicit user approval in the dashboard.