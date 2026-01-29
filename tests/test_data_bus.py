#!/usr/bin/env python3
"""DataBus Unit Tests

Version: 0.3.5i (package 3.9a, stage 7.7a/7.7)
"""
import sys
import os
import unittest
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from data_bus import DataBus, Message


class TestDataBus(unittest.TestCase):
    """Test DataBus functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bus = DataBus(max_history=100)
    
    def tearDown(self):
        """Clean up"""
        pass
    
    def test_publish_and_subscribe(self):
        """Test basic publish/subscribe"""
        received = []
        
        def callback(msg):
            received.append(msg.data)
        
        self.bus.subscribe('test.topic', callback)
        self.bus.publish('test.topic', {'value': 42})
        
        # Small delay for async delivery
        time.sleep(0.01)
        
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['value'], 42)
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers to same topic"""
        received1 = []
        received2 = []
        
        self.bus.subscribe('test.topic', lambda msg: received1.append(msg.data))
        self.bus.subscribe('test.topic', lambda msg: received2.append(msg.data))
        
        self.bus.publish('test.topic', {'value': 42})
        time.sleep(0.01)
        
        self.assertEqual(len(received1), 1)
        self.assertEqual(len(received2), 1)
    
    def test_wildcard_subscription(self):
        """Test wildcard subscriptions"""
        received = []
        
        self.bus.subscribe('test.*', lambda msg: received.append(msg.topic))
        
        self.bus.publish('test.topic1', {})
        self.bus.publish('test.topic2', {})
        self.bus.publish('other.topic', {})  # Should not match
        
        time.sleep(0.01)
        
        self.assertEqual(len(received), 2)
        self.assertIn('test.topic1', received)
        self.assertIn('test.topic2', received)
    
    def test_priority(self):
        """Test message priority"""
        received = []
        
        self.bus.subscribe('test.*', lambda msg: received.append(msg.data))
        
        # Publish with different priorities
        self.bus.publish('test.low', {'priority': 'low'}, priority=1)
        self.bus.publish('test.high', {'priority': 'high'}, priority=10)
        self.bus.publish('test.medium', {'priority': 'medium'}, priority=5)
        
        time.sleep(0.05)
        
        # High priority should be first
        self.assertEqual(received[0]['priority'], 'high')
    
    def test_unsubscribe(self):
        """Test unsubscribing"""
        received = []
        
        sub_id = self.bus.subscribe('test.topic', lambda msg: received.append(msg.data))
        
        self.bus.publish('test.topic', {'value': 1})
        time.sleep(0.01)
        
        self.bus.unsubscribe(sub_id)
        
        self.bus.publish('test.topic', {'value': 2})
        time.sleep(0.01)
        
        # Should only receive first message
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['value'], 1)
    
    def test_get_history(self):
        """Test message history"""
        self.bus.publish('test.topic1', {'value': 1})
        self.bus.publish('test.topic2', {'value': 2})
        
        time.sleep(0.01)
        
        history = self.bus.get_history()
        
        self.assertGreaterEqual(len(history), 2)
    
    def test_get_stats(self):
        """Test getting statistics"""
        self.bus.subscribe('test.topic', lambda msg: None)
        self.bus.publish('test.topic', {})
        
        time.sleep(0.01)
        
        stats = self.bus.get_stats()
        
        self.assertIn('subscriptions', stats)
        self.assertIn('messages_published', stats)
        self.assertGreater(stats['subscriptions'], 0)
        self.assertGreater(stats['messages_published'], 0)
    
    def test_clear_history(self):
        """Test clearing history"""
        self.bus.publish('test.topic', {})
        time.sleep(0.01)
        
        self.bus.clear_history()
        
        history = self.bus.get_history()
        self.assertEqual(len(history), 0)


if __name__ == '__main__':
    unittest.main()
