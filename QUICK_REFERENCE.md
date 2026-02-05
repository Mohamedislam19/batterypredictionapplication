# Battery Health Prediction System - Quick Reference

## Launch Application
```bash
npm start
```

## Upload File
1. Drag CSV file to upload area, OR
2. Click "Select Battery Record File"

## CSV Format
```csv
cycle,voltage,current,temperature,capacity
1,4.185,1.485,24.3,1.982
2,4.182,1.482,24.5,1.981
...
```

## Key Metrics

| Metric | Description | Unit |
|--------|-------------|------|
| SoH | State of Health | % |
| RUL | Remaining Useful Life | cycles |
| Initial Capacity | Starting battery capacity | Ah |
| Final Capacity | Current battery capacity | Ah |
| Avg Temp | Average operating temperature | °C |

## Status Indicators

| Status | SoH Range | Color |
|--------|-----------|-------|
| NOMINAL | ≥ 90% | Blue |
| DEGRADED | 80-90% | Amber |
| CRITICAL | < 80% | Red |

## Keyboard Shortcuts
- Click upload area or button to select file
- Tab navigation through interface
- Focus indicators for accessibility

## Chart Legend
- **Blue Solid Line**: Historical observed SoH data
- **Amber Dashed Line**: Projected degradation trend
- **Hover**: View precise values at any point

## Interpretation Insights
The application automatically generates:
- Degradation pattern analysis
- End-of-life projections (80% SoH threshold)
- Temperature impact assessment
- Total capacity fade calculations

## Troubleshooting
- **File not loading**: Ensure .csv extension
- **No results**: Check CSV has numeric data
- **Chart blank**: Verify sufficient data points (10+ recommended)

## Sample Data
Use `sample-battery-data.csv` included in project directory for testing

## Support Files
- `README.md` - Project overview
- `USER_GUIDE.md` - Detailed usage instructions
- `TECHNICAL_DOCS.md` - Architecture and development guide
