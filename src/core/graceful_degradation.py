#!/usr/bin/env python3
"""Graceful Degradation

Version: 0.3.5j (package 3.9a, stage 7.7b/7.7)

Package 3.9a Stage 7.7b: Graceful degradation patterns.

Features:
- Fallback mechanisms
- Component health tracking
- Automatic retry
- Circuit breaker pattern
"""
import time
import threading
from typing import Optional, Callable, Any
from enum import Enum


class ComponentStatus(Enum):
    """Component health status"""
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    FAILED = 'failed'
    RECOVERING = 'recovering'


class CircuitBreaker:
    """Circuit Breaker Pattern
    
    Prevents cascading failures by temporarily disabling failed components.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Circuit broken, calls fail immediately
    - HALF_OPEN: Testing if service recovered
    
    Usage:
        >>> breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        >>> 
        >>> result = breaker.call(lambda: risky_operation())
        >>> if result is None:
        ...     # Circuit is open, use fallback
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        """Initialize circuit breaker
        
        Args:
            failure_threshold: Failures before opening circuit
            timeout: Seconds before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Optional[Any]:
        """Call function with circuit breaker
        
        Args:
            func: Function to call
            *args: Arguments
            **kwargs: Keyword arguments
        
        Returns:
            Function result or None if circuit open
        """
        with self._lock:
            # Check if circuit is open
            if self.state == 'OPEN':
                # Check if timeout expired
                if time.time() - self.last_failure_time >= self.timeout:
                    self.state = 'HALF_OPEN'
                    print(f"[CircuitBreaker] Attempting recovery (HALF_OPEN)")
                else:
                    print(f"[CircuitBreaker] Circuit OPEN, call rejected")
                    return None
        
        # Try to execute
        try:
            result = func(*args, **kwargs)
            
            with self._lock:
                # Success - reset if was recovering
                if self.state == 'HALF_OPEN':
                    print(f"[CircuitBreaker] Recovery successful (CLOSED)")
                    self.state = 'CLOSED'
                    self.failure_count = 0
            
            return result
        
        except self.expected_exception as e:
            with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                # Check if should open circuit
                if self.failure_count >= self.failure_threshold:
                    if self.state != 'OPEN':
                        print(f"[CircuitBreaker] Opening circuit after {self.failure_count} failures")
                        self.state = 'OPEN'
                
                print(f"[CircuitBreaker] Call failed ({self.failure_count}/{self.failure_threshold}): {e}")
            
            return None
    
    def reset(self):
        """Reset circuit breaker"""
        with self._lock:
            self.state = 'CLOSED'
            self.failure_count = 0
            self.last_failure_time = None
            print(f"[CircuitBreaker] Reset to CLOSED")
    
    def get_state(self) -> str:
        """Get current state"""
        return self.state


class RetryStrategy:
    """Automatic Retry Strategy
    
    Automatically retries failed operations with exponential backoff.
    
    Usage:
        >>> retry = RetryStrategy(max_attempts=3, backoff=2)
        >>> result = retry.execute(lambda: unstable_operation())
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        backoff: float = 2.0,
        max_backoff: float = 30.0
    ):
        """Initialize retry strategy
        
        Args:
            max_attempts: Maximum retry attempts
            backoff: Backoff multiplier
            max_backoff: Maximum backoff time
        """
        self.max_attempts = max_attempts
        self.backoff = backoff
        self.max_backoff = max_backoff
    
    def execute(
        self,
        func: Callable,
        *args,
        on_retry: Optional[Callable[[int, Exception], None]] = None,
        **kwargs
    ) -> Optional[Any]:
        """Execute with retry
        
        Args:
            func: Function to execute
            *args: Arguments
            on_retry: Callback on retry(attempt, error)
            **kwargs: Keyword arguments
        
        Returns:
            Function result or None
        """
        last_exception = None
        wait_time = 1.0
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_attempts:
                    if on_retry:
                        on_retry(attempt, e)
                    
                    print(f"[Retry] Attempt {attempt}/{self.max_attempts} failed: {e}")
                    print(f"[Retry] Waiting {wait_time:.1f}s before retry...")
                    
                    time.sleep(wait_time)
                    wait_time = min(wait_time * self.backoff, self.max_backoff)
        
        print(f"[Retry] All {self.max_attempts} attempts failed")
        return None


class FallbackChain:
    """Fallback Chain
    
    Tries multiple strategies in order until one succeeds.
    
    Usage:
        >>> chain = FallbackChain()
        >>> chain.add(primary_method)
        >>> chain.add(backup_method)
        >>> chain.add(lambda: default_value)
        >>> result = chain.execute()
    """
    
    def __init__(self):
        """Initialize fallback chain"""
        self.strategies = []
    
    def add(self, func: Callable, *args, **kwargs):
        """Add strategy to chain
        
        Args:
            func: Function to try
            *args: Arguments
            **kwargs: Keyword arguments
        """
        self.strategies.append((func, args, kwargs))
    
    def execute(self) -> Optional[Any]:
        """Execute fallback chain
        
        Returns:
            First successful result or None
        """
        for i, (func, args, kwargs) in enumerate(self.strategies):
            try:
                print(f"[Fallback] Trying strategy {i+1}/{len(self.strategies)}")
                result = func(*args, **kwargs)
                print(f"[Fallback] Strategy {i+1} succeeded")
                return result
            
            except Exception as e:
                print(f"[Fallback] Strategy {i+1} failed: {e}")
                if i == len(self.strategies) - 1:
                    print(f"[Fallback] All strategies failed")
        
        return None


# Testing
if __name__ == '__main__':
    print("="*60)
    print("Graceful Degradation Test")
    print("="*60)
    print()
    
    # Test 1: Circuit Breaker
    print("Test 1: Circuit Breaker")
    breaker = CircuitBreaker(failure_threshold=3, timeout=2)
    
    def failing_func():
        raise Exception("Service unavailable")
    
    # Trigger failures
    for i in range(5):
        result = breaker.call(failing_func)
        print(f"  Result: {result}")
    
    print()
    
    # Test 2: Retry Strategy
    print("Test 2: Retry Strategy")
    retry = RetryStrategy(max_attempts=3, backoff=1.5)
    
    attempt_count = [0]
    def unstable_func():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise Exception("Temporary failure")
        return "Success!"
    
    result = retry.execute(unstable_func)
    print(f"  Final result: {result}")
    
    print()
    
    # Test 3: Fallback Chain
    print("Test 3: Fallback Chain")
    chain = FallbackChain()
    chain.add(lambda: (_ for _ in ()).throw(Exception("Primary failed")))
    chain.add(lambda: (_ for _ in ()).throw(Exception("Backup failed")))
    chain.add(lambda: "Default value")
    
    result = chain.execute()
    print(f"  Final result: {result}")
    
    print("\n✅ Test completed!")
