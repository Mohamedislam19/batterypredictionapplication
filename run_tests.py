"""
Autonomous Test Runner for Battery Health Prediction System
Runs all test cases and collects results
"""
import json
import subprocess
from pathlib import Path
import pandas as pd

test_dir = Path('test_data')
results_file = Path('test_results.json')

# Python executable path
python_exe = Path('.venv/Scripts/python.exe')
pipeline_script = Path('pipeline.py')

# Expected results for validation
EXPECTED_RESULTS = {
    'test_1_healthy.csv': {'soh_range': (90, 100), 'state': 'EXCELLENT'},
    'test_2_moderate.csv': {'soh_range': (80, 90), 'state': 'GOOD'},
    'test_3_aged.csv': {'soh_range': (70, 85), 'state': 'FAIR'},
}

print("=" * 70)
print("BATTERY HEALTH PREDICTION SYSTEM - AUTOMATED TESTING")
print("=" * 70)

# Collect all test files
test_files = sorted(test_dir.glob('test_*.csv'))
print(f"\nFound {len(test_files)} test files\n")

results = []

for i, test_file in enumerate(test_files, 1):
    print(f"[{i}/{len(test_files)}] Testing: {test_file.name}")
    print("-" * 70)
    
    try:
        # Run pipeline.py on test file
        result = subprocess.run(
            [str(python_exe), str(pipeline_script), str(test_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"  ERROR: Pipeline failed")
            print(f"  STDERR: {result.stderr[:200]}")
            results.append({
                'test_file': test_file.name,
                'success': False,
                'error': result.stderr,
                'stdout': result.stdout
            })
            continue
        
        # Parse JSON output
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"  ERROR: Invalid JSON output")
            print(f"  STDOUT: {result.stdout[:200]}")
            results.append({
                'test_file': test_file.name,
                'success': False,
                'error': 'Invalid JSON',
                'raw_output': result.stdout
            })
            continue
        
        # Extract predictions
        if not output.get('success'):
            print(f"  PREDICTION FAILED: {output.get('error', 'Unknown error')}")
            results.append({
                'test_file': test_file.name,
                'success': False,
                'error': output.get('error'),
                'full_output': output
            })
            continue
        
        predictions = output['predictions']
        soh_value = predictions['soh']['estimated_value']
        rul_value = predictions['rul']['estimated_cycles']
        soh_class = predictions['soh']['class_name']
        rul_class = predictions['rul']['class_name']
        confidence = predictions['confidence']
        
        print(f"  SOH: {soh_value:.1f}% ({soh_class})")
        print(f"  RUL: {rul_value:.0f} cycles ({rul_class})")
        print(f"  Confidence: {confidence:.3f}")
        print(f"  Records: {output['records']}")
        
        # Load test data to compute ground truth
        test_data = pd.read_csv(test_file)
        first_capacity = test_data['capacity'].iloc[0]
        last_capacity = test_data['capacity'].iloc[-1]
        true_soh = (last_capacity / first_capacity) * 100
        
        print(f"  True SOH (from capacity): {true_soh:.1f}%")
        print(f"  Prediction Error: {abs(soh_value - true_soh):.1f}%")
        
        results.append({
            'test_file': test_file.name,
            'success': True,
            'predictions': {
                'soh': soh_value,
                'rul': rul_value,
                'soh_class': soh_class,
                'rul_class': rul_class,
                'confidence': confidence
            },
            'ground_truth': {
                'soh': true_soh,
                'first_capacity': first_capacity,
                'last_capacity': last_capacity,
                'cycles': len(test_data)
            },
            'error': abs(soh_value - true_soh),
            'records': output['records']
        })
        
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: Test exceeded 30 seconds")
        results.append({
            'test_file': test_file.name,
            'success': False,
            'error': 'Timeout (>30s)'
        })
    except Exception as e:
        print(f"  EXCEPTION: {str(e)}")
        results.append({
            'test_file': test_file.name,
            'success': False,
            'error': str(e)
        })
    
    print()

# Save results
with open(results_file, 'w') as f:
    json.dump(results, f, indent=2)

print("=" * 70)
print("TEST EXECUTION COMPLETE")
print("=" * 70)
print(f"\nResults saved to: {results_file.absolute()}")

# Calculate statistics
successful_tests = [r for r in results if r['success']]
failed_tests = [r for r in results if not r['success']]

print(f"\nSuccessful: {len(successful_tests)}/{len(results)}")
print(f"Failed: {len(failed_tests)}/{len(results)}")

if successful_tests:
    errors = [r['error'] for r in successful_tests]
    avg_error = sum(errors) / len(errors)
    max_error = max(errors)
    min_error = min(errors)
    
    print(f"\nSOH Prediction Error Statistics:")
    print(f"  Average: {avg_error:.2f}%")
    print(f"  Min: {min_error:.2f}%")
    print(f"  Max: {max_error:.2f}%")

if failed_tests:
    print(f"\nFailed Tests:")
    for test in failed_tests:
        print(f"  - {test['test_file']}: {test.get('error', 'Unknown error')}")
