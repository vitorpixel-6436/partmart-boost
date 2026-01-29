#!/usr/bin/env python3
"""PartMart Boost Launcher

Version: 0.3.5d_hotfix8 (Package 3.9a, Stage 7.8a)

Launcher with standalone Modern GUI (no cache issues)
"""
import sys
import os
import subprocess
import shutil
from pathlib import Path

# Version info
VERSION = '0.3.5d_hotfix8'
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

def clear_cache():
    """Clear Python cache to prevent 'core' import errors"""
    print('[*] Clearing Python cache...')
    
    try:
        # Get project root
        project_root = Path(__file__).parent
        
        # Remove __pycache__ directories
        pycache_count = 0
        for pycache_dir in project_root.rglob('__pycache__'):
            try:
                shutil.rmtree(pycache_dir)
                pycache_count += 1
            except:
                pass
        
        # Remove .pyc files
        pyc_count = 0
        for pyc_file in project_root.rglob('*.pyc'):
            try:
                pyc_file.unlink()
                pyc_count += 1
            except:
                pass
        
        if pycache_count > 0 or pyc_count > 0:
            print(f'    ✓ Removed {pycache_count} cache directories and {pyc_count} .pyc files')
        else:
            print('    ✓ Cache already clean')
        
        print()
    
    except Exception as e:
        print(f'    ! Cache clear failed (non-critical): {e}')
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
        # Step 1: Uninstall
        print('[1/4] Uninstalling corrupted PyQt6...')
        subprocess.run(
            [sys.executable, '-m', 'pip', 'uninstall', 'PyQt6', 'PyQt6-Qt6', 'PyQt6-sip', '-y'],
            capture_output=True,
            check=False
        )
        print('      ✓ PyQt6 removed')
        print()
        
        # Step 2: Clear cache
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
        
        # Step 4: Reinstall
        print('[4/4] Reinstalling PyQt6...')
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'PyQt6'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print('      ✓ PyQt6 installed successfully!')
            print()
            print('[+] PyQt6 fix completed!')
            print('[*] Retrying Modern GUI...')
            print()
            return True
        else:
            print('      ✗ PyQt6 installation failed')
            print()
            return False
            
    except Exception as e:
        print(f'[!] Auto-fix failed: {e}')
        print()
        return False

def launch_modern_gui(retry_after_fix=True):
    """Launch standalone Modern GUI"""
    print('[*] Launching Modern GUI (Standalone Liquid Glass UI)...')
    print()
    
    # Clear cache first to prevent 'core' errors
    clear_cache()
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QFont
        
        # Import standalone version (no src dependencies!)
        from src.gui.modern_main_window_standalone import ModernMainWindow
        
        app = QApplication(sys.argv)
        
        # Set global font
        font = QFont('Segoe UI', 13)
        app.setFont(font)
        
        window = ModernMainWindow()
        window.show()
        
        print('[+] Modern GUI launched successfully!')
        print('    Beautiful Liquid Glass interface ready!')
        print('    Standalone version - no cache issues!')
        print()
        
        sys.exit(app.exec())
        
    except ImportError as e:
        error_msg = str(e)
        
        # Check if DLL error
        if ('DLL load failed' in error_msg or 'QtCore' in error_msg) and retry_after_fix:
            print(f'[-] PyQt6 DLL Error detected')
            print()
            
            if fix_pyqt6():
                return launch_modern_gui(retry_after_fix=False)
            else:
                print('[!] PyQt6 fix failed.')
                print('[!] Please use CLI mode (option 2)')
                print()
                return False
        else:
            print(f'[-] Failed to import: {error_msg}')
            print()
            
            if retry_after_fix and 'PyQt6' in error_msg:
                print('[*] Installing PyQt6...')
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', 'PyQt6'],
                    capture_output=True
                )
                
                if result.returncode == 0:
                    print('[+] PyQt6 installed, retrying...')
                    print()
                    return launch_modern_gui(retry_after_fix=False)
            
            print('[!] Please use CLI mode (option 2)')
            print()
            return False
                
    except Exception as e:
        print(f'[-] GUI launch failed: {e}')
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
    print('  1. Modern GUI (Standalone Liquid Glass UI) ⭐ RECOMMENDED')
    print('  2. CLI Mode (Terminal interface)')
    print('  0. Exit')
    print()
    print('Note: Standalone version with automatic cache cleanup')
    print()
    
    choice = input('Select option (0-2): ').strip()
    print()
    
    if choice == '1':
        result = launch_modern_gui()
        if not result:
            print()
            print('[*] Modern GUI failed. Try CLI mode (option 2)?')
            retry = input('Launch CLI? (y/n): ').strip().lower()
            if retry == 'y':
                print()
                launch_cli()
    elif choice == '2':
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
