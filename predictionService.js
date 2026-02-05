/**
 * Battery Prediction Service - Node.js module for calling Python ML pipeline
 * This bridges the Electron UI to the trained NASA battery health models
 */

const { spawn } = require('child_process');
const path = require('path');
const BatteryAgent = require('./agents/BatteryAgent');

class BatteryPredictionService {
    constructor() {
        // Use virtual environment Python
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
            let pythonProcess;
            
            try {
                pythonProcess = spawn(this.pythonPath, [this.pipelinePath, csvPath]);
            } catch (error) {
                reject(new Error(`Failed to spawn Python process: ${error.message}`));
                return;
            }
            
            let stdout = '';
            let stderr = '';

            pythonProcess.on('error', (error) => {
                reject(new Error(`Python process error: ${error.message}. Make sure Python is installed and in your PATH.`));
            });

            pythonProcess.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            pythonProcess.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            pythonProcess.on('close', (code) => {
                if (code !== 0) {
                    const errorMsg = stderr || stdout || 'Unknown error';
                    reject(new Error(`Python pipeline failed with code ${code}: ${errorMsg}`));
                    return;
                }

                if (!stdout || stdout.trim().length === 0) {
                    reject(new Error('Python script produced no output'));
                    return;
                }

                try {
                    const result = JSON.parse(stdout);
                    console.log('[PredictionService] Raw ML output:', JSON.stringify(result.predictions, null, 2));
                    console.log('[PredictionService] Engineered Features Sample:');
                    console.log('  ', JSON.stringify(result.sample_features, null, 2));
                    console.log('[PredictionService] Total features engineered:', result.features_engineered);
                    
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

                    // Clear agent history for fresh analysis of each battery
                    // (prevents previous batteries from affecting current prediction)
                    this.agent.clearHistory();

                    // Get intelligent decision from agent
                    const agentDecision = this.agent.analyze(agentInput);
                    console.log('[PredictionService] Agent decision:', agentDecision.state, 'Action:', agentDecision.recommendedAction);

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
                            recommendedAction: agentDecision.recommendedAction,
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
                    reject(new Error(`Failed to parse prediction results: ${error.message}\nOutput: ${stdout.substring(0, 500)}`));
                }
            });

            // Add timeout to prevent hanging
            setTimeout(() => {
                if (pythonProcess && !pythonProcess.killed) {
                    pythonProcess.kill();
                    reject(new Error('Python process timed out after 30 seconds'));
                }
            }, 30000);
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

