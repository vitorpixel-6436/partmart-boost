#!/usr/bin/env python3
"""
PartMart Boost - Main entry point
🐉 GPU/RAM Optimizer (+40-80% FPS)

Usage:
    python src/main.py
"""

import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/partmart-boost.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Initialize application environment"""
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    # Check for admin rights
    if os.name == 'nt':  # Windows
        try:
            import ctypes
            is_admin = ctypes.windll.shell.IsUserAnAdmin()
            if not is_admin:
                logger.warning("⚠️ PartMart Boost requires Administrator privileges!")
                logger.warning("Please run this application as Administrator.")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Could not check admin rights: {e}")
    
    logger.info("✅ Environment initialized")

def check_dependencies():
    """Check if all required dependencies are installed"""
    required = {
        'PyQt6': 'PyQt6.QtWidgets',
        'pynvml': 'pynvml',
        'psutil': 'psutil',
        'requests': 'requests',
    }
    
    missing = []
    for name, import_name in required.items():
        try:
            __import__(import_name)
            logger.info(f"✅ {name} found")
        except ImportError:
            logger.error(f"❌ {name} not found")
            missing.append(name)
    
    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        logger.error("Install with: pip install -r requirements.txt")
        sys.exit(1)
    
    logger.info("✅ All dependencies satisfied")

def main():
    """Main application entry point"""
    try:
        # Setup
        setup_environment()
        check_dependencies()
        
        logger.info("\n" + "="*60)
        logger.info("🐉 PartMart Boost v0.1-alpha")
        logger.info("Твой ПК. Твоя мощь.")
        logger.info("="*60 + "\n")
        
        # Import UI (lazy import to avoid import errors)
        from PyQt6.QtWidgets import QApplication
        
        # TODO: Import main window UI
        # from src.ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        
        # TODO: Initialize main window
        # window = MainWindow()
        # window.show()
        
        logger.info("✅ PartMart Boost started successfully")
        logger.info("📝 Status: UI not yet implemented (Phase 1)")
        
        # Temporary: Print status
        print("\n" + "="*60)
        print("🐉 PartMart Boost - Alpha Build")
        print("="*60)
        print("\nStatus: Development Phase 1 (MVP)")
        print("\nPlanned features:")
        print("  ✅ NVIDIA GPU Optimization (Week 1-2)")
        print("  ✅ RAM XMP Enable (Week 1-2)")
        print("  ✅ Quick Boost Button (Week 1-2)")
        print("  ✅ RTSS Overlay (Week 1-2)")
        print("  ⏳ AMD GPU Support (Week 3-4)")
        print("  ⏳ FrameGen Integration (Week 3-4)")
        print("  ⏳ Game Profiles (Week 3-4)")
        print("  ⏳ Premium Tier (Week 5-6)")
        print("\nGitHub: https://github.com/vitorpixel-6436/partmart-boost")
        print("="*60 + "\n")
        
        # For now, run empty app
        sys.exit(app.exec())
        
    except KeyboardInterrupt:
        logger.info("\n🛑 PartMart Boost interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
