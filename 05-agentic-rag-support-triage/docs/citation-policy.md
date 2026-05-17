# Citation Policy

## Requirement
Every AI-generated response MUST be grounded in the retrieved context.

## Enforcement
- The system prompt explicitly instructs the model: "Answer ONLY using the provided context."
- The `ValidationService` performs a keyword overlap check. If the answer contains terms not found in the context, it is flagged as unverified.
- Low confidence scores trigger a "Human Handoff" workflow in the frontend.