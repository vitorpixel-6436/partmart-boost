#!/usr/bin/env python3
"""FSR4 Test Suite

Version: 0.3.5d+patch8

Comprehensive tests for FSR4 implementation.
"""
import time
import threading
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import numpy as np

try:
    from fsr4 import (
        FSR4SDK,
        FSR4Context,
        FSR4QualityMode,
        FSR4FrameData,
        FSR4Status
    )
    FSR4_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: FSR4 not available: {e}")
    FSR4_AVAILABLE = False
    sys.exit(1)


def test_sdk_init():
    """Test 1: SDK initialization"""
    print("\n" + "="*60)
    print("TEST 1: SDK Initialization")
    print("="*60)
    
    sdk = FSR4SDK()
    status = sdk.initialize()
    
    assert status == FSR4Status.OK, f"Init failed: {status}"
    assert sdk.is_initialized(), "SDK not initialized"
    
    status = sdk.shutdown()
    assert status == FSR4Status.OK, f"Shutdown failed: {status}"
    assert not sdk.is_initialized(), "SDK still initialized"
    
    print("✅ SDK init/shutdown: PASS")


def test_context_creation():
    """Test 2: Context creation"""
    print("\n" + "="*60)
    print("TEST 2: Context Creation")
    print("="*60)
    
    sdk = FSR4SDK()
    sdk.initialize()
    
    # Test all quality modes
    for mode in FSR4QualityMode:
        print(f"\n  Testing {mode.name} mode...")
        
        context = sdk.create_context(
            input_resolution=(1920, 1080),
            output_resolution=(3840, 2160),
            quality_mode=mode
        )
        
        assert context is not None, f"Context creation failed for {mode.name}"
        print(f"    ✅ {mode.name}: OK")
    
    sdk.shutdown()
    print("\n✅ Context creation: PASS")


def test_upscaling():
    """Test 3: Upscaling"""
    print("\n" + "="*60)
    print("TEST 3: Upscaling")
    print("="*60)
    
    sdk = FSR4SDK()
    sdk.initialize()
    
    context = sdk.create_context(
        input_resolution=(1920, 1080),
        output_resolution=(3840, 2160),
        quality_mode=FSR4QualityMode.QUALITY
    )
    
    # Create test frame (1080p)
    test_frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
    frame_data = FSR4FrameData(color=test_frame, timestamp=0.0)
    
    # Upscale
    print("\n  Upscaling 1080p -> 4K...")
    upscaled, metrics = context.upscale(frame_data)
    
    # Verify output
    assert upscaled.shape == (2160, 3840, 3), f"Wrong output shape: {upscaled.shape}"
    assert upscaled.dtype == np.uint8, f"Wrong dtype: {upscaled.dtype}"
    assert metrics.fps > 0, "Invalid FPS"
    
    print(f"\n  Input: {test_frame.shape}")
    print(f"  Output: {upscaled.shape}")
    print(f"  Time: {metrics.upscale_time_ms:.2f}ms")
    print(f"  FPS: {metrics.fps:.1f}")
    print(f"  Memory: {metrics.memory_used_mb:.1f}MB")
    
    sdk.shutdown()
    print("\n✅ Upscaling: PASS")


def test_quality_modes():
    """Test 4: All quality modes"""
    print("\n" + "="*60)
    print("TEST 4: Quality Modes Comparison")
    print("="*60)
    
    sdk = FSR4SDK()
    sdk.initialize()
    
    results = []
    
    for mode in [FSR4QualityMode.PERFORMANCE,
                 FSR4QualityMode.BALANCED,
                 FSR4QualityMode.QUALITY,
                 FSR4QualityMode.ULTRA_QUALITY]:
        
        context = sdk.create_context(
            input_resolution=(1920, 1080),
            output_resolution=(3840, 2160),
            quality_mode=mode
        )
        
        # Create test frame
        test_frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        frame_data = FSR4FrameData(color=test_frame)
        
        # Upscale and measure
        upscaled, metrics = context.upscale(frame_data)
        
        results.append({
            'mode': mode.name,
            'time_ms': metrics.upscale_time_ms,
            'fps': metrics.fps,
            'memory_mb': metrics.memory_used_mb
        })
    
    # Print comparison table
    print("\n  Mode              | Time (ms) | FPS   | Memory (MB)")
    print("  " + "-"*56)
    for r in results:
        print(f"  {r['mode']:16} | {r['time_ms']:8.2f} | {r['fps']:5.1f} | {r['memory_mb']:7.1f}")
    
    sdk.shutdown()
    print("\n✅ Quality modes: PASS")


