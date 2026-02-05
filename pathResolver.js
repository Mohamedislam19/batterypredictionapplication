
/**
 * Path resolver for packaged application
 * Automatically detects if running in development or production
 */
const path = require('path');
const { app } = require('electron');

function getResourcePath(...pathSegments) {
    if (app.isPackaged) {
        // Production: use resources folder
        return path.join(process.resourcesPath, ...pathSegments);
    } else {
        // Development: use project root
        return path.join(__dirname, ...pathSegments);
    }
}

function getPythonExecutable() {
    if (app.isPackaged) {
        // Production: use bundled Python
        return path.join(process.resourcesPath, 'python-dist', 'python.exe');
    } else {
        // Development: use venv
        return path.join(__dirname, '.venv', 'Scripts', 'python.exe');
    }
}

module.exports = {
    getResourcePath,
    getPythonExecutable
};
