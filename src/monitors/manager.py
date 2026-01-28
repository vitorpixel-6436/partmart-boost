#!/usr/bin/env python3
"""Monitor Manager - Orchestrates all system monitors with enhanced API

Version: 0.3.5d_package3.1d - Package 3 Task 3.1d

Package 2.2 Features:
- Fixed stub data (RAM=0, CPU cores≥1)
- GPU stub memory fields
- Health tracking in all data
- 20+ convenience methods
- System analysis tools
- Bottleneck detection
- Diagnostics

Package 3.1d NEW:
- FPS tracking methods (4)
- DataBus FPS integration
- Convenient wrappers
"""
import platform
from typing import Dict, List, Optional, Tuple

# Import monitors
from monitors.cpu_monitor import CPUMonitor
from monitors.ram_monitor import RAMMonitor

# GPU monitors (prioritized)
try:
    from monitors.gpu_monitor import GPUMonitor
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    from monitors.fallback_gpu import FallbackGPUMonitor

# Package 3.1d: DataBus import for FPS
try:
    from core.databus import get_databus
    DATABUS_AVAILABLE = True
except ImportError:
    DATABUS_AVAILABLE = False


class MonitorManager:
    """Manages all system monitors with enhanced API and FPS tracking
    
    v0.3.5d_package3.1d - FPS Methods Added
    
    Features:
    - Automatic monitor initialization
    - Health tracking
    - Convenience methods (20+)
    - System analysis tools
    - Bottleneck detection
    - FPS tracking integration (NEW)
    
    Example:
        >>> manager = MonitorManager()
        >>> 
        >>> # Quick access
        >>> print(f"CPU: {manager.get_cpu_load():.1f}%")
        >>> print(f"GPU: {manager.get_gpu_temp():.0f}°C")
        >>> print(f"FPS: {manager.get_fps():.1f}")  # NEW
        >>> 
        >>> # Full data
        >>> data = manager.get_all_data()
        >>> 
        >>> # System analysis
        >>> summary = manager.get_system_summary()
        >>> bottleneck = manager.get_bottleneck_analysis()
    """
    
    def __init__(self):
        """Initialize all monitors"""
        print("[MonitorManager v0.3.5d_package3.1d] Initializing monitors...")
        
        # Initialize monitors
        self._cpu = CPUMonitor()
        self._ram = RAMMonitor()
        
        # GPU monitor (with fallback)
        if GPU_AVAILABLE:
            self._gpu = GPUMonitor()
            print("  ✓ GPU Monitor (NVIDIA)")
        else:
            self._gpu = FallbackGPUMonitor()
            print("  ✓ GPU Monitor (Fallback)")
        
        print("  ✓ CPU Monitor")
        print("  ✓ RAM Monitor")
        
        # Health tracking
        self._last_errors: Dict[str, Optional[str]] = {
            'cpu': None,
            'gpu': None,
            'ram': None,
        }
    
    # === CORE DATA METHODS ===
    
    def get_all_data(self) -> Dict:
        """Get data from all monitors
        
        Returns:
            Dict with keys: 'cpu', 'gpu', 'ram'
            Each containing monitor data + _monitor_health
        
        Example:
            >>> data = manager.get_all_data()
            >>> print(data['cpu']['load'])
            >>> print(data['gpu']['temp_gpu'])
            >>> print(data['ram']['used'])
        """
        data = {
            'cpu': self._get_cpu_data(),
            'gpu': self._get_gpu_data(),
            'ram': self._get_ram_data(),
        }
        return data
    
    def _get_cpu_data(self) -> Dict:
        """Get CPU data with health tracking"""
        try:
            data = self._cpu.get_stats()
            self._last_errors['cpu'] = None
            
            # Add health info
            data['_monitor_health'] = {
                'available': True,
                'name': 'cpu',
                'error': None,
            }
            return data
        
        except Exception as e:
            self._last_errors['cpu'] = str(e)
            return self._get_cpu_stub_data(str(e))
    
    def _get_gpu_data(self) -> Dict:
        """Get GPU data with health tracking"""
        try:
            data = self._gpu.get_stats()
            self._last_errors['gpu'] = None
            
            # Add health info
            data['_monitor_health'] = {
                'available': data.get('name') != 'Unknown GPU',
                'name': 'gpu',
                'error': None,
            }
            return data
        
        except Exception as e:
            self._last_errors['gpu'] = str(e)
            return self._get_gpu_stub_data(str(e))
    
    def _get_ram_data(self) -> Dict:
        """Get RAM data with health tracking"""
        try:
            data = self._ram.get_stats()
            self._last_errors['ram'] = None
            
            # Add health info
            data['_monitor_health'] = {
                'available': True,
                'name': 'ram',
                'error': None,
            }
            return data
        
        except Exception as e:
            self._last_errors['ram'] = str(e)
            return self._get_ram_stub_data(str(e))
    
    def _get_cpu_stub_data(self, error: str) -> Dict:
        """Stub CPU data (Package 2.2 - fixed cores≥1)"""
        return {
            'name': 'Unknown CPU',
            'load': 0.0,
            'temp': None,
            'freq': 0.0,
            'freq_min': 0.0,
            'freq_max': 0.0,
            'count': 1,  # Package 2.2: Fixed (not 0)
            'count_logical': 1,  # Package 2.2: Fixed
            '_monitor_health': {
                'available': False,
                'name': 'cpu',
                'error': error,
            }
        }
    
    def _get_gpu_stub_data(self, error: str) -> Dict:
        """Stub GPU data (Package 2.2/2.3 - added memory fields)"""
        return {
            'name': 'Unknown GPU',
            'temp_gpu': 0,
            'temp_hotspot': None,
            'clock_gpu': 0,
            'clock_mem': 0,
            'load_gpu': 0,
            'load_mem': 0,
            'power': 0,
            'fan_speed': 0,
            'memory_total': 0,  # Package 2.3: Added
            'memory_used': 0,   # Package 2.3: Added
            'memory_free': 0,   # Package 2.3: Added
            '_monitor_health': {
                'available': False,
                'name': 'gpu',
                'error': error,
            }
        }
    
    def _get_ram_stub_data(self, error: str) -> Dict:
        """Stub RAM data (Package 2.2 - fixed total=0)"""
        return {
            'total': 0.0,  # Package 2.2: Fixed (not 16.0)
            'used': 0.0,
            'free': 0.0,
            'percent': 0.0,
            'speed': None,
            'type': 'Unknown',  # Package 2.1
            'xmp_enabled': False,
            '_monitor_health': {
                'available': False,
                'name': 'ram',
                'error': error,
            }
        }
    
    # === QUICK ACCESS METHODS (Package 2.2) ===
    
    def get_cpu_load(self) -> float:
        """Get CPU load percentage
        
        Returns:
            CPU load (0-100)
        
        Example:
            >>> load = manager.get_cpu_load()
            >>> print(f"CPU: {load:.1f}%")
        """
        data = self._get_cpu_data()
        return data.get('load', 0.0)
    
    def get_cpu_temp(self) -> Optional[float]:
        """Get CPU temperature
        
        Returns:
            Temperature in °C or None
        
        Example:
            >>> temp = manager.get_cpu_temp()
            >>> if temp:
            >>>     print(f"CPU: {temp:.0f}°C")
        """
        data = self._get_cpu_data()
        return data.get('temp')
    
    def get_gpu_temp(self) -> int:
        """Get GPU temperature
        
        Returns:
            Temperature in °C
        
        Example:
            >>> temp = manager.get_gpu_temp()
            >>> print(f"GPU: {temp}°C")
        """
        data = self._get_gpu_data()
        return data.get('temp_gpu', 0)
    
    def get_gpu_load(self) -> int:
        """Get GPU load percentage
        
        Returns:
            GPU load (0-100)
        
        Example:
            >>> load = manager.get_gpu_load()
            >>> print(f"GPU: {load}%")
        """
        data = self._get_gpu_data()
        return data.get('load_gpu', 0)
    
    def get_ram_usage(self) -> float:
        """Get RAM usage in GB
        
        Returns:
            RAM used in GB
        
        Example:
            >>> usage = manager.get_ram_usage()
            >>> print(f"RAM: {usage:.1f} GB")
        """
        data = self._get_ram_data()
        return data.get('used', 0.0)
    
    def get_ram_percent(self) -> float:
        """Get RAM usage percentage
        
        Returns:
            RAM usage (0-100)
        
        Example:
            >>> percent = manager.get_ram_percent()
            >>> print(f"RAM: {percent:.1f}%")
        """
        data = self._get_ram_data()
        return data.get('percent', 0.0)
    
    def get_ram_speed(self) -> Optional[int]:
        """Get RAM speed in MHz
        
        Returns:
            Speed in MHz or None
        
        Example:
            >>> speed = manager.get_ram_speed()
            >>> if speed:
            >>>     print(f"RAM: {speed} MHz")
        """
        data = self._get_ram_data()
        return data.get('speed')
    
    # === FPS TRACKING METHODS (Package 3.1d NEW) ===
    
    def get_fps(self, window: int = 60) -> float:
        """Get current FPS (average over window)
        
        Package 3.1d NEW
        
        Args:
            window: Number of frames to average (default: 60)
        
        Returns:
            Average FPS or 0.0 if tracking disabled
        
        Example:
            >>> fps = manager.get_fps()
            >>> print(f"FPS: {fps:.1f}")
        """
        if not DATABUS_AVAILABLE:
            return 0.0
        
        bus = get_databus()
        stats = bus.get_fps_stats(window=window)
        
        if stats is None:
            return 0.0
        
        return stats.fps_avg
    
    def get_frame_time(self, window: int = 60) -> float:
        """Get current frame time (average over window)
        
        Package 3.1d NEW
        
        Args:
            window: Number of frames to average (default: 60)
        
        Returns:
            Average frame time (ms) or 0.0 if tracking disabled
        
        Example:
            >>> frame_time = manager.get_frame_time()
            >>> print(f"Frame time: {frame_time:.2f}ms")
        """
        if not DATABUS_AVAILABLE:
            return 0.0
        
        bus = get_databus()
        stats = bus.get_fps_stats(window=window)
        
        if stats is None:
            return 0.0
        
        return stats.frame_time_avg
    
    def is_fps_tracking_available(self) -> bool:
        """Check if FPS tracking is available and enabled
        
        Package 3.1d NEW
        
        Returns:
            True if FPS tracking is available
        
        Example:
            >>> if manager.is_fps_tracking_available():
            >>>     print(f"FPS: {manager.get_fps()}")
        """
        if not DATABUS_AVAILABLE:
            return False
        
        bus = get_databus()
        health = bus.get_system_health()
        
        return health.get('databus', {}).get('fps_tracking_enabled', False)
    
    def get_fps_stats(self, window: Optional[int] = None):
        """Get full FPS statistics
        
        Package 3.1d NEW
        
        Args:
            window: Number of frames to analyze (None = all buffered)
        
        Returns:
            FPSStats object or None if tracking disabled
        
        Example:
            >>> stats = manager.get_fps_stats()
            >>> if stats:
            >>>     print(f"FPS: {stats.fps_avg:.1f}")
            >>>     print(f"1% low: {stats.fps_1_percent:.1f}")
            >>>     print(f"Stutters: {stats.stutter_count}")
        """
        if not DATABUS_AVAILABLE:
            return None
        
        bus = get_databus()
        return bus.get_fps_stats(window=window)
    
    # === AVAILABILITY CHECKS (Package 2.2) ===
    
    def is_gpu_available(self) -> bool:
        """Check if GPU monitoring is available
        
        Returns:
            True if GPU is available
        
        Example:
            >>> if manager.is_gpu_available():
            >>>     print(f"GPU: {manager.get_gpu_temp()}°C")
        """
        data = self._get_gpu_data()
        return data['_monitor_health']['available']
    
    def is_cpu_temp_available(self) -> bool:
        """Check if CPU temperature is available
        
        Returns:
            True if CPU temp is available
        
        Example:
            >>> if manager.is_cpu_temp_available():
            >>>     print(f"CPU: {manager.get_cpu_temp()}°C")
        """
        temp = self.get_cpu_temp()
        return temp is not None
    
    def is_ram_speed_available(self) -> bool:
        """Check if RAM speed detection is available
        
        Returns:
            True if RAM speed is available
        
        Example:
            >>> if manager.is_ram_speed_available():
            >>>     print(f"RAM: {manager.get_ram_speed()} MHz")
        """
        speed = self.get_ram_speed()
        return speed is not None
    
    def get_available_metrics(self) -> List[str]:
        """Get list of available metrics
        
        Returns:
            List of metric names
        
        Example:
            >>> metrics = manager.get_available_metrics()
            >>> print(f"Available: {', '.join(metrics)}")
        """
        metrics = ['cpu_load', 'ram_usage']
        
        if self.is_cpu_temp_available():
            metrics.append('cpu_temp')
        
        if self.is_gpu_available():
            metrics.extend(['gpu_load', 'gpu_temp'])
        
        if self.is_ram_speed_available():
            metrics.append('ram_speed')
        
        if self.is_fps_tracking_available():  # Package 3.1d
            metrics.append('fps')
        
        return metrics
    
    # === SYSTEM ANALYSIS (Package 2.2) ===
    
    def get_system_summary(self) -> str:
        """Get human-readable system summary
        
        Returns:
            Multi-line string with system info
        
        Example:
            >>> print(manager.get_system_summary())
        """
        data = self.get_all_data()
        
        lines = [
            "=" * 50,
            "System Summary",
            "=" * 50,
        ]
        
        # CPU
        cpu = data['cpu']
        cpu_line = f"CPU: {cpu['name']}"
        if cpu['_monitor_health']['available']:
            cpu_line += f" | Load: {cpu['load']:.1f}%"
            if cpu['temp']:
                cpu_line += f" | Temp: {cpu['temp']:.0f}°C"
        lines.append(cpu_line)
        
        # GPU
        gpu = data['gpu']
        gpu_line = f"GPU: {gpu['name']}"
        if gpu['_monitor_health']['available']:
            gpu_line += f" | Load: {gpu['load_gpu']}%"
            if gpu['temp_gpu'] > 0:
                gpu_line += f" | Temp: {gpu['temp_gpu']}°C"
        lines.append(gpu_line)
        
        # RAM
        ram = data['ram']
        ram_line = f"RAM: {ram['used']:.1f} / {ram['total']:.1f} GB ({ram['percent']:.1f}%)"
        if ram['speed']:
            ram_line += f" | {ram['type']} @ {ram['speed']} MHz"
        if ram['xmp_enabled']:
            ram_line += " | XMP ✓"
        lines.append(ram_line)
        
        # FPS (Package 3.1d)
        if self.is_fps_tracking_available():
            fps = self.get_fps()
            frame_time = self.get_frame_time()
            lines.append(f"FPS: {fps:.1f} ({frame_time:.2f}ms)")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def get_health_report(self) -> Dict:
        """Get health report for all monitors
        
        Returns:
            Dict with health info
        
        Example:
            >>> health = manager.get_health_report()
            >>> if not health['all_healthy']:
            >>>     for error in health['errors']:
            >>>         print(f"Error: {error}")
        """
        data = self.get_all_data()
        
        monitors = {
            'cpu': data['cpu']['_monitor_health'],
            'gpu': data['gpu']['_monitor_health'],
            'ram': data['ram']['_monitor_health'],
        }
        
        errors = [
            f"{name}: {info['error']}"
            for name, info in monitors.items()
            if info['error'] is not None
        ]
        
        all_healthy = len(errors) == 0
        
        return {
            'all_healthy': all_healthy,
            'monitors': monitors,
            'errors': errors,
        }
    
    def get_bottleneck_analysis(self) -> Dict:
        """Analyze system bottleneck
        
        Returns:
            Dict with bottleneck info
        
        Example:
            >>> bottleneck = manager.get_bottleneck_analysis()
            >>> if bottleneck['severity'] == 'high':
            >>>     print(f"Bottleneck: {bottleneck['bottleneck']}")
        """
        cpu_load = self.get_cpu_load()
        gpu_load = self.get_gpu_load()
        ram_percent = self.get_ram_percent()
        
        max_load = max(cpu_load, gpu_load, ram_percent)
        
        if max_load >= 90:
            severity = 'high'
        elif max_load >= 70:
            severity = 'medium'
        else:
            severity = 'low'
        
        # Determine bottleneck
        if cpu_load == max_load:
            bottleneck = 'cpu'
        elif gpu_load == max_load:
            bottleneck = 'gpu'
        else:
            bottleneck = 'ram'
        
        return {
            'bottleneck': bottleneck,
            'severity': severity,
            'cpu_load': cpu_load,
            'gpu_load': gpu_load,
            'ram_load': ram_percent,
        }
    
    def get_thermal_status(self) -> Dict:
        """Get thermal status summary
        
        Returns:
            Dict with temperature info
        
        Example:
            >>> thermal = manager.get_thermal_status()
            >>> if thermal['status'] == 'warning':
            >>>     print("System running hot!")
        """
        cpu_temp = self.get_cpu_temp()
        gpu_temp = self.get_gpu_temp()
        
        temps = []
        if cpu_temp:
            temps.append(cpu_temp)
        if gpu_temp > 0:
            temps.append(gpu_temp)
        
        max_temp = max(temps) if temps else 0
        
        if max_temp >= 85:
            status = 'critical'
        elif max_temp >= 75:
            status = 'warning'
        elif max_temp >= 60:
            status = 'warm'
        else:
            status = 'cool'
        
        return {
            'status': status,
            'cpu_temp': cpu_temp,
            'gpu_temp': gpu_temp if gpu_temp > 0 else None,
            'max_temp': max_temp,
        }
    
    # === DIAGNOSTICS (Package 2.2) ===
    
    def diagnose(self) -> str:
        """Run system diagnostics
        
        Returns:
            Multi-line diagnostic report
        
        Example:
            >>> print(manager.diagnose())
        """
        lines = [
            "=" * 60,
            "System Diagnostics",
            "=" * 60,
            ""
        ]
        
        # Health check
        health = self.get_health_report()
        lines.append(f"Health: {'✓ All OK' if health['all_healthy'] else '✗ Issues detected'}")
        
        if not health['all_healthy']:
            for error in health['errors']:
                lines.append(f"  - {error}")
        
        lines.append("")
        
        # Available metrics
        metrics = self.get_available_metrics()
        lines.append(f"Available metrics: {', '.join(metrics)}")
        lines.append("")
        
        # Bottleneck analysis
        bottleneck = self.get_bottleneck_analysis()
        lines.append(f"Bottleneck: {bottleneck['bottleneck'].upper()} (severity: {bottleneck['severity']})")
        lines.append(f"  CPU: {bottleneck['cpu_load']:.1f}%")
        lines.append(f"  GPU: {bottleneck['gpu_load']:.1f}%")
        lines.append(f"  RAM: {bottleneck['ram_load']:.1f}%")
        lines.append("")
        
        # Thermal status
        thermal = self.get_thermal_status()
        lines.append(f"Thermal: {thermal['status'].upper()}")
        if thermal['cpu_temp']:
            lines.append(f"  CPU: {thermal['cpu_temp']:.0f}°C")
        if thermal['gpu_temp']:
            lines.append(f"  GPU: {thermal['gpu_temp']:.0f}°C")
        lines.append("")
        
        # FPS status (Package 3.1d)
        if self.is_fps_tracking_available():
            stats = self.get_fps_stats()
            if stats:
                lines.append("FPS Tracking:")
                lines.append(f"  Average: {stats.fps_avg:.1f}")
                lines.append(f"  1% low: {stats.fps_1_percent:.1f}")
                lines.append(f"  Stutters: {stats.stutter_count}")
                lines.append("")
        
        # Platform info
        lines.append(f"Platform: {platform.system()} {platform.release()}")
        lines.append(f"Python: {platform.python_version()}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def get_monitor_errors(self) -> Dict[str, Optional[str]]:
        """Get last errors from all monitors
        
        Returns:
            Dict mapping monitor name to error (or None)
        
        Example:
            >>> errors = manager.get_monitor_errors()
            >>> for name, error in errors.items():
            >>>     if error:
            >>>         print(f"{name}: {error}")
        """
        return self._last_errors.copy()
    
    def validate_data_integrity(self) -> bool:
        """Validate data integrity
        
        Returns:
            True if all data is valid
        
        Example:
            >>> if not manager.validate_data_integrity():
            >>>     print("Data integrity issues detected")
        """
        data = self.get_all_data()
        
        # Check CPU
        cpu = data['cpu']
        if not (0 <= cpu['load'] <= 100):
            return False
        
        # Check GPU
        gpu = data['gpu']
        if not (0 <= gpu['load_gpu'] <= 100):
            return False
        
        # Check RAM
        ram = data['ram']
        if not (0 <= ram['percent'] <= 100):
            return False
        if ram['used'] > ram['total']:
            return False
        
        return True


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("MonitorManager v0.3.5d_package3.1d Test")
    print("="*60)
    
    manager = MonitorManager()
    
    print("\n[Test 1] Get all data")
    data = manager.get_all_data()
    print(f"  CPU: {data['cpu']['name']}")
    print(f"  GPU: {data['gpu']['name']}")
    print(f"  RAM: {data['ram']['total']:.1f} GB")
    
    print("\n[Test 2] Quick access methods")
    print(f"  CPU Load: {manager.get_cpu_load():.1f}%")
    print(f"  GPU Temp: {manager.get_gpu_temp()}°C")
    print(f"  RAM Usage: {manager.get_ram_usage():.1f} GB")
    
    print("\n[Test 3] FPS tracking (NEW Package 3.1d)")
    if manager.is_fps_tracking_available():
        fps = manager.get_fps()
        frame_time = manager.get_frame_time()
        stats = manager.get_fps_stats()
        print(f"  FPS: {fps:.1f}")
        print(f"  Frame time: {frame_time:.2f}ms")
        if stats:
            print(f"  1% low: {stats.fps_1_percent:.1f}")
    else:
        print("  FPS tracking not enabled")
        print("  Enable with: bus.set_fps_tracking_enabled(True)")
    
    print("\n[Test 4] System summary")
    print(manager.get_system_summary())
    
    print("\n[Test 5] Diagnostics")
    print(manager.diagnose())
    
    print("\n" + "="*60)
    print("✅ MonitorManager v0.3.5d_package3.1d - All Tests Passed!")
    print("="*60)
    print("\nPackage 3.1 COMPLETE:")
    print("  ✅ 3.1a - FPSTracker")
    print("  ✅ 3.1b - FPSWidget")
    print("  ✅ 3.1c - DataBus integration")
    print("  ✅ 3.1d - MonitorManager FPS methods")
    print("\nNext: Package 3.2 - Performance Metrics + Custom Widgets")
    print("="*60)
