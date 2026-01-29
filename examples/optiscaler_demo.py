#!/usr/bin/env python3
"""OptiScaler Demo

Demonstrates OptiScaler usage:
- Installation
- Configuration
- Game injection

Version: 0.3.5d (package 3.8a)
"""

from pathlib import Path
from optiscaler import (
    OptiScalerManager,
    OptiScalerConfig,
    OptiScalerBackend,
    OptiScalerQuality
)


def demo_installation():
    """Demo: Install OptiScaler"""
    print("\n=== OptiScaler Installation Demo ===")
    
    manager = OptiScalerManager()
    manager.initialize()
    
    if not manager.is_installed():
        print("OptiScaler not installed. Installing...")
        
        def progress(status, percent):
            print(f"[{percent:3d}%] {status}")
        
        try:
            manager.install(progress_callback=progress)
            print("\n✅ Installation successful!")
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            return False
    else:
        info = manager.get_info()
        print(f"✅ OptiScaler {info.version} already installed")
        print(f"   Backends: {[b.name for b in info.backends_available]}")
    
    return True


def demo_configuration():
    """Demo: Configure OptiScaler"""
    print("\n=== OptiScaler Configuration Demo ===")
    
    manager = OptiScalerManager()
    manager.initialize()
    
    if not manager.is_installed():
        print("❌ OptiScaler not installed")
        return
    
    # Create configuration
    config = OptiScalerConfig(
        backend=OptiScalerBackend.FSR3,
        quality=OptiScalerQuality.ULTRA_QUALITY,
        sharpness=0.8,
        enable_frame_gen=True,
        enable_hud_fix=True,
        enable_overlay=False
    )
    
    print("Configuration:")
    print(f"  Backend: {config.backend.name}")
    print(f"  Quality: {config.quality.name}")
    print(f"  Sharpness: {config.sharpness}")
    print(f"  Frame Generation: {config.enable_frame_gen}")
    print(f"  HUD Fix: {config.enable_hud_fix}")
    
    # Apply configuration
    if manager.configure(config):
        print("\n✅ Configuration applied")
    else:
        print("\n❌ Configuration failed")


def demo_game_injection():
    """Demo: Inject OptiScaler into game"""
    print("\n=== Game Injection Demo ===")
    
    manager = OptiScalerManager()
    manager.initialize()
    
    if not manager.is_installed():
        print("❌ OptiScaler not installed")
        return
    
    # Example game directory (change to your game)
    game_dir = Path("C:/Games/Cyberpunk 2077/bin/x64")
    
    if not game_dir.exists():
        print(f"⚠️  Game directory not found: {game_dir}")
        print("   Please update game_dir to your game's directory")
        return
    
    print(f"Detecting game in: {game_dir}")
    
    # Detect game
    game = manager.detect_game(game_dir)
    
    if not game:
        print("❌ No game detected")
        return
    
    print(f"\n✅ Detected: {game.name}")
    print(f"   Executable: {game.exe_path.name}")
    print(f"   DLSS Support: {game.has_dlss}")
    print(f"   FSR2 Support: {game.has_fsr}")
    print(f"   XeSS Support: {game.has_xess}")
    
    # Ask for confirmation
    print(f"\nInject OptiScaler into {game.name}? (y/n): ", end="")
    response = input().lower()
    
    if response != 'y':
        print("Injection cancelled")
        return
    
    # Inject
    try:
        if manager.inject_into_game(game):
            print(f"\n✅ OptiScaler injected into {game.name}!")
            print("   Game now uses FSR 3.1!")
            print("   Original DLLs backed up to optiscaler_backup/")
        else:
            print("\n❌ Injection failed")
    except Exception as e:
        print(f"\n❌ Injection error: {e}")


def demo_supported_games():
    """Demo: List supported games"""
    print("\n=== Supported Games Demo ===")
    
    manager = OptiScalerManager()
    games = manager.get_supported_games()
    
    print(f"\nOptiScaler supports {len(games)}+ games:")
    print("\nPopular titles:")
    for i, game in enumerate(games[:10], 1):
        print(f"  {i}. {game}")
    
    print(f"\n  ... and {len(games) - 10} more!")


def main():
    """Run all demos"""
    print("""
╔═══════════════════════════════════════════╗
║     OptiScaler Demo - Package 3.8a       ║
║   Real FSR 3.1 via OptiScaler Middleware ║
╚═══════════════════════════════════════════╝
    """)
    
    # Demo 1: Installation
    if not demo_installation():
        print("\n⚠️  Installation failed. Cannot continue.")
        return
    
    # Demo 2: Configuration
    demo_configuration()
    
    # Demo 3: Supported games
    demo_supported_games()
    
    # Demo 4: Game injection (interactive)
    print("\n" + "="*50)
    print("Ready for game injection demo? (y/n): ", end="")
    if input().lower() == 'y':
        demo_game_injection()
    else:
        print("\nSkipping game injection demo.")
    
    print("""
╔═══════════════════════════════════════════╗
║              Demo Complete!              ║
║                                          ║
║  Your system now has:                   ║
║  ✅ OptiScaler installed                 ║
║  ✅ FSR 3.1 configured                   ║
║  ✅ Ready for game injection!            ║
║                                          ║
║  Enjoy real FSR 3.1 on GPU! 🚀           ║
╚═══════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
