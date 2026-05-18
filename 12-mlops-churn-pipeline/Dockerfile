FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pipeline/ ./pipeline/
COPY tests/ ./tests/
COPY pytest.ini .

ENV MLFLOW_TRACKING_URI=http://mlflow-server:5000
ENV PYTHONPATH=/app

CMD ["python", "-m", "pipeline.trainer"]
