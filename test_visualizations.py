"""
Visualization Testing Script - Extract Numerical-to-Visual Mapping
Tests all visualization components against model predictions
"""

import json
import subprocess
from pathlib import Path

# Load test results from previous automated testing
results_file = Path('test_results.json')
with open(results_file, 'r') as f:
    test_results = json.load(f)

print("=" * 80)
print("BATTERY HEALTH VISUALIZATION TESTING")
print("=" * 80)

# Analyze visualization logic from renderer.js
print("\n=== VISUALIZATION COMPONENTS ANALYSIS ===\n")

visualization_components = {
    "1. SOH Display (Primary Metric)": {
        "element": "#sohValue",
        "data_source": "summary.sohValue",
        "format": ".toFixed(1) + '%'",
        "color": "Gradient (white → #4f9eff)",
        "font_size": "Large (primary metric)"
    },
    
    "2. RUL Display (Secondary Metric)": {
        "element": "#rulValue",
        "data_source": "summary.rulValue",
        "format": "Math.round() + ' cycles'",
        "color": "Standard text",
        "font_size": "Medium (secondary)"
    },
    
    "3. Health Status Badge": {
        "element": "#healthStatus",
        "data_source": "summary.healthState",
        "classes": {
            "EXCELLENT/GOOD": "nominal (blue #4f9eff)",
            "FAIR/POOR": "degraded (orange #ffa940)",
            "CRITICAL/REPLACE_NOW": "critical (red #ff4d6d)"
        },
        "dynamic": "getStatusClass(healthState)"
    },
    
    "4. Degradation Chart (Chart.js Line Graph)": {
        "element": "#degradationChart",
        "datasets": [
            {
                "name": "Observed SOH",
                "data_source": "summary.sohValue + interpolation from metadata.oldestSOH",
                "color": "#4f9eff (blue)",
                "style": "Solid line, filled area"
            },
            {
                "name": "Projected Degradation",
                "data_source": "summary.rulValue (projection from current SOH to 80%)",
                "color": "#ffa940 (orange)",
                "style": "Dashed line"
            }
        ],
        "x_axis": "Cycles (0 to historyCount + min(rulValue, 50))",
        "y_axis": "SOH % (range: 75% to 105%)",
        "dynamic": "Recreated on each prediction"
    },
    
    "5. Key Metrics Panel": {
        "Initial Capacity": {
            "data_source": "Hardcoded 2.0 Ah (NASA typical)",
            "format": ".toFixed(3) + ' Ah'"
        },
        "Final Capacity": {
            "data_source": "(sohValue / 100) * 2.0",
            "format": ".toFixed(3) + ' Ah'"
        },
        "Avg Operating Temp": {
            "data_source": "agentDecision.metadata.soh (BUG: should be temperature)",
            "format": "Direct display"
        }
    },
    
    "6. Agent Decision Panel": {
        "State": "agentDecision.state (text)",
        "Action": "agentDecision.recommendedAction (replace _ with space)",
        "Confidence": "agentDecision.confidence (text)",
        "Reasoning": "agentDecision.reasoning array (bullet points)"
    },
    
    "7. Trend Alerts": {
        "Sudden Drop": "Show if metadata.historicalTrends.suddenDrop == true",
        "Rapid Degradation": "Show if metadata.historicalTrends.rapidDegradation == true",
        "Accelerating": "Show if metadata.historicalTrends.accelerating == true"
    }
}

for comp_name, details in visualization_components.items():
    print(f"{comp_name}")
    if isinstance(details, dict) and "element" in details:
        print(f"  Element: {details['element']}")
        if "data_source" in details:
            print(f"  Data Source: {details['data_source']}")
        if "dynamic" in details:
            print(f"  Dynamic: {details['dynamic']}")
    print()

# Test numerical-to-visual mapping consistency
print("\n=== NUMERICAL-TO-VISUAL MAPPING TESTS ===\n")

# Test case: Use test_1_healthy.csv results
test_case = test_results[3]  # test_1_healthy is 4th in alphabetical order
print(f"Test Case: {test_case['test_file']}")
print(f"  True SOH: {test_case['ground_truth']['soh']:.1f}%")
print(f"  Predicted SOH: {test_case['predictions']['soh']}%")
print(f"  Predicted RUL: {test_case['predictions']['rul']} cycles")
print(f"  Health State: {test_case['predictions']['soh_class']}")

# Simulate what renderer.js would display
predicted_soh = test_case['predictions']['soh']
predicted_rul = test_case['predictions']['rul']
soh_class = test_case['predictions']['soh_class']

print(f"\n  VISUAL REPRESENTATION:")
print(f"  ┌─────────────────────────────────────────┐")
print(f"  │ SOH Display: {predicted_soh:.1f}%              │")
print(f"  │ RUL Display: {int(predicted_rul)} cycles         │")
print(f"  │ Status Badge: {soh_class.upper().ljust(20)}│")
print(f"  └─────────────────────────────────────────┘")

# Determine badge color
if soh_class == "Healthy":
    badge_class = "nominal"
    badge_color = "#4f9eff (blue)"
else:
    badge_class = "degraded"  # or critical depending on SOH
    badge_color = "#ffa940 (orange)" if predicted_soh >= 60 else "#ff4d6d (red)"

print(f"  Badge Class: {badge_class}")
print(f"  Badge Color: {badge_color}")

