#!/usr/bin/env python3
"""Tests for DataAggregator

Version: 0.3.5e (package 3.9a, stage 7.7b.8.1/7.7b.8)
"""
import unittest
import tempfile
import os
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.historical_data_store import HistoricalDataStore, DataRetentionPolicy
from core.data_aggregator import DataAggregator, AggregationConfig


class TestDataAggregator(unittest.TestCase):
    """Test DataAggregator"""
    
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
        
        self.config = AggregationConfig(
            collection_interval=0.5,  # Fast for testing
            aggregation_interval=1.0
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_initialization(self):
        """Test aggregator initialization"""
        aggregator = DataAggregator(self.store, config=self.config)
        
        self.assertFalse(aggregator.is_running())
        self.assertEqual(aggregator._collections_count, 0)
    
    def test_start_stop_collection(self):
        """Test starting and stopping collection"""
        aggregator = DataAggregator(self.store, config=self.config)
        
        # Start
        aggregator.start_collection()
        self.assertTrue(aggregator.is_running())
        
        # Wait a bit
        time.sleep(0.2)
        
        # Stop
        aggregator.stop_collection()
        self.assertFalse(aggregator.is_running())
    
    def test_collect_now(self):
        """Test immediate collection"""
        # Mock health monitor
        mock_health_monitor = Mock()
        mock_health_monitor.get_system_health.return_value = {
            'status': 'healthy',
            'total_components': 2,
            'healthy_count': 2,
            'statistics': {'uptime': 100},
            'components': {
                'Component1': {
                    'status': 'healthy',
                    'message': 'OK',
                    'metrics': {'cpu': 50}
                }
            }
        }
        
        aggregator = DataAggregator(
            self.store,
            health_monitor=mock_health_monitor,
            config=self.config
        )
        
        # Collect
        aggregator.collect_now()
        
        # Verify data stored
        counts = self.store.get_record_counts()
        self.assertGreater(counts['health_records'], 0)
        
        # Verify health monitor was called
        mock_health_monitor.get_system_health.assert_called()
    
    def test_collect_error_data(self):
        """Test collecting error data"""
        # Mock error reporter
        mock_error_reporter = Mock()
        mock_error_reporter.get_errors.return_value = [
            {
                'timestamp': time.time(),
                'severity': 'error',
                'component': 'Component1',
                'message': 'Test error',
                'details': 'Error details'
            }
        ]
        
        aggregator = DataAggregator(
            self.store,
            error_reporter=mock_error_reporter,
            config=self.config
        )
        
        # Collect
        aggregator.collect_now()
        
        # Verify data stored
        counts = self.store.get_record_counts()
        self.assertGreater(counts['error_records'], 0)
    
    def test_collect_recovery_data(self):
        """Test collecting recovery data"""
        # Mock recovery coordinator
        mock_recovery = Mock()
        mock_recovery.get_recovery_history.return_value = [
            {
                'timestamp': time.time(),
                'component': 'Component1',
                'strategy': 'restart',
                'status': 'success',
                'duration': 1.5,
                'message': 'Recovered'
            }
        ]
        
        aggregator = DataAggregator(
            self.store,
            recovery_coordinator=mock_recovery,
            config=self.config
        )
        
        # Collect
        aggregator.collect_now()
        
        # Verify data stored
        counts = self.store.get_record_counts()
        self.assertGreater(counts['recovery_records'], 0)
    
    def test_periodic_collection(self):
        """Test periodic automatic collection"""
        mock_health_monitor = Mock()
        mock_health_monitor.get_system_health.return_value = {
            'status': 'healthy',
            'total_components': 1,
            'healthy_count': 1,
            'statistics': {},
            'components': {}
        }
        
        aggregator = DataAggregator(
            self.store,
            health_monitor=mock_health_monitor,
            config=self.config
        )
        
        # Start collection
        aggregator.start_collection()
        
        # Wait for multiple collections
        time.sleep(1.5)  # Should collect 2-3 times
        
        # Stop
        aggregator.stop_collection()
        
        # Verify multiple collections occurred
        stats = aggregator.get_statistics()
        self.assertGreater(stats['collections_count'], 1)
    
    def test_get_statistics(self):
        """Test getting aggregator statistics"""
        aggregator = DataAggregator(self.store, config=self.config)
        
        aggregator.collect_now()
        aggregator.aggregate_now()
        
        stats = aggregator.get_statistics()
        
        self.assertIn('is_running', stats)
        self.assertIn('collections_count', stats)
        self.assertIn('aggregations_count', stats)
        self.assertEqual(stats['collections_count'], 1)
        self.assertEqual(stats['aggregations_count'], 1)
    
    def test_get_time_range_statistics(self):
        """Test getting time range statistics"""
        aggregator = DataAggregator(self.store, config=self.config)
        
        # Store some test data
        timestamp = time.time()
        self.store.store_health_snapshot('C1', 'healthy', 'OK', timestamp=timestamp)
        self.store.store_error('error', 'C1', 'Error', timestamp=timestamp)
        
        # Get statistics
        stats = aggregator.get_time_range_statistics(
            timestamp - 10,
            timestamp + 10
        )
        
        self.assertIn('total_checks', stats)
        self.assertIn('total_errors', stats)
        self.assertGreater(stats['total_checks'], 0)
        self.assertGreater(stats['total_errors'], 0)
    
    def test_cleanup_old_data(self):
        """Test cleanup through aggregator"""
        aggregator = DataAggregator(self.store, config=self.config)
        
        # Store old data
        old_timestamp = time.time() - (10 * 86400)  # 10 days ago
        self.store.store_health_snapshot('C1', 'healthy', 'OK', timestamp=old_timestamp)
        
        # Cleanup
        deleted = aggregator.cleanup_old_data(retention_days=7)
        
        self.assertGreater(deleted, 0)
    
    def test_error_handling(self):
        """Test error handling during collection"""
        # Mock that raises exception
        mock_health_monitor = Mock()
        mock_health_monitor.get_system_health.side_effect = Exception("Test error")
        
        aggregator = DataAggregator(
            self.store,
            health_monitor=mock_health_monitor,
            config=self.config
        )
        
        # Should not crash
        aggregator.collect_now()
        
        # Error should be tracked
        # (in real implementation, we might want to add error tracking)
    
    def test_configuration_options(self):
        """Test configuration options"""
        config = AggregationConfig(
            collection_interval=10.0,
            aggregation_interval=3600.0,
            enable_health_collection=False,
            enable_error_collection=True,
            enable_recovery_collection=False
        )
        
        aggregator = DataAggregator(self.store, config=config)
        
        stats = aggregator.get_statistics()
        self.assertEqual(stats['collection_interval'], 10.0)
        self.assertEqual(stats['aggregation_interval'], 3600.0)


class TestAggregationConfig(unittest.TestCase):
    """Test AggregationConfig"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = AggregationConfig()
        
        self.assertEqual(config.collection_interval, 60.0)
        self.assertEqual(config.aggregation_interval, 3600.0)
        self.assertTrue(config.enable_health_collection)
        self.assertTrue(config.enable_error_collection)
        self.assertTrue(config.enable_recovery_collection)
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = AggregationConfig(
            collection_interval=30.0,
            aggregation_interval=1800.0,
            enable_health_collection=False
        )
        
        self.assertEqual(config.collection_interval, 30.0)
        self.assertEqual(config.aggregation_interval, 1800.0)
        self.assertFalse(config.enable_health_collection)


if __name__ == '__main__':
    unittest.main(verbosity=2)
