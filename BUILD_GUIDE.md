# 🏗️ CROSS-PLATFORM BUILD GUIDE
## How to Build for macOS and Linux

---

## 📦 CURRENT STATUS

✅ **Windows:** Built and ready (`Battery Health Prediction Setup 1.0.0.exe` - 75.7 MB)  
⏳ **macOS:** Not built yet (see instructions below)  
⏳ **Linux:** Not built yet (see instructions below)

---

## 🍎 BUILD FOR macOS

### Prerequisites:
- **You MUST have a macOS computer to build .dmg files**
- Cannot build macOS apps on Windows/Linux
- Node.js and npm installed on macOS

### Steps on macOS:

```bash
# 1. Clone/copy your project to macOS machine
# 2. Open Terminal

# 3. Install dependencies
cd /path/to/battery-health-pred-ui
npm install

# 4. Build for macOS
npm run build:mac

# This will create:
# dist/Battery Health Prediction-1.0.0.dmg (~80-90 MB)
# dist/Battery Health Prediction-1.0.0-mac.zip
```

### Troubleshooting macOS Build:

**Error: "Code signing required"**
```bash
# Disable code signing for local builds:
# Edit package.json, add to "build" section:
"mac": {
  "identity": null,
  "target": "dmg"
}
```

**Error: "Cannot find Python"**
```bash
# Install Python on macOS:
brew install python@3.10

# Or download from python.org
```

---

## 🐧 BUILD FOR LINUX

### Option A: Build on Linux Machine

**Requirements:**
- Ubuntu 20.04+ / Debian 11+ / Fedora 38+
- Node.js and npm

```bash
# 1. On Linux machine
cd /path/to/battery-health-pred-ui
npm install

# 2. Install required tools
sudo apt-get install -y rpm  # For .rpm packages (optional)

# 3. Build for Linux (creates AppImage + .deb)
npm run build:linux

# This will create:
# dist/Battery-Health-Prediction-1.0.0.AppImage (~85 MB)
# dist/battery-health-prediction_1.0.0_amd64.deb (~82 MB)
```

### Option B: Build from Windows (Cross-compile)

**Using Docker:**

```powershell
# 1. Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop

# 2. Create build script
# Create file: build-linux.sh
```

```bash
#!/bin/bash
npm install
npm run build:linux
```

```powershell
# 3. Run Docker container
docker run --rm -v ${PWD}:/project electronuserland/builder:wine /bin/bash -c "cd /project && chmod +x build-linux.sh && ./build-linux.sh"
```

**Pros:** ✅ Build from Windows  
**Cons:** ❌ Complex setup, ❌ Large Docker image download

---

## 🔧 UPDATE PACKAGE.JSON FOR ALL PLATFORMS

Add these build targets to your `package.json`:

```json
{
  "build": {
    "appId": "com.batteryhealth.prediction",
    "productName": "Battery Health Prediction",
    "directories": {
      "output": "dist",
      "buildResources": "build-resources"
    },
    "win": {
      "target": ["nsis"],
      "icon": "build-resources/icon.ico"
    },
    "mac": {
      "target": ["dmg"],
      "icon": "build-resources/icon.icns",
      "category": "public.app-category.utilities"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "icon": "build-resources/icon.png",
      "category": "Utility"
    }
  }
}
```

---

## 🎨 CREATE ICONS FOR EACH PLATFORM

### Required Icon Sizes:

- **Windows:** `icon.ico` (256x256px)
- **macOS:** `icon.icns` (512x512px)
- **Linux:** `icon.png` (512x512px)

### Free Tools to Create Icons:

1. **Online:** https://cloudconvert.com/png-to-ico
   - Upload your logo PNG
   - Convert to .ico, .icns

2. **Windows:** Paint.NET / GIMP
   - Resize to 512x512
   - Export as PNG/ICO

3. **macOS:** Icon Composer (Xcode)
   - Create .icns from PNG

4. **Linux:** ImageMagick
   ```bash
   convert logo.png -resize 512x512 icon.png
   ```

### Recommended Icon:
Create a simple battery icon with:
- ⚡ Lightning bolt
- 🔋 Battery outline
- Health indicator (green/yellow/red)
- Text: "BH" or "Battery Health"

---

## 📊 EXPECTED FILE SIZES

| Platform | Format | Estimated Size |
|----------|--------|----------------|
| Windows | .exe (NSIS) | ~75-80 MB ✅ |
| macOS | .dmg | ~85-95 MB |
| Linux | .AppImage | ~85-90 MB |
| Linux | .deb | ~80-85 MB |

**Why so large?**
- Embedded Python runtime
- ML models (scikit-learn)
- NumPy/Pandas libraries
- Electron framework
- Test data files

---

## 🚀 AUTOMATED BUILD SCRIPT (All Platforms)

Create `build-all.ps1` for Windows PowerShell:

