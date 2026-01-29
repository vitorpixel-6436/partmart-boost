# PartMart Boost - Developer Guide

**Version:** 0.3.5g (Package 3.9a)

## Architecture

### Core Systems

```
SystemIntegratorFinal
    ├── ConfigManager           # Configuration
    ├── ErrorReporter           # Error tracking
    ├── SystemHealthMonitor     # Health monitoring
    ├── RecoveryCoordinator     # Auto-recovery
    ├── HistoricalDataStore     # Data storage
    └── DataAggregator          # Data collection
```

### Component Communication

1. **Health Monitor** checks components
2. **Error Reporter** logs issues
3. **Recovery Coordinator** applies fixes
4. **Data Aggregator** collects metrics
5. **Historical Store** saves data
6. **GUI** displays information

## Development Setup

```bash
# Clone
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost

# Install dev dependencies
pip install PyQt6 pyqtgraph pytest coverage

# Run tests
python src/main.py --test

# Run with coverage
coverage run -m pytest tests/
coverage report
```

## Project Structure

```
src/
├── core/              # Core systems
│   ├── config_manager.py
│   ├── error_reporter.py
│   ├── system_health_monitor.py
│   ├── recovery_coordinator.py
│   ├── historical_data_store.py
│   ├── data_aggregator.py
│   └── system_integrator_final.py
├── ui/                # User interface
│   ├── widgets/
│   └── main_window_complete.py
└── main.py           # Entry point

tests/                # Test suite
docs/                 # Documentation
config/               # Configuration files
data/                 # Data storage
```

## Adding Components

### 1. Create Component

```python
class MyComponent:
    def __init__(self):
        self.name = "MyComponent"
    
    def check_health(self) -> dict:
        return {
            'status': 'healthy',
            'message': 'OK'
        }
```

### 2. Register with Health Monitor

```python
health_monitor.register_component(my_component)
```

### 3. Add Tests

```python
class TestMyComponent(unittest.TestCase):
    def test_health_check(self):
        component = MyComponent()
        health = component.check_health()
        self.assertEqual(health['status'], 'healthy')
```

## API Reference

### ConfigManager

```python
from core.config_manager import get_config_manager

config = get_config_manager()
value = config.get('monitoring.check_interval')
config.set('ui.theme', 'dark')
config.save()
```

### SystemIntegratorFinal

```python
from core.system_integrator_final import SystemIntegratorFinal

integrator = SystemIntegratorFinal()
integrator.initialize()
integrator.start()
status = integrator.get_status()
integrator.stop()
```

### HistoricalDataStore

```python
from core.historical_data_store import HistoricalDataStore

store = HistoricalDataStore('data/history.db')
store.store_health_snapshot('Component', 'healthy', 'OK')
records = store.query_health_history(start_time, end_time)
```

## Testing

### Run All Tests
```bash
python src/main.py --test
```

### Run Specific Test
```bash
python -m unittest tests.test_config_manager
```

### Coverage
```bash
coverage run -m pytest tests/
coverage html
```

## Building

### Standalone Executable
```bash
pip install pyinstaller
pyinstaller --onefile --windowed src/main.py
```

### Distribution Package
```bash
python setup.py sdist bdist_wheel
```

## Contributing

1. Fork repository
2. Create feature branch
3. Add tests
4. Submit pull request

## Code Style

- Follow PEP 8
- Use type hints
- Document functions
- Write tests
- Keep functions small

---

For user documentation, see [User Guide](USER_GUIDE.md)
