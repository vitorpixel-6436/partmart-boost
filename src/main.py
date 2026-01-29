#!/usr/bin/env python3
"""PartMart Boost - Main Entry Point

Version: 0.3.5g (package 3.9a, stage 7.7b.9.1 COMPLETE!)

Package 3.9a Progress:
  Stage 7.7b.1-5: Core monitoring systems ✅
  Stage 7.7b.6: System-wide error recovery ✅
    - 7.7b.6.1: ErrorReporter ✅
    - 7.7b.6.2: SystemHealthMonitor ✅
    - 7.7b.6.3: RecoveryCoordinator ✅
  Stage 7.7b.7: GUI Monitoring Integration ✅
  Stage 7.7b.8: Advanced Features ✅
    - 7.7b.8.1: Historical Data System ✅
    - 7.7b.8.2: Charts & Visualization ✅
  Stage 7.7b.9: Finalization 🔄
    - 7.7b.9.1: Final Integration ✅
    - 7.7b.9.2: Complete Documentation ⏳
    - 7.7b.9.3: Final Testing ⏳
    - 7.7b.9.4: Package Release ⏳

USAGE:
    python src/main.py              # Full application with GUI
    python src/main.py --check      # Check dependencies
    python src/main.py --test       # Run test suite
    python src/main.py --no-gui     # Console mode only
"""
import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

VERSION = "0.3.5g"
PACKAGE = "3.9a"
STAGE = "7.7b.9.1 COMPLETE! (Final Integration)"


def print_banner():
    """Print application banner"""
    print("="*70)
    print(f"  PartMart Boost v{VERSION} (Package {PACKAGE})")
    print(f"  Stage: {STAGE}")
    print("  Gaming Performance Optimizer - USER READY")
    print("="*70)
    print()


def check_dependencies():
    """Check dependencies"""
    print("Checking dependencies...\n")
    
    dependencies = {
        'PyQt6': False,
        'pyqtgraph': False,
        'sqlite3': False
    }
    
    # Check PyQt6
    try:
        import PyQt6
        dependencies['PyQt6'] = True
    except ImportError:
        pass
    
    # Check pyqtgraph
    try:
        import pyqtgraph
        dependencies['pyqtgraph'] = True
    except ImportError:
        pass
    
    # Check sqlite3
    try:
        import sqlite3
        dependencies['sqlite3'] = True
    except ImportError:
        pass
    
    # Print results
    all_ok = True
    for name, available in dependencies.items():
        status = "✅" if available else "❌"
        print(f"{status} {name}: {'Available' if available else 'Missing'}")
        if not available:
            all_ok = False
    
    print()
    
    if not all_ok:
        print("⚠️  Some dependencies are missing. Install with:")
        print("   pip install PyQt6 pyqtgraph")
        return 1
    else:
        print("✅ All dependencies available!")
        return 0


def run_tests():
    """Run test suite"""
    print("Running test suite...\n")
    
    try:
        import unittest
        
        # Discover and run tests
        loader = unittest.TestLoader()
        tests_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            'tests'
        )
        
        if not os.path.exists(tests_dir):
            print("❌ Tests directory not found")
            return 1
        
        suite = loader.discover(tests_dir, pattern='test_*.py')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        print()
        if result.wasSuccessful():
            print("✅ All tests passed!")
            return 0
        else:
            print("❌ Some tests failed")
            return 1
    
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main entry point"""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='PartMart Boost - Gaming Performance Optimizer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py              Launch full application
  python src/main.py --check      Check dependencies
  python src/main.py --test       Run tests
  python src/main.py --no-gui     Console mode
        """
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check dependencies only'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run test suite'
    )
    parser.add_argument(
        '--no-gui',
        action='store_true',
        help='Run without GUI (console mode)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'PartMart Boost v{VERSION} (Package {PACKAGE})'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check dependencies
    if args.check:
        return check_dependencies()
    
    # Run tests
    if args.test:
        return run_tests()
    
    # Initialize system
    print("Initializing PartMart Boost...\n")
    
    try:
        from core.system_integrator_final import SystemIntegratorFinal
        
        # Create integrator
        integrator = SystemIntegratorFinal()
        
        # Initialize
        if not integrator.initialize():
            print("❌ Initialization failed")
            return 1
        
        # Start systems
        if not integrator.start():
            print("❌ Start failed")
            return 1
        
        # Print status
        integrator.print_status()
        
        # Launch GUI (unless --no-gui)
        if not args.no_gui:
            print("Launching GUI...\n")
            
            try:
                from PyQt6.QtWidgets import QApplication
                from ui.main_window_complete import MainWindowComplete
                
                app = QApplication(sys.argv)
                app.setApplicationName("PartMart Boost")
                app.setApplicationVersion(VERSION)
                
                # Create window
                window = MainWindowComplete(integrator)
                window.show()
                
                print("✅ GUI launched successfully")
                print("\n✅ Application ready for use!")
                print("   - Status monitoring active")
                print("   - Historical data collection running")
                print("   - Charts available")
                print("   - Auto-recovery enabled")
                print("\nClose window to exit.\n")
                
                # Run application
                exit_code = app.exec()
                
                # Cleanup
                print("\nShutting down...")
                integrator.stop()
                
                return exit_code
            
            except ImportError as e:
                print(f"❌ GUI not available: {e}")
                print("\nInstall GUI dependencies with:")
                print("   pip install PyQt6 pyqtgraph")
                print("\nOr run in console mode with --no-gui")
                integrator.stop()
                return 1
        
        else:
            # Console mode
            print("✅ Running in console mode (--no-gui)")
            print("\nPress Ctrl+C to stop...\n")
            
            try:
                # Keep running
                import time
                while True:
                    time.sleep(1)
            
            except KeyboardInterrupt:
                print("\n\nStopping...")
                integrator.stop()
                return 0
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
