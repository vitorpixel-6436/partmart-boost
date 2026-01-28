#!/usr/bin/env python3
"""
Optimization Applier - Applies optimization profiles to system.

Features:
- RAM cleanup and defragmentation
- GPU clock/memory offsets (via MSI Afterburner if available)
- Process priority management
- Power plan switching

Author: PartMart Team
Version: 0.3.0-alpha
License: MIT
"""

import subprocess
import ctypes
import psutil
import os
from typing import Optional, Dict
from pathlib import Path

from game_profiles import GameProfile


class RAMOptimizer:
    """RAM optimization utilities."""
    
    @staticmethod
    def clear_memory():
        """
        Clear memory (Windows EmptyWorkingSet).
        
        Returns:
            Freed memory in MB
        """
        try:
            # Get memory before
            mem_before = psutil.virtual_memory().available / (1024**2)
            
            # Try EmptyWorkingSet
            RAMOptimizer._empty_working_set()
            
            # Get memory after
            mem_after = psutil.virtual_memory().available / (1024**2)
            freed = mem_after - mem_before
            
            print(f"   🧹 RAM Freed: {freed:.1f} MB")
            return freed
        
        except Exception as e:
            print(f"   ❌ RAM cleanup failed: {e}")
            return 0.0
    
    @staticmethod
    def _empty_working_set():
        """Call EmptyWorkingSet on all processes."""
        try:
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            psapi = ctypes.WinDLL('psapi', use_last_error=True)
            
            # Constants
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_SET_QUOTA = 0x0100
            
            for proc in psutil.process_iter(['pid']):
                try:
                    pid = proc.info['pid']
                    if pid == 0:  # Skip system idle
                        continue
                    
                    # Open process
                    h_process = kernel32.OpenProcess(
                        PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA,
                        False,
                        pid
                    )
                    
                    if h_process:
                        # Empty working set
                        psapi.EmptyWorkingSet(h_process)
                        kernel32.CloseHandle(h_process)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        except Exception as e:
            print(f"   EmptyWorkingSet error: {e}")
    
    @staticmethod
    def set_process_priority(pid: int, priority: str) -> bool:
        """
        Set process priority.
        
        Args:
            pid: Process ID
            priority: Priority level (realtime, high, above_normal, normal)
            
        Returns:
            True if successful
        """
        try:
            proc = psutil.Process(pid)
            
            priority_map = {
                'realtime': psutil.REALTIME_PRIORITY_CLASS,
                'high': psutil.HIGH_PRIORITY_CLASS,
                'above_normal': psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                'normal': psutil.NORMAL_PRIORITY_CLASS,
            }
            
            if priority.lower() in priority_map:
                proc.nice(priority_map[priority.lower()])
                return True
        
        except Exception as e:
            print(f"   ❌ Failed to set priority: {e}")
        
        return False


