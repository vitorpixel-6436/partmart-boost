#!/usr/bin/env python3
"""Universal Upscaler Test Suite

Version: 0.4.0-alpha
"""
import sys
import time
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import numpy as np

try:
    from upscaler import (
        UniversalUpscaler,
        UpscalerContext,
        QualityMode,
        UpscalerBackend,
        FrameData
    )
    UPSCALER_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: Upscaler not available: {e}")
    UPSCALER_AVAILABLE = False
    sys.exit(1)


def test_gpu_detection():
    """Test 1: GPU Detection"""
    print("\n" + "="*60)
    print("TEST 1: GPU Detection")
    print("="*60)
    
    from upscaler.gpu_detector import detect_gpu
    
    gpu = detect_gpu()
    
    print(f"\n  GPU Vendor: {gpu.vendor.name}")
    print(f"  GPU Name: {gpu.name}")
    print(f"  GPU Memory: {gpu.memory_mb} MB")
    print(f"  Driver: {gpu.driver_version}")
    print(f"  FSR Support: {'✅' if gpu.supports_fsr else '❌'}")
    print(f"  XeSS Support: {'✅' if gpu.supports_xess else '❌'}")
    
    assert gpu.vendor.name in ['NVIDIA', 'AMD', 'INTEL', 'UNKNOWN']
    print("\n✅ GPU detection: PASS")


def test_initialization():
    """Test 2: Upscaler Initialization"""
    print("\n" + "="*60)
    print("TEST 2: Upscaler Initialization")
    print("="*60)
    
    upscaler = UniversalUpscaler()
    status = upscaler.initialize()
    
    assert upscaler.is_initialized(), "Upscaler not initialized"
    
    backend = upscaler.get_active_backend()
    print(f"\n  Active backend: {backend.name}")
    
    gpu_info = upscaler.get_gpu_info()
    print(f"  GPU: {gpu_info.get('name', 'Unknown')}")
    
    upscaler.shutdown()
    assert not upscaler.is_initialized(), "Upscaler still initialized"
    
    print("\n✅ Initialization: PASS")


def test_context_creation():
    """Test 3: Context Creation"""
    print("\n" + "="*60)
    print("TEST 3: Context Creation")
    print("="*60)
    
    upscaler = UniversalUpscaler()
    upscaler.initialize()
    
    # Test all quality modes
    for mode in [QualityMode.PERFORMANCE, QualityMode.BALANCED,
                 QualityMode.QUALITY, QualityMode.ULTRA_QUALITY]:
        
        print(f"\n  Testing {mode.name} mode...")
        
        context = upscaler.create_context(
            input_resolution=(1920, 1080),
            output_resolution=(3840, 2160),
            quality_mode=mode
        )
        
        assert context is not None, f"Context creation failed for {mode.name}"
        print(f"    ✅ {mode.name}: OK")
    
    upscaler.shutdown()
    print("\n✅ Context creation: PASS")


def test_upscaling():
    """Test 4: Upscaling"""
    print("\n" + "="*60)
    print("TEST 4: Upscaling")
    print("="*60)
    
    upscaler = UniversalUpscaler()
    upscaler.initialize()
    
    context = upscaler.create_context(
        input_resolution=(1920, 1080),
        output_resolution=(3840, 2160),
        quality_mode=QualityMode.QUALITY
    )
    
    # Create test frame
    test_frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
    frame_data = FrameData(color=test_frame)
    
    # Upscale
    print("\n  Upscaling 1080p → 4K...")
    upscaled, metrics = context.upscale(frame_data)
    
    # Verify
    assert upscaled.shape == (2160, 3840, 3), f"Wrong output shape: {upscaled.shape}"
    assert upscaled.dtype == np.uint8, f"Wrong dtype: {upscaled.dtype}"
    
    print(f"\n  Input: {test_frame.shape}")
    print(f"  Output: {upscaled.shape}")
    print(f"  Backend: {metrics.backend.name}")
    print(f"  Time: {metrics.upscale_time_ms:.2f}ms")
    print(f"  FPS: {metrics.fps:.1f}")
    print(f"  Memory: {metrics.memory_used_mb:.1f}MB")
    
    upscaler.shutdown()
    print("\n✅ Upscaling: PASS")


def test_backend_swapping():
    """Test 5: Backend Swapping"""
    print("\n" + "="*60)
    print("TEST 5: Backend Swapping")
    print("="*60)
    
    upscaler = UniversalUpscaler()
    upscaler.initialize()
    
    initial_backend = upscaler.get_active_backend()
    print(f"\n  Initial backend: {initial_backend.name}")
    
    # Try to swap
    available_backends = [UpscalerBackend.FSR3, UpscalerBackend.XESS, UpscalerBackend.SOFTWARE]
    
    for backend in available_backends:
        if backend != initial_backend:
            print(f"\n  Swapping to {backend.name}...")
            success = upscaler.swap_backend(backend)
            
            if success:
                new_backend = upscaler.get_active_backend()
                print(f"    ✅ Swapped to {new_backend.name}")
            else:
                print(f"    ⚠️ {backend.name} not available")
    
    upscaler.shutdown()
    print("\n✅ Backend swapping: PASS")


