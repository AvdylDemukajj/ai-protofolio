# Agent Behavior Policy

## Routing Rules
- **Billing**: Keywords: "bill", "pay", "invoice", "charge".
- **Technical**: Keywords: "error", "bug", "login", "api".
- **Refunds**: Keywords: "cancel", "return", "money back".

## Escalation
- Any query with aggressive sentiment or low confidence (<0.6) escalates to "Human Review".
- Financial commitments > $1000 require manual approval.