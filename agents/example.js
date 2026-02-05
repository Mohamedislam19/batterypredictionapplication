/**
 * example.js
 * Example usage and input/output contract for BatteryAgent
 * 
 * This file demonstrates:
 * - How to use BatteryAgent
 * - Expected input format
 * - Output structure
 * - Different scenarios
 */

const BatteryAgent = require('./BatteryAgent');
const { BatteryState, RecommendedAction, ConfidenceLevel } = require('./DecisionTypes');

// Initialize the agent
const agent = new BatteryAgent();

console.log('=== BatteryAgent Examples ===\n');

// ==========================================
// Example 1: Excellent Battery (High SOH, all indicators)
// ==========================================
console.log('Example 1: Excellent Battery');
console.log('----------------------------');

const excellentInput = {
  soh: 95.5,
  classification: 'EXCELLENT',
  rul: 450,
  confidence: 0.92
};

const excellentResult = agent.analyze(excellentInput);
console.log('Input:', JSON.stringify(excellentInput, null, 2));
console.log('\nOutput:');
console.log(JSON.stringify(excellentResult, null, 2));
console.log('\n');

// ==========================================
// Example 2: Degrading Battery (Medium SOH)
// ==========================================
console.log('Example 2: Degrading Battery');
console.log('----------------------------');

const degradingInput = {
  soh: 68.3,
  classification: 'FAIR',
  rul: 180,
  confidence: 0.78
};

const degradingResult = agent.analyze(degradingInput);
console.log('Input:', JSON.stringify(degradingInput, null, 2));
console.log('\nOutput:');
console.log(JSON.stringify(degradingResult, null, 2));
console.log('\n');

// ==========================================
// Example 3: Critical Battery (Low SOH, Low RUL)
// ==========================================
console.log('Example 3: Critical Battery');
console.log('----------------------------');

const criticalInput = {
  soh: 35.2,
  classification: 'CRITICAL',
  rul: 30,
  confidence: 0.88
};

const criticalResult = agent.analyze(criticalInput);
console.log('Input:', JSON.stringify(criticalInput, null, 2));
console.log('\nOutput:');
console.log(JSON.stringify(criticalResult, null, 2));
console.log('\n');

// ==========================================
// Example 4: SOH Only (No Classification or RUL)
// ==========================================
console.log('Example 4: SOH Only (Minimal Input)');
console.log('----------------------------');

const minimalInput = {
  soh: 82.0
};

const minimalResult = agent.analyze(minimalInput);
console.log('Input:', JSON.stringify(minimalInput, null, 2));
console.log('\nOutput:');
console.log(JSON.stringify(minimalResult, null, 2));
console.log('\n');

// ==========================================
// Example 5: Conflicting Signals (Good SOH but Low RUL)
// ==========================================
console.log('Example 5: Conflicting Signals');
console.log('----------------------------');

const conflictingInput = {
  soh: 85.0,
  classification: 'GOOD',
  rul: 40,  // Very low despite good SOH
  confidence: 0.65
};

const conflictingResult = agent.analyze(conflictingInput);
console.log('Input:', JSON.stringify(conflictingInput, null, 2));
console.log('\nOutput:');
console.log(JSON.stringify(conflictingResult, null, 2));
console.log('\n');

// ==========================================
// Example 6: Batch Analysis
// ==========================================
console.log('Example 6: Batch Analysis');
console.log('----------------------------');

const batchInputs = [
  { soh: 92.0, classification: 'EXCELLENT' },
  { soh: 78.5, classification: 'GOOD' },
  { soh: 55.3, classification: 'FAIR', rul: 120 },
  { soh: 28.1, classification: 'CRITICAL', rul: 15 }
];

const batchResults = agent.analyzeBatch(batchInputs);
console.log('Batch Results Summary:');
batchResults.forEach((result, index) => {
  console.log(`  Battery ${index + 1}: ${result.state} - ${result.recommendedAction}`);
});
console.log('\n');

// ==========================================
// Example 7: Trend Comparison
// ==========================================
console.log('Example 7: Trend Comparison');
console.log('----------------------------');

const oldReading = agent.analyze({ soh: 85.0, classification: 'GOOD' });
const newReading = agent.analyze({ soh: 78.5, classification: 'GOOD' });

const trend = agent.compareTrend(oldReading, newReading);
console.log('Old SOH: 85.0% → New SOH: 78.5%');
console.log('Trend Analysis:', JSON.stringify(trend, null, 2));
console.log('\n');

// ==========================================
// CONTRACT DOCUMENTATION
// ==========================================
console.log('=== INPUT/OUTPUT CONTRACT ===\n');

console.log('INPUT SCHEMA:');
console.log(`{
  soh: number,           // Required. State of Health (0-100)
  classification: string, // Optional. Model classification result
  rul: number,           // Optional. Remaining Useful Life (cycles)
  confidence: number     // Optional. Model confidence (0-1)
}`);

console.log('\nOUTPUT SCHEMA:');
console.log(`{
  state: string,              // BatteryState enum
  confidence: string,         // ConfidenceLevel enum
  recommendedAction: string,  // RecommendedAction enum
  reasoning: string[],        // Array of human-readable explanations
  metadata: {
    soh: number,
    classification: string | null,
    rul: number | null,
    modelConfidence: number | null,
    thresholdsUsed: object
  },
  timestamp: string          // ISO timestamp
}`);

console.log('\nAVAILABLE STATES:');
console.log(Object.keys(BatteryState).join(', '));

console.log('\nAVAILABLE ACTIONS:');
console.log(Object.keys(RecommendedAction).join(', '));

console.log('\nCONFIDENCE LEVELS:');
console.log(Object.keys(ConfidenceLevel).join(', '));
