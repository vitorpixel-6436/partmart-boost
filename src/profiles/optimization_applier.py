"""Apply optimization profiles to games

Version: 0.3.5a
"""
import psutil
import sys
from typing import Optional
from .game_profiles import GameProfile


class ProfileApplier:
    """Apply optimization profiles to running games"""
    
    def __init__(self):
        self.applied_optimizations = {}
    
    def apply_profile(self, profile: GameProfile, pid: int):
        """Apply profile optimizations to process"""
        try:
            proc = psutil.Process(pid)
            
            # Store original values for reverting
            original = {
                'priority': proc.nice() if sys.platform != 'win32' else proc.nice(),
                'affinity': proc.cpu_affinity() if hasattr(proc, 'cpu_affinity') else None,
            }
            
            self.applied_optimizations[pid] = original
            
            # Apply priority
            self._apply_priority(proc, profile.priority)
            
            # Apply affinity
            if profile.affinity != "auto":
                self._apply_affinity(proc, profile.affinity)
            
            # RAM cleanup
            if profile.ram_enabled and profile.ram_cleanup:
                self._cleanup_ram(profile.ram_reserved_mb)
            
            print(f"[OK] Applied profile: {profile.game_name} (PID: {pid})")
            return True
        
        except Exception as e:
            print(f"[ERROR] Failed to apply profile: {e}")
            return False
    
    def _apply_priority(self, proc: psutil.Process, priority: str):
        """Set process priority"""
        if sys.platform == 'win32':
            priority_map = {
                'realtime': psutil.REALTIME_PRIORITY_CLASS,
                'high': psutil.HIGH_PRIORITY_CLASS,
                'above_normal': psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                'normal': psutil.NORMAL_PRIORITY_CLASS,
            }
        else:
            priority_map = {
                'realtime': -20,
                'high': -10,
                'above_normal': -5,
                'normal': 0,
            }
        
        if priority in priority_map:
            proc.nice(priority_map[priority])
            print(f"[OK] Set priority: {priority}")
    
    def _apply_affinity(self, proc: psutil.Process, affinity: str):
        """Set CPU affinity"""
        if not hasattr(proc, 'cpu_affinity'):
            return
        
        cpu_count = psutil.cpu_count(logical=True)
        
        if affinity == "performance_cores":
            # Use first half of CPUs (usually P-cores)
            cores = list(range(cpu_count // 2))
        elif affinity == "all_cores":
            cores = list(range(cpu_count))
        else:
            return
        
        proc.cpu_affinity(cores)
        print(f"[OK] Set affinity: {cores}")
    
    def _cleanup_ram(self, reserved_mb: int):
        """Clean up RAM (placeholder for now)"""
        # This would be implemented in RAM tuner module
        print(f"[INFO] RAM cleanup requested (reserve {reserved_mb} MB)")
    
    def revert_optimizations(self):
        """Revert all applied optimizations"""
        for pid, original in self.applied_optimizations.items():
            try:
                proc = psutil.Process(pid)
                
                if original['priority'] is not None:
                    proc.nice(original['priority'])
                
                if original['affinity'] is not None:
                    proc.cpu_affinity(original['affinity'])
                
                print(f"[OK] Reverted optimizations for PID {pid}")
            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        self.applied_optimizations.clear()


if __name__ == "__main__":
    print("[TEST] Optimization Applier")
    print("="*60)
    
    from game_profiles import GameProfile
    
    # Test profile
    profile = GameProfile(
        game_name="Test Game",
        enabled=True,
        executable_names=["test.exe"],
        priority="high",
        ram_cleanup=True,
        ram_reserved_mb=4096,
    )
    
    applier = ProfileApplier()
    
    # Apply to current process (for testing)
    import os
    pid = os.getpid()
    
    print(f"\n[TEST] Applying profile to current process (PID: {pid})")
    success = applier.apply_profile(profile, pid)
    
    if success:
        print("\n✅ Profile applied successfully!")
        print("\n[TEST] Reverting optimizations...")
        applier.revert_optimizations()
        print("✅ Reverted successfully!")
    
    print("\n" + "="*60)
