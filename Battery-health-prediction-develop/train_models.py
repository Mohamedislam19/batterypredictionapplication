"""
Train ML models for battery health prediction

This script extracts and runs the final trained models from classification_modeling.ipynb
to generate the required model artifacts for the desktop application.

Run this ONCE to generate model files in Battery-health-prediction-develop/models/
"""

import sys
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold

# Setup paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "processed_data"
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("BATTERY HEALTH PREDICTION - MODEL TRAINING")
print("=" * 70)

# Load selected features
soh_features_df = pd.read_csv(DATA_DIR / "selected_features_soh.csv")
rul_features_df = pd.read_csv(DATA_DIR / "selected_features_rul.csv")

SOH_FEATURES = soh_features_df['feature'].tolist()
RUL_FEATURES = rul_features_df['feature'].tolist()

print(f"\n✓ SOH Features: {len(SOH_FEATURES)}")
print(f"✓ RUL Features: {len(RUL_FEATURES)}")

# Load aggregated feature data
print("\n" + "=" * 70)
print("LOADING PROCESSED DATA")
print("=" * 70)

data = pd.read_csv(DATA_DIR / "feature_aggregation.csv")
print(f"✓ Feature data shape: {data.shape}")

# SOH is already in the data (capitalized) - it's in decimal form (0-1)
if 'SOH' not in data.columns:
    raise ValueError("SOH column not found in feature_aggregation.csv")

# Create binary SOH labels (Healthy >= 0.80, Not-Healthy < 0.80)
# SOH is in decimal form (0-1) not percentage
data['soh_binary'] = (data['SOH'] >= 0.80).astype(int)

# Create RUL binary labels (using quantile-based threshold)
# RUL is already in the data
if 'RUL' not in data.columns:
    raise ValueError("RUL column not found in feature_aggregation.csv")

# Use lowest 1/3 as "short RUL"
rul_threshold = data['RUL'].quantile(0.33)
data['rul_binary'] = (data['RUL'] <= rul_threshold).astype(int)

print(f"\n✓ SOH class distribution: {data['soh_binary'].value_counts().to_dict()}")
print(f"✓ RUL class distribution: {data['rul_binary'].value_counts().to_dict()}")
print(f"✓ RUL threshold: {rul_threshold:.0f} cycles")

# Drop rows with NaN in required features
print("\nHandling missing values...")
initial_rows = len(data)
data_soh = data[SOH_FEATURES + ['soh_binary', 'battery_id']].dropna()
data_rul = data[RUL_FEATURES + ['rul_binary', 'battery_id']].dropna()
print(f"✓ SOH data: {initial_rows} → {len(data_soh)} rows (dropped {initial_rows - len(data_soh)} with NaN)")
print(f"✓ RUL data: {initial_rows} → {len(data_rul)} rows (dropped {initial_rows - len(data_rul)} with NaN)")

# Prepare training data
X_soh = data_soh[SOH_FEATURES].values
y_soh = data_soh['soh_binary'].values
groups_soh = data_soh['battery_id'].values

X_rul = data_rul[RUL_FEATURES].values
y_rul = data_rul['rul_binary'].values
groups_rul = data_rul['battery_id'].values

print("\n" + "=" * 70)
print("TRAINING SOH CLASSIFICATION MODELS")
print("=" * 70)

# Train SOH LogisticRegression (tuned with GroupKFold CV)
print("\n[1/2] Training LogisticRegression (tuned, group-CV)...")
soh_logreg = LogisticRegression(
    C=0.1,  # Regularization strength (from tuning)
    max_iter=1000,
    random_state=42,
    class_weight='balanced'
)
soh_logreg.fit(X_soh, y_soh)
print(f"✓ Trained on {X_soh.shape[0]} samples")

# Train SOH RandomForest (regularized)
print("\n[2/2] Training RandomForestClassifier (regularized)...")
soh_rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,  # Regularization
    min_samples_split=20,
    min_samples_leaf=10,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)
soh_rf.fit(X_soh, y_soh)
print(f"✓ Trained on {X_soh.shape[0]} samples")

print("\n" + "=" * 70)
print("TRAINING RUL CLASSIFICATION MODELS")
print("=" * 70)

# Train RUL LogisticRegression (tuned with GroupKFold CV)
print("\n[1/2] Training LogisticRegression (tuned, group-CV)...")
rul_logreg = LogisticRegression(
    C=0.01,  # Regularization strength (from tuning)
    max_iter=1000,
    random_state=42,
    class_weight='balanced'
)
rul_logreg.fit(X_rul, y_rul)
print(f"✓ Trained on {X_rul.shape[0]} samples")

# Train RUL RandomForest (tuned with GroupKFold CV)
print("\n[2/2] Training RandomForestClassifier (tuned, group-CV)...")
rul_rf = RandomForestClassifier(
    n_estimators=150,
    max_depth=12,  # From tuning
    min_samples_split=15,
    min_samples_leaf=8,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)
rul_rf.fit(X_rul, y_rul)
print(f"✓ Trained on {X_rul.shape[0]} samples")

print("\n" + "=" * 70)
print("SAVING MODEL ARTIFACTS")
print("=" * 70)

# Save SOH models
joblib.dump(soh_logreg, MODELS_DIR / "soh_classifier_LogisticRegression_tuned_group-CV.joblib")
joblib.dump(soh_rf, MODELS_DIR / "soh_classifier_RandomForestClassifier_regularized.joblib")
joblib.dump(SOH_FEATURES, MODELS_DIR / "soh_features.joblib")

# Save RUL models
joblib.dump(rul_logreg, MODELS_DIR / "rul_classifier_LogisticRegression_tuned_group-CV.joblib")
joblib.dump(rul_rf, MODELS_DIR / "rul_classifier_RandomForestClassifier_tuned_group-CV.joblib")
joblib.dump(RUL_FEATURES, MODELS_DIR / "rul_features.joblib")

# Save metadata
soh_metadata = {
    'binary_scheme': 'Healthy (SOH >= 80%) vs Not-Healthy (SOH < 80%)',
    'class_names': ['Not-Healthy', 'Healthy'],
    'pos_label_meaning': 'SOH >= 80%'
}
joblib.dump(soh_metadata, MODELS_DIR / "soh_metadata.joblib")

rul_metadata = {
    'class_scheme': f'Short RUL (<= {rul_threshold:.0f} cycles) vs Not-Short RUL',
    'class_names': ['Not-Short RUL', 'Short RUL'],
    'rul_source': 'Calculated as max(cycle) - current_cycle per battery'
}
joblib.dump(rul_metadata, MODELS_DIR / "rul_metadata.joblib")

print("\n✓ Saved SOH models:")
print(f"  - soh_classifier_LogisticRegression_tuned_group-CV.joblib")
print(f"  - soh_classifier_RandomForestClassifier_regularized.joblib")
print(f"  - soh_features.joblib")
print(f"  - soh_metadata.joblib")

print("\n✓ Saved RUL models:")
print(f"  - rul_classifier_LogisticRegression_tuned_group-CV.joblib")
print(f"  - rul_classifier_RandomForestClassifier_tuned_group-CV.joblib")
print(f"  - rul_features.joblib")
print(f"  - rul_metadata.joblib")

print("\n" + "=" * 70)
print("MODEL TRAINING COMPLETE")
print("=" * 70)
print("\nModels are ready for inference via tools.py")
print(f"Location: {MODELS_DIR.absolute()}")
