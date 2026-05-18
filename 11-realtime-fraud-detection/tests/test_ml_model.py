import os
import tempfile

import joblib
import numpy as np
import pytest
from sklearn.ensemble import IsolationForest

from stream_processor.ml_model import FraudModel


def test_fraud_model_predict_range():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "fraud_model.pkl")
        model = IsolationForest(contamination=0.01, random_state=42)
        model.fit(np.random.rand(200, 3))
        joblib.dump(model, path)

        os.environ["MODEL_PATH"] = path
        fraud = FraudModel()
        score = fraud.predict({"amount": 100.0, "hour": 12, "velocity": 1})
        assert 0.0 <= score <= 1.0
