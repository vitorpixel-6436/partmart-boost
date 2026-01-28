#!/usr/bin/env python3
"""Integration Tests for PartMart Boost

Version: 0.3.5d_package3.6a.4 - Full System Test

Comprehensive testing of all modules.
"""
import sys
import time
import threading
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

print("="*80)
print("🧪 PARTMART BOOST - FULL SYSTEM TEST")
print("Version: 0.3.5d_package3.6a.4")
print("="*80)

# Test results
test_results = []

def run_test(name: str, test_func) -> bool:
    """Run a test and track result"""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {name}")
    print(f"{'='*80}")
    
    try:
        start = time.perf_counter()
        test_func()
        elapsed = time.perf_counter() - start
        
        print(f"\n✅ PASSED in {elapsed:.3f}s")
        test_results.append((name, True, elapsed))
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        test_results.append((name, False, 0))
        return False

# ========== TEST MODULES ==========

def test_fps_tracker():
    """Test FPS Tracker"""
    from core.fps_tracker import FPSTracker
    
    tracker = FPSTracker(window_size=30)
    
    # Simulate 60 FPS
    for i in range(60):
        time.sleep(1/60)
        fps = tracker.frame()
    
    stats = tracker.get_stats()
    print(f"FPS: {stats.average:.1f}")
    
    assert 50 < stats.average < 70, f"FPS out of range: {stats.average}"
    
    # Test thread safety
    def worker():
        for _ in range(20):
            tracker.frame()
            time.sleep(0.01)
    
    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    health = tracker.get_health_stats()
    print(f"Health: {health}")

def test_performance_monitor():
    """Test Performance Monitor"""
    from monitors.performance_monitor import PerformanceMonitor
    
    monitor = PerformanceMonitor()
    monitor.start()
    
    # Collect metrics
    for i in range(5):
        metrics = monitor.get_metrics()
        if metrics:
            print(f"Sample {i+1}: FPS={metrics.fps:.1f}, GPU={metrics.gpu_util:.1f}%")
        time.sleep(0.1)
    
    health = monitor.get_health_stats()
    print(f"Health: {health}")
    
    monitor.stop()

def test_frame_generator():
    """Test Frame Generator"""
    from framegen.generator import FrameGenerator, FrameBuffer
    import numpy as np
    
    gen = FrameGenerator()
    
    # Create test frames
    frame1 = FrameBuffer(
        data=np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8),
        width=1920,
        height=1080,
        stride=1920 * 3,
        format='RGB',
        timestamp=0.0,
    )
    frame1.checksum = gen._calculate_checksum(frame1)
    
    frame2 = FrameBuffer(
        data=np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8),
        width=1920,
        height=1080,
        stride=1920 * 3,
        format='RGB',
        timestamp=0.016,
    )
    frame2.checksum = gen._calculate_checksum(frame2)
    
    # Generate intermediate
    result = gen.generate(frame1, frame2, 0.5)
    print(f"Generated: {result.width}x{result.height} @ {result.timestamp:.6f}s")
    
    # Verify checksum
    assert result.checksum is not None
    assert gen._verify_checksum(result)
    
    stats = gen.get_stats()
    print(f"Stats: {stats}")

def test_upscaler():
    """Test Upscaler"""
    from upscaler.upscaler import Upscaler, ScalingMode
    import numpy as np
    
    upscaler = Upscaler()
    
    # Test standard resolution
    input_img = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
    output = upscaler.upscale(input_img, (3840, 2160), ScalingMode.FIT)
    print(f"Upscaled: {input_img.shape[1]}x{input_img.shape[0]} -> {output.shape[1]}x{output.shape[0]}")
    
    # Test ultra-wide
    input_img = np.random.randint(0, 256, (1080, 2560, 3), dtype=np.uint8)
    output = upscaler.upscale(input_img, (5120, 2160), ScalingMode.FIT)
    print(f"Ultra-wide: {input_img.shape[1]}x{input_img.shape[0]} -> {output.shape[1]}x{output.shape[0]}")
    
    stats = upscaler.get_stats()
    print(f"Stats: {stats}")

