"""PartMart Boost - Entry point"""
import sys
import os
from PyQt6.QtWidgets import QApplication

# Add src to path
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize core systems
from core.config import init_config
from core.logger import init_logger

def main():
    """Main entry point"""
    # Initialize configuration
    config = init_config("config/settings.json")
    
    # Initialize logging
    log_level = config.get('log_level', 'INFO')
    logger = init_logger("logs", log_level)
    
    logger.info("="*60)
    logger.info("PartMart Boost v0.3.4-alpha starting...")
    logger.info(f"Python {sys.version}")
    logger.info(f"Config: {config.config_path}")
    logger.info(f"Language: {config.get_language()}")
    logger.info(f"ML Optimizer: {'Enabled' if config.is_ml_enabled() else 'Disabled'}")
    logger.info("="*60)
    
    try:
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("PartMart Boost")
        app.setApplicationVersion("0.3.4-alpha")
        app.setOrganizationName("PartMart")
        
        # Import and create main window
        from ui.main_window import PartMartMainWindow
        
        window = PartMartMainWindow()
        window.show()
        
        logger.info("Main window displayed")
        
        # First launch check
        if config.is_first_launch():
            logger.info("First launch detected")
            config.mark_launched()
        
        # Run application
        exit_code = app.exec()
        
        logger.info(f"Application exited with code: {exit_code}")
        logger.log_shutdown()
        
        return exit_code
    
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