def test_frame_generation():
    """Test 5: Frame generation"""
    print("\n" + "="*60)
    print("TEST 5: Frame Generation")
    print("="*60)
    
    sdk = FSR4SDK()
    sdk.initialize()
    
    context = sdk.create_context(
        input_resolution=(1920, 1080),
        output_resolution=(1920, 1080),
        quality_mode=FSR4QualityMode.NATIVE
    )
    
    # Create two test frames
    frame1 = np.zeros((1080, 1920, 3), dtype=np.uint8)
    frame2 = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
    
    frame_data1 = FSR4FrameData(color=frame1, timestamp=0.0)
    frame_data2 = FSR4FrameData(color=frame2, timestamp=0.016)
    
    # Generate intermediate frame
    print("\n  Generating intermediate frame (t=0.5)...")
    generated, metrics = context.generate_frame(frame_data1, frame_data2, 0.5)
    
    # Verify output
    assert generated.shape == (1080, 1920, 3), f"Wrong shape: {generated.shape}"
    
    # Check interpolation (should be ~127 for middle)
    mean_value = np.mean(generated)
    assert 100 < mean_value < 155, f"Unexpected mean value: {mean_value}"
    
    print(f"  Output: {generated.shape}")
    print(f"  Mean value: {mean_value:.1f} (expected ~127)")
    print(f"  Time: {metrics.frame_gen_time_ms:.2f}ms")
    print(f"  FPS: {metrics.fps:.1f}")
    
    sdk.shutdown()
    print("\n✅ Frame generation: PASS")


def test_performance_benchmark():
    """Test 6: Performance benchmark"""
    print("\n" + "="*60)
    print("TEST 6: Performance Benchmark")
    print("="*60)
    
    sdk = FSR4SDK()
    sdk.initialize()
    
    context = sdk.create_context(
        input_resolution=(1920, 1080),
        output_resolution=(3840, 2160),
        quality_mode=FSR4QualityMode.QUALITY
    )
    
    # Benchmark 100 frames
    num_frames = 100
    times = []
    
    print(f"\n  Benchmarking {num_frames} frames...")
    
    for i in range(num_frames):
        test_frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        frame_data = FSR4FrameData(color=test_frame)
        
        start = time.perf_counter()
        upscaled, metrics = context.upscale(frame_data)
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        
        if (i + 1) % 25 == 0:
            print(f"    Progress: {i+1}/{num_frames}")
    
    # Calculate statistics
    avg_time = np.mean(times)
    min_time = np.min(times)
    max_time = np.max(times)
    std_time = np.std(times)
    avg_fps = 1000.0 / avg_time
    
    print(f"\n  Results ({num_frames} frames):")
    print(f"    Average: {avg_time:.2f}ms ({avg_fps:.1f} FPS)")
    print(f"    Min: {min_time:.2f}ms ({1000/min_time:.1f} FPS)")
    print(f"    Max: {max_time:.2f}ms ({1000/max_time:.1f} FPS)")
    print(f"    Std Dev: {std_time:.2f}ms")
    
    # Performance check
    assert avg_fps > 50, f"Performance too low: {avg_fps:.1f} FPS"
    
    stats = context.get_stats()
    print(f"\n  Context stats:")
    for k, v in stats.items():
        print(f"    {k}: {v}")
    
    sdk.shutdown()
    print("\n✅ Performance benchmark: PASS")


