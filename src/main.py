#!/usr/bin/env python3
"""PartMart Boost - Main entry point

Version: 0.3.5d - Package 2 Complete

Package 2 improvements:
- Schema consistency across all monitors
- Enhanced APIs (40+ new methods)
- Health tracking and auto-recovery
- Advanced event system (9 new signals)
- Data history buffering
- Adaptive behavior
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from ui.main_window import PartMartMainWindow
from core.logger import get_logger


def main():
    """Main entry point"""
    print("[*] Launching PartMart Boost v0.3.5d Package 2...")
    print("\n" + "="*56)
    print("📦 Package 2 Complete:")
    print("  ✅ Schema consistency (RAM/GPU/CPU)")
    print("  ✅ Enhanced APIs (40+ methods)")
    print("  ✅ Health tracking + auto-recovery")
    print("  ✅ Advanced events (9 signals)")
    print("  ✅ Data history (60 samples)")
    print("  ✅ Adaptive intervals")
    print("="*56)
    print()
    
    logger = get_logger()
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("PartMart Boost")
        app.setApplicationVersion("0.3.5d")
        
        window = PartMartMainWindow()
        window.show()
        
        sys.exit(app.exec())
    
    except Exception as e:
        logger.log_error_with_trace("Critical error in main", e)
        print(f"\n[CRITICAL] Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
