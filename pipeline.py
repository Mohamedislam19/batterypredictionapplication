"""
End-to-end battery health prediction pipeline
Orchestrates feature engineering + model inference
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from feature_engineering import engineer_features_from_cycle_data
from python_bridge import predict_battery_health
import pandas as pd


def predict_from_csv(csv_path):
    """
    Complete pipeline: CSV → Features → Predictions
    
    Args:
        csv_path: Path to CSV file with battery cycle data
        
    Returns:
        Dictionary with predictions and metadata
    """
    try:
        # Step 1: Load CSV
        df = pd.read_csv(csv_path)
        cycle_data = df.to_dict('records')
        
        # Step 2: Engineer features
        features = engineer_features_from_cycle_data(cycle_data)
        
        # Step 3: Get predictions
        predictions = predict_battery_health(features)
        
        if not predictions.get('success'):
            return predictions
        
        # Step 4: Combine results
        return {
            "success": True,
            "file": str(csv_path),
            "records": len(cycle_data),
            "features_engineered": len(features),
            "predictions": predictions,
            "engineered_features": features,  # Include full feature set for verification
            "sample_features": {k: features[k] for k in list(features.keys())[:5]}  # First 5 for debugging
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": __import__('traceback').format_exc()
        }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python pipeline.py <csv_file_path>"
        }))
        sys.exit(1)
    
    csv_path = sys.argv[1]
    result = predict_from_csv(csv_path)
    print(json.dumps(result, indent=2))
    
    if not result.get('success'):
        sys.exit(1)


if __name__ == "__main__":
    main()
