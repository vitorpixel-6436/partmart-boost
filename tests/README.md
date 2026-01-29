# PartMart Boost Test Suite

**Version:** 0.3.5i (Package 3.9a, Stage 7.7a/7.7)

## Overview

Comprehensive test suite for PartMart Boost components.

## Running Tests

### Run All Tests

```bash
python tests/run_tests.py
```

### Verbose Output

```bash
python tests/run_tests.py -v
```

### Run Specific Test

```bash
python -m unittest tests.test_config_manager
python -m unittest tests.test_data_bus
python -m unittest tests.test_performance_history
```

### Run Single Test Method

```bash
python -m unittest tests.test_config_manager.TestConfigManager.test_get_default_value
```

## Test Coverage

### ConfigManager Tests (`test_config_manager.py`)

- ✅ Default values
- ✅ Get/Set operations
- ✅ Type validation
- ✅ Choice validation
- ✅ Range validation
- ✅ Subscriptions
- ✅ Wildcard subscriptions
- ✅ Save/Load
- ✅ Reset functionality
- ✅ Schema operations

### DataBus Tests (`test_data_bus.py`)

- ✅ Publish/Subscribe
- ✅ Multiple subscribers
- ✅ Wildcard subscriptions
- ✅ Message priority
- ✅ Unsubscribe
- ✅ Message history
- ✅ Statistics
- ✅ Clear history

### PerformanceHistory Tests (`test_performance_history.py`)

- ✅ Add snapshots
- ✅ Get latest
- ✅ Statistics calculation
- ✅ Trend detection
- ✅ Circular buffer
- ✅ Get recent
- ✅ Get all
- ✅ Clear history
- ✅ CSV export

### PerformanceAnalytics Tests (`test_performance_analytics.py`)

- ✅ Analysis with no data
- ✅ Normal load analysis
- ✅ CPU bottleneck detection
- ✅ GPU bottleneck detection
- ✅ RAM bottleneck detection
- ✅ Thermal throttling detection
- ✅ Performance scoring
- ✅ Efficiency calculation
- ✅ Recommendation generation
- ✅ Trend analysis
- ✅ Severity classification

### MonitoringIntegration Tests (`test_monitoring_integration.py`)

- ✅ Initialization
- ✅ Start/Stop
- ✅ History recording
- ✅ Analytics generation
- ✅ DataBus publishing
- ✅ Clear history

## Mock Objects

### Available Mocks (`mock_objects.py`)

- `MockPerformanceMonitor` - Mock performance monitor
- `MockDataBus` - Mock data bus
- `MockConfigManager` - Mock configuration manager
- `MockQtSignals` - Mock Qt signals

### Using Mocks

```python
from tests.mock_objects import MockPerformanceMonitor, MockDataBus

# Create mocks
monitor = MockPerformanceMonitor()
bus = MockDataBus()

# Set test data
monitor.set_metrics(cpu=60, gpu=70)

# Use in tests
integration = MonitoringIntegration(monitor=monitor, data_bus=bus)
```

## Writing New Tests

### Test Template

```python
import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from your_module import YourClass

class TestYourClass(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.obj = YourClass()
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    def test_something(self):
        """Test something"""
        result = self.obj.method()
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
```

## Test Best Practices

1. **One assertion per test** (when possible)
2. **Descriptive test names** (`test_what_when_expected`)
3. **Use setUp/tearDown** for common initialization
4. **Test edge cases** (empty input, None, extremes)
5. **Test error handling** (exceptions, invalid input)
6. **Mock external dependencies**
7. **Keep tests fast** (<1s per test)
8. **Tests should be independent**

## Continuous Integration

### GitHub Actions (future)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: python tests/run_tests.py
```

## Coverage Report (future)

```bash
# Install coverage
pip install coverage

# Run with coverage
coverage run tests/run_tests.py

# Generate report
coverage report
coverage html
```

## Troubleshooting

### ImportError: No module named 'xyz'

Make sure you're running from the project root:

```bash
cd partmart-boost
python tests/run_tests.py
```

### Tests fail with "File not found"

Some tests create temporary files. Make sure you have write permissions in `/tmp` or `%TEMP%`.

### Mock objects not working

Ensure `tests/` is in your Python path:

```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
```
