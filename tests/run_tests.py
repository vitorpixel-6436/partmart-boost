#!/usr/bin/env python3
"""Test Runner

Version: 0.3.5i (package 3.9a, stage 7.7a/7.7)

Runs all unit tests and generates report.

Usage:
    python tests/run_tests.py              # Run all tests
    python tests/run_tests.py -v           # Verbose output
    python tests/run_tests.py --fast       # Skip slow tests
"""
import sys
import os
import unittest
import time
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))


class ColoredTextTestResult(unittest.TextTestResult):
    """Test result with colored output"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_times = {}
    
    def startTest(self, test):
        super().startTest(test)
        self.test_times[test] = time.time()
    
    def addSuccess(self, test):
        super().addSuccess(test)
        elapsed = time.time() - self.test_times[test]
        if self.showAll:
            self.stream.write(f" \033[92m✓\033[0m ({elapsed:.3f}s)\n")
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.showAll:
            self.stream.write(" \033[91m✗ ERROR\033[0m\n")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.showAll:
            self.stream.write(" \033[91m✗ FAIL\033[0m\n")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.showAll:
            self.stream.write(f" \033[93m⊘ SKIP\033[0m: {reason}\n")


def run_tests(verbosity=1, pattern='test_*.py', fast=False):
    """Run all tests
    
    Args:
        verbosity: Verbosity level (0-2)
        pattern: Test file pattern
        fast: Skip slow tests
    
    Returns:
        True if all tests passed
    """
    # Discover tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern=pattern)
    
    # Run tests
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        resultclass=ColoredTextTestResult
    )
    
    print("="*70)
    print("PartMart Boost Test Suite")
    print("Version: 0.3.5i (Package 3.9a, Stage 7.7a/7.7)")
    print("="*70)
    print()
    
    start_time = time.time()
    result = runner.run(suite)
    elapsed = time.time() - start_time
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"\033[92mPassed: {result.testsRun - len(result.failures) - len(result.errors)}\033[0m")
    
    if result.failures:
        print(f"\033[91mFailed: {len(result.failures)}\033[0m")
    
    if result.errors:
        print(f"\033[91mErrors: {len(result.errors)}\033[0m")
    
    if result.skipped:
        print(f"\033[93mSkipped: {len(result.skipped)}\033[0m")
    
    print(f"\nTime: {elapsed:.2f}s")
    print("="*70)
    
    # Print failures and errors
    if result.failures:
        print("\n\033[91mFAILURES:\033[0m")
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)
    
    if result.errors:
        print("\n\033[91mERRORS:\033[0m")
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)
    
    # Return success status
    return result.wasSuccessful()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run PartMart Boost tests')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--fast', action='store_true',
                       help='Skip slow tests')
    parser.add_argument('--pattern', default='test_*.py',
                       help='Test file pattern')
    
    args = parser.parse_args()
    
    verbosity = 2 if args.verbose else 1
    
    success = run_tests(
        verbosity=verbosity,
        pattern=args.pattern,
        fast=args.fast
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
