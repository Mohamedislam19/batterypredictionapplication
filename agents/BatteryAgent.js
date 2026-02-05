/**
 * BatteryAgent.js
 * Intelligent decision-making agent for battery health analysis
 * 
 * Design Principles:
 * - Deterministic: Same inputs always produce same outputs
 * - Explainable: Every decision includes human-readable reasoning
 * - Rule-based: No ML training, pure logic on top of model predictions
 * - Structured: Consistent output format for UI consumption
 */

const { BatteryState, RecommendedAction, ConfidenceLevel, AgentDecision } = require('./DecisionTypes');

class BatteryAgent {
  constructor(memorySize = 20) {
    // Thresholds for SOH-based classification
    this.sohThresholds = {
      excellent: 90,
      good: 75,
      fair: 60,
      poor: 45,
      critical: 30
    };

    // Thresholds for RUL-based urgency (in cycles)
    this.rulThresholds = {
      urgent: 50,
      warning: 150,
      normal: 300
    };

    // SHORT-TERM MEMORY: In-memory history of predictions
    this.memorySize = memorySize;
    this.history = [];  // Circular buffer of past readings

    // Trend detection thresholds
    this.trendThresholds = {
      suddenDrop: 5.0,        // SOH drop > 5% between readings = sudden
      rapidDegradation: 10.0, // SOH drop > 10% over memory window = rapid
      normalDegradation: 0.5, // Expected degradation per reading
      accelerating: 1.5       // Degradation rate multiplier for acceleration
    };
  }

  /**
   * Main decision-making method (now with historical awareness)
   * @param {Object} modelPredictions - Output from ML models
   * @param {number} modelPredictions.soh - State of Health (0-100)
   * @param {string} modelPredictions.classification - Model classification result
   * @param {number} [modelPredictions.rul] - Remaining Useful Life (optional)
   * @param {number} [modelPredictions.confidence] - Model confidence (optional)
   * @returns {AgentDecision} Structured decision with state, action, reasoning
   */
  analyze(modelPredictions) {
    const { soh, classification, rul, confidence } = modelPredictions;

    // Validate inputs
    if (typeof soh !== 'number' || soh < 0 || soh > 100) {
      throw new Error('Invalid SOH value. Must be a number between 0 and 100.');
    }

    const reasoning = [];
    let state, action, confidenceLevel;

    // MEMORY: Analyze historical trends before making decision
    const trendAnalysis = this._analyzeTrends(soh, reasoning);

    // Step 1: Determine base state from SOH
    const baseState = this._determineStateFromSOH(soh, reasoning);

    // Step 2: Cross-validate with classification if available
    const validatedState = this._crossValidateWithClassification(
      baseState, 
      classification, 
      soh, 
      reasoning
    );

    // Step 3: Adjust based on RUL if available
    let adjustedState = this._adjustForRUL(validatedState, rul, reasoning);

    // Step 4: MEMORY-AWARE: Adjust state based on historical trends
    adjustedState = this._adjustForTrends(adjustedState, trendAnalysis, soh, reasoning);

    // Step 5: Determine recommended action
    action = this._determineAction(adjustedState, rul, soh, reasoning, trendAnalysis);

    // Step 6: Calculate confidence level (with trend awareness)
    confidenceLevel = this._determineConfidence(soh, classification, rul, confidence, reasoning, trendAnalysis);

    // Step 7: Build metadata (include trend data)
    const metadata = this._buildMetadata(soh, classification, rul, confidence, trendAnalysis);

    // MEMORY: Store this reading in history
    this._addToHistory({ soh, classification, rul, confidence, timestamp: new Date() });

    return new AgentDecision(adjustedState, confidenceLevel, action, reasoning, metadata);
  }

  /**
   * Add a reading to short-term memory
   * @private
   */
  _addToHistory(reading) {
    this.history.push(reading);
    
    // Maintain circular buffer - remove oldest if exceeds size
    if (this.history.length > this.memorySize) {
      this.history.shift();
    }
  }

