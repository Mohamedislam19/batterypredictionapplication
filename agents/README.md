# Battery Health Agent

An intelligent, deterministic decision-making agent for battery health analysis.

## Overview

The BatteryAgent consumes ML model predictions and applies rule-based reasoning to make actionable recommendations. It transforms raw model outputs (SOH, classification, RUL) into structured decisions with confidence levels and human-readable explanations.

## Design Principles

- **Deterministic**: Same inputs always produce same outputs
- **Explainable**: Every decision includes reasoning steps
- **Rule-based**: No ML training, pure logic on top of predictions
- **Structured**: Consistent output format for UI integration

## Folder Structure

```
agents/
├── BatteryAgent.js      # Main agent implementation
├── DecisionTypes.js     # Type definitions and enums
├── example.js           # Usage examples and contract
└── README.md           # This file
```

## Usage

```javascript
const BatteryAgent = require('./agents/BatteryAgent');

const agent = new BatteryAgent();

// Analyze battery with model predictions
const decision = agent.analyze({
  soh: 82.5,              // State of Health (required)
  classification: 'GOOD',  // Model classification (optional)
  rul: 250,               // Remaining Useful Life (optional)
  confidence: 0.85        // Model confidence (optional)
});

console.log(decision);
```

## Input Contract

```typescript
{
  soh: number,           // Required. State of Health (0-100)
  classification: string, // Optional. Model classification result
  rul: number,           // Optional. Remaining Useful Life in cycles
  confidence: number     // Optional. Model confidence (0-1)
}
```

## Output Contract

```typescript
{
  state: BatteryState,              // Health state enum
  confidence: ConfidenceLevel,      // Decision confidence enum
  recommendedAction: RecommendedAction, // Suggested action enum
  reasoning: string[],              // Explanation steps
  metadata: {
    soh: number,
    classification: string | null,
    rul: number | null,
    modelConfidence: number | null,
    thresholdsUsed: object
  },
  timestamp: string                 // ISO timestamp
}
```

## Decision States

- **EXCELLENT**: Battery in peak condition (SOH ≥ 90%)
- **GOOD**: Healthy battery (SOH 75-90%)
- **FAIR**: Moderate degradation (SOH 60-75%)
- **POOR**: Significant degradation (SOH 45-60%)
- **CRITICAL**: Severe degradation (SOH 30-45%)
- **REPLACE_NOW**: End of life (SOH < 30%)

## Recommended Actions

- **CONTINUE_NORMAL_USE**: No action needed
- **MONITOR_CLOSELY**: Track battery performance
- **REDUCE_INTENSIVE_TASKS**: Limit heavy usage
- **BACKUP_DATA**: Prepare for potential failure
- **SCHEDULE_REPLACEMENT**: Plan battery replacement
- **IMMEDIATE_REPLACEMENT**: Urgent replacement needed

## Confidence Levels

- **VERY_HIGH**: >90% confidence (multiple consistent indicators)
- **HIGH**: 75-90% confidence (good supporting evidence)
- **MEDIUM**: 50-75% confidence (some indicators available)
- **LOW**: <50% confidence (limited data)

## Advanced Features

### Batch Analysis
```javascript
const results = agent.analyzeBatch([
  { soh: 92.0 },
  { soh: 78.5 },
  { soh: 55.3, rul: 120 }
]);
```

### Trend Comparison
```javascript
const oldDecision = agent.analyze({ soh: 85.0 });
const newDecision = agent.analyze({ soh: 78.5 });
const trend = agent.compareTrend(oldDecision, newDecision);
```

## Decision Logic

1. **Base Assessment**: Determine state from SOH thresholds
2. **Cross-Validation**: Verify with model classification
3. **RUL Adjustment**: Modify state based on remaining life
4. **Action Selection**: Choose appropriate user action
5. **Confidence Calculation**: Assess decision reliability

## Integration with UI

The UI should:
1. Collect model predictions from models.tools
2. Pass predictions to BatteryAgent.analyze()
3. Display decision.state, decision.recommendedAction
4. Show decision.reasoning for transparency
5. Never call ML models directly

## Example Output

```json
{
  "state": "FAIR",
  "confidence": "HIGH",
  "recommendedAction": "MONITOR_CLOSELY",
  "reasoning": [
    "SOH is 68.3%, battery shows moderate degradation",
    "Model classification confirms SOH-based assessment",
    "RUL is 180 cycles - approaching end of usable life",
    "Monitor battery health regularly to track degradation",
    "Good confidence with supporting evidence from models"
  ],
  "metadata": {
    "soh": 68.3,
    "classification": "FAIR",
    "rul": 180,
    "modelConfidence": 0.78,
    "thresholdsUsed": { ... }
  },
  "timestamp": "2026-02-05T..."
}
```

## Testing

Run the examples:
```bash
node agents/example.js
```

## Customization

Adjust thresholds in the BatteryAgent constructor:
```javascript
this.sohThresholds = {
  excellent: 90,
  good: 75,
  fair: 60,
  poor: 45,
  critical: 30
};

this.rulThresholds = {
  urgent: 50,
  warning: 150,
  normal: 300
};
```
