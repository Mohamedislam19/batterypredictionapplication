/**
 * DecisionTypes.js
 * Structured decision formats for the BatteryAgent
 */

// Battery health states (from best to worst)
const BatteryState = {
  EXCELLENT: 'EXCELLENT',
  GOOD: 'GOOD',
  FAIR: 'FAIR',
  POOR: 'POOR',
  CRITICAL: 'CRITICAL',
  REPLACE_NOW: 'REPLACE_NOW'
};

// Recommended actions for the user
const RecommendedAction = {
  CONTINUE_NORMAL_USE: 'CONTINUE_NORMAL_USE',
  MONITOR_CLOSELY: 'MONITOR_CLOSELY',
  REDUCE_INTENSIVE_TASKS: 'REDUCE_INTENSIVE_TASKS',
  BACKUP_DATA: 'BACKUP_DATA',
  SCHEDULE_REPLACEMENT: 'SCHEDULE_REPLACEMENT',
  IMMEDIATE_REPLACEMENT: 'IMMEDIATE_REPLACEMENT'
};

// Confidence levels for decisions
const ConfidenceLevel = {
  VERY_HIGH: 'VERY_HIGH',   // >90%
  HIGH: 'HIGH',             // 75-90%
  MEDIUM: 'MEDIUM',         // 50-75%
  LOW: 'LOW'                // <50%
};

// Decision structure returned by agent
class AgentDecision {
  constructor(state, confidence, action, reasoning, metadata = {}) {
    this.state = state;                    // BatteryState
    this.confidence = confidence;          // ConfidenceLevel
    this.recommendedAction = action;       // RecommendedAction
    this.reasoning = reasoning;            // Array of explanation strings
    this.metadata = metadata;              // Additional context
    this.timestamp = new Date().toISOString();
  }
}

module.exports = {
  BatteryState,
  RecommendedAction,
  ConfidenceLevel,
  AgentDecision
};
