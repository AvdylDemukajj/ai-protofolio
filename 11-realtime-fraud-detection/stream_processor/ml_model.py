from sklearn.ensemble import IsolationForest
from sklearn.externals import joblib # Deprecated in new sklearn, use joblib directly
import joblib
import numpy as np
import os

class FraudModel:
    def __init__(self):
        self.model = None
        self._load_or_train()

    def _load_or_train(self):
        model_path = os.getenv('MODEL_PATH', 'models/fraud_model.pkl')
        
        # In production, load from S3 or mounted volume
        # For demo, we train a dummy model on startup if not exists
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            print("⚠️ No model found. Training dummy model...")
            # Dummy training data
            X = np.random.rand(1000, 3) 
            self.model = IsolationForest(contamination=0.01, random_state=42)
            self.model.fit(X)
            # Save it
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(self.model, model_path)

    def predict(self, features: dict) -> float:
        """Returns risk score 0.0 to 1.0"""
        vector = np.array([
            features['amount'],
            features['hour'],
            features['velocity']
        ]).reshape(1, -1)
        
        # -1 is outlier (fraud), 1 is normal
        prediction = self.model.predict(vector)[0]
        
        # Convert to probability-like score
        if prediction == -1:
            return 0.95 # High risk
        else:
            return 0.1 # Low risk