  /**
   * Analyze historical trends to detect degradation patterns
   * @private
   */
  _analyzeTrends(currentSOH, reasoning) {
    const trend = {
      hasSufficientHistory: this.history.length >= 2,
      suddenDrop: false,
      rapidDegradation: false,
      accelerating: false,
      degradationRate: 0,
      recentAverage: currentSOH,
      oldestSOH: currentSOH
    };

    // Need at least 2 readings for trend analysis
    if (this.history.length < 2) {
      return trend;
    }

    const recentHistory = this.history.slice(-5);  // Last 5 readings
    const oldestReading = this.history[0];
    const previousReading = this.history[this.history.length - 1];

    trend.oldestSOH = oldestReading.soh;

    // Calculate recent average
    const recentSOHs = recentHistory.map(r => r.soh);
    trend.recentAverage = recentSOHs.reduce((a, b) => a + b, 0) / recentSOHs.length;

    // Detect SUDDEN DROP (compared to previous reading)
    const dropSincePrevious = previousReading.soh - currentSOH;
    if (dropSincePrevious > this.trendThresholds.suddenDrop) {
      trend.suddenDrop = true;
      reasoning.push(`⚠️ SUDDEN DROP: SOH dropped ${dropSincePrevious.toFixed(1)}% since last reading`);
    }

    // Calculate overall degradation rate
    const totalDrop = oldestReading.soh - currentSOH;
    const readingsSpan = this.history.length;
    trend.degradationRate = totalDrop / readingsSpan;

    // Detect RAPID DEGRADATION (over entire history)
    if (totalDrop > this.trendThresholds.rapidDegradation) {
      trend.rapidDegradation = true;
      reasoning.push(`⚠️ RAPID DEGRADATION: SOH dropped ${totalDrop.toFixed(1)}% over ${readingsSpan} readings`);
    }

    // Detect ACCELERATION (recent degradation faster than overall average)
    if (this.history.length >= 4) {
      const midPoint = Math.floor(this.history.length / 2);
      const olderHalf = this.history.slice(0, midPoint);
      const newerHalf = this.history.slice(midPoint);

      const olderAvg = olderHalf.reduce((sum, r) => sum + r.soh, 0) / olderHalf.length;
      const newerAvg = newerHalf.reduce((sum, r) => sum + r.soh, 0) / newerHalf.length;
      
      const recentRate = (olderAvg - newerAvg) / newerHalf.length;
      const overallRate = trend.degradationRate;

      if (recentRate > overallRate * this.trendThresholds.accelerating && recentRate > this.trendThresholds.normalDegradation) {
        trend.accelerating = true;
        reasoning.push(`📉 ACCELERATING: Degradation rate is increasing over time`);
      }
    }

    return trend;
  }

  /**
   * Adjust state based on historical trends
   * @private
   */
  _adjustForTrends(state, trendAnalysis, currentSOH, reasoning) {
    if (!trendAnalysis.hasSufficientHistory) {
      return state;
    }

    let adjustedState = state;

    // SUDDEN DROP: Escalate state even if current SOH seems OK
    if (trendAnalysis.suddenDrop) {
      if (state === BatteryState.EXCELLENT || state === BatteryState.GOOD) {
        adjustedState = BatteryState.FAIR;
        reasoning.push(`State downgraded to FAIR due to sudden performance drop`);
      } else if (state === BatteryState.FAIR) {
        adjustedState = BatteryState.POOR;
        reasoning.push(`State downgraded to POOR due to sudden performance drop`);
      }
    }

    // RAPID DEGRADATION + ACCELERATING: Escalate further
    if (trendAnalysis.rapidDegradation && trendAnalysis.accelerating) {
      if (state === BatteryState.GOOD) {
        adjustedState = BatteryState.FAIR;
        reasoning.push(`State downgraded due to rapid and accelerating degradation`);
      } else if (state === BatteryState.FAIR) {
        adjustedState = BatteryState.POOR;
        reasoning.push(`State downgraded due to rapid and accelerating degradation`);
      } else if (state === BatteryState.POOR) {
        adjustedState = BatteryState.CRITICAL;
        reasoning.push(`State escalated to CRITICAL due to dangerous degradation pattern`);
      }
    }

    // POSITIVE TREND: If SOH is stable or improving (rare but possible after recalibration)
    if (trendAnalysis.degradationRate < 0) {  // Negative rate = improvement
      reasoning.push(`✓ Battery health is stable or improving`);
    }

    return adjustedState;
  }

  /**
   * Determine battery state based on SOH value
   */
  _determineStateFromSOH(soh, reasoning) {
    let state;

    if (soh >= this.sohThresholds.excellent) {
      state = BatteryState.EXCELLENT;
      reasoning.push(`SOH is ${soh.toFixed(1)}%, indicating excellent battery health`);
    } else if (soh >= this.sohThresholds.good) {
      state = BatteryState.GOOD;
      reasoning.push(`SOH is ${soh.toFixed(1)}%, battery is in good condition`);
    } else if (soh >= this.sohThresholds.fair) {
      state = BatteryState.FAIR;
      reasoning.push(`SOH is ${soh.toFixed(1)}%, battery shows moderate degradation`);
    } else if (soh >= this.sohThresholds.poor) {
      state = BatteryState.POOR;
      reasoning.push(`SOH is ${soh.toFixed(1)}%, battery health is significantly degraded`);
    } else if (soh >= this.sohThresholds.critical) {
      state = BatteryState.CRITICAL;
      reasoning.push(`SOH is ${soh.toFixed(1)}%, battery is in critical condition`);
    } else {
      state = BatteryState.REPLACE_NOW;
      reasoning.push(`SOH is ${soh.toFixed(1)}%, battery has reached end of life`);
    }

    return state;
  }

