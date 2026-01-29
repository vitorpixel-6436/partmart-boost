#!/usr/bin/env python3
"""ErrorReporter Tests

Version: 0.3.5q (package 3.9a, stage 7.7b.6.1/7.7)
"""
import sys
import os
import unittest
import tempfile
import shutil
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from error_reporter import (
    ErrorReporter,
    ErrorSeverity,
    ErrorRecord
)


class TestErrorReporter(unittest.TestCase):
    """Test ErrorReporter functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.reporter = ErrorReporter(max_records=100, aggregate=True)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test reporter initialization"""
        stats = self.reporter.get_statistics()
        self.assertEqual(stats['total_errors'], 0)
        self.assertEqual(stats['current_errors'], 0)
        self.assertTrue(stats['aggregation_enabled'])
    
    def test_report_error(self):
        """Test error reporting"""
        result = self.reporter.report_error(
            component='TestComponent',
            severity=ErrorSeverity.ERROR,
            message='Test error message'
        )
        
        self.assertTrue(result)
        
        stats = self.reporter.get_statistics()
        self.assertEqual(stats['total_errors'], 1)
        self.assertEqual(stats['current_errors'], 1)
    
    def test_error_aggregation(self):
        """Test error aggregation (deduplication)"""
        # Report same error multiple times
        for i in range(5):
            self.reporter.report_error(
                component='TestComp',
                severity=ErrorSeverity.ERROR,
                message='Same error'
            )
        
        stats = self.reporter.get_statistics()
        self.assertEqual(stats['total_errors'], 5)  # Total count
        self.assertEqual(stats['current_errors'], 1)  # Aggregated to 1
        
        # Get error record
        errors = self.reporter.get_errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].count, 5)  # Count should be 5
    
    def test_no_aggregation(self):
        """Test without aggregation"""
        reporter = ErrorReporter(max_records=100, aggregate=False)
        
        # Report same error multiple times
        for i in range(5):
            reporter.report_error(
                component='TestComp',
                severity=ErrorSeverity.ERROR,
                message='Same error'
            )
        
        stats = reporter.get_statistics()
        self.assertEqual(stats['total_errors'], 5)
        self.assertEqual(stats['current_errors'], 5)  # All stored separately
    
    def test_report_exception(self):
        """Test exception reporting"""
        try:
            raise ValueError("Test exception")
        except Exception as e:
            result = self.reporter.report_exception(
                component='TestComp',
                exception=e,
                severity=ErrorSeverity.ERROR
            )
            
            self.assertTrue(result)
        
        errors = self.reporter.get_errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].exception_type, 'ValueError')
        self.assertIsNotNone(errors[0].traceback)
    
    def test_statistics(self):
        """Test statistics tracking"""
        # Report errors from different components
        self.reporter.report_error('Comp1', ErrorSeverity.ERROR, 'Error 1')
        self.reporter.report_error('Comp1', ErrorSeverity.WARNING, 'Warning 1')
        self.reporter.report_error('Comp2', ErrorSeverity.CRITICAL, 'Critical 1')
        self.reporter.report_error('Comp2', ErrorSeverity.ERROR, 'Error 2')
        
        stats = self.reporter.get_statistics()
        
        # Check component stats
        self.assertEqual(stats['errors_by_component']['Comp1'], 2)
        self.assertEqual(stats['errors_by_component']['Comp2'], 2)
        
        # Check severity stats
        self.assertEqual(stats['errors_by_severity']['error'], 2)
        self.assertEqual(stats['errors_by_severity']['warning'], 1)
        self.assertEqual(stats['errors_by_severity']['critical'], 1)
    
    def test_get_errors_filtering(self):
        """Test error filtering"""
        # Report various errors
        self.reporter.report_error('Comp1', ErrorSeverity.ERROR, 'Error 1')
        self.reporter.report_error('Comp1', ErrorSeverity.WARNING, 'Warning 1')
        self.reporter.report_error('Comp2', ErrorSeverity.ERROR, 'Error 2')
        self.reporter.report_error('Comp2', ErrorSeverity.CRITICAL, 'Critical 1')
        
        # Filter by component
        errors = self.reporter.get_errors(component='Comp1')
        self.assertEqual(len(errors), 2)
        self.assertTrue(all(e.component == 'Comp1' for e in errors))
        
        # Filter by severity
        errors = self.reporter.get_errors(severity=ErrorSeverity.ERROR)
        self.assertEqual(len(errors), 2)
        self.assertTrue(all(e.severity == ErrorSeverity.ERROR for e in errors))
        
        # Filter by minimum severity
        errors = self.reporter.get_errors(min_severity=ErrorSeverity.ERROR)
        self.assertEqual(len(errors), 3)  # ERROR and CRITICAL
        
        # Apply limit
        errors = self.reporter.get_errors(limit=2)
        self.assertEqual(len(errors), 2)
    
    def test_callbacks(self):
        """Test error callbacks"""
        callback_data = []
        
        def callback(error: ErrorRecord):
            callback_data.append(error.message)
        
        # Add callback
        callback_id = self.reporter.add_callback(callback)
        self.assertGreaterEqual(callback_id, 0)
        
        # Report error
        self.reporter.report_error('Test', ErrorSeverity.ERROR, 'Test message')
        
        # Check callback was called
        self.assertEqual(len(callback_data), 1)
        self.assertEqual(callback_data[0], 'Test message')
    
    def test_callback_error_isolation(self):
        """Test callback errors are isolated"""
        def bad_callback(error):
            raise Exception("Callback error!")
        
        def good_callback(error):
            pass  # Should still be called
        
        self.reporter.add_callback(bad_callback)
        self.reporter.add_callback(good_callback)
        
        # Should not raise
        result = self.reporter.report_error('Test', ErrorSeverity.ERROR, 'Test')
        self.assertTrue(result)
    
    def test_generate_json_report(self):
        """Test JSON report generation"""
        self.reporter.report_error('Test', ErrorSeverity.ERROR, 'Test error')
        
        report = self.reporter.generate_report(format='json')
        
        # Parse JSON
        data = json.loads(report)
        
        self.assertIn('generated_at', data)
        self.assertIn('statistics', data)
        self.assertIn('errors', data)
        self.assertEqual(len(data['errors']), 1)
    
    def test_generate_text_report(self):
        """Test text report generation"""
        self.reporter.report_error('Test', ErrorSeverity.ERROR, 'Test error')
        
        report = self.reporter.generate_report(format='text')
        
        self.assertIn('ERROR REPORT', report)
        self.assertIn('STATISTICS', report)
        self.assertIn('Test error', report)
    
    def test_generate_html_report(self):
        """Test HTML report generation"""
        self.reporter.report_error('Test', ErrorSeverity.ERROR, 'Test error')
        
        report = self.reporter.generate_report(format='html')
        
        self.assertIn('<!DOCTYPE html>', report)
        self.assertIn('Error Report', report)
        self.assertIn('Test error', report)
    
    def test_export_report(self):
        """Test report export to file"""
        self.reporter.report_error('Test', ErrorSeverity.ERROR, 'Test error')
        
        # Export JSON
        json_path = os.path.join(self.temp_dir, 'report.json')
        result = self.reporter.export_report(json_path, format='json')
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(json_path))
        
        # Check file content
        with open(json_path, 'r') as f:
            data = json.load(f)
            self.assertIn('errors', data)
    
    def test_clear_all(self):
        """Test clearing all errors"""
        # Report some errors
        for i in range(5):
            self.reporter.report_error('Test', ErrorSeverity.ERROR, f'Error {i}')
        
        stats = self.reporter.get_statistics()
        self.assertEqual(stats['total_errors'], 5)
        
        # Clear all
        self.reporter.clear()
        
        errors = self.reporter.get_errors()
        self.assertEqual(len(errors), 0)
    
    def test_clear_filtered(self):
        """Test clearing filtered errors"""
        # Report errors
        self.reporter.report_error('Comp1', ErrorSeverity.ERROR, 'Error 1')
        self.reporter.report_error('Comp2', ErrorSeverity.ERROR, 'Error 2')
        self.reporter.report_error('Comp1', ErrorSeverity.WARNING, 'Warning 1')
        
        # Clear Comp1 only
        self.reporter.clear(component='Comp1')
        
        errors = self.reporter.get_errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].component, 'Comp2')
    
    def test_max_records_limit(self):
        """Test max records limit (without aggregation)"""
        reporter = ErrorReporter(max_records=10, aggregate=False)
        
        # Report more than max
        for i in range(20):
            reporter.report_error('Test', ErrorSeverity.ERROR, f'Error {i}')
        
        errors = reporter.get_errors()
        self.assertEqual(len(errors), 10)  # Should be limited to 10
    
    def test_error_severity_comparison(self):
        """Test error severity comparison"""
        self.assertTrue(ErrorSeverity.DEBUG < ErrorSeverity.INFO)
        self.assertTrue(ErrorSeverity.WARNING < ErrorSeverity.ERROR)
        self.assertTrue(ErrorSeverity.ERROR < ErrorSeverity.CRITICAL)
    
    def test_error_record_to_dict(self):
        """Test ErrorRecord to_dict conversion"""
        self.reporter.report_error(
            component='Test',
            severity=ErrorSeverity.ERROR,
            message='Test message',
            details='Test details'
        )
        
        errors = self.reporter.get_errors()
        error_dict = errors[0].to_dict()
        
        self.assertIn('timestamp', error_dict)
        self.assertIn('datetime', error_dict)
        self.assertIn('component', error_dict)
        self.assertIn('severity', error_dict)
        self.assertIn('message', error_dict)
        self.assertEqual(error_dict['component'], 'Test')
        self.assertEqual(error_dict['message'], 'Test message')


if __name__ == '__main__':
    unittest.main()
