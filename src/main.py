#!/usr/bin/env python3
"""PartMart Boost - Main Entry Point

Version: 0.3.5d_package3.6a.4+hotfix

GUI launcher (requires PyQt6).
For CLI testing, use main_cli.py instead.
"""
import sys
from pathlib import Path

print("="*80)
print("🚀 PARTMART BOOST")
print("Version: 0.3.5d")
print("="*80)

# Check Python version
if sys.version_info < (3, 8):
    print("\n❌ Error: Python 3.8+ required")
    print(f"   Current: Python {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)

# Try to import PyQt6
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    print("\n✅ PyQt6 found - GUI mode available")
    GUI_AVAILABLE = True
except ImportError:
    print("\n⚠️  PyQt6 not found - GUI not available")
    print("\nOptions:")
    print("  1. Install PyQt6: pip install PyQt6")
    print("  2. Use CLI mode: python src/main_cli.py")
    print("  3. Run tests: python tests/test_all_modules.py")
    print("\nNote: GUI will be implemented in v0.4.0 (UI & Visualization)")
    print("      For now, CLI mode provides full functionality.")
    GUI_AVAILABLE = False

if not GUI_AVAILABLE:
    print("\n" + "="*80)
    print("Exiting... Use CLI mode for testing.")
    print("="*80)
    sys.exit(1)

# If GUI is available, show placeholder
print("\n[*] Starting GUI...")
print("\nNote: GUI is under development (v0.4.0)")
print("      This is a placeholder window.")

try:
    app = QApplication(sys.argv)
    
    # TODO: Create main window in v0.4.0
    # For now, just show that GUI can start
    print("\n✅ GUI initialized successfully")
    print("\nGUI features coming in v0.4.0:")
    print("  - Real-time performance overlay")
    print("  - FPS graphs and charts")
    print("  - Configuration interface")
    print("  - System monitoring dashboard")
    
    # Exit after 3 seconds
    print("\nClosing in 3 seconds...")
    QTimer.singleShot(3000, app.quit)
    
    sys.exit(app.exec())

except Exception as e:
    print(f"\n❌ Error starting GUI: {e}")
    print("\nFalling back to CLI mode...")
    import subprocess
    subprocess.run([sys.executable, "src/main_cli.py"])