  /**
   * Cross-validate SOH state with model classification
   */
  _crossValidateWithClassification(baseState, classification, soh, reasoning) {
    if (!classification) {
      return baseState;
    }

    const classNormalized = classification.toUpperCase();

    // Check for agreement/disagreement
    if (classNormalized.includes('EXCELLENT') && baseState !== BatteryState.EXCELLENT) {
      reasoning.push(`Model classification suggests excellent health, adjusting assessment`);
      return BatteryState.EXCELLENT;
    }

    if (classNormalized.includes('CRITICAL') || classNormalized.includes('REPLACE')) {
      if (soh < this.sohThresholds.fair) {
        reasoning.push(`Model classification confirms critical state`);
        return BatteryState.REPLACE_NOW;
      }
    }

    if (classNormalized.includes('POOR') && soh < this.sohThresholds.good) {
      reasoning.push(`Model classification aligns with poor battery health assessment`);
      return BatteryState.POOR;
    }

    // If classification agrees with base assessment
    reasoning.push(`Model classification confirms SOH-based assessment`);
    return baseState;
  }

  /**
   * Adjust state based on Remaining Useful Life prediction
   */
  _adjustForRUL(state, rul, reasoning) {
    if (typeof rul !== 'number' || rul < 0) {
      return state;
    }

    if (rul < this.rulThresholds.urgent) {
      reasoning.push(`RUL is only ${rul} cycles - immediate attention required`);
      
      // Escalate to more critical state if RUL is very low
      if (rul < 25) {
        return BatteryState.REPLACE_NOW;
      } else if (state === BatteryState.GOOD || state === BatteryState.EXCELLENT) {
        return BatteryState.FAIR; // Downgrade if RUL is low despite good SOH
      }
      return BatteryState.CRITICAL;
    }

    if (rul < this.rulThresholds.warning) {
      reasoning.push(`RUL is ${rul} cycles - approaching end of usable life`);
      
      if (state === BatteryState.EXCELLENT) {
        return BatteryState.GOOD; // Slight downgrade
      }
    } else {
      reasoning.push(`RUL is ${rul} cycles - sufficient remaining lifespan`);
    }

    return state;
  }

  /**
   * Determine recommended action based on state and metrics (with trend awareness)
   */
  _determineAction(state, rul, soh, reasoning, trendAnalysis = {}) {
    let action;

    switch (state) {
      case BatteryState.EXCELLENT:
      case BatteryState.GOOD:
        action = RecommendedAction.CONTINUE_NORMAL_USE;
        reasoning.push(`Battery is healthy - no action required`);
        
        // But warn if trends are concerning
        if (trendAnalysis.accelerating) {
          reasoning.push(`However, monitor closely due to accelerating degradation`);
        }
        break;

      case BatteryState.FAIR:
        if (rul && rul < this.rulThresholds.warning) {
          action = RecommendedAction.MONITOR_CLOSELY;
          reasoning.push(`Begin monitoring battery performance and plan for eventual replacement`);
        } else if (trendAnalysis.suddenDrop || trendAnalysis.accelerating) {
          action = RecommendedAction.MONITOR_CLOSELY;
          reasoning.push(`Monitor closely due to concerning degradation pattern`);
        } else {
          action = RecommendedAction.MONITOR_CLOSELY;
          reasoning.push(`Monitor battery health regularly to track degradation`);
        }
        break;

      case BatteryState.POOR:
        action = RecommendedAction.REDUCE_INTENSIVE_TASKS;
        reasoning.push(`Avoid intensive tasks and keep device plugged in when possible`);
        
        if (rul && rul < this.rulThresholds.warning) {
          action = RecommendedAction.BACKUP_DATA;
          reasoning.push(`Begin backing up important data as precaution`);
        }

        // Escalate if trends are dangerous
        if (trendAnalysis.rapidDegradation && trendAnalysis.accelerating) {
          action = RecommendedAction.BACKUP_DATA;
          reasoning.push(`Backup data immediately due to dangerous degradation trend`);
        }
        break;

      case BatteryState.CRITICAL:
        action = RecommendedAction.SCHEDULE_REPLACEMENT;
        reasoning.push(`Schedule battery replacement soon to avoid sudden failure`);
        
        if (trendAnalysis.suddenDrop) {
          reasoning.push(`Urgent action needed due to sudden performance drop`);
        }
        break;

      case BatteryState.REPLACE_NOW:
        action = RecommendedAction.IMMEDIATE_REPLACEMENT;
        reasoning.push(`Battery replacement is urgent - risk of failure or damage`);
        break;

      default:
        action = RecommendedAction.MONITOR_CLOSELY;
    }

    return action;
  }

