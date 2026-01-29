# Error Handling & Robustness

**Version:** 0.3.5j (Package 3.9a, Stage 7.7b/7.7)

## Overview

Comprehensive error handling and robustness features for PartMart Boost.

## Components

### 1. Error Handler (`error_handler.py`)

Centralized error handling system.

#### Features

- **Error Severity Levels:**
  - DEBUG 🔍
  - INFO ℹ️
  - WARNING ⚠️
  - ERROR ❌
  - CRITICAL 🔥

- **Error Context:** Captures component, operation, traceback, timestamp
- **Recovery Strategies:** Automatic error recovery
- **Statistics:** Error tracking and reporting
- **Thread-Safe:** Safe for concurrent use

#### Usage

```python
from core.error_handler import ErrorHandler, ErrorSeverity

handler = ErrorHandler.get_instance()

try:
    risky_operation()
except Exception as e:
    handler.handle_error(
        component='ComponentName',
        operation='operation_name',
        error=e,
        severity=ErrorSeverity.ERROR,
        recoverable=True
    )
```

#### Recovery Strategies

Register custom recovery functions:

```python
def recovery_strategy(ctx, context):
    # Attempt recovery
    return True  # or False

handler.register_recovery_strategy(
    component='Network',
    operation='connect',
    strategy=recovery_strategy
)
```

#### Statistics

```python
stats = handler.get_stats()
print(f"Total errors: {stats['total_errors']}")
print(f"Recovery rate: {stats['recovery_rate']:.1f}%")

handler.print_summary()  # Pretty print
```

### 2. Logger (`logger.py`)

Multi-level logging system.

#### Features

- **Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Output:** Console and file
- **Colored Console:** Color-coded severity levels
- **Thread-Safe:** Safe for concurrent logging
- **Timestamps:** Millisecond precision

#### Usage

```python
from core.logger import Logger, LogLevel

logger = Logger.get_instance()

logger.debug('Debug message', component='MyComponent')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message')
logger.critical('Critical message')
```

#### Configuration

```python
# Set log level
logger.set_level(LogLevel.DEBUG)

# Custom log file
logger = Logger(log_file='custom.log', level=LogLevel.INFO)
```

#### Output Format

```
ℹ️ 2026-01-29 02:30:15.123 [INFO][Component] Message
❌ 2026-01-29 02:30:16.456 [ERROR][Component] Error occurred
```

### 3. Input Validators (`validators.py`)

Comprehensive input validation.

#### Available Validators

```python
from core.validators import Validator, ValidationError

# Type validation
Validator.validate_type(value, int, 'param_name')
Validator.validate_type(value, (int, float))  # Multiple types

# Range validation
Validator.validate_range(value, min_value=0, max_value=100)

# Not None/Empty
Validator.validate_not_none(value)
Validator.validate_not_empty(collection)

# Choice validation
Validator.validate_choice(value, ['option1', 'option2'])

# String validation
Validator.validate_string_length(text, min_length=1, max_length=100)
Validator.validate_regex(text, r'^[a-z]+$')

# Numeric validation
Validator.validate_positive(value)
Validator.validate_percentage(value)  # 0-100

# Dictionary validation
Validator.validate_dict_keys(data, ['key1', 'key2'])
```

#### Safe Validation

```python
is_valid, error_msg = Validator.safe_validate(
    Validator.validate_range,
    value, 0, 100
)

if not is_valid:
    print(f"Validation failed: {error_msg}")
```

### 4. Graceful Degradation (`graceful_degradation.py`)

Patterns for handling failures gracefully.

#### Circuit Breaker

Prevents cascading failures:

```python
from core.graceful_degradation import CircuitBreaker

breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60
)

result = breaker.call(lambda: risky_service())
if result is None:
    # Circuit is open, use fallback
    result = fallback_value
```

**States:**
- CLOSED: Normal operation
- OPEN: Circuit broken, calls fail immediately
- HALF_OPEN: Testing recovery

#### Retry Strategy

Automatic retry with exponential backoff:

```python
from core.graceful_degradation import RetryStrategy

retry = RetryStrategy(
    max_attempts=3,
    backoff=2.0,
    max_backoff=30.0
)

result = retry.execute(
    lambda: unstable_operation(),
    on_retry=lambda attempt, error: print(f"Retry {attempt}")
)
```

#### Fallback Chain

Try multiple strategies:

```python
from core.graceful_degradation import FallbackChain

chain = FallbackChain()
chain.add(primary_method)
chain.add(backup_method)
chain.add(lambda: default_value)

result = chain.execute()
```

## Best Practices

