#!/usr/bin/env python3
"""PartMart Boost - Main Entry Point

Version: 0.3.5e (package 3.9a, stage 7.1/7.7)

Main application entry point with proper initialization.

Package 3.9a Stage 7.1: System initialization and bootstrap.

Usage:
    python src/main.py                  # Normal startup
    python src/main.py --diagnose       # Diagnostic mode
    python src/main.py --minimal        # Minimal mode
    python src/main.py --check          # Check dependencies
"""
import sys
import os
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

print("="*60)
print("PartMart Boost v0.3.5e (Package 3.9a, Stage 7.1)")
print("="*60)
print()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PartMart Boost - PC Performance Optimizer')
    parser.add_argument('--diagnose', action='store_true', help='Diagnostic mode')
    parser.add_argument('--minimal', action='store_true', help='Minimal mode')
    parser.add_argument('--check', action='store_true', help='Check dependencies only')
    parser.add_argument('--no-gui', action='store_true', help='Run without GUI')
    
    args = parser.parse_args()
    
    # Check dependencies only
    if args.check:
        print("Checking dependencies...\n")
        
        try:
            from core.dependency_checker import DependencyChecker
            checker = DependencyChecker()
            checker.print_report()
            
            result = checker.check_all()
            return 0 if result.success else 1
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    # Initialize system
    print("Initializing system...\n")
    
    try:
        from core.system_init import SystemInitializer
        
        # Determine mode
        if args.diagnose:
            mode = 'diagnostic'
        elif args.minimal:
            mode = 'minimal'
        else:
            mode = 'full'
        
        # Initialize
        initializer = SystemInitializer(mode=mode)
        init_result = initializer.initialize()
        
        # Print summary
        initializer.print_summary()
        
        if not init_result.success:
            print(f"❌ Initialization failed: {init_result.error}")
            print("\nTry running with --check to diagnose dependencies")
            return 1
        
        # Get integrator
        integrator = initializer.get_integrator()
        
        if not integrator:
            print("❌ Failed to create integrator")
            return 1
        
        # Print status
        integrator.print_status()
        
        # Launch GUI (if available and not disabled)
        if not args.no_gui:
            print("Launching GUI...\n")
            
            try:
                from PyQt6.QtWidgets import QApplication
                from gui.main_window import MainWindow
                
                # Create Qt application
                app = QApplication(sys.argv)
                app.setApplicationName("PartMart Boost")
                app.setApplicationVersion("0.3.5e")
                
                # Create main window with integrator
                window = MainWindow(integrator=integrator)
                window.show()
                
                print("✅ GUI launched successfully\n")
                print("Application running. Close window to exit.")
                
                # Run event loop
                return app.exec()
            
            except ImportError as e:
                print(f"❌ GUI not available: {e}")
                print("\nTry installing PyQt6:")
                print("   pip install PyQt6")
                print("\nOr run without GUI:")
                print("   python src/main.py --no-gui")
                return 1
            
            except Exception as e:
                print(f"❌ GUI error: {e}")
                import traceback
                traceback.print_exc()
                return 1
        
        else:
            # No GUI mode
            print("Running without GUI (--no-gui)")
            print("\nSystem is running. Press Ctrl+C to exit.")
            
            try:
                # Keep running
                import time
                while True:
                    time.sleep(1)
            
            except KeyboardInterrupt:
                print("\n\nShutting down...")
                return 0
    
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
