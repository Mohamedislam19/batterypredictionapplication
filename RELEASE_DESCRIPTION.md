## Battery Health Prediction System v1.0.0

NASA-trained ML models for Li-ion battery health analysis.

### 🚀 Features

- **SOH (State of Health) Prediction** - LogisticRegression model
- **RUL (Remaining Useful Life) Prediction** - RandomForest model
- **ML Confidence Display** - See both model probabilities
- **Real-time Visualization** - Charts and graphs
- **BatteryAgent AI** - Intelligent decision system
- **No Dependencies Required** - Everything included in installer

### 📥 Installation

1. Download `Battery Health Prediction Setup 1.0.0.exe` below
2. Run the installer
3. Launch the app from Start Menu
4. Use the test CSV files on your Desktop

### 📊 What's Included

- Complete Windows application (75.7 MB)
- NASA-trained ML models (trained on 2247 battery samples)
- 27 engineered features per prediction
- Test battery data files
- Embedded Python runtime and dependencies

### 💻 System Requirements

- Windows 10/11 (64-bit)
- 4GB RAM minimum
- 500MB free disk space

### 🧪 Testing

Test files are copied to your Desktop after installation:
- `excellent_battery.csv` - High health battery
- `good_battery.csv` - Good condition
- `fair_battery.csv` - Moderate degradation
- `poor_battery.csv` - Significant degradation
- `critical_battery.csv` - Critical condition

Each file produces **different ML confidence scores** - proving the models work independently!

### 🔬 ML Model Details

- **SOH Model**: Logistic Regression
  - Classifies: Healthy vs Not-Healthy
  - Confidence shown in UI

- **RUL Model**: Random Forest Classifier
  - Classifies: Short vs Long remaining life
  - Confidence shown in UI

### 📝 Usage

1. Click "Upload Battery Data"
2. Select a CSV file with columns: `voltage`, `current`, `temperature`, `capacity`
3. View results:
   - SOH percentage + ML confidence
   - RUL cycles + ML confidence
   - Health state classification
   - Recommended actions

Press F12 to see detailed model outputs in console.

### 🔒 Privacy

All processing happens locally - no data sent to external servers.

### 📧 Support

Open an issue on GitHub for bugs or questions.

---

**Built with:** Electron, Python, scikit-learn, Chart.js  
**License:** MIT
