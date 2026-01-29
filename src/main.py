#!/usr/bin/env python3
"""PartMart Boost - Main Entry Point

Version: 0.3.5e (package 3.9a, stage 7.3/7.7)

Package 3.9a Stage 7.3: Complete frontend integration.

Usage:
    python src/main.py              # Normal launch
    python src/main.py --check      # Check dependencies
    python src/main.py --diagnose   # Diagnostic mode
    python src/main.py --minimal    # Minimal mode
    python src/main.py --no-gui     # No GUI
"""
import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

VERSION = "0.3.5e"
PACKAGE = "3.9a"
STAGE = "7.3/7.7"


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


def main():
    """Main entry point"""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='PartMart Boost - Gaming Performance Optimizer'
    )
    parser.add_argument('--check', action='store_true',
                       help='Check dependencies only')
    parser.add_argument('--diagnose', action='store_true',
                       help='Run in diagnostic mode')
    parser.add_argument('--minimal', action='store_true',
                       help='Minimal initialization')
    parser.add_argument('--no-gui', action='store_true',
                       help='Run without GUI')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check dependencies only
    if args.check:
        return check_dependencies()
    
    # Determine mode
    if args.diagnose:
        mode = 'diagnostic'
    elif args.minimal:
        mode = 'minimal'
    else:
        mode = 'full'
    
    print(f"Initializing system...\n")
    
    # Initialize system
    try:
        from core.system_init import SystemInitializer
        
        init = SystemInitializer(mode=mode)
        result = init.initialize()
        
        # Print summary
        init.print_summary()
        
        if not result.success:
            print(f"❌ System initialization failed: {result.error}")
            return 1
        
        # Print application status
        integrator = init.get_integrator()
        if integrator:
            integrator.print_status()
        
        # Launch GUI (unless --no-gui)
        if not args.no-gui:
            print("Launching GUI...\n")
            
            try:
                from PyQt6.QtWidgets import QApplication
                from ui.main_window_stage7 import MainWindowStage7
                
                app = QApplication(sys.argv)
                
                # Create window with integrator
                window = MainWindowStage7(integrator)
                window.show()
                
                print("✅ GUI launched successfully")
                print("\nApplication running. Close window to exit.\n")
                
                return app.exec()
            
            except ImportError as e:
                print(f"❌ GUI not available: {e}")
                print("Running in console mode...")
                
                # Keep console open
                input("Press Enter to exit...")
                return 0
        
        else:
            print("Running without GUI (--no-gui)")
            input("Press Enter to exit...")
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
