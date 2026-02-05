"""
Battery Health Prediction - Python Bridge for Electron
Provides inference API callable from Node.js via child_process
"""

import sys
import json
import numpy as np
from pathlib import Path

# Add parent directory to path to import tools
sys.path.insert(0, str(Path(__file__).parent / "Battery-health-prediction-develop"))

try:
    import tools
except ImportError as e:
    print(json.dumps({"error": f"Failed to import tools: {e}"}))
    sys.exit(1)

def predict_battery_health(features_dict):
    """
    Predict battery health from features
    
    Args:
        features_dict: Dictionary of battery features
        
    Returns:
        Dictionary with SOH and RUL predictions
    """
    try:
        # SOH Classification
        soh_class, soh_proba = tools.predict_soh_class(features_dict)
        
        # RUL Classification
        rul_class, rul_proba = tools.predict_rul_class(features_dict)
        
        # Interpret results
        soh_healthy_prob = float(soh_proba[1])  # Probability of Healthy (SOH >= 80%)
        rul_short_prob = float(rul_proba[1])     # Probability of Short RUL
        
        # Estimate numerical SOH (approximate from probability)
        # If healthy prob is high, SOH is likely > 80%
        # This is an approximation since classifier only gives binary output
        estimated_soh = 80 + (soh_healthy_prob * 20)  # Maps 0->80%, 1->100%
        
        # Estimate numerical RUL (approximate from probability)
        # From training: threshold was ~81 cycles
        # If short RUL prob is high, RUL is likely < 81 cycles
        rul_threshold = 81
        estimated_rul = rul_threshold * (1 - rul_short_prob) + rul_threshold * rul_short_prob * 0.5
        
        return {
            "success": True,
            "soh": {
                "class": int(soh_class),
                "class_name": "Healthy" if soh_class == 1 else "Not-Healthy",
                "probability": soh_healthy_prob,
                "estimated_value": round(estimated_soh, 1)
            },
            "rul": {
                "class": int(rul_class),
                "class_name": "Short RUL" if rul_class == 1 else "Not-Short RUL",
                "probability": rul_short_prob,
                "estimated_cycles": round(estimated_rul, 0)
            },
            "classification": "Healthy" if soh_class == 1 else "Not-Healthy",
            "confidence": float((soh_healthy_prob + (1 - rul_short_prob)) / 2)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": __import__('traceback').format_exc()
        }


def get_feature_names():
    """Get required feature names"""
    try:
        return {
            "success": True,
            "soh_features": tools.get_soh_feature_names(),
            "rul_features": tools.get_rul_feature_names()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main entry point for command-line interface"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "No command provided. Usage: python python_bridge.py <command> [args]"
        }))
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "predict":
        # Expecting features as JSON string in argv[2]
        if len(sys.argv) < 3:
            print(json.dumps({"error": "No features provided"}))
            sys.exit(1)
        
        try:
            features = json.loads(sys.argv[2])
            result = predict_battery_health(features)
            print(json.dumps(result))
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {e}"}))
            sys.exit(1)
    
    elif command == "features":
        # Return required feature names
        result = get_feature_names()
        print(json.dumps(result))
    
    elif command == "test":
        # Test with sample features (using average values from training data)
        test_features = {
            "energy_int_wh": 5.5,
            "time_to_3v6": 1000.0,
            "v_t50": 3.5,
            "Rct_imp": 0.07,
            "chg_v_mean": 4.15,
            "v_t90": 3.4,
            "Re_imp": 0.05,
            "v_mean": 3.5,
            "dvdt_mean": -0.0002,
            "dvdt_std": 0.0025,
            "chg_v_min": 3.3,
            "chg_temp_max": 30.0,
            "chg_temp_std": 1.5,
            "chg_v_end": 4.2,
            "chg_i_cmd_mae": 0.005,
            "chg_v_cmd_mae": 0.6,
            "cap_int": 1.6,
            "v_max": 4.2,
            "chg_frac_active": 0.8,
            "chg_duration_s": 10000.0,
            "chg_i_end": 0.001,
            "chg_i_max": 1.52,
            "v_min": 2.65,
            "chg_v_max": 4.21,
            "i_dis_min": 0.0,
            "chg_energy_wh": 6.0,
            "chg_i_min": 0.0
        }
        result = predict_battery_health(test_features)
        print(json.dumps(result, indent=2))
    
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
