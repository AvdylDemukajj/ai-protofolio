# Hardening Guide for n8n Developers

## ✅ DO:
- Use the **Credentials** feature in n8n for all API keys and passwords.
- Add **Error Trigger** nodes to catch failures in critical steps.
- Use **HTTPS** for all webhook URLs and API endpoints.
- Validate incoming webhook payloads (e.g., check GitHub signatures).

## ❌ DON'T:
- Never paste API keys directly into the "Parameters" field of a node.
- Never commit `.env` files containing real secrets.
- Don't ignore error outputs from HTTP Request nodes.

## Example: Secure Credential Usage
Instead of typing `my-secret-key` in the node:
1. Go to **Credentials** > **Add New**.
2. Select **HTTP Header Auth** or specific API type.
3. Reference it in the node via the dropdown menu.