# 🚀 AUTOMATED DEPLOYMENT GUIDE
**Battery Health Prediction System - Complete Packaging & Distribution**

This guide provides **fully automated** packaging, installer creation, and distribution for your desktop application with integrated AI models.

---

## 📋 PREREQUISITES

### Required Software
1. **Node.js** (v16 or higher)
   - Download: https://nodejs.org/
   - Verify: `node --version`

2. **Python 3.13** (already configured in `.venv`)
   - Virtual environment already set up
   - All ML dependencies installed

3. **Git** (for GitHub Releases)
   - Download: https://git-scm.com/
   - Verify: `git --version`

### Required Accounts & Tokens
1. **GitHub Account** (for hosting releases)
   - Create account: https://github.com/signup
   - Create repository for your project

2. **GitHub Personal Access Token** (for automated uploads)
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control)
   - Copy the token (you'll only see it once!)

---

## 🎯 ONE-COMMAND DEPLOYMENT

### Step 1: Configure GitHub
Edit `build-scripts/release.js` (lines 26-27):
```javascript
owner: process.env.GITHUB_OWNER || 'YOUR-GITHUB-USERNAME',  // Change this
repo: process.env.GITHUB_REPO || 'battery-health-prediction',  // Change this
```

### Step 2: Set GitHub Token (Windows)
```cmd
set GITHUB_TOKEN=your_personal_access_token_here
set GITHUB_OWNER=your-github-username
set GITHUB_REPO=battery-health-prediction
```

**For macOS/Linux:**
```bash
export GITHUB_TOKEN=your_personal_access_token_here
export GITHUB_OWNER=your-github-username
export GITHUB_REPO=battery-health-prediction
```

### Step 3: Run Automated Deployment
```cmd
npm run deploy
```

This single command will:
1. ✅ **Install dependencies** (Node.js & Electron Builder)
2. ✅ **Bundle Python environment** (copy .venv and ML models)
3. ✅ **Fix all paths** (relative paths for bundled distribution)
4. ✅ **Build Electron app** (compile JavaScript, package resources)
5. ✅ **Create Windows installer** (NSIS installer with shortcuts)
6. ✅ **Upload to GitHub** (create release and upload installer)
7. ✅ **Generate download link** (public HTTPS link for end users)

**Expected time:** 5-10 minutes (depending on internet speed)

---

## 📦 WHAT GETS PACKAGED

Your installer includes **everything needed** to run the application:

### Application Components
- ✅ Electron desktop app (UI, logic, IPC handlers)
- ✅ Python runtime (entire .venv with interpreter)
- ✅ AI models (8 .joblib files, ~50 MB)
- ✅ Python scripts (pipeline.py, feature_engineering.py, etc.)
- ✅ Sample data (sample-battery-data.csv)
- ✅ BatteryAgent with memory system
- ✅ Chart.js visualization library

### What Users Get
- **Installer size:** ~150-200 MB
- **Installed size:** ~400-500 MB
- **Installation time:** ~1-2 minutes
- **No dependencies required:** Everything is bundled
- **Fully offline:** No internet needed after download

---

## 🔧 MANUAL STEP-BY-STEP (Alternative)

If you prefer to run each step manually:

### 1. Package Application
```cmd
npm run package
```
This creates the installer in `dist/` directory.

### 2. Upload to GitHub
```cmd
npm run release
```
This uploads the installer and generates download link.

### 3. Find Your Download Link
After successful upload, you'll see:
```
🔗 Direct Installer Link:
   https://github.com/YOUR-USERNAME/battery-health-prediction/releases/download/v1.0.0/Battery-Health-Prediction-Setup-1.0.0.exe
```

Share this link with users!

---

## 📊 BUILD OUTPUT

After running `npm run deploy`, you'll find:

```
dist/
├── Battery-Health-Prediction-Setup-1.0.0.exe   ← Windows installer (share this!)
├── win-unpacked/                                ← Portable version (optional)
│   ├── Battery Health Prediction.exe
│   ├── resources/
│   │   ├── app.asar                            ← Packaged Electron app
│   │   ├── .venv/                              ← Bundled Python environment
│   │   └── models/                             ← AI models (.joblib files)
│   └── [Electron runtime files]
└── latest.yml                                   ← Auto-update metadata
```

---

## 🚀 DISTRIBUTION OPTIONS

### Option 1: GitHub Releases (Recommended)
✅ **Automated** with `npm run release`
✅ Free for public repositories
✅ Professional release page
✅ Version management
✅ Download statistics

**Download link format:**
```
https://github.com/{owner}/{repo}/releases/download/v{version}/{installer-name}.exe
```

### Option 2: Manual Cloud Storage

If you prefer other platforms:

#### Google Drive
1. Upload installer to Google Drive
2. Right-click → Get link
3. Set to "Anyone with the link"
4. Share the link

#### Dropbox
1. Upload installer to Dropbox
2. Get shareable link
3. Change `?dl=0` to `?dl=1` for direct download

#### AWS S3
1. Create S3 bucket (public-read)
2. Upload installer
3. Get object URL
4. Share: `https://bucket.s3.region.amazonaws.com/installer.exe`

---

## 🧪 TESTING THE INSTALLER

### Automated Testing
After building, test the installer:

```cmd
# Install to temporary directory
dist\Battery-Health-Prediction-Setup-1.0.0.exe /S /D=C:\Temp\BatteryTest

# Run the installed app
C:\Temp\BatteryTest\Battery Health Prediction.exe

# Verify predictions work (should output SOH and RUL)
```

### Manual Testing Checklist
1. ✅ **Install:** Run the installer on a clean Windows machine
2. ✅ **Launch:** Open application from Desktop or Start Menu
3. ✅ **Load Data:** Import `sample-battery-data.csv`
4. ✅ **Predict:** Click "Predict Battery Health"
5. ✅ **Verify Output:**
   - SOH: ~80%
   - RUL: ~41 cycles
   - Charts display correctly
6. ✅ **Agent Features:** Check memory stats, recommendations
7. ✅ **Uninstall:** Remove via Windows Settings → Apps

---

## 🔍 TROUBLESHOOTING

### Problem: "GITHUB_TOKEN not set"
**Solution:**
```cmd
set GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
Make sure to use your actual token from https://github.com/settings/tokens

### Problem: "dist/ directory not found"
**Solution:** Run packaging first:
```cmd
npm run package
```

### Problem: "electron-builder command not found"
**Solution:** Install dependencies:
```cmd
npm install
```

### Problem: "Python not found" (after installation)
**Cause:** Path detection failed in bundled app
**Solution:** Check `predictionService.js` lines 29-48 for bundled path detection

### Problem: Upload fails with "403 Forbidden"
**Causes:**
1. Token doesn't have `repo` scope
2. Repository doesn't exist
3. Token expired

**Solution:** Generate new token with correct permissions

### Problem: Installer doesn't run on Windows
**Causes:**
1. Windows SmartScreen blocking unknown publisher
2. Antivirus software blocking

**Solution:** Users should:
1. Click "More info" on SmartScreen
2. Click "Run anyway"
3. Or: Code sign the installer (requires certificate, ~$200/year)

---

## 📈 VERSION MANAGEMENT

### Updating Version Number
Edit `package.json`:
```json
{
  "version": "1.1.0"
}
```

Then rebuild:
```cmd
npm run deploy
```

This creates a new release: `v1.1.0`

### Semantic Versioning
- **Major (1.0.0 → 2.0.0):** Breaking changes
- **Minor (1.0.0 → 1.1.0):** New features, backward compatible
- **Patch (1.0.0 → 1.0.1):** Bug fixes

---

## 🎨 CUSTOMIZATION

### Change App Icon
1. Create icons:
   - Windows: `build-resources/icon.ico` (256x256)
   - macOS: `build-resources/icon.icns` (512x512)
2. Use online tools: https://cloudconvert.com/png-to-ico

### Change Installer Name
Edit `package.json`:
```json
"build": {
  "productName": "My Custom Name"
}
```

### Change Installer Behavior
Edit NSIS options in `package.json`:
```json
"win": {
  "target": "nsis",
  "nsis": {
    "oneClick": false,          // Show installation wizard
    "allowToChangeInstallationDirectory": true,
    "createDesktopShortcut": true,
    "createStartMenuShortcut": true
  }
}
```

---

## 📚 ADVANCED: CODE SIGNING

For production releases, consider code signing to avoid Windows SmartScreen warnings.

### Requirements
1. **Code Signing Certificate** (~$200-500/year)
   - Providers: DigiCert, Sectigo, GlobalSign
2. **Configure electron-builder:**

```json
"win": {
  "certificateFile": "path/to/certificate.pfx",
  "certificatePassword": "your_password",
  "signAndEditExecutable": true
}
```

### Benefits
- ✅ No SmartScreen warnings
- ✅ Professional appearance
- ✅ User trust
- ✅ Enterprise deployment ready

---

## 🌐 MULTI-PLATFORM BUILDS

Currently configured for **Windows only**. To support macOS:

### macOS Build (requires Mac hardware)
```cmd
npm run build:mac
```

Creates `.dmg` installer for macOS.

### Linux Build
```cmd
npm run build:linux
```

Creates `.AppImage` for Linux.

### Build All Platforms (on Mac)
```cmd
npm run build:all
```

**Note:** Windows .exe can only be built on Windows (code signing). macOS .dmg requires macOS.

---

## ✅ DEPLOYMENT CHECKLIST

Before sharing with users:

- [ ] Tested installer on clean Windows 10/11 machine
- [ ] Verified predictions work with sample data
- [ ] Checked all visualizations display correctly
- [ ] Tested memory stats and agent features
- [ ] Verified uninstaller removes all files
- [ ] Updated version number in package.json
- [ ] Added release notes to GitHub release
- [ ] Tested download link (public access)
- [ ] Created user documentation (USER_GUIDE.md)
- [ ] Considered code signing (for production)

---

## 🎯 FINAL RESULT

After running `npm run deploy`, you get:

1. **Installer File:**
   ```
   Battery-Health-Prediction-Setup-1.0.0.exe (150-200 MB)
   ```

2. **Download Link:**
   ```
   https://github.com/YOUR-USERNAME/battery-health-prediction/releases/latest
   ```

3. **User Instructions:** Share this:
   ```
   1. Download Battery-Health-Prediction-Setup-1.0.0.exe
   2. Run the installer
   3. Launch "Battery Health Prediction" from your desktop
   4. Import battery data CSV file
   5. Click "Predict Battery Health"
   ```

**That's it!** Your AI-powered desktop application is now ready for distribution! 🚀

---

## 📞 SUPPORT

For issues during deployment:
1. Check `TROUBLESHOOTING` section above
2. Review build logs in console output
3. Check `dist/` directory for generated files
4. Verify GitHub token permissions

**Happy Deploying!** 🎉
