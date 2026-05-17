FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for building packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY pipeline/ ./pipeline/
COPY tests/ ./tests/

# Set environment variable for MLflow
ENV MLFLOW_TRACKING_URI=http://mlflow-server:5000
