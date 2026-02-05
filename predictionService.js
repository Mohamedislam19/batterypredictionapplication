/**
 * Battery Prediction Service - Node.js module for calling Python ML pipeline
 * This bridges the Electron UI to the trained NASA battery health models
 */

const { spawn } = require('child_process');
const path = require('path');
const BatteryAgent = require('./agents/BatteryAgent');

class BatteryPredictionService {
    constructor() {
        this.pythonPath = path.join(__dirname, '.venv', 'Scripts', 'python.exe');
        this.pipelinePath = path.join(__dirname, 'pipeline.py');
        this.agent = new BatteryAgent(20); // 20 readings memory
    }

    /**
     * Predict battery health from CSV file
     * @param {string} csvPath - Absolute path to CSV file
     * @returns {Promise<Object>} - Prediction results with agent decision
     */
    async predictFromFile(csvPath) {
        return new Promise((resolve, reject) => {
            const pythonProcess = spawn(this.pythonPath, [this.pipelinePath, csvPath]);
            
            let stdout = '';
            let stderr = '';

            pythonProcess.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            pythonProcess.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            pythonProcess.on('close', (code) => {
                if (code !== 0) {
                    reject(new Error(`Python pipeline failed: ${stderr}`));
                    return;
                }

                try {
                    const result = JSON.parse(stdout);
                    
                    if (!result.success) {
                        reject(new Error(result.error || 'Prediction failed'));
                        return;
                    }

                    // Extract model predictions
                    const modelPredictions = result.predictions;
                    
                    // Prepare input for Battery Agent
                    const agentInput = {
                        soh: modelPredictions.soh.estimated_value,
                        classification: modelPredictions.classification,
                        rul: modelPredictions.rul.estimated_cycles,
                        confidence: modelPredictions.confidence
                    };

                    // Get intelligent decision from agent
                    const agentDecision = this.agent.analyze(agentInput);

                    // Combine ML predictions + Agent decision
                    resolve({
                        success: true,
                        file: result.file,
                        recordCount: result.records,
                        
                        // Raw ML model outputs
                        mlPredictions: {
                            soh: modelPredictions.soh,
                            rul: modelPredictions.rul
                        },
                        
                        // Intelligent agent decision
                        agentDecision: {
                            state: agentDecision.state,
                            confidence: agentDecision.confidence,
                            action: agentDecision.recommendedAction,
                            reasoning: agentDecision.reasoning,
                            metadata: agentDecision.metadata
                        },
                        
                        // Summary for UI
                        summary: {
                            sohValue: modelPredictions.soh.estimated_value,
                            rulValue: modelPredictions.rul.estimated_cycles,
                            healthState: agentDecision.state,
                            recommendedAction: agentDecision.recommendedAction,
                            confidence: agentDecision.confidence
                        }
                    });
                    
                } catch (error) {
                    reject(new Error(`Failed to parse prediction results: ${error.message}`));
                }
            });
        });
    }

    /**
     * Get agent memory statistics
     */
    getMemoryStats() {
        return this.agent.getMemoryStats();
    }

    /**
     * Clear agent history
     */
    clearHistory() {
        this.agent.clearHistory();
    }
}

module.exports = BatteryPredictionService;
