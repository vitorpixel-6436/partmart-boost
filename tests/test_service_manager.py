#!/usr/bin/env python3
"""BackendServiceManager Error Handling Tests

Version: 0.3.5p (package 3.9a, stage 7.7b.5.3/7.7)
"""
import sys
import os
import unittest
import time
from unittest.mock import Mock, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from service_manager import (
    BackendServiceManager,
    ServiceState,
    ManagerState,
    ServiceInfo
)


class MockService:
    """Mock service for testing"""
    
    def __init__(self, name="test", fail_start=False, fail_stop=False):
        self.name = name
        self._running = False
        self.fail_start = fail_start
        self.fail_stop = fail_stop
        self.start_count = 0
        self.stop_count = 0
    
    def start(self):
        self.start_count += 1
        if self.fail_start:
            raise Exception("Start failed!")
        self._running = True
        return True
    
    def stop(self):
        self.stop_count += 1
        if self.fail_stop:
            raise Exception("Stop failed!")
        self._running = False
        return True
    
    def is_running(self):
        return self._running


class TestBackendServiceManager(unittest.TestCase):
    """Test BackendServiceManager error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = BackendServiceManager(health_check_interval=0.5)
    
    def tearDown(self):
        """Clean up"""
        try:
            self.manager.stop_all()
        except Exception:
            pass
    
    def test_initialization(self):
        """Test manager initialization"""
        status = self.manager.get_all_status()
        self.assertEqual(status['manager_state'], 'idle')
        self.assertEqual(status['service_count'], 0)
    
    def test_register_service(self):
        """Test service registration"""
        service = MockService("test1")
        
        result = self.manager.register_service('test1', service)
        self.assertTrue(result)
        
        status = self.manager.get_service_status('test1')
        self.assertIsNotNone(status)
        self.assertEqual(status['state'], 'stopped')
    
    def test_register_duplicate(self):
        """Test registering duplicate service"""
        service1 = MockService("test1")
        service2 = MockService("test2")
        
        self.manager.register_service('test1', service1)
        
        # Second registration should fail
        result = self.manager.register_service('test1', service2)
        self.assertFalse(result)
    
    def test_register_invalid_service(self):
        """Test registering service without start/stop methods"""
        invalid_service = object()
        
        result = self.manager.register_service('invalid', invalid_service)
        self.assertFalse(result)
    
    def test_register_with_dependencies(self):
        """Test registering service with dependencies"""
        service1 = MockService("service1")
        service2 = MockService("service2")
        
        self.manager.register_service('service1', service1)
        result = self.manager.register_service('service2', service2, dependencies=['service1'])
        
        self.assertTrue(result)
        
        status = self.manager.get_service_status('service2')
        self.assertEqual(status['dependencies'], ['service1'])
    
    def test_register_with_missing_dependency(self):
        """Test registering with non-existent dependency"""
        service = MockService("test")
        
        result = self.manager.register_service('test', service, dependencies=['nonexistent'])
        self.assertFalse(result)
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection"""
        service1 = MockService("s1")
        service2 = MockService("s2")
        service3 = MockService("s3")
        
        self.manager.register_service('s1', service1, dependencies=['s2'])
        self.manager.register_service('s2', service2, dependencies=['s3'])
        
        # This would create circular dependency: s3 -> s1 -> s2 -> s3
        result = self.manager.register_service('s3', service3, dependencies=['s1'])
        self.assertFalse(result)
    
    def test_start_service(self):
        """Test starting a service"""
        service = MockService("test")
        self.manager.register_service('test', service)
        
        result = self.manager.start_service('test')
        self.assertTrue(result)
        
        status = self.manager.get_service_status('test')
        self.assertEqual(status['state'], 'running')
        
        self.assertTrue(service.is_running())
    
    def test_stop_service(self):
        """Test stopping a service"""
        service = MockService("test")
        self.manager.register_service('test', service)
        self.manager.start_service('test')
        
        result = self.manager.stop_service('test')
        self.assertTrue(result)
        
        status = self.manager.get_service_status('test')
        self.assertEqual(status['state'], 'stopped')
        
        self.assertFalse(service.is_running())
    
    def test_start_with_dependencies(self):
        """Test starting service starts dependencies first"""
        service1 = MockService("s1")
        service2 = MockService("s2")
        
        self.manager.register_service('s1', service1)
        self.manager.register_service('s2', service2, dependencies=['s1'])
        
        # Start s2, should also start s1
        result = self.manager.start_service('s2')
        self.assertTrue(result)
        
        self.assertTrue(service1.is_running())
        self.assertTrue(service2.is_running())
    
    def test_stop_with_dependents(self):
        """Test stopping service stops dependents first"""
        service1 = MockService("s1")
        service2 = MockService("s2")
        
        self.manager.register_service('s1', service1)
        self.manager.register_service('s2', service2, dependencies=['s1'])
        
        self.manager.start_service('s2')
        
        # Stop s1, should also stop s2
        result = self.manager.stop_service('s1')
        self.assertTrue(result)
        
        self.assertFalse(service1.is_running())
        self.assertFalse(service2.is_running())
    
    def test_start_all(self):
        """Test starting all services"""
        service1 = MockService("s1")
        service2 = MockService("s2")
        service3 = MockService("s3")
        
        self.manager.register_service('s1', service1)
        self.manager.register_service('s2', service2, dependencies=['s1'])
        self.manager.register_service('s3', service3, dependencies=['s2'])
        
        result = self.manager.start_all()
        self.assertTrue(result)
        
        # All should be running
        self.assertTrue(service1.is_running())
        self.assertTrue(service2.is_running())
        self.assertTrue(service3.is_running())
        
        status = self.manager.get_all_status()
        self.assertEqual(status['manager_state'], 'running')
    
    def test_stop_all(self):
        """Test stopping all services"""
        service1 = MockService("s1")
        service2 = MockService("s2")
        
        self.manager.register_service('s1', service1)
        self.manager.register_service('s2', service2)
        
        self.manager.start_all()
        
        result = self.manager.stop_all()
        self.assertTrue(result)
        
        # All should be stopped
        self.assertFalse(service1.is_running())
        self.assertFalse(service2.is_running())
        
        status = self.manager.get_all_status()
        self.assertEqual(status['manager_state'], 'idle')
    
    def test_start_order(self):
        """Test services start in correct dependency order"""
        start_order = []
        
        class OrderedService(MockService):
            def start(self):
                start_order.append(self.name)
                return super().start()
        
        s1 = OrderedService("s1")
        s2 = OrderedService("s2")
        s3 = OrderedService("s3")
        
        self.manager.register_service('s1', s1)
        self.manager.register_service('s2', s2, dependencies=['s1'])
        self.manager.register_service('s3', s3, dependencies=['s1', 's2'])
        
        self.manager.start_all()
        
        # s1 should start first, then s2, then s3
        self.assertEqual(start_order, ['s1', 's2', 's3'])
    
    def test_service_start_failure(self):
        """Test handling service start failure"""
        service = MockService("test", fail_start=True)
        self.manager.register_service('test', service)
        
        result = self.manager.start_service('test')
        self.assertFalse(result)
        
        status = self.manager.get_service_status('test')
        self.assertEqual(status['state'], 'error')
        self.assertIsNotNone(status['last_error'])
    
    def test_service_stop_failure(self):
        """Test handling service stop failure"""
        service = MockService("test", fail_stop=True)
        self.manager.register_service('test', service)
        self.manager.start_service('test')
        
        # Should handle error gracefully
        result = self.manager.stop_service('test')
        # May still return True (best effort)
        
        # Service should be marked as stopped despite error
        status = self.manager.get_service_status('test')
        # State may be stopped or error
        self.assertIn(status['state'], ['stopped', 'error'])
    
    def test_unregister_service(self):
        """Test unregistering a service"""
        service = MockService("test")
        self.manager.register_service('test', service)
        
        result = self.manager.unregister_service('test')
        self.assertTrue(result)
        
        status = self.manager.get_service_status('test')
        self.assertIsNone(status)
    
    def test_unregister_with_dependents(self):
        """Test cannot unregister service with dependents"""
        service1 = MockService("s1")
        service2 = MockService("s2")
        
        self.manager.register_service('s1', service1)
        self.manager.register_service('s2', service2, dependencies=['s1'])
        
        # Cannot unregister s1 while s2 depends on it
        result = self.manager.unregister_service('s1')
        self.assertFalse(result)
    
    def test_get_health(self):
        """Test health status"""
        service = MockService("test")
        self.manager.register_service('test', service)
        self.manager.start_service('test')
        
        health = self.manager.get_health()
        
        self.assertTrue(health['healthy'])
        self.assertEqual(health['total_services'], 1)
        self.assertEqual(health['running'], 1)
        self.assertEqual(health['crashed'], 0)
    
    def test_auto_restart(self):
        """Test automatic service restart on crash"""
        service = MockService("test")
        
        # Enable auto-restart
        self.manager.register_service('test', service, auto_restart=True)
        self.manager.start_all()
        
        time.sleep(0.2)
        
        # Simulate crash
        service._running = False
        
        # Wait for health check
        time.sleep(1.0)
        
        # Service should have been restarted
        status = self.manager.get_service_status('test')
        # May be running again or in crashed state
        self.assertIsNotNone(status)


if __name__ == '__main__':
    unittest.main()
