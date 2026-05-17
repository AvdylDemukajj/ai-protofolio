import pytest
from pipeline.data_loader import generate_synthetic_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def test_data_generation():
    df = generate_synthetic_data()
    assert len(df) > 0
    assert 'churn' in df.columns
    print("✅ Data generation test passed.")

def test_model_training():
    df = generate_synthetic_data()
    df['contract_type'] = df['contract_type'].map({'Month-to-month': 0, 'One year': 1, 'Two year': 2})
    X = df[['tenure', 'monthly_charges', 'total_charges', 'contract_type']]
    y = df['churn']
    
    clf = RandomForestClassifier(n_estimators=10)
    clf.fit(X, y)
    preds = clf.predict(X)
    
    acc = accuracy_score(y, preds)
    assert acc > 0.5 # Better than random
    print(f"✅ Training test passed with accuracy {acc:.2f}")

if __name__ == "__main__":
    test_data_generation()
    test_model_training()