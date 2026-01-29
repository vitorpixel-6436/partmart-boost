#!/usr/bin/env python3
"""PartMart Boost Launcher

Version: 0.3.5d_hotfix6 (Package 3.9a, Stage 7.8a)

Launcher with automatic PyQt6 fix and Liquid Glass UI
"""
import sys
import os
import subprocess
from pathlib import Path

# Version info
VERSION = '0.3.5d_hotfix6'
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

def fix_pyqt6():
    """Automatically fix PyQt6 DLL errors"""
    print()
    print('=' * 70)
    print('  Auto-Fixing PyQt6 Installation')
    print('=' * 70)
    print()
    print('[*] Detected PyQt6 DLL error - fixing automatically...')
    print()
    
    try:
        # Step 1: Uninstall all PyQt6 components
        print('[1/4] Uninstalling corrupted PyQt6 components...')
        subprocess.run(
            [sys.executable, '-m', 'pip', 'uninstall', 'PyQt6', 'PyQt6-Qt6', 'PyQt6-sip', '-y'],
            capture_output=True,
            check=False
        )
        print('      ✓ PyQt6 components removed')
        print()
        
        # Step 2: Clear pip cache
        print('[2/4] Clearing pip cache...')
        subprocess.run(
            [sys.executable, '-m', 'pip', 'cache', 'purge'],
            capture_output=True,
            check=False
        )
        print('      ✓ Pip cache cleared')
        print()
        
        # Step 3: Upgrade pip
        print('[3/4] Upgrading pip...')
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools'],
            capture_output=True,
            check=False
        )
        print('      ✓ Pip upgraded')
        print()
        
        # Step 4: Reinstall PyQt6
        print('[4/4] Reinstalling PyQt6 cleanly...')
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'PyQt6'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print('      ✓ PyQt6 installed successfully!')
            print()
            print('[+] PyQt6 fix completed!')
            print('[*] Retrying Modern GUI launch...')
            print()
            return True
        else:
            print('      ✗ PyQt6 installation failed')
            print()
            print('[!] Could not fix PyQt6 automatically')
            print('[!] Will use Legacy GUI instead')
            print()
            return False
            
    except Exception as e:
        print(f'[!] Auto-fix failed: {e}')
        print('[!] Will use Legacy GUI instead')
        print()
        return False

def launch_modern_gui(retry_after_fix=True):
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
        
        # Check if it's a DLL error
        if ('DLL load failed' in error_msg or 'QtCore' in error_msg) and retry_after_fix:
            print(f'[-] PyQt6 DLL Error detected')
            print()
            
            # Automatically fix PyQt6
            if fix_pyqt6():
                # Retry Modern GUI after fix
                return launch_modern_gui(retry_after_fix=False)
            else:
                # Fix failed, fallback to Legacy GUI
                print('[*] Falling back to Legacy GUI...')
                print()
                return launch_legacy_gui()
        else:
            # Other import error
            print(f'[-] Failed to import PyQt6: {error_msg}')
            print('[!] Installing PyQt6...')
            print()
            
            # Try to install PyQt6
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 'PyQt6'],
                capture_output=True
            )
            
            if result.returncode == 0 and retry_after_fix:
                print('[+] PyQt6 installed, retrying...')
                print()
                return launch_modern_gui(retry_after_fix=False)
            else:
                print('[!] PyQt6 installation failed')
                print('[*] Falling back to Legacy GUI...')
                print()
                return launch_legacy_gui()
                
    except Exception as e:
        print(f'[-] GUI launch failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def launch_legacy_gui():
    """Launch legacy GUI (old design)"""
    print('[*] Launching Legacy GUI...')
    print('[!] Note: Legacy GUI has basic design')
    print('[!] All features available, just different look')
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
        print('[!] PyQt6 is required for any GUI mode')
        print('[!] Use CLI mode instead')
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
