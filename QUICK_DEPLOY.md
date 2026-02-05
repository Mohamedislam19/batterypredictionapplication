# 🚀 QUICK DEPLOYMENT - Battery Health Prediction System

## ⚡ ONE-COMMAND DEPLOYMENT

### 1. Set GitHub Credentials (One-Time Setup)
```cmd
set GITHUB_TOKEN=your_github_token_here
set GITHUB_OWNER=your-github-username
set GITHUB_REPO=battery-health-prediction
```

### 2. Edit Configuration
Open `build-scripts/release.js` and change lines 26-27:
```javascript
owner: 'your-github-username',  // Your GitHub username
repo: 'battery-health-prediction'  // Your repository name
```

### 3. Deploy Everything
```cmd
npm run deploy
```

**This single command:**
- ✅ Installs all dependencies
- ✅ Bundles Python + AI models
- ✅ Creates Windows installer
- ✅ Uploads to GitHub Releases
- ✅ Generates public download link

**Time:** ~5-10 minutes

---

## 📦 WHAT YOU GET

**Installer:** `dist/Battery-Health-Prediction-Setup-1.0.0.exe` (~180 MB)

**Download Link:**
```
https://github.com/YOUR-USERNAME/battery-health-prediction/releases/download/v1.0.0/Battery-Health-Prediction-Setup-1.0.0.exe
```

Share this link with users - they can download and install immediately!

---

## 📋 REQUIREMENTS

Before running `npm run deploy`:

1. ✅ **Node.js installed** (verify: `node --version`)
2. ✅ **GitHub account created**
3. ✅ **GitHub repository created** for this project
4. ✅ **GitHub token generated** with `repo` scope
   - Get token: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scope: `repo`
   - Copy the token

---

## 🔧 MANUAL DEPLOYMENT (Alternative)

If you prefer step-by-step:

### Step 1: Package Application
```cmd
npm run package
```
Creates installer in `dist/` directory.

### Step 2: Upload to GitHub
```cmd
npm run release
```
Uploads installer and generates download link.

---

## 🧪 TEST THE INSTALLER

After deployment:

1. Download the installer from GitHub release
2. Run it on a Windows machine
3. Install the application
4. Launch "Battery Health Prediction"
5. Load `sample-battery-data.csv`
6. Click "Predict Battery Health"
7. Verify output: SOH ~80%, RUL ~41 cycles

---

## 📊 WHAT'S BUNDLED

Your installer includes **everything users need**:

- ✅ Desktop application (Electron UI)
- ✅ Python runtime (no installation needed)
- ✅ AI models (8 NASA-trained .joblib files)
- ✅ All dependencies (sklearn, pandas, numpy, joblib, Chart.js)
- ✅ Sample battery data
- ✅ BatteryAgent with memory system

**Users don't need:**
- ❌ Python installation
- ❌ pip packages
- ❌ Node.js
- ❌ Internet connection (after download)

**Fully offline, fully autonomous!**

---

## 🚨 TROUBLESHOOTING

### Error: "GITHUB_TOKEN not set"
```cmd
set GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### Error: "dist/ directory not found"
```cmd
npm run package
```

### Error: "electron-builder not found"
```cmd
npm install
```

### Error: Upload fails with 403
- Check token has `repo` scope
- Verify repository exists
- Confirm owner/repo names are correct

---

## ✅ SUCCESS INDICATORS

After `npm run deploy` completes, you should see:

```
=======================================================
✓ DEPLOYMENT COMPLETED SUCCESSFULLY!
=======================================================

📦 Download Link:
   https://github.com/your-username/battery-health-prediction/releases/tag/v1.0.0

🔗 Direct Installer Link:
   https://github.com/your-username/battery-health-prediction/releases/download/v1.0.0/Battery-Health-Prediction-Setup-1.0.0.exe

✓ Users can now download and install your application!
```

Copy the **Direct Installer Link** and share it with users!

---

## 📚 FULL DOCUMENTATION

For detailed information, see:
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete packaging & distribution guide
- **[USER_GUIDE.md](USER_GUIDE.md)** - End-user instructions
- **[TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)** - Architecture and implementation

---

## 🎯 NEXT STEPS

1. **Test the installer** on a clean Windows machine
2. **Share the download link** with your users
3. **Monitor GitHub releases** for download statistics
4. **Update version** in package.json for future releases
5. **Consider code signing** for production (removes SmartScreen warnings)

---

**Ready to deploy?** Run: `npm run deploy`

🚀 **Your AI-powered desktop application will be available for download in minutes!**
