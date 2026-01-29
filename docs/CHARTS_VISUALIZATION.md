# Charts & Visualization

**Version:** 0.3.5f (Package 3.9a, Stage 7.7b.8.2)

## Overview

The Charts & Visualization system provides interactive data visualization for historical monitoring data using PyQtGraph.

## Components

### 1. ChartWidget

**Purpose:** Base widget for creating various chart types.

**Location:** `src/ui/widgets/chart_widget.py`

**Features:**
- Line charts for time series
- Bar charts for comparisons
- Pie charts for distributions
- Interactive zoom and pan
- Export to image
- Real-time updates

### 2. HistoricalDataViewer

**Purpose:** Complete visualization interface for historical monitoring data.

**Location:** `src/ui/widgets/historical_data_viewer.py`

**Features:**
- Multiple chart views
- Time range selection
- Component filtering
- Auto-refresh
- Statistics display

## Dependencies

### Required:
```bash
pip install pyqtgraph
```

### Optional (for better performance):
```bash
pip install numpy
```

## Usage

### Basic ChartWidget Usage

#### Line Chart

```python
from ui.widgets.chart_widget import LineChartWidget

# Create line chart
chart = LineChartWidget()

# Set data
x_data = [1, 2, 3, 4, 5]
y_data = [10, 20, 15, 25, 30]
chart.set_data(x_data, y_data)

# Add single point
chart.add_data_point(6, 35)

# Update all data
new_x = [1, 2, 3, 4, 5, 6, 7]
new_y = [12, 22, 17, 27, 32, 37, 42]
chart.update_data(new_x, new_y)

# Clear
chart.clear()
```

#### Bar Chart

```python
from ui.widgets.chart_widget import BarChartWidget

# Create bar chart
chart = BarChartWidget()

# Set data with labels
x_data = list(range(5))
y_data = [10, 25, 15, 30, 20]
labels = ['Component A', 'Component B', 'Component C', 'Component D', 'Component E']

chart.set_data(x_data, y_data, labels)
```

#### Pie Chart

```python
from ui.widgets.chart_widget import PieChartWidget

# Create pie chart
chart = PieChartWidget()

# Set data with labels
values = [30, 20, 25, 15, 10]
labels = ['Success', 'Failed', 'In Progress', 'Pending', 'Cancelled']

chart.set_data([], values, labels)  # x_data not used for pie charts
```

### HistoricalDataViewer Usage

#### Basic Setup

```python
from ui.widgets.historical_data_viewer import HistoricalDataViewer
from core.historical_data_store import HistoricalDataStore, DataRetentionPolicy

# Create historical store
store = HistoricalDataStore(
    db_path="data/monitoring_history.db",
    retention_policy=DataRetentionPolicy.DAYS_30
)

# Create viewer
viewer = HistoricalDataViewer()
viewer.set_historical_store(store)

# Show widget
viewer.show()
```

#### Integration with Main Window

```python
from PyQt6.QtWidgets import QMainWindow, QTabWidget
from ui.widgets.historical_data_viewer import HistoricalDataViewer

class MainWindow(QMainWindow):
    def __init__(self, historical_store):
        super().__init__()
        
        # Create tabs
        tabs = QTabWidget()
        
        # Add historical data viewer
        self.history_viewer = HistoricalDataViewer()
        self.history_viewer.set_historical_store(historical_store)
        tabs.addTab(self.history_viewer, "History")
        
        self.setCentralWidget(tabs)
```

### Programmatic Data Refresh

```python
# Manual refresh
viewer.refresh_data()

# Enable auto-refresh
viewer.auto_refresh_checkbox.setChecked(True)

# Disable auto-refresh
viewer.auto_refresh_checkbox.setChecked(False)
```

### Time Range Selection

```python
# Set time range
viewer.time_range_combo.setCurrentText("Last Hour")
viewer.time_range_combo.setCurrentText("Last 24 Hours")
viewer.time_range_combo.setCurrentText("Last 7 Days")

# Custom time range
from PyQt6.QtCore import QDateTime

viewer.time_range_combo.setCurrentText("Custom")
viewer.start_time_edit.setDateTime(QDateTime.currentDateTime().addDays(-7))
viewer.end_time_edit.setDateTime(QDateTime.currentDateTime())
viewer.refresh_data()
```

