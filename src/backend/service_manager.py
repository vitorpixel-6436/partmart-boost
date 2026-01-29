#!/usr/bin/env python3
"""Backend Service Manager with Error Handling

Version: 0.3.5p (package 3.9a, stage 7.7b.5.3/7.7)

Package 3.9a Stage 7.7b.5.3: Error handling in BackendServiceManager.

Features:
- Service lifecycle management
- Dependency management
- Health monitoring
- Automatic recovery
- Comprehensive error handling
"""
import threading
import time
from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass
from enum import Enum

try:
    from logger import AppLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False


class ServiceState(Enum):
    """Service state enum"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    CRASHED = "crashed"


class ManagerState(Enum):
    """Manager state enum"""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ServiceInfo:
    """Service information
    
    Attributes:
        name: Service name
        instance: Service instance
        state: Current state
        dependencies: List of service names this depends on
        auto_restart: Enable automatic restart on crash
        health_check: Health check callable
        start_timeout: Start timeout in seconds
        stop_timeout: Stop timeout in seconds
    """
    name: str
    instance: Any
    state: ServiceState
    dependencies: List[str]
    auto_restart: bool = True
    health_check: Optional[Callable[[], bool]] = None
    start_timeout: float = 5.0
    stop_timeout: float = 5.0
    restart_count: int = 0
    last_error: Optional[str] = None
    last_restart_time: float = 0.0


class BackendServiceManager:
    """Backend service manager with error handling
    
    v0.3.5p (package 3.9a, stage 7.7b.5.3/7.7)
    
    Features:
    - Service lifecycle management
    - Dependency resolution
    - Health monitoring
    - Automatic recovery
    - Thread-safe operation
    - Comprehensive error handling
    
    Usage:
        >>> manager = BackendServiceManager()
        >>> 
        >>> # Register services
        >>> manager.register_service(
        ...     'performance_monitor',
        ...     performance_monitor,
        ...     dependencies=[]
        ... )
        >>> manager.register_service(
        ...     'game_detection',
        ...     game_detection,
        ...     dependencies=['performance_monitor']
        ... )
        >>> 
        >>> # Start all services
        >>> manager.start_all()
        >>> 
        >>> # Check health
        >>> health = manager.get_health()
        >>> 
        >>> # Stop all services
        >>> manager.stop_all()
    """
    
    def __init__(self, health_check_interval: float = 5.0):
        """Initialize manager
        
        Args:
            health_check_interval: Health check interval in seconds
        """
        self._services: Dict[str, ServiceInfo] = {}
        self._lock = threading.RLock()
        self._state = ManagerState.IDLE
        self._logger = None
        
        # Health monitoring
        self._health_check_interval = max(1.0, health_check_interval)
        self._health_thread: Optional[threading.Thread] = None
        self._health_enabled = False
        
        # Error tracking
        self._error_count = 0
        self._max_errors = 20
        
        # Get logger
        if LOGGER_AVAILABLE:
            try:
                self._logger = AppLogger.get_instance()
                self._log_debug("BackendServiceManager initializing")
            except Exception:
                pass
        
        self._log_info("Initialized")
    
    def _log_debug(self, message: str):
        """Log debug message"""
        if self._logger:
            self._logger.debug(message, component="ServiceManager")
    
    def _log_info(self, message: str):
        """Log info message"""
        if self._logger:
            self._logger.info(message, component="ServiceManager")
        else:
            print(f"[ServiceManager] {message}")
    
    def _log_warning(self, message: str):
        """Log warning message"""
        if self._logger:
            self._logger.warning(message, component="ServiceManager")
        else:
            print(f"[ServiceManager] WARNING: {message}")
    
    def _log_error(self, message: str, exc_info: bool = False):
        """Log error message"""
        if self._logger:
            self._logger.error(message, component="ServiceManager", exc_info=exc_info)
        else:
            print(f"[ServiceManager] ERROR: {message}")
    
    def register_service(
        self,
        name: str,
        instance: Any,
        dependencies: Optional[List[str]] = None,
        auto_restart: bool = True,
        health_check: Optional[Callable[[], bool]] = None,
        start_timeout: float = 5.0,
        stop_timeout: float = 5.0
    ) -> bool:
        """Register a service
        
        Args:
            name: Service name
            instance: Service instance (must have start() and stop() methods)
            dependencies: List of service names this depends on
            auto_restart: Enable automatic restart on crash
            health_check: Health check function returning bool
            start_timeout: Start timeout in seconds
            stop_timeout: Stop timeout in seconds
        
        Returns:
            True if registered successfully
        """
        try:
            if not name or not instance:
                self._log_error("Invalid service name or instance")
                return False
            
            # Check for start/stop methods
            if not hasattr(instance, 'start') or not hasattr(instance, 'stop'):
                self._log_error(f"Service {name} missing start/stop methods")
                return False
            
            with self._lock:
                if name in self._services:
                    self._log_warning(f"Service {name} already registered")
                    return False
                
                # Validate dependencies
                deps = dependencies or []
                for dep in deps:
                    if dep not in self._services:
                        self._log_error(f"Service {name} depends on unknown service: {dep}")
                        return False
                
                # Check for circular dependencies
                if self._has_circular_dependency(name, deps):
                    self._log_error(f"Circular dependency detected for service: {name}")
                    return False
                
                # Create service info
                info = ServiceInfo(
                    name=name,
                    instance=instance,
                    state=ServiceState.STOPPED,
                    dependencies=deps,
                    auto_restart=auto_restart,
                    health_check=health_check,
                    start_timeout=start_timeout,
                    stop_timeout=stop_timeout
                )
                
                self._services[name] = info
            
            self._log_info(f"Registered service: {name} (deps: {deps})")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to register service {name}: {e}", exc_info=True)
            return False
    
    def _has_circular_dependency(self, service_name: str, dependencies: List[str]) -> bool:
        """Check for circular dependencies
        
        Args:
            service_name: Service being checked
            dependencies: Its dependencies
        
        Returns:
            True if circular dependency detected
        """
        visited = set()
        
        def visit(name: str) -> bool:
            if name == service_name:
                return True
            
            if name in visited:
                return False
            
            visited.add(name)
            
            service = self._services.get(name)
            if service:
                for dep in service.dependencies:
                    if visit(dep):
                        return True
            
            return False
        
        for dep in dependencies:
            if visit(dep):
                return True
        
        return False
    
    def unregister_service(self, name: str) -> bool:
        """Unregister a service
        
        Args:
            name: Service name
        
        Returns:
            True if unregistered successfully
        """
        try:
            with self._lock:
                if name not in self._services:
                    self._log_warning(f"Service {name} not registered")
                    return False
                
                service = self._services[name]
                
                # Check if other services depend on this
                for svc_name, svc_info in self._services.items():
                    if name in svc_info.dependencies:
                        self._log_error(f"Cannot unregister {name}: {svc_name} depends on it")
                        return False
                
                # Stop if running
                if service.state in (ServiceState.RUNNING, ServiceState.STARTING):
                    self._log_info(f"Stopping {name} before unregister")
                    self._stop_service(service)
                
                # Remove
                del self._services[name]
            
            self._log_info(f"Unregistered service: {name}")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to unregister service {name}: {e}", exc_info=True)
            return False
    
    def start_service(self, name: str) -> bool:
        """Start a specific service
        
        Args:
            name: Service name
        
        Returns:
            True if started successfully
        """
        try:
            with self._lock:
                if name not in self._services:
                    self._log_error(f"Service {name} not registered")
                    return False
                
                service = self._services[name]
                
                # Check if already running
                if service.state == ServiceState.RUNNING:
                    self._log_debug(f"Service {name} already running")
                    return True
                
                # Start dependencies first
                for dep in service.dependencies:
                    if not self.start_service(dep):
                        self._log_error(f"Failed to start dependency {dep} for {name}")
                        return False
            
            # Start the service (outside lock)
            return self._start_service(service)
        
        except Exception as e:
            self._log_error(f"Failed to start service {name}: {e}", exc_info=True)
            return False
    
    def _start_service(self, service: ServiceInfo) -> bool:
        """Start a service with error handling
        
        Args:
            service: Service info
        
        Returns:
            True if started successfully
        """
        try:
            with self._lock:
                service.state = ServiceState.STARTING
            
            self._log_info(f"Starting service: {service.name}")
            
            # Call start method
            start_time = time.time()
            
            try:
                result = service.instance.start()
                
                if result is False:
                    raise Exception("Start method returned False")
            
            except Exception as e:
                with self._lock:
                    service.state = ServiceState.ERROR
                    service.last_error = str(e)
                
                self._log_error(f"Service {service.name} start failed: {e}", exc_info=True)
                return False
            
            # Wait for startup (with timeout)
            timeout = service.start_timeout
            while time.time() - start_time < timeout:
                # Check if service reports running
                try:
                    if hasattr(service.instance, 'is_running'):
                        if service.instance.is_running():
                            break
                    else:
                        # No is_running method, assume started
                        break
                
                except Exception as e:
                    self._log_warning(f"Error checking {service.name} running state: {e}")
                    break
                
                time.sleep(0.1)
            
            # Update state
            with self._lock:
                service.state = ServiceState.RUNNING
                service.last_error = None
            
            self._log_info(f"Service {service.name} started successfully")
            return True
        
        except Exception as e:
            with self._lock:
                service.state = ServiceState.ERROR
                service.last_error = str(e)
            
            self._log_error(f"Failed to start service {service.name}: {e}", exc_info=True)
            return False
    
    def stop_service(self, name: str) -> bool:
        """Stop a specific service
        
        Args:
            name: Service name
        
        Returns:
            True if stopped successfully
        """
        try:
            with self._lock:
                if name not in self._services:
                    self._log_error(f"Service {name} not registered")
                    return False
                
                service = self._services[name]
                
                # Check if already stopped
                if service.state == ServiceState.STOPPED:
                    self._log_debug(f"Service {name} already stopped")
                    return True
                
                # Check if other services depend on this
                for svc_name, svc_info in self._services.items():
                    if name in svc_info.dependencies:
                        if svc_info.state == ServiceState.RUNNING:
                            self._log_info(f"Stopping dependent service {svc_name}")
                            self.stop_service(svc_name)
            
            # Stop the service
            return self._stop_service(service)
        
        except Exception as e:
            self._log_error(f"Failed to stop service {name}: {e}", exc_info=True)
            return False
    
    def _stop_service(self, service: ServiceInfo) -> bool:
        """Stop a service with error handling
        
        Args:
            service: Service info
        
        Returns:
            True if stopped successfully
        """
        try:
            with self._lock:
                service.state = ServiceState.STOPPING
            
            self._log_info(f"Stopping service: {service.name}")
            
            # Call stop method
            try:
                result = service.instance.stop()
                
                if result is False:
                    self._log_warning(f"Service {service.name} stop returned False")
            
            except Exception as e:
                self._log_error(f"Service {service.name} stop error: {e}", exc_info=True)
                # Continue anyway
            
            # Wait for shutdown (with timeout)
            start_time = time.time()
            timeout = service.stop_timeout
            
            while time.time() - start_time < timeout:
                try:
                    if hasattr(service.instance, 'is_running'):
                        if not service.instance.is_running():
                            break
                    else:
                        break
                
                except Exception:
                    break
                
                time.sleep(0.1)
            
            # Update state
            with self._lock:
                service.state = ServiceState.STOPPED
            
            self._log_info(f"Service {service.name} stopped")
            return True
        
        except Exception as e:
            with self._lock:
                service.state = ServiceState.ERROR
                service.last_error = str(e)
            
            self._log_error(f"Failed to stop service {service.name}: {e}", exc_info=True)
            return False
    
    def start_all(self) -> bool:
        """Start all services in dependency order
        
        Returns:
            True if all started successfully
        """
        try:
            with self._lock:
                if self._state == ManagerState.RUNNING:
                    self._log_info("Manager already running")
                    return True
                
                self._state = ManagerState.STARTING
            
            self._log_info("Starting all services")
            
            # Get start order
            start_order = self._get_start_order()
            
            # Start services in order
            success = True
            for name in start_order:
                if not self.start_service(name):
                    self._log_error(f"Failed to start service: {name}")
                    success = False
                    break
            
            if success:
                # Start health monitoring
                self._start_health_monitoring()
                
                with self._lock:
                    self._state = ManagerState.RUNNING
                
                self._log_info("All services started successfully")
            else:
                with self._lock:
                    self._state = ManagerState.ERROR
                
                self._log_error("Failed to start all services")
            
            return success
        
        except Exception as e:
            with self._lock:
                self._state = ManagerState.ERROR
            
            self._log_error(f"Failed to start all services: {e}", exc_info=True)
            return False
    
    def stop_all(self) -> bool:
        """Stop all services in reverse dependency order
        
        Returns:
            True if all stopped successfully
        """
        try:
            with self._lock:
                if self._state == ManagerState.IDLE:
                    self._log_debug("Manager already idle")
                    return True
                
                self._state = ManagerState.STOPPING
            
            self._log_info("Stopping all services")
            
            # Stop health monitoring
            self._stop_health_monitoring()
            
            # Get stop order (reverse of start)
            start_order = self._get_start_order()
            stop_order = list(reversed(start_order))
            
            # Stop services in order
            success = True
            for name in stop_order:
                if not self.stop_service(name):
                    self._log_error(f"Failed to stop service: {name}")
                    success = False
                    # Continue stopping others
            
            with self._lock:
                self._state = ManagerState.IDLE
            
            if success:
                self._log_info("All services stopped successfully")
            else:
                self._log_warning("Some services failed to stop")
            
            return success
        
        except Exception as e:
            with self._lock:
                self._state = ManagerState.ERROR
            
            self._log_error(f"Failed to stop all services: {e}", exc_info=True)
            return False
    
    def _get_start_order(self) -> List[str]:
        """Get service start order based on dependencies
        
        Returns:
            List of service names in start order
        """
        order = []
        visited = set()
        
        def visit(name: str):
            if name in visited:
                return
            
            visited.add(name)
            
            service = self._services.get(name)
            if service:
                # Visit dependencies first
                for dep in service.dependencies:
                    visit(dep)
                
                order.append(name)
        
        with self._lock:
            for name in self._services:
                visit(name)
        
        return order
    
    def _start_health_monitoring(self):
        """Start health monitoring thread"""
        try:
            self._health_enabled = True
            
            self._health_thread = threading.Thread(
                target=self._health_worker,
                name='HealthMonitor',
                daemon=True
            )
            self._health_thread.start()
            
            self._log_debug("Health monitoring started")
        
        except Exception as e:
            self._log_error(f"Failed to start health monitoring: {e}")
    
    def _stop_health_monitoring(self):
        """Stop health monitoring thread"""
        try:
            self._health_enabled = False
            
            if self._health_thread and self._health_thread.is_alive():
                self._health_thread.join(timeout=2.0)
            
            self._log_debug("Health monitoring stopped")
        
        except Exception as e:
            self._log_error(f"Failed to stop health monitoring: {e}")
    
    def _health_worker(self):
        """Health monitoring worker thread"""
        self._log_debug("Health worker started")
        
        while self._health_enabled:
            try:
                time.sleep(self._health_check_interval)
                
                if not self._health_enabled:
                    break
                
                self._check_services_health()
            
            except Exception as e:
                self._log_error(f"Health worker error: {e}", exc_info=True)
                time.sleep(1.0)
        
        self._log_debug("Health worker stopped")
    
    def _check_services_health(self):
        """Check health of all services"""
        with self._lock:
            services = list(self._services.values())
        
        for service in services:
            try:
                # Skip if not running
                if service.state != ServiceState.RUNNING:
                    continue
                
                # Check if service is still running
                if hasattr(service.instance, 'is_running'):
                    if not service.instance.is_running():
                        self._log_warning(f"Service {service.name} crashed!")
                        self._handle_crashed_service(service)
                        continue
                
                # Run custom health check if provided
                if service.health_check:
                    try:
                        if not service.health_check():
                            self._log_warning(f"Service {service.name} failed health check")
                            self._handle_unhealthy_service(service)
                    
                    except Exception as e:
                        self._log_error(f"Health check failed for {service.name}: {e}")
            
            except Exception as e:
                self._log_error(f"Error checking health of {service.name}: {e}", exc_info=True)
    
    def _handle_crashed_service(self, service: ServiceInfo):
        """Handle crashed service
        
        Args:
            service: Crashed service
        """
        try:
            with self._lock:
                service.state = ServiceState.CRASHED
                service.restart_count += 1
            
            self._log_error(f"Service {service.name} crashed (restart count: {service.restart_count})")
            
            # Auto-restart if enabled
            if service.auto_restart:
                now = time.time()
                
                # Check restart cooldown (30 seconds)
                if now - service.last_restart_time < 30.0:
                    self._log_warning(f"Service {service.name} restarting too quickly, waiting")
                    return
                
                # Check restart limit
                if service.restart_count > 5:
                    self._log_error(f"Service {service.name} restarted too many times, giving up")
                    return
                
                self._log_info(f"Auto-restarting service: {service.name}")
                
                with self._lock:
                    service.last_restart_time = now
                
                # Restart service
                if self._start_service(service):
                    self._log_info(f"Service {service.name} restarted successfully")
                else:
                    self._log_error(f"Failed to restart service: {service.name}")
        
        except Exception as e:
            self._log_error(f"Error handling crashed service {service.name}: {e}", exc_info=True)
    
    def _handle_unhealthy_service(self, service: ServiceInfo):
        """Handle unhealthy service
        
        Args:
            service: Unhealthy service
        """
        self._log_warning(f"Service {service.name} is unhealthy")
        # Could implement restart logic here too
    
    def get_service_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific service
        
        Args:
            name: Service name
        
        Returns:
            Status dictionary or None
        """
        try:
            with self._lock:
                if name not in self._services:
                    return None
                
                service = self._services[name]
                
                return {
                    'name': service.name,
                    'state': service.state.value,
                    'dependencies': service.dependencies,
                    'auto_restart': service.auto_restart,
                    'restart_count': service.restart_count,
                    'last_error': service.last_error,
                }
        
        except Exception as e:
            self._log_error(f"Failed to get service status for {name}: {e}")
            return None
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all services
        
        Returns:
            Status dictionary
        """
        try:
            with self._lock:
                services = {}
                for name, service in self._services.items():
                    services[name] = {
                        'state': service.state.value,
                        'dependencies': service.dependencies,
                        'restart_count': service.restart_count,
                        'last_error': service.last_error,
                    }
                
                return {
                    'manager_state': self._state.value,
                    'service_count': len(self._services),
                    'services': services,
                    'error_count': self._error_count,
                }
        
        except Exception as e:
            self._log_error(f"Failed to get all status: {e}")
            return {'error': str(e)}
    
    def get_health(self) -> Dict[str, Any]:
        """Get health status
        
        Returns:
            Health dictionary
        """
        try:
            with self._lock:
                total = len(self._services)
                running = sum(1 for s in self._services.values() if s.state == ServiceState.RUNNING)
                crashed = sum(1 for s in self._services.values() if s.state == ServiceState.CRASHED)
                errors = sum(1 for s in self._services.values() if s.state == ServiceState.ERROR)
                
                healthy = running == total and crashed == 0 and errors == 0
                
                return {
                    'healthy': healthy,
                    'total_services': total,
                    'running': running,
                    'crashed': crashed,
                    'errors': errors,
                    'manager_state': self._state.value,
                }
        
        except Exception as e:
            self._log_error(f"Failed to get health: {e}")
            return {'healthy': False, 'error': str(e)}


# Testing
if __name__ == '__main__':
    print("="*60)
    print("BackendServiceManager Test (with Error Handling)")
    print("="*60)
    print()
    
    # Mock service class
    class MockService:
        def __init__(self, name):
            self.name = name
            self._running = False
        
        def start(self):
            print(f"  [{self.name}] Starting...")
            time.sleep(0.1)
            self._running = True
            return True
        
        def stop(self):
            print(f"  [{self.name}] Stopping...")
            self._running = False
            return True
        
        def is_running(self):
            return self._running
    
    # Create manager
    manager = BackendServiceManager(health_check_interval=2.0)
    
    # Register services with dependencies
    service1 = MockService("Service1")
    service2 = MockService("Service2")
    service3 = MockService("Service3")
    
    print("Registering services...")
    manager.register_service('service1', service1, dependencies=[])
    manager.register_service('service2', service2, dependencies=['service1'])
    manager.register_service('service3', service3, dependencies=['service1', 'service2'])
    print()
    
    # Start all
    print("Starting all services...")
    if manager.start_all():
        print("✅ All started\n")
    else:
        print("❌ Start failed\n")
    
    # Get status
    status = manager.get_all_status()
    print("Status:")
    print(f"  Manager: {status['manager_state']}")
    print(f"  Services: {status['service_count']}")
    for name, svc in status['services'].items():
        print(f"    {name}: {svc['state']}")
    print()
    
    # Get health
    health = manager.get_health()
    print("Health:")
    print(f"  Healthy: {health['healthy']}")
    print(f"  Running: {health['running']}/{health['total_services']}")
    print()
    
    # Wait a bit
    print("Running for 5 seconds...")
    time.sleep(5)
    print()
    
    # Stop all
    print("Stopping all services...")
    if manager.stop_all():
        print("✅ All stopped")
    else:
        print("❌ Stop failed")
    
    print()
    print("✅ Test completed!")
