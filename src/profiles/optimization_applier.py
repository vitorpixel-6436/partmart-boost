"""Apply optimization profiles to games

Version: 0.3.5b_hotfix
Fixed: Windows priority handling
Fixed: Better error handling
"""
import psutil
import sys
import platform
from typing import Optional, Dict
from .game_profiles import GameProfile


class ProfileApplier:
    """Apply optimization profiles to running games
    
    Version: 0.3.5b_hotfix
    Fixed: Proper priority handling for Windows/Linux
    """
    
    def __init__(self):
        self.applied_optimizations: Dict[int, Dict] = {}
        self.is_windows = platform.system() == 'Windows'
    
    def apply_profile(self, profile: GameProfile, pid: int) -> bool:
        """Apply profile optimizations to process
        
        Fixed: Better error handling and priority management
        """
        try:
            # Check if process exists
            if not psutil.pid_exists(pid):
                print(f"[ERROR] Process {pid} does not exist")
                return False
            
            proc = psutil.Process(pid)
            
            # Store original values for reverting
            original = {
                'priority': self._get_priority(proc),
                'affinity': proc.cpu_affinity() if hasattr(proc, 'cpu_affinity') else None,
            }
            
            self.applied_optimizations[pid] = original
            
            # Apply priority
            if profile.priority:
                self._apply_priority(proc, profile.priority)
            
            # Apply affinity
            if profile.affinity and profile.affinity != "auto":
                self._apply_affinity(proc, profile.affinity)
            
            # RAM cleanup
            if profile.ram_enabled and profile.ram_cleanup:
                self._cleanup_ram(profile.ram_reserved_mb)
            
            print(f"[OK] Applied profile: {profile.game_name} (PID: {pid})")
            return True
        
        except psutil.NoSuchProcess:
            print(f"[ERROR] Process {pid} no longer exists")
            return False
        except psutil.AccessDenied:
            print(f"[ERROR] Access denied for process {pid} - need admin rights")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to apply profile: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_priority(self, proc: psutil.Process) -> int:
        """Get current process priority
        
        Fixed: Proper handling for Windows vs Linux
        """
        try:
            if self.is_windows:
                # Windows uses priority classes
                return proc.nice()
            else:
                # Linux/Unix uses nice values
                return proc.nice()
        except Exception:
            return 0
    
    def _apply_priority(self, proc: psutil.Process, priority: str):
        """Set process priority
        
        Fixed: Proper priority mapping
        """
        try:
            if self.is_windows:
                priority_map = {
                    'realtime': psutil.REALTIME_PRIORITY_CLASS,
                    'high': psutil.HIGH_PRIORITY_CLASS,
                    'above_normal': psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                    'normal': psutil.NORMAL_PRIORITY_CLASS,
                }
            else:
                # Linux nice values: lower = higher priority
                priority_map = {
                    'realtime': -20,
                    'high': -10,
                    'above_normal': -5,
                    'normal': 0,
                }
            
            if priority in priority_map:
                proc.nice(priority_map[priority])
                print(f"[OK] Set priority: {priority}")
            else:
                print(f"[WARN] Unknown priority: {priority}")
        
        except psutil.AccessDenied:
            print(f"[ERROR] Cannot set priority - need admin rights")
        except Exception as e:
            print(f"[ERROR] Failed to set priority: {e}")
    
    def _apply_affinity(self, proc: psutil.Process, affinity: str):
        """Set CPU affinity"""
        if not hasattr(proc, 'cpu_affinity'):
            print("[WARN] CPU affinity not supported on this platform")
            return
        
        try:
            cpu_count = psutil.cpu_count(logical=True)
            
            if affinity == "performance_cores":
                # Use first half of CPUs (usually P-cores)
                cores = list(range(cpu_count // 2))
            elif affinity == "all_cores":
                cores = list(range(cpu_count))
            else:
                print(f"[WARN] Unknown affinity: {affinity}")
                return
            
            proc.cpu_affinity(cores)
            print(f"[OK] Set affinity: {cores}")
        
        except Exception as e:
            print(f"[ERROR] Failed to set affinity: {e}")
    
    def _cleanup_ram(self, reserved_mb: int):
        """Clean up RAM (placeholder)"""
        print(f"[INFO] RAM cleanup requested (reserve {reserved_mb} MB)")
        # TODO: Implement actual RAM cleanup
    
    def revert_optimizations(self):
        """Revert all applied optimizations
        
        Fixed: Better error handling
        """
        for pid, original in list(self.applied_optimizations.items()):
            try:
                if not psutil.pid_exists(pid):
                    continue
                
                proc = psutil.Process(pid)
                
                # Revert priority
                if original.get('priority') is not None:
                    try:
                        proc.nice(original['priority'])
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                
                # Revert affinity
                if original.get('affinity') is not None:
                    try:
                        proc.cpu_affinity(original['affinity'])
                    except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
                        pass
                
                print(f"[OK] Reverted optimizations for PID {pid}")
            
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"[WARN] Could not revert PID {pid}: {e}")
            except Exception as e:
                print(f"[ERROR] Revert failed for PID {pid}: {e}")
        
        self.applied_optimizations.clear()
        print("[OK] All optimizations reverted")
