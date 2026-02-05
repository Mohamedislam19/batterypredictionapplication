/**
 * AUTOMATED RELEASE SCRIPT
 * Uploads built installer to GitHub Releases and generates public download link
 * 
 * Prerequisites:
 * 1. GitHub repository exists
 * 2. GitHub Personal Access Token with 'repo' scope
 * 3. Application has been built (run 'npm run package' first)
 * 
 * Usage:
 *   Set environment variable: GITHUB_TOKEN=your_token_here
 *   Run: npm run release
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
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

// Configuration
const CONFIG = {
    owner: process.env.GITHUB_OWNER || 'Mohamedislam19',
    repo: process.env.GITHUB_REPO || 'batterypredictionapplication',
    token: process.env.GITHUB_TOKEN,
    version: require('../package.json').version
};

async function createGitHubRelease() {
    log('\n' + '='.repeat(80), 'blue');
    log('AUTOMATED RELEASE TO GITHUB', 'blue');
    log('='.repeat(80) + '\n', 'blue');

    // Validate configuration
    if (!CONFIG.token) {
        log('ERROR: GITHUB_TOKEN environment variable not set', 'red');
        log('\nTo set up:', 'yellow');
        log('1. Go to https://github.com/settings/tokens', 'yellow');
        log('2. Generate new token with "repo" scope', 'yellow');
        log('3. Set environment variable:', 'yellow');
        log('   Windows: set GITHUB_TOKEN=your_token_here', 'blue');
        log('   macOS/Linux: export GITHUB_TOKEN=your_token_here', 'blue');
        process.exit(1);
    }

    // Find installer file
    const distDir = path.join(__dirname, '..', 'dist');
    if (!fs.existsSync(distDir)) {
        log('ERROR: dist/ directory not found. Run "npm run package" first.', 'red');
        process.exit(1);
    }

    const files = fs.readdirSync(distDir);
    const installer = files.find(f => f.endsWith('.exe') && f.includes('Setup'));
    
    if (!installer) {
        log('ERROR: No installer found in dist/ directory', 'red');
        log('Available files:', 'yellow');
        files.forEach(f => log(`  - ${f}`, 'yellow'));
        process.exit(1);
    }

    const installerPath = path.join(distDir, installer);
    const fileSize = fs.statSync(installerPath).size;
    log(`Found installer: ${installer} (${(fileSize / 1024 / 1024).toFixed(2)} MB)`, 'green');

    // Create release
    const tagName = `v${CONFIG.version}`;
    const releaseName = `Battery Health Prediction ${CONFIG.version}`;
    const releaseBody = `
# Battery Health Prediction System v${CONFIG.version}

## What's New
- NASA-trained ML models for Li-ion battery health prediction
- State of Health (SOH) and Remaining Useful Life (RUL) estimation
- Intelligent agent with memory and trend detection
- Real-time degradation visualization

## Installation
1. Download \`${installer}\` below
2. Run the installer
3. Follow the installation wizard
4. Launch "Battery Health Prediction" from your desktop or start menu

## System Requirements
- Windows 10/11 (64-bit)
- 500 MB free disk space
- No internet connection required (fully offline AI)

## Download
`;

    log('\nCreating GitHub release...', 'yellow');

    const releaseData = {
        tag_name: tagName,
        name: releaseName,
        body: releaseBody,
        draft: false,
        prerelease: false
    };

    try {
        const release = await githubRequest('POST', `/repos/${CONFIG.owner}/${CONFIG.repo}/releases`, releaseData);
        log(`✓ Release created: ${release.html_url}`, 'green');

        // Upload installer
        log('\nUploading installer...', 'yellow');
        const uploadUrl = release.upload_url.replace('{?name,label}', `?name=${installer}`);
        
        await uploadFile(uploadUrl, installerPath, installer);
        
        log('\n' + '='.repeat(80), 'green');
        log('✓ RELEASE COMPLETED SUCCESSFULLY!', 'green');
        log('='.repeat(80), 'green');
        
        log('\n📦 Download Link:', 'blue');
        log(`   ${release.html_url}`, 'green');
        
        log('\n🔗 Direct Installer Link:', 'blue');
        log(`   https://github.com/${CONFIG.owner}/${CONFIG.repo}/releases/download/${tagName}/${installer}`, 'green');
        
        log('\n✓ Users can now download and install your application!', 'green');
        
    } catch (error) {
        log('\n✗ Release failed:', 'red');
        log(error.message, 'red');
        if (error.response) {
            log(error.response, 'red');
        }
        process.exit(1);
    }
}

function githubRequest(method, path, data = null) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'api.github.com',
            path: path,
            method: method,
            headers: {
                'Authorization': `token ${CONFIG.token}`,
                'User-Agent': 'Battery-Health-Release-Script',
                'Accept': 'application/vnd.github.v3+json'
            }
        };

        if (data) {
            const jsonData = JSON.stringify(data);
            options.headers['Content-Type'] = 'application/json';
            options.headers['Content-Length'] = Buffer.byteLength(jsonData);
        }

        const req = https.request(options, (res) => {
            let responseData = '';
            
            res.on('data', (chunk) => {
                responseData += chunk;
            });
            
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try {
                        resolve(JSON.parse(responseData));
                    } catch (e) {
                        resolve(responseData);
                    }
                } else {
                    const error = new Error(`GitHub API error: ${res.statusCode}`);
                    error.response = responseData;
                    reject(error);
                }
            });
        });

        req.on('error', reject);

        if (data) {
            req.write(JSON.stringify(data));
        }

        req.end();
    });
}

function uploadFile(uploadUrl, filePath, fileName) {
    return new Promise((resolve, reject) => {
        const fileContent = fs.readFileSync(filePath);
        const fileSize = fs.statSync(filePath).size;
        
        const url = new URL(uploadUrl);
        
        const options = {
            hostname: url.hostname,
            path: url.pathname + url.search,
            method: 'POST',
            headers: {
                'Authorization': `token ${CONFIG.token}`,
                'User-Agent': 'Battery-Health-Release-Script',
                'Content-Type': 'application/octet-stream',
                'Content-Length': fileSize
            }
        };

        log(`Uploading ${(fileSize / 1024 / 1024).toFixed(2)} MB...`, 'yellow');
        
        const req = https.request(options, (res) => {
            let responseData = '';
            
            res.on('data', (chunk) => {
                responseData += chunk;
            });
            
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    log('✓ Upload complete', 'green');
                    try {
                        resolve(JSON.parse(responseData));
                    } catch (e) {
                        resolve(responseData);
                    }
                } else {
                    const error = new Error(`Upload failed: ${res.statusCode}`);
                    error.response = responseData;
                    reject(error);
                }
            });
        });

        req.on('error', reject);
        req.write(fileContent);
        req.end();
    });
}

// Alternative: Google Drive upload (if GitHub not available)
async function uploadToGoogleDrive() {
    log('\n📦 Alternative: Upload to Google Drive', 'blue');
    log('For Google Drive upload, use the Google Drive API or manual upload:', 'yellow');
    log('1. Go to https://drive.google.com', 'yellow');
    log('2. Upload the installer from dist/ directory', 'yellow');
    log('3. Right-click → Get link → Set to "Anyone with the link"', 'yellow');
    log('4. Share the link with your users', 'yellow');
}

createGitHubRelease().catch(error => {
    log('\nIf GitHub is not available, you can:', 'yellow');
    log('1. Use Google Drive: Upload installer and make it public', 'yellow');
    log('2. Use Dropbox: Upload and create public link', 'yellow');
    log('3. Use AWS S3: Create public bucket and upload', 'yellow');
    process.exit(1);
});