def test_thermal_manager():
    """Test Thermal Manager"""
    from adaptive.thermal_manager_advanced import ThermalManagerAdvanced, ThermalConfig
    
    config = ThermalConfig(
        warning_temp=80.0,
        throttle_temp=90.0,
        critical_temp=100.0,
        emergency_temp=110.0,
        cooldown_time=0.2,
    )
    
    manager = ThermalManagerAdvanced(config)
    
    # Test heating
    temps = [70, 75, 80, 85, 90]
    for temp in temps:
        manager.update_temperature(temp)
        time.sleep(0.3)
        state = manager.get_state()
        print(f"  {temp}°C: {state.value}")
    
    health = manager.get_health_stats()
    print(f"Health: {health}")

def test_power_manager():
    """Test Power Manager"""
    from adaptive.power_manager_advanced import PowerManagerAdvanced, PowerMode
    
    manager = PowerManagerAdvanced()
    
    # Update state
    for i in range(3):
        manager.update()
        state = manager.get_power_state()
        mode = manager.get_power_mode()
        print(f"  Update {i+1}: {state.value} / {mode.value}")
        time.sleep(0.2)
    
    # Change mode
    manager.set_power_mode(PowerMode.PERFORMANCE)
    time.sleep(0.2)
    manager.set_power_mode(PowerMode.POWER_SAVER)
    
    health = manager.get_health_stats()
    print(f"Health: {health}")

def test_resource_manager():
    """Test Resource Manager"""
    from core.resource_manager import ResourceManager
    
    manager = ResourceManager()
    
    # Simple acquire/release
    handle = manager.acquire("gpu", "thread1", timeout=1.0)
    assert handle is not None
    print(f"Acquired: {handle}")
    
    assert manager.release(handle)
    print(f"Released: {handle}")
    
    # Concurrent access
    handle1 = manager.acquire("gpu", "thread1", timeout=1.0)
    handle2 = manager.acquire("gpu", "thread2", timeout=0.5)
    print(f"Thread1: {handle1}")
    print(f"Thread2: {handle2}")  # Should be None
    
    if handle1:
        manager.release(handle1)
    
    stats = manager.get_stats()
    print(f"Stats: {stats}")

def test_system_integration():
    """Test System Integration"""
    from adaptive.system_integration import SystemIntegration
    
    system = SystemIntegration()
    
    # Initialize
    assert system.initialize(), "Failed to initialize"
    
    # Start
    assert system.start(), "Failed to start"
    
    # Update loop
    for i in range(3):
        assert system.update(), f"Update {i+1} failed"
        time.sleep(0.1)
    
    # Check state
    assert system.is_running(), "System not running"
    
    # Shutdown
    system.shutdown()
    
    print("System integration test passed")

# ========== RUN ALL TESTS ==========

print("\n" + "="*80)
print("🚀 RUNNING ALL TESTS")
print("="*80)

tests = [
    ("FPS Tracker", test_fps_tracker),
    ("Performance Monitor", test_performance_monitor),
    ("Frame Generator", test_frame_generator),
    ("Upscaler", test_upscaler),
    ("Thermal Manager", test_thermal_manager),
    ("Power Manager", test_power_manager),
    ("Resource Manager", test_resource_manager),
    ("System Integration", test_system_integration),
]

for name, func in tests:
    run_test(name, func)
    time.sleep(0.5)  # Brief pause between tests

# ========== RESULTS ==========

print("\n" + "="*80)
print("📊 TEST RESULTS")
print("="*80)

passed = sum(1 for _, result, _ in test_results if result)
total = len(test_results)

for name, result, elapsed in test_results:
    status = "✅ PASS" if result else "❌ FAIL"
    time_str = f"{elapsed:.3f}s" if result else "N/A"
    print(f"{status:10s} {time_str:>8s}  {name}")

print("\n" + "="*80)
print(f"📈 SUMMARY: {passed}/{total} tests passed ({passed*100//total}%)")
print("="*80)

if passed == total:
    print("\n🎉 ALL TESTS PASSED! 🎉")
    sys.exit(0)
else:
    print(f"\n⚠️  {total - passed} TEST(S) FAILED")
    sys.exit(1)
