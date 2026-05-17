import os
import mlflow
import mlflow.sklearn
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from pipeline.data_loader import load_data
from pipeline.drift_detector import check_drift
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_pipeline():
    # 1. Setup MLflow
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment("churn_prediction_prod")
    
    logger.info("🚀 Starting MLOps Pipeline...")
    
    # 2. Load Data
    df = load_data()
    logger.info(f"Loaded {len(df)} records.")
    
    # 3. Prepare Features
    # Simple encoding for demo
    df['contract_type'] = df['contract_type'].map({'Month-to-month': 0, 'One year': 1, 'Two year': 2})
    X = df[['tenure', 'monthly_charges', 'total_charges', 'contract_type']]
    y = df['churn']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Check for Existing Model & Drift
    # In prod, load last registered model's training data as reference
    reference_data = X_train # Simplified for demo
    current_data = X_test 
    
    drift_detected = check_drift(reference_data, current_data)
    
    if drift_detected:
        logger.warning("⚠️  Drift detected! Triggering retraining...")
    else:
        logger.info("✅ No significant drift. Checking model performance...")
        # Logic to load existing model and evaluate could go here
        # For demo, we always train to show the flow
    
    # 5. Train Model
    logger.info("Training Random Forest Classifier...")
    with mlflow.start_run():
        clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        clf.fit(X_train, y_train)
        
        # 6. Evaluate
        preds = clf.predict(X_test)
        acc = accuracy_score(y_test, preds)
        
        logger.info(f"Model Accuracy: {acc:.4f}")
        logger.info(classification_report(y_test, preds))
        
        # Log parameters and metrics
        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("accuracy", acc)
        
        # 7. Register Model if good enough
        threshold = float(os.getenv("MIN_ACCURACY_THRESHOLD", 0.75))
        if acc >= threshold:
            model_info = mlflow.sklearn.log_model(clf, "model")
            mlflow.register_model(model_info.model_uri, "ChurnPredictionModel")
            logger.info(f"✅ Model registered successfully with accuracy {acc:.4f}")
            
            # Save locally too
            os.makedirs("models", exist_ok=True)
            joblib.dump(clf, "models/model_v_latest.pkl")
        else:
            logger.error(f"❌ Model accuracy {acc:.4f} is below threshold {threshold}. Not registering.")
            raise Exception("Model performance below threshold")

if __name__ == "__main__":
    run_pipeline()