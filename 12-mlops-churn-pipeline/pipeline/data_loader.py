import pandas as pd
import os

def load_data(file_path: str = "data/raw/customers.csv") -> pd.DataFrame:
    """Loads and performs basic cleaning on raw data."""
    if not os.path.exists(file_path):
        # Generate synthetic data for demo if file missing
        print("⚠️  Raw data not found. Generating synthetic dataset...")
        return generate_synthetic_data()
    
    df = pd.read_csv(file_path)
    
    # Basic Cleaning
    df = df.dropna()
    df = df.drop_duplicates()
    
    # Feature Engineering (Example)
    if 'total_charges' in df.columns:
        df['total_charges'] = pd.to_numeric(df['total_charges'], errors='coerce')
        
    return df

def generate_synthetic_data() -> pd.DataFrame:
    """Generates realistic mock data for Churn Prediction."""
    import numpy as np
    np.random.seed(42)
    n = 1000
    
    data = {
        'tenure': np.random.randint(1, 72, n),
        'monthly_charges': np.random.uniform(20, 120, n),
        'total_charges': np.random.uniform(100, 8000, n),
        'contract_type': np.random.choice(['Month-to-month', 'One year', 'Two year'], n),
        'payment_method': np.random.choice(['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card'], n),
        'churn': np.random.choice([0, 1], n, p=[0.7, 0.3])
    }
    return pd.DataFrame(data)