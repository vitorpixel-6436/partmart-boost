#!/usr/bin/env python3
"""PartMart Boost - Main Entry Point

Version: 0.3.5j (package 3.9a, stage 7.7b/7.7)

Package 3.9a Stage 7.7b: Error handling and robustness.

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

VERSION = "0.3.5j"
PACKAGE = "3.9a"
STAGE = "7.7b/7.7"


def print_banner():
    """Print application banner"""
    print("="*60)
    print(f"PartMart Boost v{VERSION} (Package {PACKAGE}, Stage {STAGE})")
    print("="*60)
    print()


def check_dependencies():
    """Check dependencies only"""
    print("Checking dependencies...\n")
    
    try:
        from core.dependency_checker import DependencyChecker
        from core.logger import Logger
        
        logger = Logger.get_instance()
        logger.info("Checking dependencies", component="Main")
        
        checker = DependencyChecker()
        result = checker.check_all()
        
        if result.success:
            print("✅ All dependencies OK")
            logger.info("All dependencies satisfied")
            return 0
        else:
            print(f"❌ Missing: {', '.join(result.missing)}")
            logger.error(f"Missing dependencies: {result.missing}")
            return 1
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def run_tests():
    """Run test suite"""
    print("Running test suite...\n")
    
    try:
        from core.logger import Logger
        logger = Logger.get_instance()
        logger.info("Starting test suite", component="Main")
        
        # Add tests to path
        tests_dir = os.path.join(os.path.dirname(__file__), '..', 'tests')
        sys.path.insert(0, tests_dir)
        
        # Import and run tests
        from run_tests import run_tests as execute_tests
        
        success = execute_tests(verbosity=2)
        
        if success:
            logger.info("All tests passed")
        else:
            logger.error("Some tests failed")
        
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
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Initialize logger early
    try:
        from core.logger import Logger, LogLevel
        logger = Logger.get_instance()
        
        if args.debug:
            logger.set_level(LogLevel.DEBUG)
            logger.debug("Debug logging enabled")
        
        logger.info(f"PartMart Boost v{VERSION} starting", component="Main")
    except Exception as e:
        print(f"Warning: Could not initialize logger: {e}")
        logger = None
    
    # Check dependencies only
    if args.check:
        return check_dependencies()
    
    # Run tests
    if args.test:
        return run_tests()
    
    # Determine mode
    if args.diagnose:
        mode = 'diagnostic'
    elif args.minimal:
        mode = 'minimal'
    else:
        mode = 'full'
    
    if logger:
        logger.info(f"Initialization mode: {mode}", component="Main")
    
    print(f"Initializing system...\n")
    
    # Initialize system
    try:
        from core.system_init import SystemInitializer
        from core.error_handler import ErrorHandler
        
        # Initialize error handler
        error_handler = ErrorHandler.get_instance()
        
        if logger:
            logger.info("Error handler initialized", component="Main")
        
        init = SystemInitializer(mode=mode)
        result = init.initialize()
        
        # Print summary
        init.print_summary()
        
        if not result.success:
            error_msg = f"System initialization failed: {result.error}"
            print(f"❌ {error_msg}")
            
            if logger:
                logger.critical(error_msg, component="Main")
            
            return 1
        
        # Print application status
        integrator = init.get_integrator()
        if integrator:
            integrator.print_status()
        
        # Launch GUI (unless --no-gui)
        if not args.no_gui:
            print("Launching GUI...\n")
            
            if logger:
                logger.info("Launching GUI", component="Main")
            
            try:
                from PyQt6.QtWidgets import QApplication
                from ui.main_window_stage7 import MainWindowStage7
                
                app = QApplication(sys.argv)
                
                # Create window with integrator
                window = MainWindowStage7(integrator)
                window.show()
                
                print("✅ GUI launched successfully")
                print("\nApplication running. Close window to exit.\n")
                
                if logger:
                    logger.info("GUI launched successfully", component="Main")
                
                return_code = app.exec()
                
                if logger:
                    logger.info(f"Application exited with code {return_code}", component="Main")
                
                return return_code
            
            except ImportError as e:
                error_msg = f"GUI not available: {e}"
                print(f"❌ {error_msg}")
                print("Running in console mode...")
                
                if logger:
                    logger.warning(error_msg, component="Main")
                
                # Keep console open
                input("Press Enter to exit...")
                return 0
            
            except Exception as e:
                error_msg = f"GUI launch failed: {e}"
                print(f"❌ {error_msg}")
                
                if logger:
                    logger.error(error_msg, component="Main")
                
                import traceback
                traceback.print_exc()
                return 1
        
        else:
            print("Running without GUI (--no-gui)")
            
            if logger:
                logger.info("Running in no-GUI mode", component="Main")
            
            input("Press Enter to exit...")
            return 0
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        
        if logger:
            logger.info("Interrupted by user", component="Main")
        
        return 130
    
    except Exception as e:
        error_msg = f"Fatal error: {e}"
        print(f"❌ {error_msg}")
        
        if logger:
            logger.critical(error_msg, component="Main")
        
        import traceback
        traceback.print_exc()
        
        # Print error summary if handler available
        try:
            from core.error_handler import ErrorHandler
            handler = ErrorHandler.get_instance()
            handler.print_summary()
        except:
            pass
        
        return 1


if __name__ == '__main__':
    sys.exit(main())
