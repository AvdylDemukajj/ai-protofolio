# Audit Methodology

## 1. Static Analysis
We parse the JSON structure of n8n workflows without executing them. This ensures safety and speed.

## 2. Pattern Matching
Regular expressions are used to detect known secret patterns (e.g., `sk-...` for OpenAI).

## 3. Graph Traversal
(In advanced versions) We traverse the node connections to ensure every critical action has an error handling path (Error Trigger).

## 4. Compliance Check
Workflows are checked against internal security policies:
- No plaintext credentials.
- All external HTTP calls must use HTTPS.
- Webhooks must validate signatures.