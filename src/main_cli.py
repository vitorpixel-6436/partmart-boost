#!/usr/bin/env python3
"""PartMart Boost - CLI Launcher

Version: 0.3.5d_package3.6a.4+hotfix

Command-line interface for testing all modules.
"""
import sys
import time
from pathlib import Path

print("="*80)
print("🚀 PARTMART BOOST - CLI MODE")
print("Version: 0.3.5d (Package 3.6a Complete)")
print("="*80)

# Check Python version
if sys.version_info < (3, 8):
    print("\n❌ Error: Python 3.8+ required")
    print(f"   Current: Python {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)

print("\n[*] Checking dependencies...")

# Check numpy
try:
    import numpy as np
    print(f"    ✅ NumPy {np.__version__}")
except ImportError:
    print("    ❌ NumPy not found")
    print("    Install: pip install numpy")
    sys.exit(1)

print("\n[*] All dependencies OK!")

# Menu
def show_menu():
    print("\n" + "="*80)
    print("📝 MENU")
    print("="*80)
    print("1. Run Full System Test (All Modules)")
    print("2. Test FPS Tracker")
    print("3. Test Performance Monitor")
    print("4. Test Frame Generator")
    print("5. Test Upscaler")
    print("6. Test Thermal Manager")
    print("7. Test Power Manager")
    print("8. Test Resource Manager")
    print("9. Test System Integration")
    print("")
    print("0. Exit")
    print("="*80)

def run_module_test(module_name: str, module_path: str):
    """Run individual module test"""
    print(f"\n{'='*80}")
    print(f"🧪 Running: {module_name}")
    print(f"{'='*80}")
    
    try:
        # Execute module's __main__ block
        import subprocess
        result = subprocess.run(
            [sys.executable, module_path],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n✅ {module_name} test completed successfully")
        else:
            print(f"\n❌ {module_name} test failed")
    
    except Exception as e:
        print(f"\n❌ Error running {module_name}: {e}")

def main():
    """Main CLI loop"""
    
    while True:
        show_menu()
        
        try:
            choice = input("\nSelect option (0-9): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            break
        
        if choice == "0":
            print("\n👋 Goodbye!")
            break
        
        elif choice == "1":
            # Full test suite
            tests_path = Path(__file__).parent.parent / "tests" / "test_all_modules.py"
            run_module_test("Full System Test", str(tests_path))
        
        elif choice == "2":
            run_module_test("FPS Tracker", "src/core/fps_tracker.py")
        
        elif choice == "3":
            run_module_test("Performance Monitor", "src/monitors/performance_monitor.py")
        
        elif choice == "4":
            run_module_test("Frame Generator", "src/framegen/generator.py")
        
        elif choice == "5":
            run_module_test("Upscaler", "src/upscaler/upscaler.py")
        
        elif choice == "6":
            run_module_test("Thermal Manager", "src/adaptive/thermal_manager_advanced.py")
        
        elif choice == "7":
            run_module_test("Power Manager", "src/adaptive/power_manager_advanced.py")
        
        elif choice == "8":
            run_module_test("Resource Manager", "src/core/resource_manager.py")
        
        elif choice == "9":
            run_module_test("System Integration", "src/adaptive/system_integration.py")
        
        else:
            print("\n❌ Invalid option. Please select 0-9.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)