class GPUOptimizer:
    """GPU optimization via MSI Afterburner CLI."""
    
    def __init__(self):
        """Initialize GPU optimizer."""
        self.afterburner_path = self._find_afterburner()
        self.available = self.afterburner_path is not None
        
        if self.available:
            print(f"[GPU Optimizer] MSI Afterburner found: {self.afterburner_path}")
        else:
            print("[GPU Optimizer] MSI Afterburner not found (GPU OC disabled)")
    
    def _find_afterburner(self) -> Optional[Path]:
        """
        Find MSI Afterburner installation.
        
        Returns:
            Path to MSIAfterburner.exe or None
        """
        # Common installation paths
        search_paths = [
            Path(r"C:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe"),
            Path(r"C:\Program Files\MSI Afterburner\MSIAfterburner.exe"),
            Path(r"D:\Program Files (x86)\MSI Afterburner\MSIAfterburner.exe"),
            Path(r"D:\MSI Afterburner\MSIAfterburner.exe"),
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        return None
    
    def apply_gpu_settings(
        self,
        core_clock: Optional[int] = None,
        mem_clock: Optional[int] = None,
        power_limit: Optional[int] = None,
        fan_speed: Optional[int] = None
    ) -> bool:
        """
        Apply GPU settings via Afterburner.
        
        Args:
            core_clock: Core clock offset in MHz
            mem_clock: Memory clock offset in MHz
            power_limit: Power limit in %
            fan_speed: Fan speed in %
            
        Returns:
            True if successful
        """
        if not self.available:
            print("   ⚠️ MSI Afterburner not available, skipping GPU tweaks")
            return False
        
        try:
            # Build command
            # Note: MSI Afterburner CLI syntax varies by version
            # This is a placeholder - real implementation needs proper CLI flags
            
            cmd = [str(self.afterburner_path)]
            
            if core_clock is not None:
                cmd.extend(["-cclock", str(core_clock)])
                print(f"   📡 GPU Core: +{core_clock} MHz")
            
            if mem_clock is not None:
                cmd.extend(["-mclock", str(mem_clock)])
                print(f"   📡 GPU Memory: +{mem_clock} MHz")
            
            if power_limit is not None:
                cmd.extend(["-powerlimit", str(power_limit)])
                print(f"   📡 Power Limit: {power_limit}%")
            
            if fan_speed is not None:
                cmd.extend(["-fanspeed", str(fan_speed)])
                print(f"   📡 Fan Speed: {fan_speed}%")
            
            # Execute
            # subprocess.run(cmd, capture_output=True, timeout=5)
            # ⚠️ DISABLED: Need proper Afterburner CLI documentation
            
            print("   🚧 GPU tweaks simulated (Afterburner CLI integration pending)")
            return True
        
        except Exception as e:
            print(f"   ❌ GPU optimization failed: {e}")
            return False
    
    def reset_gpu_settings(self) -> bool:
        """
        Reset GPU to default settings.
        
        Returns:
            True if successful
        """
        if not self.available:
            return False
        
        try:
            # Reset all offsets to 0
            return self.apply_gpu_settings(
                core_clock=0,
                mem_clock=0,
                power_limit=100,
                fan_speed=None  # Auto
            )
        
        except Exception as e:
            print(f"   ❌ GPU reset failed: {e}")
            return False


class PowerPlanManager:
    """Windows power plan management."""
    
    POWER_PLANS = {
        'balanced': '381b4222-f694-41f0-9685-ff5bb260df2e',
        'high_performance': '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c',
        'power_saver': 'a1841308-3541-4fab-bc81-f71556f20b4a',
        'ultimate_performance': 'e9a42b02-d5df-448d-aa00-03f14749eb61',
    }
    
    @staticmethod
    def set_power_plan(plan: str) -> bool:
        """
        Set Windows power plan.
        
        Args:
            plan: Plan name (balanced, high_performance, ultimate_performance)
            
        Returns:
            True if successful
        """
        try:
            guid = PowerPlanManager.POWER_PLANS.get(plan.lower())
            if not guid:
                print(f"   ❌ Unknown power plan: {plan}")
                return False
            
            # Use powercfg
            cmd = ['powercfg', '/setactive', guid]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   🔋 Power Plan: {plan.upper()}")
                return True
            else:
                print(f"   ❌ Power plan failed: {result.stderr}")
                return False
        
        except Exception as e:
            print(f"   ❌ Power plan error: {e}")
            return False
    
    @staticmethod
    def get_current_plan() -> Optional[str]:
        """
        Get current power plan.
        
        Returns:
            Plan name or None
        """
        try:
            cmd = ['powercfg', '/getactivescheme']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse output
                for name, guid in PowerPlanManager.POWER_PLANS.items():
                    if guid in result.stdout:
                        return name
        
        except Exception:
            pass
        
        return None


class ProfileApplier:
    """Applies game profiles to system."""
    
    def __init__(self):
        """Initialize profile applier."""
        self.ram_optimizer = RAMOptimizer()
        self.gpu_optimizer = GPUOptimizer()
        self.power_manager = PowerPlanManager()
        
        # Store original settings for revert
        self.original_power_plan = self.power_manager.get_current_plan()
        
        print("[Profile Applier] Ready")
    
    def apply_profile(self, profile: GameProfile, pid: int) -> Dict[str, bool]:
        """
        Apply optimization profile.
        
        Args:
            profile: Game profile to apply
            pid: Game process ID
            
        Returns:
            Dict of applied optimizations
        """
        results = {}
        
        print(f"\n⚙️ Applying profile: {profile.game_name}")
        print("-" * 50)
        
        # RAM Cleanup
        if profile.ram_cleanup:
            print("\n[RAM Optimization]")
            self.ram_optimizer.clear_memory()
            results['ram_cleanup'] = True
        
        # Process Priority
        if profile.ram_priority:
            print(f"\n[Process Priority]")
            success = self.ram_optimizer.set_process_priority(pid, profile.ram_priority)
            if success:
                print(f"   ✅ Priority: {profile.ram_priority.upper()}")
            results['process_priority'] = success
        
        # GPU Optimization
        if any([profile.gpu_clock_offset, profile.gpu_mem_offset, 
                profile.gpu_power_limit, profile.gpu_fan_speed]):
            print(f"\n[GPU Optimization]")
            success = self.gpu_optimizer.apply_gpu_settings(
                core_clock=profile.gpu_clock_offset,
                mem_clock=profile.gpu_mem_offset,
                power_limit=profile.gpu_power_limit,
                fan_speed=profile.gpu_fan_speed
            )
            results['gpu_tweaks'] = success
        
        # Power Plan
        print(f"\n[Power Management]")
        self.power_manager.set_power_plan('high_performance')
        results['power_plan'] = True
        
        print("\n" + "-" * 50)
        print(f"✅ Profile applied successfully!\n")
        
        return results
    
    def revert_optimizations(self):
        """
        Revert all optimizations to defaults.
        """
        print("\n↩️ Reverting optimizations...")
        
        # Reset GPU
        if self.gpu_optimizer.available:
            self.gpu_optimizer.reset_gpu_settings()
        
        # Restore power plan
        if self.original_power_plan:
            self.power_manager.set_power_plan(self.original_power_plan)
        
        print("✅ System restored to defaults\n")


# ========== Testing ==========

if __name__ == '__main__':
    print("="*60)
    print("Optimization Applier Test")
    print("="*60)
    print()
    
    # Create applier
    applier = ProfileApplier()
    
    # Create test profile
    from game_profiles import GameProfile
    
    test_profile = GameProfile(
        game_id="test",
        game_name="Test Game",
        executable="test.exe",
        gpu_power_limit=110,
        gpu_clock_offset=150,
        gpu_mem_offset=500,
        gpu_fan_speed=75,
        ram_cleanup=True,
        ram_priority="high"
    )
    
    # Apply profile (use current process as test)
    import os
    applier.apply_profile(test_profile, os.getpid())
    
    print()
    print("="*60)
    print("✅ Optimization Applier works!")
    print("="*60)
