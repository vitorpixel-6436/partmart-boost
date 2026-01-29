#!/usr/bin/env python3
"""UniversalUpscaler Demo

Demonstrates UniversalUpscaler usage:
- Auto-detection
- Context creation
- Frame upscaling
- Performance metrics

Version: 0.3.5d (package 3.8a)
"""

import numpy as np
import time

from upscaler import (
    UniversalUpscaler,
    UpscalerQuality,
    UpscaleConfig,
    FrameData
)


def demo_auto_detection():
    """Demo: Auto-detect best backend"""
    print("\n=== Auto-Detection Demo ===")
    
    upscaler = UniversalUpscaler()
    
    print("Initializing upscaler...")
    upscaler.initialize()
    
    # Get backend info
    info = upscaler.get_backend_info()
    
    print(f"\n✅ Backend: {info.backend.name}")
    print(f"   Version: {info.version}")
    print(f"   GPU: {info.gpu_name}")
    print(f"   Driver: {info.driver_version}")
    print(f"   Features: {info.features}")
    
    return upscaler


def demo_upscaling(upscaler):
    """Demo: Upscale a frame"""
    print("\n=== Upscaling Demo ===")
    
    # Create test frame (1080p)
    print("Creating test frame (1920x1080)...")
    test_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    
    # Create upscale context (1080p → 4K)
    print("Creating upscale context (1080p → 4K)...")
    config = UpscaleConfig(
        input_resolution=(1920, 1080),
        output_resolution=(3840, 2160),
        quality=UpscalerQuality.QUALITY,
        sharpness=0.8
    )
    
    context = upscaler.create_context(config)
    
    # Upscale frame
    print("\nUpscaling frame...")
    frame_data = FrameData(color=test_frame)
    
    start_time = time.perf_counter()
    upscaled, metrics = context.upscale(frame_data)
    elapsed = time.perf_counter() - start_time
    
    # Display results
    print(f"\n✅ Upscaling complete!")
    print(f"   Input: {test_frame.shape[1]}x{test_frame.shape[0]}")
    print(f"   Output: {upscaled.shape[1]}x{upscaled.shape[0]}")
    print(f"   Backend: {metrics.backend.name}")
    print(f"   Time: {metrics.total_time_ms:.2f} ms")
    print(f"   FPS: {metrics.fps:.1f}")
    print(f"   Memory: {metrics.memory_used_mb:.2f} MB")


def demo_quality_comparison(upscaler):
    """Demo: Compare quality modes"""
    print("\n=== Quality Mode Comparison ===")
    
    test_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    frame_data = FrameData(color=test_frame)
    
    quality_modes = [
        (UpscalerQuality.PERFORMANCE, "Performance (2.0x)"),
        (UpscalerQuality.BALANCED, "Balanced (1.7x)"),
        (UpscalerQuality.QUALITY, "Quality (1.5x)"),
        (UpscalerQuality.ULTRA_QUALITY, "Ultra Quality (1.3x)"),
    ]
    
    print("\nTesting quality modes...\n")
    
    for quality, name in quality_modes:
        config = UpscaleConfig(
            input_resolution=(1920, 1080),
            output_resolution=(3840, 2160),
            quality=quality,
            sharpness=0.5
        )
        
        context = upscaler.create_context(config)
        _, metrics = context.upscale(frame_data)
        
        print(f"{name:25} - {metrics.fps:6.1f} FPS - {metrics.total_time_ms:6.2f} ms")


def demo_benchmark(upscaler):
    """Demo: Performance benchmark"""
    print("\n=== Performance Benchmark ===")
    
    test_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    frame_data = FrameData(color=test_frame)
    
    config = UpscaleConfig(
        input_resolution=(1920, 1080),
        output_resolution=(3840, 2160),
        quality=UpscalerQuality.QUALITY,
        sharpness=0.5
    )
    
    context = upscaler.create_context(config)
    
    # Warmup
    print("\nWarming up...")
    for _ in range(5):
        context.upscale(frame_data)
    
    # Benchmark
    print("Running benchmark (100 frames)...")
    
    times = []
    for i in range(100):
        start = time.perf_counter()
        context.upscale(frame_data)
        times.append(time.perf_counter() - start)
        
        if (i + 1) % 25 == 0:
            print(f"  Progress: {i + 1}/100")
    
    # Statistics
    times_ms = [t * 1000 for t in times]
    avg_time = np.mean(times_ms)
    min_time = np.min(times_ms)
    max_time = np.max(times_ms)
    std_time = np.std(times_ms)
    
    print(f"\n✅ Benchmark Results:")
    print(f"   Average: {avg_time:.2f} ms ({1000/avg_time:.1f} FPS)")
    print(f"   Min: {min_time:.2f} ms ({1000/min_time:.1f} FPS)")
    print(f"   Max: {max_time:.2f} ms ({1000/max_time:.1f} FPS)")
    print(f"   Std Dev: {std_time:.2f} ms")


def main():
    """Run all demos"""
    print("""
╔═══════════════════════════════════════════╗
║  UniversalUpscaler Demo - Package 3.8a   ║
║      Multi-Backend Upscaling System      ║
╚═══════════════════════════════════════════╝
    """)
    
    # Demo 1: Auto-detection
    upscaler = demo_auto_detection()
    
    # Demo 2: Basic upscaling
    demo_upscaling(upscaler)
    
    # Demo 3: Quality comparison
    demo_quality_comparison(upscaler)
    
    # Demo 4: Performance benchmark
    print("\n" + "="*50)
    print("Run performance benchmark? (takes ~30 seconds) (y/n): ", end="")
    if input().lower() == 'y':
        demo_benchmark(upscaler)
    else:
        print("\nSkipping benchmark.")
    
    print("""
╔═══════════════════════════════════════════╗
║              Demo Complete!              ║
║                                          ║
║  UniversalUpscaler is ready to use!     ║
║  ✅ Auto-detection working                ║
║  ✅ Multiple quality modes                ║
║  ✅ High performance                      ║
║                                          ║
║  Integrate into your application! 🚀     ║
╚═══════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
