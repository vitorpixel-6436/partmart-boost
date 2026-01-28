# Development Guide

**Version:** 0.3.5d+patch5

## Project Structure

```
partmart-boost/
├── src/
│   ├── core/              # Core systems
│   │   ├── fps_tracker.py
│   │   └── resource_manager.py
│   ├── monitors/          # Performance monitoring
│   │   └── performance_monitor.py
│   ├── framegen/          # Frame generation
│   │   ├── interfaces.py
│   │   └── generator.py
│   ├── upscaler/          # Upscaling
│   │   └── upscaler.py
│   ├── adaptive/          # Adaptive systems
│   │   ├── thermal_manager_advanced.py
│   │   ├── power_manager_advanced.py
│   │   └── system_integration.py
│   ├── fsr4/              # FSR 4 (v0.5.0)
│   │   └── __init__.py
│   ├── gui/               # GUI modules
│   │   ├── main_window.py
│   │   ├── dashboard_widget.py
│   │   ├── performance_widget.py
│   │   ├── settings_widget.py
│   │   └── logs_widget.py
│   ├── main.py            # GUI launcher
│   └── main_cli.py        # CLI launcher
├── tests/
│   └── test_all_modules.py
└── docs/                  # Documentation
```

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Tests

```bash
python tests/test_all_modules.py
```

## Coding Standards

### Style Guide

- Follow PEP 8
- Use type hints
- Document all public APIs
- Write docstrings for modules, classes, and functions

### Example:

```python
def process_frame(frame: np.ndarray, quality: str = 'balanced') -> np.ndarray:
    """Process frame with specified quality.
    
    Args:
        frame: Input frame as numpy array
        quality: Quality preset ('performance', 'balanced', 'quality')
    
    Returns:
        Processed frame
    
    Raises:
        ValueError: If quality preset is invalid
    """
    if quality not in ['performance', 'balanced', 'quality']:
        raise ValueError(f"Invalid quality: {quality}")
    
    # Implementation
    return frame
```

### Thread Safety

- Use locks for shared state
- Prefer `threading.Lock()` for simple cases
- Use `threading.RLock()` for reentrant locks
- Document thread-safety guarantees

### Memory Management

- Clean up resources in `__del__` or context managers
- Avoid circular references
- Use weak references when appropriate

## Testing

### Unit Tests

Each module should have a `__main__` block:

```python
if __name__ == "__main__":
    print("Testing ModuleName...")
    
    # Test 1: Basic functionality
    obj = ModuleName()
    result = obj.method()
    assert result is not None
    
    print("✅ All tests passed")
```

### Integration Tests

Add tests to `tests/test_all_modules.py`:

```python
def test_new_module():
    """Test new module"""
    from src.new_module import NewModule
    
    module = NewModule()
    result = module.process()
    
    assert result is not None
    return True
```

## Adding New Features

### 1. Create Module

```bash
# Create new module file
touch src/new_module/feature.py
```

### 2. Implement

```python
#!/usr/bin/env python3
"""New Feature Module

Version: 0.x.x
"""

class NewFeature:
    """Description of feature"""
    
    def __init__(self):
        pass
    
    def method(self):
        """Method description"""
        pass
```

### 3. Add Tests

```python
if __name__ == "__main__":
    # Self-test
    print("Testing NewFeature...")
    feature = NewFeature()
    # Tests here
    print("✅ Tests passed")
```

### 4. Integrate

- Add to `test_all_modules.py`
- Update README.md
- Add to CHANGELOG.md

## Git Workflow

### Commit Messages

Format: `type: description`

Types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvement
- `chore:` - Maintenance

Examples:
```
feat: Add FSR 4 upscaling support
fix: Resolve memory leak in FPS tracker
docs: Update installation guide
test: Add unit tests for thermal manager
```

### Branching

- `main` - Production ready
- `develop` - Development branch
- `feature/name` - New features
- `fix/name` - Bug fixes

## Performance Guidelines

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Optimization

- Profile before optimizing
- Focus on hot paths
- Use numpy for array operations
- Minimize memory allocations
- Cache expensive computations

## Release Process

### 1. Version Bump

```bash
echo "0.x.x" > VERSION
```

### 2. Update CHANGELOG.md

```markdown
## [0.x.x] - YYYY-MM-DD

### Added
- Feature 1
- Feature 2

### Fixed
- Bug 1
- Bug 2
```

### 3. Run Tests

```bash
python tests/test_all_modules.py
```

### 4. Commit and Tag

```bash
git add .
git commit -m "Release v0.x.x"
git tag v0.x.x
git push origin main --tags
```

## Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(name)s: %(message)s'
)
```

### Common Issues

**Import Errors:**
- Check PYTHONPATH
- Ensure `__init__.py` exists
- Use absolute imports

**Thread Safety:**
- Use locks
- Avoid global state
- Test with multiple threads

**Memory Leaks:**
- Check circular references
- Use weak references
- Profile memory usage

## Resources

- [Python Documentation](https://docs.python.org/3/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Threading Guide](https://docs.python.org/3/library/threading.html)

---

**Questions?** Open an issue on GitHub!