def test_performance():
    """Test 6: Performance Benchmark"""
    print("\n" + "="*60)
    print("TEST 6: Performance Benchmark")
    print("="*60)
    
    upscaler = UniversalUpscaler()
    upscaler.initialize()
    
    context = upscaler.create_context(
        input_resolution=(1920, 1080),
        output_resolution=(3840, 2160),
        quality_mode=QualityMode.QUALITY
    )
    
    # Benchmark 100 frames
    num_frames = 100
    times = []
    
    print(f"\n  Benchmarking {num_frames} frames...")
    
    for i in range(num_frames):
        frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        frame_data = FrameData(color=frame)
        
        start = time.perf_counter()
        upscaled, metrics = context.upscale(frame_data)
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        
        if (i + 1) % 25 == 0:
            print(f"    Progress: {i+1}/{num_frames}")
    
    # Statistics
    avg_time = np.mean(times)
    min_time = np.min(times)
    max_time = np.max(times)
    avg_fps = 1000.0 / avg_time
    
    backend = upscaler.get_active_backend()
    
    print(f"\n  Results ({num_frames} frames, {backend.name} backend):")
    print(f"    Average: {avg_time:.2f}ms ({avg_fps:.1f} FPS)")
    print(f"    Min: {min_time:.2f}ms ({1000/min_time:.1f} FPS)")
    print(f"    Max: {max_time:.2f}ms ({1000/max_time:.1f} FPS)")
    
    upscaler.shutdown()
    print("\n✅ Performance benchmark: PASS")


def test_error_handling():
    """Test 7: Error Handling"""
    print("\n" + "="*60)
    print("TEST 7: Error Handling")
    print("="*60)
    
    upscaler = UniversalUpscaler()
    
    # Test: Create context before init
    print("\n  Test: Context before init...")
    context = upscaler.create_context((1920, 1080), (3840, 2160))
    assert context is None, "Should fail without init"
    print("    ✅ Correctly rejected")
    
    upscaler.initialize()
    
    # Test: Invalid resolution
    print("\n  Test: Invalid resolution...")
    try:
        context = upscaler.create_context((0, 0), (3840, 2160))
        print("    ✅ Handled gracefully")
    except Exception as e:
        print(f"    ✅ Exception caught: {e}")
    
    upscaler.shutdown()
    print("\n✅ Error handling: PASS")


def test_multithreaded():
    """Test 8: Multi-threaded Stress Test"""
    print("\n" + "="*60)
    print("TEST 8: Multi-threaded Stress Test")
    print("="*60)
    
    upscaler = UniversalUpscaler()
    upscaler.initialize()
    
    context = upscaler.create_context(
        input_resolution=(1920, 1080),
        output_resolution=(3840, 2160),
        quality_mode=QualityMode.QUALITY
    )
    
    errors = []
    
    def worker(thread_id, num_frames):
        try:
            for i in range(num_frames):
                frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
                frame_data = FrameData(color=frame)
                upscaled, metrics = context.upscale(frame_data)
            print(f"    Thread {thread_id}: OK ({num_frames} frames)")
        except Exception as e:
            errors.append((thread_id, str(e)))
            print(f"    Thread {thread_id}: ERROR - {e}")
    
    # Launch 4 threads
    num_threads = 4
    frames_per_thread = 25
    
    print(f"\n  Launching {num_threads} threads ({frames_per_thread} frames each)...")
    
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i, frames_per_thread))
        t.start()
        threads.append(t)
    
    # Wait
    for t in threads:
        t.join()
    
    assert len(errors) == 0, f"Errors in threads: {errors}"
    
    upscaler.shutdown()
    print("\n✅ Multi-threaded test: PASS")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("UNIVERSAL UPSCALER TEST SUITE")
    print("Version: 0.4.0-alpha")
    print("="*60)
    
    if not UPSCALER_AVAILABLE:
        print("\n❌ Upscaler not available!")
        return False
    
    tests = [
        ("GPU Detection", test_gpu_detection),
        ("Initialization", test_initialization),
        ("Context Creation", test_context_creation),
        ("Upscaling", test_upscaling),
        ("Backend Swapping", test_backend_swapping),
        ("Performance", test_performance),
        ("Error Handling", test_error_handling),
        ("Multi-threaded", test_multithreaded),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ {name}: FAIL - {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ {name}: ERROR - {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"  Total: {passed + failed}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return True
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
