import os

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest


class FraudModel:
    def __init__(self):
        self.model = None
        self._load_or_train()

    def _load_or_train(self):
        model_path = os.getenv("MODEL_PATH", "models/fraud_model.pkl")

        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            print("No model found. Training dummy model...")
            x = np.random.rand(1000, 3)
            self.model = IsolationForest(contamination=0.01, random_state=42)
            self.model.fit(x)
            os.makedirs(os.path.dirname(model_path) or ".", exist_ok=True)
            joblib.dump(self.model, model_path)

    def predict(self, features: dict) -> float:
        """Returns risk score 0.0 to 1.0."""
        vector = np.array(
            [features["amount"], features["hour"], features["velocity"]]
        ).reshape(1, -1)

        prediction = self.model.predict(vector)[0]
        return 0.95 if prediction == -1 else 0.1