  /**
   * Determine confidence level in the decision (with trend data)
   */
  _determineConfidence(soh, classification, rul, modelConfidence, reasoning, trendAnalysis = {}) {
    let confidenceScore = 0;

    // Base confidence from SOH clarity
    if (soh > 85 || soh < 40) {
      confidenceScore += 30; // Clear cases
    } else {
      confidenceScore += 15; // Borderline cases
    }

    // Confidence from classification agreement
    if (classification) {
      confidenceScore += 25;
    } else {
      confidenceScore += 10;
    }

    // Confidence from RUL availability
    if (typeof rul === 'number' && rul >= 0) {
      confidenceScore += 25;
    } else {
      confidenceScore += 10;
    }

    // Confidence from model's own confidence
    if (modelConfidence && modelConfidence > 0.8) {
      confidenceScore += 20;
    } else if (modelConfidence && modelConfidence > 0.6) {
      confidenceScore += 10;
    } else {
      confidenceScore += 5;
    }

    // BONUS: Historical data increases confidence
    if (trendAnalysis.hasSufficientHistory) {
      confidenceScore += 10;
      reasoning.push(`Historical trend data strengthens confidence`);
    }

    // PENALTY: Conflicting trends reduce confidence
    if (trendAnalysis.suddenDrop) {
      confidenceScore -= 5;
    }

    // Classify confidence level
    if (confidenceScore >= 90) {
      reasoning.push(`High confidence in assessment based on multiple consistent indicators`);
      return ConfidenceLevel.VERY_HIGH;
    } else if (confidenceScore >= 75) {
      reasoning.push(`Good confidence with supporting evidence from models`);
      return ConfidenceLevel.HIGH;
    } else if (confidenceScore >= 50) {
      reasoning.push(`Moderate confidence - some indicators available`);
      return ConfidenceLevel.MEDIUM;
    } else {
      reasoning.push(`Limited confidence - recommend additional monitoring`);
      return ConfidenceLevel.LOW;
    }
  }

  /**
   * Build metadata object with all relevant metrics (including trends)
   */
  _buildMetadata(soh, classification, rul, modelConfidence, trendAnalysis = {}) {
    return {
      soh: soh,
      classification: classification || null,
      rul: rul || null,
      modelConfidence: modelConfidence || null,
      thresholdsUsed: {
        soh: this.sohThresholds,
        rul: this.rulThresholds
      },
      historicalTrends: {
        readingsInMemory: this.history.length,
        suddenDrop: trendAnalysis.suddenDrop || false,
        rapidDegradation: trendAnalysis.rapidDegradation || false,
        accelerating: trendAnalysis.accelerating || false,
        degradationRate: trendAnalysis.degradationRate || 0,
        recentAverage: trendAnalysis.recentAverage || soh,
        oldestSOH: trendAnalysis.oldestSOH || soh
      }
    };
  }

  /**
   * Get historical readings (read-only access to memory)
   */
  getHistory() {
    return [...this.history];  // Return copy to prevent external modification
  }

  /**
   * Clear historical memory (useful for testing or new battery)
   */
  clearHistory() {
    this.history = [];
  }

  /**
   * Get memory statistics
   */
  getMemoryStats() {
    if (this.history.length === 0) {
      return {
        count: 0,
        oldestSOH: null,
        newestSOH: null,
        averageSOH: null,
        totalDegradation: null
      };
    }

    const sohs = this.history.map(r => r.soh);
    const oldest = this.history[0];
    const newest = this.history[this.history.length - 1];

    return {
      count: this.history.length,
      oldestSOH: oldest.soh,
      newestSOH: newest.soh,
      averageSOH: sohs.reduce((a, b) => a + b, 0) / sohs.length,
      totalDegradation: oldest.soh - newest.soh,
      oldestTimestamp: oldest.timestamp,
      newestTimestamp: newest.timestamp
    };
  }

  /**
   * Batch analysis for multiple battery readings
   * Useful for trend analysis or comparison
   */
  analyzeBatch(predictionsList) {
    return predictionsList.map(prediction => this.analyze(prediction));
  }

  /**
   * Compare two battery states to detect degradation
   */
  compareTrend(oldDecision, newDecision) {
    const oldSOH = oldDecision.metadata.soh;
    const newSOH = newDecision.metadata.soh;
    const sohChange = newSOH - oldSOH;

    const trend = {
      improving: sohChange > 0,
      stable: Math.abs(sohChange) < 2,
      degrading: sohChange < -2,
      sohChange: sohChange,
      stateChange: oldDecision.state !== newDecision.state,
      recommendation: null
    };

    if (trend.degrading && sohChange < -5) {
      trend.recommendation = 'Rapid degradation detected - investigate usage patterns';
    } else if (trend.stable) {
      trend.recommendation = 'Battery health is stable';
    }

    return trend;
  }
}

module.exports = BatteryAgent;
