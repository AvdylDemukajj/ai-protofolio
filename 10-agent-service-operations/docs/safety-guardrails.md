# Safety Guardrails Implementation

## Layers
1. **Input Filter**: Scans for injection keywords.
2. **Pre-Execution Check**: Validates tool arguments against policy before calling Python function.
3. **Environment Switch**: Global kill-switch via ENV variable.

## Response to Violations
If a guardrail is triggered, the agent returns a standardized error message explaining the policy violation, rather than executing the tool.