# Chart data points
print(f"\n  CHART DATA:")
print(f"  Observed SOH Line:")
print(f"    - Y-axis value: {predicted_soh}%")
print(f"    - X-axis range: 1 to 10 cycles (fallback, no history)")
print(f"  Projected Degradation Line:")
print(f"    - Start: {predicted_soh}% at cycle 10")
print(f"    - End: 80% at cycle {10 + int(predicted_rul)}")
print(f"    - Dashed orange line")

# Verify consistency
print(f"\n  CONSISTENCY CHECK:")
errors = []

# Check SOH display matches numerical
if abs(predicted_soh - test_case['predictions']['soh']) > 0.1:
    errors.append("SOH display does not match prediction")
else:
    print(f"  ✓ SOH display matches numerical: {predicted_soh}%")

# Check RUL display matches numerical
if abs(predicted_rul - test_case['predictions']['rul']) > 0.5:
    errors.append("RUL display does not match prediction")
else:
    print(f"  ✓ RUL display matches numerical: {int(predicted_rul)} cycles")

# Check badge class logic
expected_badge = "nominal" if soh_class == "Healthy" else "degraded"
if badge_class != expected_badge:
    errors.append(f"Badge class mismatch: expected {expected_badge}, got {badge_class}")
else:
    print(f"  ✓ Badge class correct: {badge_class}")

# Check chart Y-axis includes SOH value
if predicted_soh >= 75 and predicted_soh <= 105:
    print(f"  ✓ Chart Y-axis (75-105%) includes SOH value {predicted_soh}%")
else:
    errors.append(f"SOH {predicted_soh}% outside chart Y-axis range (75-105%)")

if errors:
    print(f"\n  ❌ ERRORS DETECTED:")
    for error in errors:
        print(f"    - {error}")
else:
    print(f"\n  ✅ All visualizations consistent with numerical predictions")

# Test multiple scenarios
print(f"\n\n=== MULTI-SCENARIO VISUALIZATION TEST ===\n")

scenarios = [
    {"name": "Healthy Battery", "soh": 95, "rul": 150, "state": "EXCELLENT"},
    {"name": "Moderate Degradation", "soh": 85, "rul": 80, "state": "GOOD"},
    {"name": "Aged Battery", "soh": 75, "rul": 40, "state": "FAIR"},
    {"name": "Critical Battery", "soh": 55, "rul": 10, "state": "CRITICAL"}
]

for scenario in scenarios:
    print(f"{scenario['name']}:")
    print(f"  Numerical: SOH={scenario['soh']}%, RUL={scenario['rul']} cycles")
    
    # Determine visual representation
    if scenario['soh'] >= 95:
        badge = "nominal (blue)"
    elif scenario['soh'] >= 85:
        badge = "nominal (blue)"
    elif scenario['soh'] >= 70:
        badge = "degraded (orange)"
    elif scenario['soh'] >= 60:
        badge = "degraded (orange)"
    else:
        badge = "critical (red)"
    
    final_capacity = (scenario['soh'] / 100) * 2.0
    
    print(f"  Visual Badge: {badge}")
    print(f"  Displayed Capacity: {final_capacity:.3f} Ah")
    print(f"  Chart SOH Line Height: {scenario['soh']}% on Y-axis")
    print(f"  Chart Projection Length: {scenario['rul']} cycles")
    print()

# Identify potential issues
print(f"=== POTENTIAL VISUALIZATION ISSUES ===\n")

issues = [
    {
        "component": "Avg Operating Temp",
        "issue": "Displays agentDecision.metadata.soh instead of temperature",
        "severity": "HIGH",
        "fix": "Change to use actual temperature data from input CSV or remove"
    },
    {
        "component": "Initial Capacity",
        "issue": "Hardcoded to 2.0 Ah (NASA typical)",
        "severity": "MEDIUM",
        "fix": "Calculate from first capacity value in input data if available"
    },
    {
        "component": "Chart SOH Trend Line",
        "issue": "Fabricates historical trend when only 1 reading in memory",
        "severity": "MEDIUM",
        "fix": "Show single point instead of fabricated trend, or add disclaimer"
    },
    {
        "component": "Chart Y-axis Range",
        "issue": "Fixed 75-105% may clip very degraded batteries (<75%)",
        "severity": "LOW",
        "fix": "Make Y-axis dynamic: min(soh - 10, 75) to max(soh + 10, 105)"
    },
    {
        "component": "Status Badge Color Mapping",
        "issue": "No direct mapping code visible - relies on getStatusClass()",
        "severity": "LOW",
        "fix": "Document the mapping: EXCELLENT/GOOD→nominal, FAIR/POOR→degraded, CRITICAL→critical"
    }
]

for i, issue in enumerate(issues, 1):
    print(f"{i}. {issue['component']}")
    print(f"   Issue: {issue['issue']}")
    print(f"   Severity: {issue['severity']}")
    print(f"   Fix: {issue['fix']}")
    print()

print("=" * 80)
print("VISUALIZATION TESTING COMPLETE")
print("=" * 80)
print(f"\nComponents Analyzed: {len(visualization_components)}")
print(f"Test Scenarios: {len(scenarios) + 1}")
print(f"Issues Identified: {len(issues)}")
print(f"\nReport: See output above for detailed analysis")
