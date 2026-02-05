"""
Battery Health Prediction Inference Toolbox

This module provides a simple, deterministic inference API for battery health prediction.
Models are lazily loaded from disk and cached in memory for efficient repeated inference.

Usage:
    import tools
    
    # SOH classification
    soh_class, soh_proba = tools.predict_soh_class(features_dict)
    
    # RUL classification
    rul_class, rul_proba = tools.predict_rul_class(features_dict)

All functions are stateless and thread-safe (read-only operations after initial load).
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional, List

# Global cache for lazy-loaded models
_MODELS_CACHE = {}
_MODELS_DIR = Path(__file__).parent / "models"

# ============================================================================
# CANONICAL FEATURE ORDERS (extracted from training notebooks)
# ============================================================================
# These lists define the EXACT feature order used during model training.
# DO NOT MODIFY unless you retrain all models from scratch.
# Source: processed_data/selected_features_soh.csv and selected_features_rul.csv

# SOH Classification Features (25 features)
# Used by: classification_modeling.ipynb for State of Health prediction
SOH_FEATURES = [
    "energy_int_wh",      # Integrated energy (Wh)
    "time_to_3v6",        # Time to reach 3.6V (s)
    "v_t50",              # Voltage at 50% discharge time
    "Rct_imp",            # Charge transfer resistance (Ohm)
    "chg_v_mean",         # Mean voltage during charge (V)
    "v_t90",              # Voltage at 90% discharge time
    "Re_imp",             # Electrolyte resistance (Ohm)
    "v_mean",             # Mean voltage (V)
    "dvdt_mean",          # Mean voltage derivative (V/s)
    "dvdt_std",           # Std dev of voltage derivative (V/s)
    "chg_v_min",          # Min voltage during charge (V)
    "chg_temp_max",       # Max temperature during charge (°C)
    "chg_temp_std",       # Std dev of temperature during charge (°C)
    "chg_v_end",          # End voltage during charge (V)
    "chg_i_cmd_mae",      # Mean absolute error of charge current command (A)
    "chg_v_cmd_mae",      # Mean absolute error of charge voltage command (V)
    "cap_int",            # Integrated capacity (Ah)
    "v_max",              # Max voltage (V)
    "chg_frac_active",    # Fraction of active charge time
    "chg_duration_s",     # Charge duration (s)
    "chg_i_end",          # End current during charge (A)
    "chg_i_max",          # Max current during charge (A)
    "v_min",              # Min voltage (V)
    "chg_v_max",          # Max voltage during charge (V)
    "i_dis_min",          # Min current during discharge (A)
]

# RUL Classification Features (25 features)
# Used by: classification_modeling.ipynb for Remaining Useful Life prediction
RUL_FEATURES = [
    "Rct_imp",            # Charge transfer resistance (Ohm)
    "Re_imp",             # Electrolyte resistance (Ohm)
    "chg_duration_s",     # Charge duration (s)
    "chg_energy_wh",      # Charge energy (Wh)
    "v_mean",             # Mean voltage (V)
    "v_t50",              # Voltage at 50% discharge time
    "time_to_3v6",        # Time to reach 3.6V (s)
    "chg_v_mean",         # Mean voltage during charge (V)
    "dvdt_mean",          # Mean voltage derivative (V/s)
    "v_t90",              # Voltage at 90% discharge time
    "dvdt_std",           # Std dev of voltage derivative (V/s)
    "chg_i_cmd_mae",      # Mean absolute error of charge current command (A)
    "chg_v_cmd_mae",      # Mean absolute error of charge voltage command (V)
    "chg_v_min",          # Min voltage during charge (V)
    "chg_temp_std",       # Std dev of temperature during charge (°C)
    "v_max",              # Max voltage (V)
    "chg_v_end",          # End voltage during charge (V)
    "chg_frac_active",    # Fraction of active charge time
    "chg_i_end",          # End current during charge (A)
    "chg_i_max",          # Max current during charge (A)
    "cap_int",            # Integrated capacity (Ah)
    "v_min",              # Min voltage (V)
    "chg_i_min",          # Min current during charge (A)
    "i_dis_min",          # Min current during discharge (A)
    "chg_v_max",          # Max voltage during charge (V)
]

# Feature dimension checks (fail-fast if wrong)
assert len(SOH_FEATURES) == 25, f"SOH feature list corrupted: expected 25, got {len(SOH_FEATURES)}"
assert len(RUL_FEATURES) == 25, f"RUL feature list corrupted: expected 25, got {len(RUL_FEATURES)}"
assert len(SOH_FEATURES) == len(set(SOH_FEATURES)), "SOH feature list contains duplicates"
assert len(RUL_FEATURES) == len(set(RUL_FEATURES)), "RUL feature list contains duplicates"


def _load_model(model_key: str, model_filename: str):
    """
    Lazy-load a model from disk and cache it in memory.
    
    Args:
        model_key: Cache key for this model
        model_filename: Filename in the models/ directory
        
    Returns:
        The loaded model object
    """
    if model_key not in _MODELS_CACHE:
        model_path = _MODELS_DIR / model_filename
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                f"Please ensure the training notebook has been run to generate model artifacts."
            )
        _MODELS_CACHE[model_key] = joblib.load(model_path)
    return _MODELS_CACHE[model_key]


def _prepare_features(features_dict: Dict[str, float], feature_names: List[str], task_name: str = "") -> np.ndarray:
    """
    Convert a feature dictionary to a properly ordered feature array.
    
    Args:
        features_dict: Dictionary mapping feature names to values
        feature_names: Ordered list of expected feature names
        task_name: Name of the task (for error messages)
        
    Returns:
        numpy array with features in the correct order
        
    Raises:
        ValueError: If required features are missing
        RuntimeError: If feature dimensions are inconsistent with training
    """
    missing_features = set(feature_names) - set(features_dict.keys())
    if missing_features:
        raise ValueError(
            f"[{task_name}] Missing required features: {sorted(missing_features)}\n"
            f"Expected {len(feature_names)} features: {feature_names}"
        )
    
    # Extract features in the correct order
    feature_values = [features_dict[fname] for fname in feature_names]
    
    # Dimension check (fail-fast)
    if len(feature_values) != len(feature_names):
        raise RuntimeError(
            f"[{task_name}] Feature dimension mismatch: "
            f"got {len(feature_values)}, expected {len(feature_names)}"
        )
    
    # Return as 2D array (single sample)
    X = np.array(feature_values, dtype=np.float64).reshape(1, -1)
    
    # Final shape assertion (catches numpy broadcasting bugs)
    assert X.shape == (1, len(feature_names)), \
        f"[{task_name}] Shape assertion failed: {X.shape} != (1, {len(feature_names)})"
    
    return X


def predict_soh_class(features: Dict[str, float], model_name: str = "LogisticRegression_tuned_group-CV") -> Tuple[int, np.ndarray]:
    """
    Predict State of Health (SOH) class from battery features.
    
    This function classifies battery health into binary categories:
    - Class 0: Not-Healthy (SOH < 0.80)
    - Class 1: Healthy (SOH >= 0.80)
    
    Args:
        features: Dictionary mapping feature names to their values.
                 All 25 required features must be present.
        model_name: Name of the model to use. Options:
                   - "LogisticRegression_tuned_group-CV" (default, recommended)
                   - "RandomForestClassifier_regularized"
    
    Returns:
        Tuple of (predicted_class, class_probabilities)
        - predicted_class: 0 or 1
        - class_probabilities: array of shape (2,) with [P(class=0), P(class=1)]
    
    Required features (EXACT ORDER - 25 features total):
        energy_int_wh, time_to_3v6, v_t50, Rct_imp, chg_v_mean, v_t90, Re_imp, 
        v_mean, dvdt_mean, dvdt_std, chg_v_min, chg_temp_max, chg_temp_std, 
        chg_v_end, chg_i_cmd_mae, chg_v_cmd_mae, cap_int, v_max, chg_frac_active, 
        chg_duration_s, chg_i_end, chg_i_max, v_min, chg_v_max, i_dis_min
    
    Example:
        >>> features = {
        ...     'energy_int_wh': 7.2, 'time_to_3v6': 1800, 'v_t50': 3.7,
        ...     'Rct_imp': 0.05, 'chg_v_mean': 3.75, 'v_t90': 3.9,
        ...     # ... (all 25 features)
        ... }
        >>> pred_class, probas = predict_soh_class(features)
        >>> print(f"Predicted class: {pred_class}, Healthy probability: {probas[1]:.3f}")
    
    Raises:
        ValueError: If required features are missing
        RuntimeError: If feature dimensions don't match training
        FileNotFoundError: If model files haven't been generated yet
    """
    # Load model (from disk or cache)
    model = _load_model(f"soh_model_{model_name}", f"soh_classifier_{model_name}.joblib")
    
    # Use canonical feature order (hardcoded from training)
    feature_names = SOH_FEATURES
    
    # Validate loaded features match canonical (defensive check)
    loaded_features = _load_model("soh_features", "soh_features.joblib")
    if loaded_features != feature_names:
        raise RuntimeError(
            f"CRITICAL: Trained model feature order doesn't match canonical order!\n"
            f"Expected: {feature_names}\n"
            f"Got from training: {loaded_features}\n"
            f"This indicates model/code version mismatch. Retrain models or fix tools.py."
        )
    
    # Prepare input (with dimension checks)
    X = _prepare_features(features, feature_names, task_name="SOH")
    
    # Predict
    pred_class = int(model.predict(X)[0])
    pred_proba = model.predict_proba(X)[0]
    
    # Output dimension check
    assert pred_proba.shape == (2,), f"SOH probability shape mismatch: {pred_proba.shape} != (2,)"
    assert pred_class in [0, 1], f"SOH class out of range: {pred_class}"
    
    return pred_class, pred_proba


def predict_rul_class(features: Dict[str, float], model_name: str = "LogisticRegression_tuned_group-CV") -> Tuple[int, np.ndarray]:
    """
    Predict Remaining Useful Life (RUL) class from battery features.
    
    This function classifies remaining battery life into binary categories:
    - Class 0: Not-Short RUL (remaining life > threshold)
    - Class 1: Short RUL (remaining life <= threshold, battery near end-of-life)
    
    The threshold is determined from training data (lowest 1/3 quantile).
    
    Args:
        features: Dictionary mapping feature names to their values.
                 All 25 required features must be present.
        model_name: Name of the model to use. Options:
                   - "LogisticRegression_tuned_group-CV" (default, recommended)
                   - "RandomForestClassifier_tuned_group-CV"
    
    Returns:
        Tuple of (predicted_class, class_probabilities)
        - predicted_class: 0 or 1
        - class_probabilities: array of shape (2,) with [P(class=0), P(class=1)]
    
    Required features (EXACT ORDER - 25 features total):
        Rct_imp, Re_imp, chg_duration_s, chg_energy_wh, v_mean, v_t50, 
        time_to_3v6, chg_v_mean, dvdt_mean, v_t90, dvdt_std, chg_i_cmd_mae, 
        chg_v_cmd_mae, chg_v_min, chg_temp_std, v_max, chg_v_end, 
        chg_frac_active, chg_i_end, chg_i_max, cap_int, v_min, chg_i_min, 
        i_dis_min, chg_v_max
    
    Example:
        >>> features = {
        ...     'Rct_imp': 0.05, 'Re_imp': 0.02, 'chg_duration_s': 3600,
        ...     'chg_energy_wh': 7.0, 'v_mean': 3.7, 'v_t50': 3.65,
        ...     # ... (all 25 features)
        ... }
        >>> pred_class, probas = predict_rul_class(features)
        >>> print(f"Predicted class: {pred_class}, Short RUL probability: {probas[1]:.3f}")
    
    Raises:
        ValueError: If required features are missing
        RuntimeError: If feature dimensions don't match training
        FileNotFoundError: If model files haven't been generated yet
    """
    # Load model (from disk or cache)
    model = _load_model(f"rul_model_{model_name}", f"rul_classifier_{model_name}.joblib")
    
    # Use canonical feature order (hardcoded from training)
    feature_names = RUL_FEATURES
    
    # Validate loaded features match canonical (defensive check)
    loaded_features = _load_model("rul_features", "rul_features.joblib")
    if loaded_features != feature_names:
        raise RuntimeError(
            f"CRITICAL: Trained model feature order doesn't match canonical order!\n"
            f"Expected: {feature_names}\n"
            f"Got from training: {loaded_features}\n"
            f"This indicates model/code version mismatch. Retrain models or fix tools.py."
        )
    
    # Prepare input (with dimension checks)
    X = _prepare_features(features, feature_names, task_name="RUL")
    
    # Predict
    pred_class = int(model.predict(X)[0])
    pred_proba = model.predict_proba(X)[0]
    
    # Output dimension check
    assert pred_proba.shape == (2,), f"RUL probability shape mismatch: {pred_proba.shape} != (2,)"
    assert pred_class in [0, 1], f"RUL class out of range: {pred_class}"
    
    return pred_class, pred_proba


def get_soh_feature_names() -> List[str]:
    """
    Get the list of required feature names for SOH prediction, in exact order.
    
    Returns:
        List of 25 feature names in the order expected by the model
    """
    return SOH_FEATURES.copy()


def get_rul_feature_names() -> List[str]:
    """
    Get the list of required feature names for RUL prediction, in exact order.
    
    Returns:
        List of 25 feature names in the order expected by the model
    """
    return RUL_FEATURES.copy()


def get_soh_metadata() -> Dict:
    """
    Get metadata about the SOH classification task.
    
    Returns:
        Dictionary with keys:
        - binary_scheme: Classification scheme used
        - class_names: Human-readable class labels
        - pos_label_meaning: Meaning of the positive class (label=1)
    """
    return _load_model("soh_metadata", "soh_metadata.joblib")


def get_rul_metadata() -> Dict:
    """
    Get metadata about the RUL classification task.
    
    Returns:
        Dictionary with keys:
        - class_scheme: Classification scheme used
        - class_names: Human-readable class labels
        - rul_source: Description of how RUL was computed
    """
    return _load_model("rul_metadata", "rul_metadata.joblib")


# Convenience function to clear the cache (useful for testing or memory management)
def clear_cache():
    """Clear all cached models from memory."""
    global _MODELS_CACHE
    _MODELS_CACHE.clear()