```powershell
# Build for all platforms (requires macOS and Linux machines)

Write-Host "Building Battery Health Prediction for all platforms..." -ForegroundColor Cyan

# Windows (run on Windows)
Write-Host "Building Windows..." -ForegroundColor Yellow
npm run build

# macOS (requires macOS machine)
Write-Host "⚠️  macOS build requires macOS computer" -ForegroundColor Red
Write-Host "Run 'npm run build:mac' on macOS" -ForegroundColor Gray

# Linux (can use Docker on Windows)
Write-Host "⚠️  Linux build requires Linux or Docker" -ForegroundColor Red
Write-Host "Run 'npm run build:linux' on Linux or use Docker" -ForegroundColor Gray

Write-Host "`n✅ Windows build complete!" -ForegroundColor Green
Write-Host "📦 Check dist/ folder" -ForegroundColor Cyan
```

---

## 🌐 ALTERNATIVE: Use GitHub Actions (FREE CI/CD)

**Build all platforms automatically on GitHub:**

Create `.github/workflows/build.yml`:

```yaml
name: Build All Platforms

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build
      - uses: actions/upload-artifact@v3
        with:
          name: windows-installer
          path: dist/*.exe

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build:mac
      - uses: actions/upload-artifact@v3
        with:
          name: macos-installer
          path: dist/*.dmg

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build:linux
      - uses: actions/upload-artifact@v3
        with:
          name: linux-installers
          path: |
            dist/*.AppImage
            dist/*.deb
```

**How to use:**
1. Create this file in your repo
2. Push to GitHub
3. Create tag: `git tag v1.0.0 && git push --tags`
4. GitHub builds all platforms automatically (FREE)
5. Download from Actions tab

**Pros:** ✅ Automatic builds, ✅ No macOS machine needed, ✅ Free on public repos  
**Cons:** ❌ Requires GitHub, ❌ Build time ~15-20 minutes

---

## 📝 UPDATE DOWNLOAD PAGE AFTER BUILDING

After you build macOS and Linux versions:

1. **Upload to hosting** (GitHub Releases recommended)
2. **Update download-page.html:**

```html
<!-- Replace coming-soon buttons: -->

<!-- macOS -->
<a href="https://github.com/USER/REPO/releases/download/v1.0.0/Battery-Health-Prediction-1.0.0.dmg" class="download-btn">
    🍎 macOS
    <br><small>v1.0.0.dmg - 90 MB</small>
</a>

<!-- Linux AppImage -->
<a href="https://github.com/USER/REPO/releases/download/v1.0.0/Battery-Health-Prediction-1.0.0.AppImage" class="download-btn">
    🐧 Linux (AppImage)
    <br><small>v1.0.0 - 85 MB</small>
</a>

<!-- Linux .deb -->
<a href="https://github.com/USER/REPO/releases/download/v1.0.0/battery-health-prediction_1.0.0_amd64.deb" class="download-btn">
    🐧 Linux (.deb)
    <br><small>Ubuntu/Debian - 82 MB</small>
</a>
```

3. **Update file info section:**

```html
<div class="file-info">
    <strong>Windows:</strong> Battery Health Prediction Setup 1.0.0.exe | 75.7 MB<br>
    <strong>macOS:</strong> Battery Health Prediction 1.0.0.dmg | 90 MB<br>
    <strong>Linux (AppImage):</strong> Battery-Health-Prediction-1.0.0.AppImage | 85 MB<br>
    <strong>Linux (.deb):</strong> battery-health-prediction_1.0.0_amd64.deb | 82 MB
</div>
```

---

## 🎯 RECOMMENDED WORKFLOW

### For Solo Developer (No macOS access):

**Right now:**
1. ✅ Release Windows version only
2. Update download page: "macOS & Linux coming soon"
3. Share with Windows users

**In future:**
1. Get access to macOS (borrow friend's Mac, use VM, or GitHub Actions)
2. Build macOS/Linux versions
3. Update download page with new links
4. Announce multi-platform support

### For Team/Access to Multiple OS:

**Week 1:**
1. Build Windows ✅
2. Build macOS on Mac
3. Build Linux on Ubuntu

**Week 1 (continued):**
4. Test all installers
5. Upload to GitHub Releases
6. Update download page
7. Launch!

---

## ❓ FAQ

**Q: Can I build macOS app without a Mac?**  
A: Technically yes (using Hackintosh, Docker, VMs), but not recommended. Easier to use GitHub Actions or borrow a Mac for 30 minutes.

**Q: Which Linux format should I provide?**  
A: Provide both:
- `.AppImage` → Works on all distros (universal)
- `.deb` → Better integration on Ubuntu/Debian (most popular)

**Q: Do I need to code-sign?**  
A: No for free distribution. But if you plan to sell/distribute widely:
- Windows: Optional (reduces SmartScreen warnings, costs $200-400/year)
- macOS: Almost required (costs $99/year for Apple Developer)
- Linux: Not needed

**Q: File size too big?**  
A: This is normal for Electron apps with Python. To reduce:
- Remove unused Python packages
- Compress with NSIS/7-Zip (already done)
- Remove test data from dist (keep only essential files)

---

## 📞 HELP & RESOURCES

- **Electron Builder Docs:** https://www.electron.build/
- **GitHub Actions Free CI:** https://github.com/features/actions
- **Icon Tools:** https://cloudconvert.com/png-to-ico
- **Code Signing Info:** https://www.electron.build/code-signing

---

## ✅ CHECKLIST FOR MULTI-PLATFORM RELEASE

- [ ] Build Windows .exe ✅ (Done!)
- [ ] Build macOS .dmg
- [ ] Build Linux .AppImage
- [ ] Build Linux .deb
- [ ] Create icons for all platforms
- [ ] Test each installer on target OS
- [ ] Upload to GitHub Releases
- [ ] Update download-page.html with real links
- [ ] Update file sizes in HTML
- [ ] Deploy HTML to Netlify/Vercel
- [ ] Test download links
- [ ] Announce release!

---

**Current Status:** Windows ready! macOS and Linux pending.  
**Recommendation:** Release Windows now, add other platforms when ready.

---

Made with ❤️ for Battery Health Prediction System
