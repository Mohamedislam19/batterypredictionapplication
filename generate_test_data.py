"""
Generate comprehensive test data for battery health prediction system
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Create test data directory
test_dir = Path('test_data')
test_dir.mkdir(exist_ok=True)

print("=== GENERATING TEST CASES ===\n")

def generate_cycle_data(n_cycles, voltage_range, current_range, temp_range, capacity_trend, anomaly=None):
    """Generate synthetic battery cycle data with optional anomalies"""
    np.random.seed(42)
    
    data = {
        'cycle': list(range(1, n_cycles + 1)),
        'voltage': [],
        'current': [],
        'temperature': [],
        'capacity': []
    }
    
    for i in range(n_cycles):
        # Voltage with degradation
        progress = i / n_cycles
        base_voltage = voltage_range[0] + (voltage_range[1] - voltage_range[0]) * (1 - progress * 0.5)
        voltage = base_voltage + np.random.normal(0, 0.05)
        
        # Apply anomalies if specified
        if anomaly == 'voltage_spike' and i == n_cycles // 2:
            voltage += 0.5
        elif anomaly == 'voltage_drop' and i == n_cycles // 2:
            voltage -= 0.5
            
        data['voltage'].append(voltage)
        
        # Current with variation
        base_current = current_range[0] + (current_range[1] - current_range[0]) * np.random.random()
        current = base_current + np.random.normal(0, 0.1)
        
        if anomaly == 'rapid_discharge' and i > n_cycles // 2:
            current *= 1.5
            
        data['current'].append(current)
        
        # Temperature
        base_temp = temp_range[0] + (temp_range[1] - temp_range[0]) * np.random.random()
        temp = base_temp + np.random.normal(0, 2)
        data['temperature'].append(temp)
        
        # Capacity with degradation trend
        initial_capacity = capacity_trend[0]
        final_capacity = capacity_trend[1]
        degradation_rate = (initial_capacity - final_capacity) / n_cycles
        
        if anomaly == 'sudden_drop' and i == n_cycles // 2:
            current_capacity = initial_capacity - (i * degradation_rate) - 0.3
        else:
            current_capacity = initial_capacity - (i * degradation_rate)
            
        data['capacity'].append(current_capacity + np.random.normal(0, 0.01))
    
    return pd.DataFrame(data)

# ===========================
# NORMAL SCENARIOS
# ===========================

print("NORMAL SCENARIOS")
print("-" * 50)

# TEST 1: Healthy Battery (SOH > 90%)
print("\nTEST 1: Healthy Battery (Expected SOH > 90%)")
healthy_battery = generate_cycle_data(
    n_cycles=50,
    voltage_range=(3.6, 4.2),
    current_range=(1.5, 2.0),
    temp_range=(20, 30),
    capacity_trend=(2.0, 1.95)
)
healthy_battery.to_csv(test_dir / 'test_1_healthy.csv', index=False)
print(f"  Generated {len(healthy_battery)} cycles")
print(f"  Capacity: {healthy_battery['capacity'].iloc[0]:.3f} -> {healthy_battery['capacity'].iloc[-1]:.3f} Ah")

# TEST 2: Moderate Degradation (SOH 80-90%)
print("\nTEST 2: Moderate Degradation (Expected SOH 80-90%)")
moderate_battery = generate_cycle_data(
    n_cycles=80,
    voltage_range=(3.5, 4.15),
    current_range=(1.4, 1.9),
    temp_range=(22, 35),
    capacity_trend=(2.0, 1.7)
)
moderate_battery.to_csv(test_dir / 'test_2_moderate.csv', index=False)
print(f"  Generated {len(moderate_battery)} cycles")
print(f"  Capacity: {moderate_battery['capacity'].iloc[0]:.3f} -> {moderate_battery['capacity'].iloc[-1]:.3f} Ah")

# TEST 3: Aged Battery (SOH < 80%)
print("\nTEST 3: Aged Battery (Expected SOH < 80%)")
aged_battery = generate_cycle_data(
    n_cycles=120,
    voltage_range=(3.4, 4.0),
    current_range=(1.2, 1.7),
    temp_range=(25, 40),
    capacity_trend=(2.0, 1.5)
)
aged_battery.to_csv(test_dir / 'test_3_aged.csv', index=False)
print(f"  Generated {len(aged_battery)} cycles")
print(f"  Capacity: {aged_battery['capacity'].iloc[0]:.3f} -> {aged_battery['capacity'].iloc[-1]:.3f} Ah")

# ===========================
# EDGE CASES
# ===========================

print("\n\nEDGE CASES")
print("-" * 50)

# TEST 4: Extreme Cold Temperature
print("\nTEST 4: Extreme Cold (-20C)")
cold_battery = generate_cycle_data(
    n_cycles=60,
    voltage_range=(3.3, 3.9),
    current_range=(1.0, 1.5),
    temp_range=(-20, -10),
    capacity_trend=(2.0, 1.8)
)
cold_battery.to_csv(test_dir / 'test_4_extreme_cold.csv', index=False)
print(f"  Generated {len(cold_battery)} cycles at avg temp {cold_battery['temperature'].mean():.1f}C")

# TEST 5: Extreme Heat Temperature
print("\nTEST 5: Extreme Heat (60C)")
hot_battery = generate_cycle_data(
    n_cycles=60,
    voltage_range=(3.5, 4.1),
    current_range=(1.3, 1.8),
    temp_range=(55, 65),
    capacity_trend=(2.0, 1.6)
)
hot_battery.to_csv(test_dir / 'test_5_extreme_heat.csv', index=False)
print(f"  Generated {len(hot_battery)} cycles at avg temp {hot_battery['temperature'].mean():.1f}C")

# TEST 6: Rapid Discharge
print("\nTEST 6: Rapid Discharge Pattern")
rapid_discharge = generate_cycle_data(
    n_cycles=70,
    voltage_range=(3.4, 4.0),
    current_range=(1.8, 2.5),
    temp_range=(25, 35),
    capacity_trend=(2.0, 1.7),
    anomaly='rapid_discharge'
)
rapid_discharge.to_csv(test_dir / 'test_6_rapid_discharge.csv', index=False)
print(f"  Generated {len(rapid_discharge)} cycles with rapid discharge after cycle 35")

# TEST 7: Voltage Anomalies
print("\nTEST 7: Voltage Spike Anomaly")
voltage_spike = generate_cycle_data(
    n_cycles=65,
    voltage_range=(3.5, 4.1),
    current_range=(1.4, 1.9),
    temp_range=(20, 30),
    capacity_trend=(2.0, 1.75),
    anomaly='voltage_spike'
)
voltage_spike.to_csv(test_dir / 'test_7_voltage_spike.csv', index=False)
print(f"  Generated {len(voltage_spike)} cycles with voltage spike")

# TEST 8: Sudden Capacity Drop
print("\nTEST 8: Sudden Capacity Drop")
sudden_drop = generate_cycle_data(
    n_cycles=75,
    voltage_range=(3.5, 4.1),
    current_range=(1.4, 1.9),
    temp_range=(22, 32),
    capacity_trend=(2.0, 1.7),
    anomaly='sudden_drop'
)
sudden_drop.to_csv(test_dir / 'test_8_sudden_drop.csv', index=False)
print(f"  Generated {len(sudden_drop)} cycles with sudden capacity drop")

# ===========================
# STRESS TESTS
# ===========================

print("\n\nSTRESS TESTS")
print("-" * 50)

# TEST 9: Missing Values
print("\nTEST 9: Missing Values")
missing_data = generate_cycle_data(
    n_cycles=60,
    voltage_range=(3.5, 4.1),
    current_range=(1.4, 1.9),
    temp_range=(20, 30),
    capacity_trend=(2.0, 1.8)
)
# Introduce missing values
missing_indices = np.random.choice(len(missing_data), size=10, replace=False)
missing_data.loc[missing_indices, 'voltage'] = np.nan
missing_data.to_csv(test_dir / 'test_9_missing_values.csv', index=False)
print(f"  Generated {len(missing_data)} cycles with 10 missing voltage values")

# TEST 10: Minimal Data
print("\nTEST 10: Minimal Data (5 cycles)")
minimal_data = generate_cycle_data(
    n_cycles=5,
    voltage_range=(3.6, 4.2),
    current_range=(1.5, 2.0),
    temp_range=(20, 30),
    capacity_trend=(2.0, 1.98)
)
minimal_data.to_csv(test_dir / 'test_10_minimal.csv', index=False)
print(f"  Generated {len(minimal_data)} cycles (stress test for minimal data)")

# TEST 11: Out of Range Values
print("\nTEST 11: Out of Range Values")
out_of_range = generate_cycle_data(
    n_cycles=50,
    voltage_range=(2.0, 5.0),  # Unrealistic voltage range
    current_range=(0.5, 3.0),
    temp_range=(-50, 100),
    capacity_trend=(2.0, 1.8)
)
out_of_range.to_csv(test_dir / 'test_11_out_of_range.csv', index=False)
print(f"  Generated {len(out_of_range)} cycles with extreme out-of-range values")

# TEST 12: Corrupted Data Pattern
print("\nTEST 12: Corrupted Data (irregular patterns)")
corrupted = generate_cycle_data(
    n_cycles=55,
    voltage_range=(3.5, 4.1),
    current_range=(1.4, 1.9),
    temp_range=(20, 30),
    capacity_trend=(2.0, 1.75)
)
# Add random spikes
spike_indices = [10, 25, 40]
for idx in spike_indices:
    corrupted.loc[idx, 'voltage'] *= 1.5
    corrupted.loc[idx, 'current'] *= 2.0
corrupted.to_csv(test_dir / 'test_12_corrupted.csv', index=False)
print(f"  Generated {len(corrupted)} cycles with 3 data corruption spikes")

print("\n\n" + "=" * 50)
print(f"SUCCESS: 12 test files generated in {test_dir.absolute()}/")
print("=" * 50)
