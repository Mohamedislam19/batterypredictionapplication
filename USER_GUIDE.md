# Battery Health Prediction System - User Guide

## Overview

The Battery Health Prediction System is a professional desktop application designed for analyzing NASA lithium-ion battery datasets. It provides State of Health (SoH) predictions, Remaining Useful Life (RUL) estimates, and detailed degradation analysis.

## Getting Started

### Installation

1. Ensure Node.js (v16 or higher) is installed
2. Navigate to the project directory
3. Install dependencies:
   ```bash
   npm install
   ```

### Running the Application

```bash
npm start
```

For development mode with DevTools:
```bash
npm run dev
```

## Using the Application

### 1. File Upload

The application accepts CSV files containing battery historical data. You can:

- **Drag and drop** a CSV file onto the upload area
- **Click "Select Battery Record File"** to browse for a file

### 2. Required CSV Format

Your CSV file should contain columns for battery cycle data. Common column names include:

- `cycle` or `time` - Cycle number
- `capacity` or `ah` - Battery capacity in Ah
- `voltage` - Voltage in V (optional)
- `current` - Current in A (optional)
- `temperature` or `temp` - Temperature in °C (optional)

**Example CSV structure:**
```csv
cycle,voltage,current,temperature,capacity
1,4.185,1.485,24.3,1.982
2,4.182,1.482,24.5,1.981
3,4.179,1.479,24.7,1.980
...
```

A sample file `sample-battery-data.csv` is included in the project directory for testing.

### 3. Understanding the Results

Once a file is uploaded, the application displays:

#### Health Summary
- **State of Health (SoH %)**: Current battery health as a percentage
  - **Nominal** (green): SoH ≥ 90%
  - **Degraded** (amber): 80% ≤ SoH < 90%
  - **Critical** (red): SoH < 80%

- **Remaining Useful Life (RUL)**: Estimated cycles until 80% SoH threshold

#### Key Metrics
- Initial Capacity (Ah)
- Final Recorded Capacity (Ah)
- Average Operating Temperature (°C)

#### Degradation Analysis Chart
- Blue line: Observed historical SoH data
- Orange dashed line: Projected degradation trend
- Interactive hover tooltips for precise values

#### Analysis & Interpretation
Automated insights including:
- Degradation pattern assessment
- End-of-life projections
- Temperature impact analysis
- Total capacity fade metrics

## Technical Details

### Architecture
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Visualization**: Chart.js 4.4.1
- **Desktop Framework**: Electron 28.0.0

### Data Processing
The application currently uses a mock ML backend that:
1. Parses uploaded CSV files
2. Extracts battery metrics
3. Calculates SoH based on capacity degradation
4. Estimates RUL using linear degradation models
5. Generates interpretive insights

### Browser Compatibility
The application runs as a desktop app via Electron. It does not require a web browser.

## Troubleshooting

### CSV File Not Recognized
- Ensure the file has a `.csv` extension
- Check that the file contains header rows with column names
- Verify data is comma-separated

### No Results Displayed
- Check the browser console (F12) for errors
- Ensure the CSV file is not empty
- Verify at least one column contains numeric capacity or cycle data

### Chart Not Rendering
- Ensure Chart.js loaded correctly (check console)
- Verify sufficient data points (minimum 10 recommended)

## Future Enhancements

This is a reference implementation. Production deployments may include:
- Real ML model integration (TensorFlow.js, ONNX Runtime)
- Database connectivity for historical analysis
- Export functionality (PDF reports, data exports)
- Multi-battery comparison
- Advanced analytics (temperature correlation, charge rate analysis)
- Cloud deployment options

## Support

For issues or questions related to NASA battery datasets, refer to the NASA Prognostics Center of Excellence repository.

## License

MIT License - See LICENSE file for details
