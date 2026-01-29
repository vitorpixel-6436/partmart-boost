#!/usr/bin/env python3
"""PartMart Boost - Main Entry Point

Version: 0.3.6 (Package 3.9a COMPLETE!)

Package 3.9a: Advanced Monitoring & Recovery System
  Stage 7.7b.6: System-wide error recovery ✅
    - 7.7b.6.1: ErrorReporter ✅
    - 7.7b.6.2: SystemHealthMonitor ✅
    - 7.7b.6.3: RecoveryCoordinator ✅
  Stage 7.7b.7: GUI Monitoring Integration ✅
    - MonitoringPanel widget ✅
    - Alert notifications ✅
    - Main window integration ✅
  Stage 7.7b.8: Advanced Features ✅
    - 7.7b.8.1: Historical Data System ✅
    - 7.7b.8.2: Charts & Visualization ✅
    - 7.7b.8.3: Search & Dashboard [SKIPPED]
  Stage 7.7b.9: Finalization & Integration ✅

Features:
  ✅ Centralized error reporting
  ✅ Automatic health monitoring
  ✅ Auto-recovery system
  ✅ Historical data storage
  ✅ Interactive charts
  ✅ Complete GUI integration
  ✅ Performance tracking

Usage:
    python src/main.py              # Normal launch
    python src/main.py --check      # Check dependencies
    python src/main.py --diagnose   # Diagnostic mode
    python src/main.py --minimal    # Minimal mode
    python src/main.py --no-gui     # No GUI
    python src/main.py --test       # Run tests
"""
import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

VERSION = "0.3.6"
PACKAGE = "3.9a"
STAGE = "PACKAGE 3.9a COMPLETE! ✅"


def print_banner():
    """Print application banner"""
    print("="*60)
    print(f"PartMart Boost v{VERSION} (Package {PACKAGE})")
    print(f"Status: {STAGE}")
    print("="*60)
    print()
    print("Package 3.9a: Advanced Monitoring & Recovery System")
    print("  ✅ Error Reporting")
    print("  ✅ Health Monitoring")
    print("  ✅ Auto-Recovery")
    print("  ✅ Historical Data")
    print("  ✅ Data Visualization")
    print("  ✅ Complete Integration")
    print()


def check_dependencies():
    """Check dependencies only"""
    print("Checking dependencies...\n")
    
    try:
        from core.dependency_checker import DependencyChecker
        
        checker = DependencyChecker()
        result = checker.check_all()
        
        if result.success:
            print("✅ All dependencies OK")
            return 0
        else:
            print(f"❌ Missing: {', '.join(result.missing)}")
            return 1
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def run_tests():
    """Run test suite"""
    print("Running Package 3.9a test suite...\n")
    
    try:
        # Add tests to path
        tests_dir = os.path.join(os.path.dirname(__file__), '..', 'tests')
        sys.path.insert(0, tests_dir)
        
        # Import and run tests
        from run_tests import run_tests as execute_tests
        
        success = execute_tests(verbosity=2)
        return 0 if success else 1
    
    except ImportError as e:
        print(f"❌ Tests not available: {e}")
        print("\nTo run tests, make sure tests/ directory exists.")
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
        description='PartMart Boost - Gaming Performance Optimizer'
    )
    parser.add_argument('--check', action='store_true',
                       help='Check dependencies only')
    parser.add_argument('--test', action='store_true',
                       help='Run test suite')
    parser.add_argument('--diagnose', action='store_true',
                       help='Run in diagnostic mode')
    parser.add_argument('--minimal', action='store_true',
                       help='Minimal initialization')
    parser.add_argument('--no-gui', action='store_true',
                       help='Run without GUI')
    parser.add_argument('--no-monitoring', action='store_true',
                       help='Disable monitoring system')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check dependencies only
    if args.check:
        return check_dependencies()
    
    # Run tests
    if args.test:
        return run_tests()
    
    print("Initializing monitoring system...\n")
    
    # Initialize monitoring system
    integrator = None
    if not args.no_monitoring:
        try:
            from core.monitoring_system_integrator import (
                MonitoringSystemIntegrator,
                MonitoringConfig
            )
            
            # Create configuration based on mode
            if args.minimal:
                config = MonitoringConfig(
                    enable_historical_data=False,
                    enable_data_aggregation=False,
                    enable_gui_integration=False
                )
            elif args.diagnose:
                config = MonitoringConfig(
                    health_check_interval=2.0,
                    collection_interval=30.0
                )
            else:
                config = MonitoringConfig()
            
            # Initialize integrator
            integrator = MonitoringSystemIntegrator(config)
            
            if integrator.initialize():
                print("")
                if integrator.start():
                    print("")
                    integrator.print_status()
                else:
                    print("❌ Failed to start monitoring system")
                    integrator = None
            else:
                print("❌ Failed to initialize monitoring system")
                integrator = None
        
        except Exception as e:
            print(f"⚠️ Monitoring system unavailable: {e}")
            integrator = None
    
    # Launch GUI (unless --no-gui)
    if not args.no_gui:
        print("\nLaunching GUI...\n")
        
        try:
            from PyQt6.QtWidgets import QApplication
            from ui.main_window_monitoring import MainWindowMonitoring
            
            app = QApplication(sys.argv)
            
            # Create window with monitoring integration
            window = MainWindowMonitoring(integrator)
            window.show()
            
            print("✅ GUI launched successfully")
            if integrator:
                print("✅ Monitoring panel active")
                print("✅ Alert notifications enabled")
                print("✅ Historical data collection active")
                print("✅ Chart visualization available")
            print("\nApplication running. Close window to exit.\n")
            
            # Run application
            result = app.exec()
            
            # Cleanup
            if integrator:
                print("\nShutting down monitoring system...")
                integrator.stop()
            
            return result
        
        except ImportError as e:
            print(f"❌ GUI not available: {e}")
            print("Running in console mode...")
            
            # Keep console open
            if integrator:
                try:
                    input("\nPress Enter to exit...")
                except KeyboardInterrupt:
                    pass
                finally:
                    integrator.stop()
            
            return 0
    
    else:
        print("\nRunning without GUI (--no-gui)")
        if integrator:
            try:
                input("\nPress Enter to exit...")
            except KeyboardInterrupt:
                pass
            finally:
                integrator.stop()
        
        return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
