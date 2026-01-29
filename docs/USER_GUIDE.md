# PartMart Boost - User Guide

**Version:** 0.3.5g (Package 3.9a)

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost

# Install dependencies
pip install PyQt6 pyqtgraph

# Run
python src/main.py
```

### First Launch

1. **Check dependencies**
   ```bash
   python src/main.py --check
   ```

2. **Launch application**
   ```bash
   python src/main.py
   ```

3. **Click "Start Monitoring"** in main window

## Main Window

### Status Tab
- View system status
- Monitor components health
- See error count
- Check uptime

### History Tab
- View historical data
- Interactive charts
- Select time range
- Filter by component

### Settings Tab
- Configure monitoring
- Adjust intervals
- Set retention periods
- Save preferences

## Configuration

Settings stored in `config/settings.json`

### Key Settings

- **Monitoring interval:** How often to check (default: 5s)
- **Auto-recovery:** Enable automatic fixes (default: on)
- **Data retention:** How long to keep history (default: 30 days)
- **Collection interval:** Data collection frequency (default: 60s)

## Troubleshooting

### Program won't start
```bash
# Check dependencies
python src/main.py --check

# Install missing packages
pip install PyQt6 pyqtgraph
```

### Charts not showing
- Ensure PyQtGraph is installed
- Check historical data is enabled
- Wait for data collection (1 minute)

### Performance issues
- Increase monitoring interval in settings
- Reduce data retention period
- Close unused tabs

## Command Line

```bash
python src/main.py              # Full GUI
python src/main.py --check      # Check dependencies  
python src/main.py --test       # Run tests
python src/main.py --no-gui     # Console mode
python src/main.py --version    # Show version
```

## Tips

- Start monitoring before launching games
- Check History tab for performance trends
- Adjust settings for your system
- Enable auto-recovery for hands-free operation

---

For technical details, see [Developer Guide](DEVELOPER_GUIDE.md)
