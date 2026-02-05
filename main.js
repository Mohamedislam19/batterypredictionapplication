const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const BatteryPredictionService = require('./predictionService');

let mainWindow;
const predictionService = new BatteryPredictionService();

// IPC Handler for battery health predictions
ipcMain.handle('predict-battery', async (event, csvPath) => {
    try {
        console.log(`[Main] Predicting battery health from: ${csvPath}`);
        const result = await predictionService.predictFromFile(csvPath);
        console.log(`[Main] Prediction complete. SOH: ${result.summary.sohValue}%, RUL: ${result.summary.rulValue} cycles`);
        return result;
    } catch (error) {
        console.error(`[Main] Prediction error:`, error);
        return {
            success: false,
            error: error.message
        };
    }
});

// IPC Handler for agent memory stats
ipcMain.handle('get-memory-stats', () => {
    return predictionService.getMemoryStats();
});

// IPC Handler to clear agent history
ipcMain.handle('clear-history', () => {
    predictionService.clearHistory();
    return { success: true };
});

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1600,
        height: 1000,
        minWidth: 1200,
        minHeight: 800,
        backgroundColor: '#0f1419',
        title: 'Battery Health Prediction System',
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true
        },
        icon: path.join(__dirname, 'assets/icon.png'), // Optional: add icon later
        autoHideMenuBar: false,
        frame: true
    });

    mainWindow.loadFile('index.html');

    // Open DevTools in development mode
    if (process.argv.includes('--dev')) {
        mainWindow.webContents.openDevTools();
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Set window title
    mainWindow.on('page-title-updated', (event) => {
        event.preventDefault();
    });
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// Handle any uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
});
