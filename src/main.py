#!/usr/bin/env python3
"""PartMart Boost - Main Entry Point

Version: 0.4.0-alpha

GUI launcher with PyQt6.
"""
import sys
from pathlib import Path

print("="*80)
print("🚀 PARTMART BOOST")
print("Version: 0.4.0-alpha")
print("="*80)

# Check Python version
if sys.version_info < (3, 8):
    print("\n❌ Error: Python 3.8+ required")
    print(f"   Current: Python {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)

print(f"\n✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

# Try to import PyQt6
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    print("✅ PyQt6 imported")
except ImportError as e:
    print("\n❌ PyQt6 not found")
    print("\nInstall it:")
    print("  pip install PyQt6")
    print("\nOr use CLI mode:")
    print("  python src/main_cli.py")
    sys.exit(1)

# Import main window
try:
    from gui.main_window import MainWindow
    print("✅ GUI modules loaded")
except ImportError as e:
    print(f"\n❌ Error loading GUI: {e}")
    print("\nMake sure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

print("\n[*] Starting GUI...\n")

try:
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("PartMart Boost")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    print("✅ GUI started successfully")
    print("\n" + "="*80)
    print("GUI is running - check the window!")
    print("="*80 + "\n")
    
    # Run application
    sys.exit(app.exec())

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\nTrying CLI mode instead...")
    
    try:
        import subprocess
        subprocess.run([sys.executable, "src/main_cli.py"])
    except:
        pass
    
    sys.exit(1)