### Component Filtering

```python
# Filter by component
viewer.component_combo.setCurrentText("PerformanceMonitor")
viewer.refresh_data()

# Show all components
viewer.component_combo.setCurrentText("All Components")
viewer.refresh_data()
```

## Chart Types

### Line Chart

**Best for:**
- Time series data
- Trends over time
- Continuous data

**Features:**
- Interactive zoom/pan
- Auto-scaling axes
- Grid lines
- Data point markers

**Example:**
```python
chart = LineChartWidget()

# Time series data
timestamps = [1609459200, 1609545600, 1609632000]  # Unix timestamps
values = [100, 105, 103]

chart.set_data(timestamps, values)
```

### Bar Chart

**Best for:**
- Comparisons between categories
- Discrete data
- Rankings

**Features:**
- Automatic bar width
- Category labels
- Color coding

**Example:**
```python
chart = BarChartWidget()

# Component error counts
components = ['CPU', 'GPU', 'Memory', 'Disk', 'Network']
error_counts = [5, 12, 3, 8, 2]

chart.set_data(
    list(range(len(components))),
    error_counts,
    components
)
```

### Pie Chart

**Best for:**
- Percentage distributions
- Part-to-whole relationships
- Category proportions

**Features:**
- Auto-calculated percentages
- Color-coded slices
- Labels with values

**Example:**
```python
chart = PieChartWidget()

# Recovery status distribution
statuses = ['Success', 'Failed', 'Partial']
counts = [85, 10, 5]

chart.set_data([], counts, statuses)
```

## Real-Time Updates

### Continuous Data Stream

```python
from PyQt6.QtCore import QTimer

class RealTimeChart(QWidget):
    def __init__(self):
        super().__init__()
        
        self.chart = LineChartWidget()
        self.data_x = []
        self.data_y = []
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chart)
        self.timer.start(1000)  # Update every second
    
    def update_chart(self):
        # Get new data point
        new_x = time.time()
        new_y = get_current_value()  # Your data source
        
        # Add to data
        self.data_x.append(new_x)
        self.data_y.append(new_y)
        
        # Keep last 60 points
        if len(self.data_x) > 60:
            self.data_x = self.data_x[-60:]
            self.data_y = self.data_y[-60:]
        
        # Update chart
        self.chart.update_data(self.data_x, self.data_y)
```

### Periodic Updates

```python
# Update every 30 seconds
self.update_timer = QTimer()
self.update_timer.timeout.connect(self.refresh_all_charts)
self.update_timer.start(30000)

def refresh_all_charts(self):
    start_time, end_time = self.get_time_range()
    
    # Update health chart
    health_data = self.store.query_health_history(start_time, end_time)
    self.update_health_chart(health_data)
    
    # Update error chart
    error_data = self.store.query_errors(start_time, end_time)
    self.update_error_chart(error_data)
```

## Export Functionality

### Export Chart as Image

```python
# Programmatically export
from PyQt6.QtWidgets import QFileDialog

def export_chart(chart_widget, filename=None):
    if not filename:
        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Export Chart",
            f"chart_{int(time.time())}.png",
            "PNG Files (*.png);;JPEG Files (*.jpg)"
        )
    
    if filename:
        # For PyQtGraph charts
        import pyqtgraph.exporters as exporters
        exporter = exporters.ImageExporter(chart_widget.plot_widget.plotItem)
        exporter.export(filename)
```

### Export All Charts

```python
def export_all_charts(viewer, directory="exports"):
    import os
    os.makedirs(directory, exist_ok=True)
    
    timestamp = int(time.time())
    
    # Export health chart
    export_chart(
        viewer.health_chart,
        f"{directory}/health_{timestamp}.png"
    )
    
    # Export error chart
    export_chart(
        viewer.error_chart,
        f"{directory}/errors_{timestamp}.png"
    )
    
    # Export recovery chart
    export_chart(
        viewer.recovery_chart,
        f"{directory}/recovery_{timestamp}.png"
    )
```

## Customization

### Custom Colors