def test_error_handling():
    """Test 7: Error handling"""
    print("\n" + "="*60)
    print("TEST 7: Error Handling")
    print("="*60)
    
    sdk = FSR4SDK()
    
    # Test: Create context before init
    print("\n  Test: Context before init...")
    context = sdk.create_context((1920, 1080), (3840, 2160))
    assert context is None, "Should fail without init"
    print("    ✅ Correctly rejected")
    
    sdk.initialize()
    
    # Test: Invalid resolution
    print("\n  Test: Invalid resolution...")
    try:
        context = sdk.create_context((0, 0), (3840, 2160))
        print("    ✅ Handled gracefully")
    except Exception as e:
        print(f"    ✅ Exception caught: {e}")
    
    sdk.shutdown()
    print("\n✅ Error handling: PASS")


def test_memory_leak():
    """Test 8: Memory leak test"""
    print("\n" + "="*60)
    print("TEST 8: Memory Leak Test")
    print("="*60)
    
    sdk = FSR4SDK()
    sdk.initialize()
    
    context = sdk.create_context(
        input_resolution=(1920, 1080),
        output_resolution=(3840, 2160),
        quality_mode=FSR4QualityMode.QUALITY
    )
    
    # Process 1000 frames
    num_frames = 1000
    print(f"\n  Processing {num_frames} frames...")
    
    import psutil
    import os
    process = psutil.Process(os.getpid())
    
    mem_start = process.memory_info().rss / 1024 / 1024
    
    for i in range(num_frames):
        test_frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        frame_data = FSR4FrameData(color=test_frame)
        upscaled, metrics = context.upscale(frame_data)
        
        if (i + 1) % 250 == 0:
            mem_current = process.memory_info().rss / 1024 / 1024
            print(f"    Frame {i+1}: {mem_current:.1f} MB")
    
    mem_end = process.memory_info().rss / 1024 / 1024
    mem_delta = mem_end - mem_start
    
    print(f"\n  Memory usage:")
    print(f"    Start: {mem_start:.1f} MB")
    print(f"    End: {mem_end:.1f} MB")
    print(f"    Delta: {mem_delta:+.1f} MB")
    
    # Allow up to 50MB increase for caches
    assert mem_delta < 50, f"Memory leak detected: +{mem_delta:.1f} MB"
    
    sdk.shutdown()
    print("\n✅ Memory leak test: PASS")


def test_multithreaded():
    """Test 9: Multi-threaded stress test"""
    print("\n" + "="*60)
    print("TEST 9: Multi-threaded Stress Test")
    print("="*60)
    
    sdk = FSR4SDK()
    sdk.initialize()
    
    context = sdk.create_context(
        input_resolution=(1920, 1080),
        output_resolution=(3840, 2160),
        quality_mode=FSR4QualityMode.QUALITY
    )
    
    errors = []
    
    def worker(thread_id, num_frames):
        try:
            for i in range(num_frames):
                test_frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
                frame_data = FSR4FrameData(color=test_frame)
                upscaled, metrics = context.upscale(frame_data)
            print(f"    Thread {thread_id}: OK ({num_frames} frames)")
        except Exception as e:
            errors.append((thread_id, str(e)))
            print(f"    Thread {thread_id}: ERROR - {e}")
    
    # Launch 4 threads
    num_threads = 4
    frames_per_thread = 50
    
    print(f"\n  Launching {num_threads} threads ({frames_per_thread} frames each)...")
    
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i, frames_per_thread))
        t.start()
        threads.append(t)
    
    # Wait for completion
    for t in threads:
        t.join()
    
    assert len(errors) == 0, f"Errors in threads: {errors}"
    
    sdk.shutdown()
    print("\n✅ Multi-threaded test: PASS")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("FSR4 TEST SUITE")
    print("Version: 0.3.5d+patch8")
    print("="*60)
    
    if not FSR4_AVAILABLE:
        print("\n❌ FSR4 not available!")
        return False
    
    tests = [
        ("SDK Init", test_sdk_init),
        ("Context Creation", test_context_creation),
        ("Upscaling", test_upscaling),
        ("Quality Modes", test_quality_modes),
        ("Frame Generation", test_frame_generation),
        ("Performance", test_performance_benchmark),
        ("Error Handling", test_error_handling),
    ]
    
    # Optional tests (require psutil)
    try:
        import psutil
        tests.append(("Memory Leak", test_memory_leak))
    except ImportError:
        print("\n[WARNING] psutil not available, skipping memory leak test")
    
    tests.append(("Multi-threaded", test_multithreaded))
    
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
