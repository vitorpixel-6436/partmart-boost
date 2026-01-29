#!/usr/bin/env python3
"""PartMart Boost - Main Entry Point

Version: 0.3.5e (package 3.9a, stage 7/7)

Package 3.9a Stage 7: Integration & Debug
- Initialize AppIntegrator
- Setup all systems before UI
- Graceful fallback
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

print("[Main] Starting PartMart Boost v0.3.5e...")
print("[Main] Package 3.9a - Stage 7: Integration & Debug")

# STAGE 7: Initialize integration layer BEFORE creating UI
try:
    from core.app_integration import initialize_app, get_integrator
    
    print("[Main] Initializing application systems...")
    if initialize_app():
        print("[Main] ✅ All systems initialized successfully!")
        integrator = get_integrator()
    else:
        print("[Main] ⚠️ Some systems failed to initialize, continuing with fallback...")
        integrator = None

except Exception as e:
    print(f"[Main] ⚠️ Integration layer not available: {e}")
    print("[Main] Continuing without BackendBridge...")
    integrator = None

# Now import and create UI
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from gui.main_window import MainWindow
    
    print("[Main] Creating Qt application...")
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("PartMart Boost")
    app.setApplicationVersion("0.3.5e")
    
    print("[Main] Creating main window...")
    
    # STAGE 7: Pass integrator to MainWindow
    window = MainWindow(integrator=integrator)
    window.show()
    
    print("[Main] ✅ Application started successfully!")
    print("[Main] UI rendering...")
    
    sys.exit(app.exec())

except ImportError as e:
    print(f"[Main] ❌ PyQt6 not available: {e}")
    print("[Main] Please install: pip install PyQt6")
    sys.exit(1)

except Exception as e:
    print(f"[Main] ❌ Fatal error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
