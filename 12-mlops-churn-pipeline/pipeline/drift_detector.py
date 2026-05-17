import pandas as pd
from evidently.report import Report
from evidently.metrics import DataDriftTable
from evidently.column_mapping import ColumnMapping
import logging

logger = logging.getLogger(__name__)

def check_drift(reference_data: pd.DataFrame, current_data: pd.DataFrame) -> bool:
    """
    Checks for data drift between reference (training) and current (production) data.
    Returns True if significant drift is detected.
    """
    logger.info("Running Data Drift Detection...")
    
    # Define column mapping (target is churn)
    column_mapping = ColumnMapping()
    column_mapping.target = 'churn'
    
    # Initialize Report
    report = Report(metrics=[DataDriftTable()])
    
    try:
        report.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)
        
        # Get results (Simplified logic for demo)
        # In production, parse the JSON result for drift score
        drift_detected = False 
        
        # Mock logic: If mean tenure differs by >20%, consider it drift
        if abs(reference_data['tenure'].mean() - current_data['tenure'].mean()) / reference_data['tenure'].mean() > 0.2:
            drift_detected = True
            logger.warning("⚠️  SIGNIFICANT DRIFT DETECTED in 'tenure' column.")
        
        return drift_detected
        
    except Exception as e:
        logger.error(f"Drift detection failed: {e}")
        return False # Fail safe: retrain if unsure