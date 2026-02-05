"""
Feature Engineering for Battery Health Prediction
Converts raw battery cycle data (CSV) into NASA-standard engineered features
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path


def engineer_features_from_cycle_data(cycle_data):
    """
    Engineer NASA battery features from raw cycle measurements
    
    Args:
        cycle_data: List of dictionaries, each containing cycle measurements
                   Expected columns: cycle, voltage, current, temperature, capacity (optional)
    
    Returns:
        Dictionary containing all engineered features (superset for both SOH and RUL models)
    """
    df = pd.DataFrame(cycle_data)
    
    # Ensure we have required columns
    required_cols = ['voltage', 'current', 'temperature']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Use last cycle for feature engineering (most recent state)
    if 'cycle' in df.columns:
        latest_cycle = df['cycle'].max()
        cycle_df = df[df['cycle'] == latest_cycle].copy()
    else:
        cycle_df = df.copy()
    
    # If only one row, use all data
    if len(cycle_df) < 10:
        cycle_df = df.copy()
    
    features = {}
    
    try:
        # ===== VOLTAGE FEATURES =====
        v = cycle_df['voltage'].values
        features['v_min'] = float(np.nanmin(v))
        features['v_max'] = float(np.nanmax(v))
        features['v_mean'] = float(np.nanmean(v))
        
        # Voltage at time percentiles (approximate)
        n = len(v)
        features['v_t50'] = float(v[int(n * 0.5)] if n > 2 else np.nanmean(v))
        features['v_t90'] = float(v[int(n * 0.9)] if n > 10 else v[-1])
        
        # Voltage derivative (dV/dt)
        dvdt = np.diff(v)
        features['dvdt_mean'] = float(np.nanmean(dvdt)) if len(dvdt) > 0 else 0.0
        features['dvdt_std'] = float(np.nanstd(dvdt)) if len(dvdt) > 0 else 0.0
        
        # Time to specific voltages (approximate)
        time_to_3v6_idx = np.where(v <= 3.6)[0]
        features['time_to_3v6'] = float(time_to_3v6_idx[0]) if len(time_to_3v6_idx) > 0 else n
        
        # ===== CURRENT FEATURES =====
        i = cycle_df['current'].values
        i_discharge = i[i < 0] if any(i < 0) else i  # Discharge current is negative
        
        features['i_dis_min'] = float(np.nanmin(i_discharge)) if len(i_discharge) > 0 else 0.0
        
        # === == CHARGE-SPECIFIC FEATURES (approximate from available data) =====
        # Assume later part of cycle is charging if current is positive
        i_charge = i[i >= 0] if any(i >= 0) else i
        v_charge = v[i >= 0] if any(i >= 0) else v
        
        features['chg_v_min'] = float(np.nanmin(v_charge)) if len(v_charge) > 0 else features['v_min']
        features['chg_v_max'] = float(np.nanmax(v_charge)) if len(v_charge) > 0 else features['v_max']
        features['chg_v_mean'] = float(np.nanmean(v_charge)) if len(v_charge) > 0 else features['v_mean']
        features['chg_v_end'] = float(v_charge[-1]) if len(v_charge) > 0 else features['v_max']
        
        features['chg_i_min'] = 0.0
        features['chg_i_max'] = float(np.nanmax(i_charge)) if len(i_charge) > 0 else np.nanmax(np.abs(i))
        features['chg_i_end'] = float(i_charge[-1]) if len(i_charge) > 0 else 0.0
        
        # Charge duration (approximate)
        features['chg_duration_s'] = float(len(i_charge)) if len(i_charge) > 0 else n
        features['chg_frac_active'] = len(i_charge) / n if n > 0 else 1.0
        
        # ===== TEMPERATURE FEATURES =====
        temp = cycle_df['temperature'].values
        temp_charge = temp[i >= 0] if any(i >= 0) else temp
        
        features['chg_temp_max'] = float(np.nanmax(temp_charge)) if len(temp_charge) > 0 else np.nanmax(temp)
        features['chg_temp_std'] = float(np.nanstd(temp_charge)) if len(temp_charge) > 0 else np.nanstd(temp)
        
        # ===== CAPACITY AND ENERGY FEATURES =====
        # Integrated capacity (Ah) - USE ACTUAL CAPACITY if available
        dt = 1.0  # Assume 1 second intervals
        if 'capacity' in cycle_df.columns:
            cap = cycle_df['capacity'].values
            # Use median capacity (more robust than mean)
            features['cap_int'] = float(np.nanmedian(cap))
            # Calculate degradation rate from capacity trend
            if len(cap) > 10:
                cap_start = np.nanmean(cap[:5])
                cap_end = np.nanmean(cap[-5:])
                degradation = (cap_start - cap_end) / cap_start if cap_start > 0 else 0
            else:
                degradation = 0
        else:
            # Integrate current to get capacity
            features['cap_int'] = float(np.abs(np.nansum(i)) * dt / 3600.0)  # Convert to Ah
            degradation = 0
        
        # Energy (Wh) = integrate V * I
        energy = np.abs(v * i) * dt / 3600.0
        features['energy_int_wh'] = float(np.nansum(energy))
        features['chg_energy_wh'] = float(np.nansum(energy[i >= 0])) if any(i >= 0) else features['energy_int_wh']
        
        # ===== IMPEDANCE FEATURES (improved estimates based on capacity degradation) =====
        # Electrolyte resistance correlates with battery degradation
        # Use capacity data to estimate impedance more realistically
        if 'capacity' in cycle_df.columns and len(cap) > 5:
            # Estimate based on capacity fade
            initial_cap_estimate = 2.0  # NASA batteries nominal capacity
            median_cap = np.nanmedian(cap)
            soh_estimate = median_cap / initial_cap_estimate
            
            # Impedance increases as SOH decreases (empirical relationship)
            # Healthy battery (SOH>0.9): Re ~ 0.04-0.06, Rct ~ 0.06-0.10  
            # Degraded battery (SOH<0.7): Re ~ 0.08-0.12, Rct ~ 0.15-0.30
            features['Re_imp'] = 0.04 + (1 - soh_estimate) * 0.15
            features['Rct_imp'] = 0.06 + (1 - soh_estimate) * 0.25
        else:
            # Fallback: estimate from voltage drop
            if len(v) > 10 and len(i) > 10:
                # Look for voltage drop during discharge
                discharge_mask = i < -0.1
                if discharge_mask.sum() > 5:
                    v_discharge = v[discharge_mask]
                    i_discharge = i[discharge_mask]
                    if len(v_discharge) > 2:
                        dv = v_discharge[5] - v_discharge[0]
                        di = i_discharge[5] - i_discharge[0]
                        features['Re_imp'] = float(abs(dv / di)) if abs(di) > 0.01 else 0.06
                        features['Rct_imp'] = features['Re_imp'] * 1.5
                    else:
                        features['Re_imp'] = 0.06
                        features['Rct_imp'] = 0.09
                else:
                    features['Re_imp'] = 0.06
                    features['Rct_imp'] = 0.09
            else:
                features['Re_imp'] = 0.06
                features['Rct_imp'] = 0.09
        
        # Limit impedance to NASA dataset ranges (0.02 - 0.35)
        features['Re_imp'] = float(min(max(features['Re_imp'], 0.02), 0.20))
        features['Rct_imp'] = float(min(max(features['Rct_imp'], 0.03), 0.35))
        
        # ===== COMMAND TRACKING ERRORS (estimate from data variability) =====
        # Command tracking errors correlate with control stability
        # Better batteries have more stable voltage/current profiles
        i_variability = np.nanstd(i)
        v_variability = features['dvdt_std']
        
        # Scale errors based on variability (higher variability = higher error)
        features['chg_i_cmd_mae'] = float(min(max(i_variability * 0.01, 0.001), 0.02))
        features['chg_v_cmd_mae'] = float(min(max(v_variability * 50, 0.1), 1.5))
        
        # Return all features (superset for both SOH and RUL)
        # No assertion on count - we return all engineered features
        return features
        
    except Exception as e:
        raise RuntimeError(f"Feature engineering failed: {e}")


def main():
    """Command-line interface"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python feature_engineering.py <csv_file_path>"
        }))
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        cycle_data = df.to_dict('records')
        
        # Engineer features
        features = engineer_features_from_cycle_data(cycle_data)
        
        print(json.dumps({
            "success": True,
            "features": features,
            "record_count": len(cycle_data)
        }, indent=2))
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e),
            "traceback": __import__('traceback').format_exc()
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
