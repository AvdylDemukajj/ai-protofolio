import joblib, os
from sklearn.ensemble import RandomForestClassifier
def train():
    clf = RandomForestClassifier()
    clf.fit([[1,2]], [0])
    os.makedirs('models', exist_ok=True)
    joblib.dump(clf, 'models/model_v1.pkl')
    print("Model Saved")
if __name__ == "__main__": train()