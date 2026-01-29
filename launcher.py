#!/usr/bin/env python3
"""PartMart Boost Launcher

Version: 0.3.5d_hotfix5 (Package 3.9a, Stage 7.8a)

Launcher with new Liquid Glass UI option
"""
import sys
import os
from pathlib import Path

# Version info
VERSION = '0.3.5d_hotfix5'
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

def print_pyqt6_fix():
    """Print PyQt6 installation fix instructions"""
    print()
    print('=' * 70)
    print('  PyQt6 DLL Error - Windows Fix Required')
    print('=' * 70)
    print()
    print('[!] PyQt6 installation is corrupted or incomplete')
    print()
    print('FIX - Run these commands:')
    print()
    print('  1. pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y')
    print('  2. pip cache purge')
    print('  3. pip install --upgrade pip setuptools')
    print('  4. pip install PyQt6')
    print()
    print('Alternative fix (if above fails):')
    print()
    print('  pip install PyQt6==6.6.1  # Use specific stable version')
    print()
    print('After fixing, run launcher again and select Modern GUI.')
    print()
    print('=' * 70)
    print()
    input('Press Enter to continue with Legacy GUI option...')
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
        error_msg = str(e)
        print(f'[-] Failed to import PyQt6: {error_msg}')
        print()
        
        if 'DLL load failed' in error_msg or 'QtCore' in error_msg:
            # Windows DLL error - provide detailed fix
            print_pyqt6_fix()
            
            # Offer Legacy GUI as fallback
            print('[*] Falling back to Legacy GUI...')
            print()
            return launch_legacy_gui()
        else:
            # Other import error
            print('[!] Install PyQt6 with: pip install PyQt6')
            print()
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
    print('[!] Fix PyQt6 to use beautiful Liquid Glass UI!')
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
        print(f'[-] Legacy GUI also failed: {e}')
        print()
        print('[!] PyQt6 is required for GUI mode')
        print('[!] Fix PyQt6 following instructions above, or use CLI mode')
        print()
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
