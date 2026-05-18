# Project 12: MLOps Churn Prediction Pipeline

## Overview

End-to-end **MLOps** workflow for churn prediction: training, drift checks, MLflow tracking, and model registration.

## Architecture

- **MLflow Server** (port 5000) — experiments and artifacts
- **PostgreSQL** (host port 5435) — MLflow backend store
- **Pipeline runner** — trains Random Forest, logs metrics, saves `models/model_v_latest.pkl`

## Quick start

```bash
docker compose up -d --build
# Trainer runs automatically in pipeline-runner container
docker compose logs pipeline-runner
```

Open MLflow UI: http://localhost:5000

## Local training

```bash
pip install -r requirements.txt
export MLFLOW_TRACKING_URI=http://localhost:5000
export MIN_ACCURACY_THRESHOLD=0.5
python -m pipeline.trainer
```

## Tests

```bash
pytest
# or explicitly:
pytest tests/test_training.py -v
```

`pytest.ini` configures `tests/` as the default path.

## Ports

| Service | Host port |
|---------|-----------|
| MLflow | 5000 |
| MLflow Postgres | 5435 |
