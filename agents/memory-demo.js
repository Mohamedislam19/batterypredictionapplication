/**
 * memory-demo.js
 * Demonstration of BatteryAgent's short-term memory capabilities
 */

const BatteryAgent = require('./BatteryAgent');

console.log('=== BatteryAgent Memory Demonstration ===\n');

const agent = new BatteryAgent(10);  // Keep last 10 readings

// ==========================================
// Scenario 1: Normal Gradual Degradation
// ==========================================
console.log('Scenario 1: Normal Gradual Degradation');
console.log('----------------------------------------');

const normalDegradation = [
  { soh: 95.0, classification: 'EXCELLENT' },
  { soh: 93.5, classification: 'EXCELLENT' },
  { soh: 92.0, classification: 'EXCELLENT' },
  { soh: 90.5, classification: 'EXCELLENT' },
  { soh: 89.0, classification: 'GOOD' }
];

normalDegradation.forEach((reading, index) => {
  const result = agent.analyze(reading);
  console.log(`Reading ${index + 1}: SOH ${reading.soh}% → ${result.state}`);
  console.log(`  Trend Flags: Drop=${result.metadata.historicalTrends.suddenDrop}, Rapid=${result.metadata.historicalTrends.rapidDegradation}, Accel=${result.metadata.historicalTrends.accelerating}`);
});

console.log('\nMemory Stats:', agent.getMemoryStats());
console.log('\n');

// ==========================================
// Scenario 2: Sudden Drop Detection
// ==========================================
console.log('Scenario 2: Sudden Drop Detection');
console.log('----------------------------------------');

agent.clearHistory();  // Start fresh

const suddenDropReadings = [
  { soh: 88.0, classification: 'GOOD' },
  { soh: 87.5, classification: 'GOOD' },
  { soh: 87.0, classification: 'GOOD' },
  { soh: 80.0, classification: 'GOOD' }  // SUDDEN DROP of 7%!
];

suddenDropReadings.forEach((reading, index) => {
  const result = agent.analyze(reading);
  console.log(`Reading ${index + 1}: SOH ${reading.soh}% → ${result.state}`);
  
  if (result.metadata.historicalTrends.suddenDrop) {
    console.log(`  ⚠️  SUDDEN DROP DETECTED!`);
  }
  
  const relevantReasoning = result.reasoning.filter(r => r.includes('DROP') || r.includes('downgrade'));
  if (relevantReasoning.length > 0) {
    relevantReasoning.forEach(r => console.log(`  → ${r}`));
  }
});
console.log('\n');

// ==========================================
// Scenario 3: Accelerating Degradation
// ==========================================
console.log('Scenario 3: Accelerating Degradation');
console.log('----------------------------------------');

agent.clearHistory();

const acceleratingReadings = [
  { soh: 90.0 },  // Start stable
  { soh: 89.5 },
  { soh: 89.0 },
  { soh: 88.5 },
  { soh: 87.5 },  // Then accelerate
  { soh: 85.0 },
  { soh: 81.0 },
  { soh: 75.0 }
];

acceleratingReadings.forEach((reading, index) => {
  const result = agent.analyze(reading);
  console.log(`Reading ${index + 1}: SOH ${reading.soh}% → ${result.state}`);
  
  if (result.metadata.historicalTrends.accelerating) {
    console.log(`  📉 ACCELERATION DETECTED!`);
  }
  
  if (index === acceleratingReadings.length - 1) {
    console.log(`\n  Final Assessment:`);
    console.log(`    Degradation Rate: ${result.metadata.historicalTrends.degradationRate.toFixed(2)}% per reading`);
    console.log(`    Total Drop: ${(result.metadata.historicalTrends.oldestSOH - reading.soh).toFixed(1)}%`);
    console.log(`    Recommended Action: ${result.recommendedAction}`);
  }
});
console.log('\n');

// ==========================================
// Scenario 4: Rapid Degradation Warning
// ==========================================
console.log('Scenario 4: Rapid Degradation Over Time');
console.log('----------------------------------------');

agent.clearHistory();

const rapidReadings = [
  { soh: 85.0, rul: 300 },
  { soh: 82.0, rul: 280 },
  { soh: 78.0, rul: 250 },
  { soh: 73.0, rul: 220 },
  { soh: 67.0, rul: 180 }  // Dropped 18% over 5 readings
];

rapidReadings.forEach((reading, index) => {
  const result = agent.analyze(reading);
  console.log(`Reading ${index + 1}: SOH ${reading.soh}% → ${result.state}`);
  
  if (result.metadata.historicalTrends.rapidDegradation) {
    console.log(`  ⚠️  RAPID DEGRADATION WARNING!`);
  }
});

const finalStats = agent.getMemoryStats();
console.log(`\nTotal degradation: ${finalStats.totalDegradation.toFixed(1)}% over ${finalStats.count} readings`);
console.log('\n');

// ==========================================
// Scenario 5: Stable Battery (No Alerts)
// ==========================================
console.log('Scenario 5: Stable Battery Performance');
console.log('----------------------------------------');

agent.clearHistory();

const stableReadings = [
  { soh: 92.0 },
  { soh: 91.8 },
  { soh: 91.9 },
  { soh: 91.7 },
  { soh: 91.6 }
];

stableReadings.forEach((reading, index) => {
  const result = agent.analyze(reading);
  console.log(`Reading ${index + 1}: SOH ${reading.soh}% → ${result.state}`);
});

const stableStats = agent.getMemoryStats();
console.log(`\nTotal degradation: ${stableStats.totalDegradation.toFixed(1)}% (minimal/stable)`);
console.log('\n');

// ==========================================
// Scenario 6: Decision Comparison (With vs Without Memory)
// ==========================================
console.log('Scenario 6: Impact of Memory on Decisions');
console.log('----------------------------------------');

const agentWithMemory = new BatteryAgent(10);
const agentWithoutMemory = new BatteryAgent(0);  // No memory

// Simulate sudden drop scenario
const setupReadings = [
  { soh: 88.0 },
  { soh: 87.5 },
  { soh: 87.0 }
];

setupReadings.forEach(r => agentWithMemory.analyze(r));

// Critical reading
const criticalReading = { soh: 80.0 };  // 7% drop!

const resultWithMemory = agentWithMemory.analyze(criticalReading);
const resultWithoutMemory = agentWithoutMemory.analyze(criticalReading);

console.log('Same Input (SOH = 80.0%):\n');
console.log('WITH Memory:');
console.log(`  State: ${resultWithMemory.state}`);
console.log(`  Action: ${resultWithMemory.recommendedAction}`);
console.log(`  Sudden Drop: ${resultWithMemory.metadata.historicalTrends.suddenDrop}`);

console.log('\nWITHOUT Memory:');
console.log(`  State: ${resultWithoutMemory.state}`);
console.log(`  Action: ${resultWithoutMemory.recommendedAction}`);
console.log(`  Sudden Drop: ${resultWithoutMemory.metadata.historicalTrends.suddenDrop}`);

console.log('\n✓ Memory enables context-aware decisions!\n');
