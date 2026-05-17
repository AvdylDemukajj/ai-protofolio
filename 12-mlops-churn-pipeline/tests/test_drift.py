import pandas as pd
from pipeline.drift_detector import check_drift

def test_drift_detection():
    ref_data = pd.DataFrame({'tenure': [1, 2, 3, 4, 5]})
    curr_data_no_drift = pd.DataFrame({'tenure': [1.1, 2.1, 3.1, 4.1, 5.1]})
    curr_data_drift = pd.DataFrame({'tenure': [50, 60, 70, 80, 90]}) # Huge difference
    
    assert check_drift(ref_data, curr_data_no_drift) == False
    assert check_drift(ref_data, curr_data_drift) == True
    
    print("✅ Drift detection tests passed.")

if __name__ == "__main__":
    test_drift_detection()