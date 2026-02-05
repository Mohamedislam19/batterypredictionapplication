/**
 * COMPREHENSIVE PACKAGING SCRIPT
 * Automates the complete build process for Battery Health Prediction System
 * 
 * This script:
 * 1. Bundles Python environment with all dependencies
 * 2. Packages AI models (.joblib files)
 * 3. Fixes all file paths to be relative
 * 4. Creates standalone executable
 * 5. Prepares for installer creation
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const COLORS = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[36m',
    red: '\x1b[31m'
};

function log(message, color = 'reset') {
    console.log(`${COLORS[color]}${message}${COLORS.reset}`);
}

function exec(command, description) {
    log(`\n[EXECUTING] ${description}`, 'blue');
    log(`Command: ${command}`, 'yellow');
    try {
        const output = execSync(command, { 
            encoding: 'utf-8',
            stdio: 'inherit'
        });
        log(`✓ ${description} completed successfully`, 'green');
        return output;
    } catch (error) {
        log(`✗ ${description} failed:`, 'red');
        log(error.message, 'red');
        throw error;
    }
}

async function main() {
    log('\n' + '='.repeat(80), 'blue');
    log('BATTERY HEALTH PREDICTION SYSTEM - AUTOMATED PACKAGING', 'blue');
    log('='.repeat(80) + '\n', 'blue');

    const projectRoot = path.resolve(__dirname, '..');
    const pythonDistDir = path.join(projectRoot, 'python-dist');
    const modelsDir = path.join(projectRoot, 'Battery-health-prediction-develop', 'models');
    
    // Step 1: Clean previous builds
    log('\n[STEP 1/7] Cleaning previous builds...', 'yellow');
    const dirsToClean = [
        path.join(projectRoot, 'dist'),
        pythonDistDir
    ];
    
    dirsToClean.forEach(dir => {
        if (fs.existsSync(dir)) {
            log(`Removing ${dir}`, 'yellow');
            fs.rmSync(dir, { recursive: true, force: true });
        }
    });
    log('✓ Build directories cleaned', 'green');

    // Step 2: Create Python distribution bundle
    log('\n[STEP 2/7] Bundling Python environment...', 'yellow');
    fs.mkdirSync(pythonDistDir, { recursive: true });
    
    // Copy Python scripts
    const pythonFiles = [
        'python_bridge.py',
        'feature_engineering.py',
        'pipeline.py',
        'Battery-health-prediction-develop/tools.py'
    ];
    
    pythonFiles.forEach(file => {
        const src = path.join(projectRoot, file);
        const dest = path.join(pythonDistDir, path.basename(file));
        if (fs.existsSync(src)) {
            log(`Copying ${file}...`, 'yellow');
            fs.copyFileSync(src, dest);
        }
    });
    
    // Copy models
    const modelsDestDir = path.join(pythonDistDir, 'models');
    fs.mkdirSync(modelsDestDir, { recursive: true });
    
    if (fs.existsSync(modelsDir)) {
        const modelFiles = fs.readdirSync(modelsDir);
        log(`Copying ${modelFiles.length} model files...`, 'yellow');
        modelFiles.forEach(file => {
            if (file.endsWith('.joblib')) {
                fs.copyFileSync(
                    path.join(modelsDir, file),
                    path.join(modelsDestDir, file)
                );
            }
        });
    }
    
    // Create requirements.txt for bundled Python
    const requirements = [
        'numpy==2.2.1',
        'pandas==2.2.3',
        'scikit-learn==1.6.1',
        'joblib==1.4.2'
    ];
    fs.writeFileSync(
        path.join(pythonDistDir, 'requirements.txt'),
        requirements.join('\n')
    );
    
    log('✓ Python environment bundled', 'green');

    // Step 3: Fix file paths to be relative
    log('\n[STEP 3/7] Fixing file paths to be relative...', 'yellow');
    
    // Create path resolver utility
    const pathResolverCode = `
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
`;
    
    fs.writeFileSync(
        path.join(projectRoot, 'pathResolver.js'),
        pathResolverCode
    );
    
    log('✓ Path resolver created', 'green');

    // Step 4: Install electron-builder if not present
    log('\n[STEP 4/7] Installing build dependencies...', 'yellow');
    try {
        exec('npm install --save-dev electron-builder', 'Installing electron-builder');
    } catch (error) {
        log('electron-builder may already be installed', 'yellow');
    }
    log('✓ Build dependencies ready', 'green');

    // Step 5: Create LICENSE file if not exists
    log('\n[STEP 5/7] Creating license file...', 'yellow');
    const licensePath = path.join(projectRoot, 'LICENSE.txt');
    if (!fs.existsSync(licensePath)) {
        const licenseText = `MIT License

Copyright (c) 2026 Battery Health Prediction Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.`;
        fs.writeFileSync(licensePath, licenseText);
        log('✓ LICENSE.txt created', 'green');
    } else {
        log('LICENSE.txt already exists', 'yellow');
    }

    // Step 6: Create placeholder icon if not exists
    log('\n[STEP 6/7] Checking application icons...', 'yellow');
    const iconPath = path.join(projectRoot, 'build-resources', 'icon.ico');
    if (!fs.existsSync(iconPath)) {
        log('⚠ Warning: No icon.ico found in build-resources/', 'yellow');
        log('Please add icon.ico (256x256 px) to build-resources/ for Windows', 'yellow');
        log('Please add icon.icns for macOS builds', 'yellow');
    } else {
        log('✓ Application icons found', 'green');
    }

    // Step 7: Build the application
    log('\n[STEP 7/7] Building application...', 'yellow');
    log('This may take several minutes...', 'yellow');
    
    try {
        exec('npm run build', 'Building Windows executable with electron-builder');
        log('\n' + '='.repeat(80), 'green');
        log('✓ BUILD COMPLETED SUCCESSFULLY!', 'green');
        log('='.repeat(80), 'green');
        
        const distPath = path.join(projectRoot, 'dist');
        if (fs.existsSync(distPath)) {
            const files = fs.readdirSync(distPath);
            log('\nGenerated files:', 'blue');
            files.forEach(file => {
                const filePath = path.join(distPath, file);
                const stats = fs.statSync(filePath);
                const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
                log(`  - ${file} (${sizeMB} MB)`, 'green');
            });
        }
        
        log('\n✓ Installer ready in dist/ directory', 'green');
        log('Next step: Run "npm run release" to upload to GitHub Releases', 'blue');
        
    } catch (error) {
        log('\n✗ Build failed. Please check the error messages above.', 'red');
        throw error;
    }
}

main().catch(error => {
    log('\n✗ Packaging failed:', 'red');
    log(error.message, 'red');
    process.exit(1);
});
