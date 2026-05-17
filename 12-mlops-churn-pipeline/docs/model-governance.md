# Model Governance Policy

## Approval Process
- Models must achieve >75% accuracy to be registered.
- Models showing high drift (>10%) trigger an immediate retraining job.
- Promotion from "Staging" to "Production" requires manual approval via MLflow UI or API in strict environments.

## Audit Trail
- Every prediction in production should log the `model_version` used.
- All training datasets are versioned and stored as artifacts.