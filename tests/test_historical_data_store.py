#!/usr/bin/env python3
"""Tests for HistoricalDataStore

Version: 0.3.5e (package 3.9a, stage 7.7b.8.1/7.7b.8)
"""
import unittest
import tempfile
import os
import time
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.historical_data_store import (
    HistoricalDataStore,
    DataRetentionPolicy,
    HealthSnapshot,
    ErrorRecord,
    RecoveryRecord
)


class TestHistoricalDataStore(unittest.TestCase):
    """Test HistoricalDataStore"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary database
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_file.name
        self.temp_file.close()
        
        self.store = HistoricalDataStore(
            self.db_path,
            DataRetentionPolicy.DAYS_7
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_initialization(self):
        """Test store initialization"""
        self.assertTrue(os.path.exists(self.db_path))
        self.assertGreater(self.store.get_database_size(), 0)
    
    def test_store_health_snapshot(self):
        """Test storing health snapshot"""
        record_id = self.store.store_health_snapshot(
            component='TestComponent',
            status='healthy',
            message='Test message',
            metrics={'cpu': 50, 'memory': 1024}
        )
        
        self.assertIsInstance(record_id, int)
        self.assertGreater(record_id, 0)
    
    def test_store_error(self):
        """Test storing error"""
        record_id = self.store.store_error(
            severity='error',
            component='TestComponent',
            message='Test error',
            details='Error details'
        )
        
        self.assertIsInstance(record_id, int)
        self.assertGreater(record_id, 0)
    
    def test_store_recovery(self):
        """Test storing recovery"""
        record_id = self.store.store_recovery(
            component='TestComponent',
            strategy='restart',
            status='success',
            duration=1.5,
            message='Recovered'
        )
        
        self.assertIsInstance(record_id, int)
        self.assertGreater(record_id, 0)
    
    def test_query_health_history(self):
        """Test querying health history"""
        # Store test data
        timestamp = time.time()
        self.store.store_health_snapshot(
            'Component1', 'healthy', 'OK',
            timestamp=timestamp
        )
        self.store.store_health_snapshot(
            'Component2', 'degraded', 'Warning',
            timestamp=timestamp + 1
        )
        
        # Query all
        records = self.store.query_health_history(
            timestamp - 10,
            timestamp + 10
        )
        self.assertEqual(len(records), 2)
        
        # Query by component
        records = self.store.query_health_history(
            timestamp - 10,
            timestamp + 10,
            component='Component1'
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['component'], 'Component1')
        
        # Query by status
        records = self.store.query_health_history(
            timestamp - 10,
            timestamp + 10,
            status='degraded'
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['status'], 'degraded')
    
    def test_query_errors(self):
        """Test querying error history"""
        timestamp = time.time()
        
        # Store errors
        self.store.store_error(
            'warning', 'Component1', 'Warning message',
            timestamp=timestamp
        )
        self.store.store_error(
            'error', 'Component2', 'Error message',
            timestamp=timestamp + 1
        )
        
        # Query all
        records = self.store.query_errors(
            timestamp - 10,
            timestamp + 10
        )
        self.assertEqual(len(records), 2)
        
        # Query by severity
        records = self.store.query_errors(
            timestamp - 10,
            timestamp + 10,
            severity='error'
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['severity'], 'error')
    
    def test_query_recoveries(self):
        """Test querying recovery history"""
        timestamp = time.time()
        
        # Store recoveries
        self.store.store_recovery(
            'Component1', 'restart', 'success', 1.0,
            timestamp=timestamp
        )
        self.store.store_recovery(
            'Component2', 'reload', 'failed', 0.5,
            timestamp=timestamp + 1
        )
        
        # Query all
        records = self.store.query_recoveries(
            timestamp - 10,
            timestamp + 10
        )
        self.assertEqual(len(records), 2)
        
        # Query by status
        records = self.store.query_recoveries(
            timestamp - 10,
            timestamp + 10,
            status='success'
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['status'], 'success')
    
    def test_get_statistics(self):
        """Test statistics computation"""
        timestamp = time.time()
        
        # Store test data
        self.store.store_health_snapshot(
            'Component1', 'healthy', 'OK',
            timestamp=timestamp
        )
        self.store.store_health_snapshot(
            'Component2', 'degraded', 'Warning',
            timestamp=timestamp + 1
        )
        self.store.store_error(
            'error', 'Component1', 'Error',
            timestamp=timestamp
        )
        self.store.store_recovery(
            'Component1', 'restart', 'success', 1.5,
            timestamp=timestamp
        )
        
        # Get statistics
        stats = self.store.get_statistics(
            timestamp - 10,
            timestamp + 10
        )
        
        self.assertEqual(stats['total_checks'], 2)
        self.assertEqual(stats['successful_checks'], 1)
        self.assertEqual(stats['total_errors'], 1)
        self.assertEqual(stats['total_recoveries'], 1)
        self.assertGreater(stats['success_rate'], 0)
        self.assertAlmostEqual(stats['avg_recovery_duration'], 1.5)
    
    def test_cleanup_old_data(self):
        """Test cleanup of old data"""
        # Store old data
        old_timestamp = time.time() - (10 * 86400)  # 10 days ago
        self.store.store_health_snapshot(
            'Component1', 'healthy', 'OK',
            timestamp=old_timestamp
        )
        self.store.store_error(
            'error', 'Component1', 'Error',
            timestamp=old_timestamp
        )
        
        # Store recent data
        recent_timestamp = time.time()
        self.store.store_health_snapshot(
            'Component2', 'healthy', 'OK',
            timestamp=recent_timestamp
        )
        
        # Cleanup data older than 7 days
        deleted = self.store.cleanup_old_data(retention_days=7)
        
        self.assertGreater(deleted, 0)
        
        # Verify old data is gone
        records = self.store.query_health_history(
            old_timestamp - 10,
            old_timestamp + 10
        )
        self.assertEqual(len(records), 0)
        
        # Verify recent data remains
        records = self.store.query_health_history(
            recent_timestamp - 10,
            recent_timestamp + 10
        )
        self.assertEqual(len(records), 1)
    
    def test_get_record_counts(self):
        """Test getting record counts"""
        # Store some data
        self.store.store_health_snapshot('C1', 'healthy', 'OK')
        self.store.store_health_snapshot('C2', 'healthy', 'OK')
        self.store.store_error('error', 'C1', 'Error')
        self.store.store_recovery('C1', 'restart', 'success', 1.0)
        
        counts = self.store.get_record_counts()
        
        self.assertEqual(counts['health_records'], 2)
        self.assertEqual(counts['error_records'], 1)
        self.assertEqual(counts['recovery_records'], 1)
        self.assertEqual(counts['total_records'], 4)
    
    def test_vacuum(self):
        """Test database vacuum"""
        # Store and delete data
        for i in range(100):
            self.store.store_health_snapshot(f'C{i}', 'healthy', 'OK')
        
        size_before = self.store.get_database_size()
        
        # Delete all data
        self.store.cleanup_old_data(retention_days=0)
        
        # Vacuum
        self.store.vacuum()
        
        size_after = self.store.get_database_size()
        
        # Size should be smaller after vacuum
        self.assertLess(size_after, size_before)
    
    def test_concurrent_access(self):
        """Test thread-safe concurrent access"""
        import threading
        
        def store_data(component_id):
            for i in range(10):
                self.store.store_health_snapshot(
                    f'Component{component_id}',
                    'healthy',
                    f'Message {i}'
                )
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=store_data, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all records stored
        counts = self.store.get_record_counts()
        self.assertEqual(counts['health_records'], 50)  # 5 threads * 10 records


class TestDataClasses(unittest.TestCase):
    """Test data classes"""
    
    def test_health_snapshot(self):
        """Test HealthSnapshot dataclass"""
        snapshot = HealthSnapshot(
            timestamp=time.time(),
            component='Test',
            status='healthy',
            message='OK',
            metrics={'cpu': 50}
        )
        
        data = snapshot.to_dict()
        self.assertIn('timestamp', data)
        self.assertEqual(data['component'], 'Test')
        self.assertEqual(data['status'], 'healthy')
    
    def test_error_record(self):
        """Test ErrorRecord dataclass"""
        record = ErrorRecord(
            timestamp=time.time(),
            severity='error',
            component='Test',
            message='Error message',
            details='Details'
        )
        
        data = record.to_dict()
        self.assertIn('timestamp', data)
        self.assertEqual(data['severity'], 'error')
    
    def test_recovery_record(self):
        """Test RecoveryRecord dataclass"""
        record = RecoveryRecord(
            timestamp=time.time(),
            component='Test',
            strategy='restart',
            status='success',
            duration=1.5,
            message='Recovered'
        )
        
        data = record.to_dict()
        self.assertIn('timestamp', data)
        self.assertEqual(data['strategy'], 'restart')
        self.assertAlmostEqual(data['duration'], 1.5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