### 1. Always Validate Input

```python
from core.validators import Validator

def set_value(self, value: float):
    # Validate before use
    Validator.validate_range(value, 0, 100, 'value')
    self._value = value
```

### 2. Use Error Handler

```python
from core.error_handler import ErrorHandler, ErrorSeverity

handler = ErrorHandler.get_instance()

try:
    operation()
except Exception as e:
    handler.handle_error(
        component='MyComponent',
        operation='my_operation',
        error=e,
        severity=ErrorSeverity.ERROR
    )
```

### 3. Log Important Events

```python
from core.logger import Logger

logger = Logger.get_instance()

logger.info('Operation started', component='MyComponent')
# ... operation ...
logger.info('Operation completed')
```

### 4. Use Safe Execute

```python
from core.error_handler import safe_execute

result = safe_execute(
    func=risky_function,
    component='MyComponent',
    operation='risky_op',
    default=None,
    arg1=value1,
    arg2=value2
)
```

### 5. Implement Fallbacks

```python
from core.graceful_degradation import CircuitBreaker

breaker = CircuitBreaker()

result = breaker.call(external_service)
if result is None:
    # Use cached data or default
    result = get_cached_data()
```

### 6. Add Recovery Strategies

```python
def recovery_network(ctx, context):
    """Attempt network reconnection"""
    try:
        # Reconnect logic
        return True
    except:
        return False

handler.register_recovery_strategy(
    'Network', 'connect', recovery_network
)
```

## Error Categories

### 1. Recoverable Errors

- Network timeouts
- Temporary file access issues
- Resource temporarily unavailable

**Action:** Retry with backoff, use circuit breaker

### 2. Non-Recoverable Errors

- Invalid configuration
- Missing required files
- Permission denied

**Action:** Log error, use fallback, notify user

### 3. Fatal Errors

- Out of memory
- Critical system failure
- Corrupted data

**Action:** Log, graceful shutdown, error report

## Integration Example

```python
from core.error_handler import ErrorHandler, ErrorSeverity
from core.logger import Logger
from core.validators import Validator
from core.graceful_degradation import CircuitBreaker

class MyComponent:
    def __init__(self):
        self.logger = Logger.get_instance()
        self.error_handler = ErrorHandler.get_instance()
        self.breaker = CircuitBreaker()
    
    def process(self, value: float):
        """Process with full error handling"""
        try:
            # 1. Validate input
            Validator.validate_range(value, 0, 100, 'value')
            
            # 2. Log start
            self.logger.info(f'Processing value: {value}', 
                           component='MyComponent')
            
            # 3. Execute with circuit breaker
            result = self.breaker.call(
                lambda: self._risky_operation(value)
            )
            
            if result is None:
                # 4. Use fallback
                self.logger.warning('Using fallback', 
                                  component='MyComponent')
                result = self._fallback_operation(value)
            
            # 5. Log success
            self.logger.info('Processing complete', 
                           component='MyComponent')
            
            return result
        
        except Exception as e:
            # 6. Handle error
            self.error_handler.handle_error(
                component='MyComponent',
                operation='process',
                error=e,
                severity=ErrorSeverity.ERROR,
                recoverable=False
            )
            return None
```

## Performance Impact

### Logging

- **Console:** ~0.1ms per log
- **File:** ~0.5ms per log
- **Recommendation:** Use INFO level in production, DEBUG in development

### Error Handler

- **Overhead:** ~0.05ms per error
- **Memory:** ~1KB per error in history
- **Recommendation:** Set max_errors appropriately

### Validation

- **Overhead:** ~0.01ms per validation
- **Recommendation:** Validate at API boundaries only

### Circuit Breaker

- **Overhead:** ~0.02ms per call
- **Benefit:** Prevents cascading failures

## Testing

### Error Handler Test

```bash
python src/core/error_handler.py
```

### Logger Test

```bash
python src/core/logger.py
```

### Validators Test

```bash
python src/core/validators.py
```

### Graceful Degradation Test

```bash
python src/core/graceful_degradation.py
```

## Troubleshooting

### Logger not writing to file

- Check directory permissions
- Verify log directory exists
- Check disk space

### Error handler missing errors

- Check severity level
- Verify error is being caught
- Check max_errors limit

### Circuit breaker always open

- Check failure_threshold
- Verify timeout is appropriate
- Reset circuit: `breaker.reset()`

## Future Enhancements

- [ ] Remote error reporting
- [ ] Error aggregation
- [ ] Prometheus metrics
- [ ] Sentry integration
- [ ] Custom error handlers per component
- [ ] Error rate limiting
