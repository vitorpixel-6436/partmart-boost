#!/usr/bin/env python3
"""PartMart Boost Launcher

Version: 0.3.5d (Package 3.9a, Stage 7.8a)

Launcher with new Liquid Glass UI option
"""
import sys
import os
from pathlib import Path

# Version info
VERSION = '0.3.5d'
PACKAGE = '3.9a'
STAGE = '7.8a'

def print_banner():
    """Print startup banner"""
    print()
    print('=' * 70)
    print(f'  PartMart Boost v{VERSION} (Package {PACKAGE})')
    print(f'  Stage: {STAGE} - Liquid Glass UI Revolution')
    print('  Gaming Performance Optimizer - USER READY')
    print('=' * 70)
    print()

def launch_modern_gui():
    """Launch modern Liquid Glass GUI"""
    print('[*] Launching Modern GUI (Liquid Glass UI)...')
    print()
    
    try:
        from PyQt6.QtWidgets import QApplication
        from src.ui.themes import apply_theme
        from src.gui.modern_main_window import ModernMainWindow
        
        app = QApplication(sys.argv)
        apply_theme(app)
        
        window = ModernMainWindow()
        window.show()
        
        print('[+] Modern GUI launched successfully!')
        print('    Beautiful Liquid Glass interface ready!')
        print()
        
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f'[-] Failed to import PyQt6: {e}')
        print('[!] Install with: pip install PyQt6')
        return False
    except Exception as e:
        print(f'[-] GUI launch failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def launch_legacy_gui():
    """Launch legacy GUI (old design)"""
    print('[*] Launching Legacy GUI...')
    print('[!] Note: Legacy GUI has basic design')
    print('[!] Use Modern GUI for beautiful Liquid Glass UI!')
    print()
    
    try:
        from PyQt6.QtWidgets import QApplication
        from src.gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        
        print('[+] Legacy GUI launched')
        print()
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f'[-] Legacy GUI launch failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def launch_cli():
    """Launch CLI mode"""
    print('[*] Launching CLI Mode...')
    print()
    
    try:
        from src.cli.cli import CLI
        cli = CLI()
        cli.run()
    except Exception as e:
        print(f'[-] CLI launch failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main launcher"""
    print_banner()
    
    print('Select mode:')
    print()
    print('  1. Modern GUI (New Liquid Glass UI) ⭐ RECOMMENDED')
    print('  2. Legacy GUI (Old basic design)')
    print('  3. CLI Mode')
    print('  0. Exit')
    print()
    
    choice = input('Select option (0-3): ').strip()
    print()
    
    if choice == '1':
        launch_modern_gui()
    elif choice == '2':
        launch_legacy_gui()
    elif choice == '3':
        launch_cli()
    elif choice == '0':
        print('[*] Exiting...')
        sys.exit(0)
    else:
        print('[!] Invalid choice')
        print()
        main()

if __name__ == '__main__':
    main()