```python
chart = LineChartWidget()

# Set custom colors
chart._colors = [
    '#FF5733',  # Red
    '#33FF57',  # Green
    '#3357FF',  # Blue
    '#FF33F5',  # Magenta
    '#F5FF33',  # Yellow
]

chart.set_data(x_data, y_data)
```

### Custom Chart Styling

```python
import pyqtgraph as pg

# Configure PyQtGraph globally
pg.setConfigOptions(
    antialias=True,
    background='w',  # White background
    foreground='k'   # Black foreground
)

# Custom pen for line chart
pen = pg.mkPen(color='#FF5733', width=3, style=Qt.PenStyle.DashLine)
chart.plot_widget.plot(x_data, y_data, pen=pen)
```

### Custom Axes Labels

```python
chart = LineChartWidget()

# Set custom labels
chart.plot_widget.setLabel('bottom', 'Time (seconds)', units='s')
chart.plot_widget.setLabel('left', 'CPU Usage', units='%')
chart.plot_widget.setTitle('CPU Usage Over Time')
```

## Performance Tips

### Large Datasets

```python
# Downsample large datasets
def downsample(x_data, y_data, max_points=1000):
    if len(x_data) <= max_points:
        return x_data, y_data
    
    step = len(x_data) // max_points
    return x_data[::step], y_data[::step]

# Use downsampled data
x_down, y_down = downsample(x_data, y_data)
chart.set_data(x_down, y_down)
```

### Update Optimization

```python
# Batch updates
class OptimizedChart:
    def __init__(self):
        self.chart = LineChartWidget()
        self.pending_updates = []
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.flush_updates)
        self.update_timer.start(100)  # Update every 100ms
    
    def add_point(self, x, y):
        self.pending_updates.append((x, y))
    
    def flush_updates(self):
        if self.pending_updates:
            for x, y in self.pending_updates:
                self.chart.add_data_point(x, y)
            self.pending_updates.clear()
```

## Integration Examples

### Complete Monitoring Dashboard

```python
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from ui.widgets.historical_data_viewer import HistoricalDataViewer
from core.historical_data_store import HistoricalDataStore
from core.data_aggregator import DataAggregator, AggregationConfig

class MonitoringDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create historical store
        self.store = HistoricalDataStore(
            "data/monitoring.db",
            DataRetentionPolicy.DAYS_30
        )
        
        # Create aggregator
        self.aggregator = DataAggregator(
            self.store,
            config=AggregationConfig(
                collection_interval=60.0,
                aggregation_interval=3600.0
            )
        )
        self.aggregator.start_collection()
        
        # Create viewer
        self.viewer = HistoricalDataViewer()
        self.viewer.set_historical_store(self.store)
        
        # Set as central widget
        self.setCentralWidget(self.viewer)
        
        self.setWindowTitle("Monitoring Dashboard")
        self.resize(1200, 800)
    
    def closeEvent(self, event):
        # Stop aggregator on close
        self.aggregator.stop_collection()
        event.accept()
```

## Troubleshooting

### PyQtGraph Not Available

```python
# Check availability
from ui.widgets.chart_widget import PYQTGRAPH_AVAILABLE

if not PYQTGRAPH_AVAILABLE:
    print("PyQtGraph not installed")
    print("Install with: pip install pyqtgraph")
```

### Charts Not Updating

```python
# Ensure data refresh is called
viewer.refresh_data()

# Check auto-refresh is enabled
if viewer.auto_refresh_checkbox.isChecked():
    print("Auto-refresh is enabled")

# Check store is set
if viewer._historical_store:
    print("Store is set")
else:
    print("ERROR: Store not set!")
```

### Empty Charts

```python
# Check data exists in store
start_time = time.time() - 86400
end_time = time.time()

records = store.query_health_history(start_time, end_time)
print(f"Found {len(records)} health records")

errors = store.query_errors(start_time, end_time)
print(f"Found {len(errors)} error records")
```

## See Also

- [Historical Data Documentation](HISTORICAL_DATA.md)
- [System Health Monitor Documentation](SYSTEM_HEALTH.md)
- [Stage 7.7b.8.2 Plan](STAGE_7.7b.8_PLAN.md)
