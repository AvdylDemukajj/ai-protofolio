import logging
import os

import joblib
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from pipeline.data_loader import load_data
from pipeline.drift_detector import check_drift

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_pipeline():
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment("churn_prediction_prod")

    logger.info("Starting MLOps Pipeline...")

    df = load_data()
    logger.info("Loaded %s records.", len(df))

    df["contract_type"] = df["contract_type"].map(
        {"Month-to-month": 0, "One year": 1, "Two year": 2}
    )
    features = ["tenure", "monthly_charges", "total_charges", "contract_type"]
    x = df[features]
    y = df["churn"]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    if check_drift(x_train, x_test):
        logger.warning("Drift detected. Retraining...")
    else:
        logger.info("No significant drift detected.")

    logger.info("Training Random Forest Classifier...")
    with mlflow.start_run():
        clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        clf.fit(x_train, y_train)

        preds = clf.predict(x_test)
        acc = accuracy_score(y_test, preds)

        logger.info("Model Accuracy: %.4f", acc)
        logger.info("\n%s", classification_report(y_test, preds))

        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("accuracy", acc)

        threshold = float(os.getenv("MIN_ACCURACY_THRESHOLD", "0.75"))
        if acc >= threshold:
            model_info = mlflow.sklearn.log_model(clf, "model")
            try:
                mlflow.register_model(model_info.model_uri, "ChurnPredictionModel")
            except Exception as exc:
                logger.warning("Model registry skipped: %s", exc)

            os.makedirs("models", exist_ok=True)
            joblib.dump(clf, "models/model_v_latest.pkl")
            logger.info("Model registered with accuracy %.4f", acc)
        else:
            raise RuntimeError(
                f"Model accuracy {acc:.4f} is below threshold {threshold}"
            )


if __name__ == "__main__":
    run_pipeline()
