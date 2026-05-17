import mlflow

def get_latest_model_version(model_name: str = "ChurnPredictionModel"):
    """Fetches the latest version of a registered model."""
    client = mlflow.tracking.MlflowClient()
    try:
        versions = client.get_latest_versions(model_name, stages=["Production"])
        if not versions:
            # Fallback to any stage if no Production
            versions = client.get_latest_versions(model_name, stages=["Staging", "Archived"])
        return versions[0] if versions else None
    except Exception as e:
        print(f"Error fetching model: {e}")
        return None