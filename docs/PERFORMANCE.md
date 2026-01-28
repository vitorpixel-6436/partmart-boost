# Performance Guide

**Version:** 0.3.5d+patch5

## Overview

PartMart Boost is designed for high performance with minimal overhead.

## Performance Metrics

### FPS Tracking

- **Update Rate:** 100ms
- **History Size:** 60 samples
- **Memory:** ~1 KB per tracker
- **CPU Overhead:** <0.1%

### Frame Generation

- **Latency:** <5ms
- **Memory:** 2x frame buffer size
- **Quality:** Adjustable (Performance/Balanced/Quality)

### Upscaling

- **Throughput:** 60+ FPS @ 1080p→4K
- **Memory:** 3x frame buffer size
- **Quality Loss:** <2% (balanced mode)

### Adaptive Systems

- **Thermal Response:** <100ms
- **Power Adjustment:** <50ms
- **Resource Rebalancing:** <10ms

## Optimization Tips

### 1. Quality Presets

**Performance Mode:**
- Lowest latency
- Highest FPS
- Reduced quality
- Use for: Competitive gaming

**Balanced Mode:**
- Good latency
- Good FPS
- Good quality
- Use for: Most games

**Quality Mode:**
- Higher latency
- Lower FPS
- Best quality
- Use for: Single-player, story games

### 2. Frame Generation

**When to Enable:**
- GPU-limited scenarios
- Target FPS below 60
- Stable frame times

**When to Disable:**
- CPU-limited scenarios
- Already high FPS (>144)
- Competitive gaming (adds latency)

### 3. Upscaling

**When to Enable:**
- GPU-limited
- Want higher resolution
- Accept small quality loss

**When to Disable:**
- Native resolution gameplay
- Pixel-perfect games
- Already meeting performance targets

### 4. Thermal Management

**Target Temperatures:**
- Cool: 75°C (quieter, longer lifespan)
- Balanced: 80°C (good compromise)
- Performance: 85°C (max performance)

**Tips:**
- Good case airflow helps
- Clean dust regularly
- Repaste thermal compound if needed

### 5. Power Management

**AC Power:**
- Set to "Performance" mode
- No power limits
- Best performance

**Battery:**
- Set to "Balanced" or "Power Saver"
- Extends battery life
- Reduces heat

## Benchmarks

### Test System

- CPU: AMD Ryzen 7 5800X
- GPU: NVIDIA RTX 3080
- RAM: 32GB DDR4-3600
- OS: Windows 11

### Results

#### FPS Tracking Overhead

| Scenario | Without | With | Overhead |
|----------|---------|------|----------|
| Idle | - | - | 0.0% |
| Gaming | 120 FPS | 120 FPS | 0.1% |
| Stress | 200 FPS | 199 FPS | 0.5% |

#### Frame Generation

| Input FPS | Output FPS | Latency |
|-----------|------------|----------|
| 30 | 60 | +8ms |
| 45 | 90 | +6ms |
| 60 | 120 | +5ms |

#### Upscaling Performance

| Input Res | Output Res | FPS (Native) | FPS (Upscaled) | Gain |
|-----------|------------|--------------|----------------|------|
| 1080p | 1440p | 85 | 110 | +29% |
| 1440p | 4K | 60 | 80 | +33% |
| 1080p | 4K | 45 | 70 | +56% |

#### Memory Usage

| Component | Memory |
|-----------|--------|
| Core Systems | 5 MB |
| GUI | 25 MB |
| Frame Buffers | 50 MB @ 1080p |
| Total | ~80 MB |

## Profiling

### Enable Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run workload
for _ in range(1000):
    fps_tracker.frame()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Key Metrics

- **Total Time:** Time spent in function
- **Cumulative Time:** Time including callees
- **Calls:** Number of invocations
- **Per Call:** Average time per call

### Hot Spots

Typical hot spots:
1. Frame processing (30-40%)
2. Upscaling (20-30%)
3. Frame generation (15-25%)
4. Monitoring (5-10%)
5. GUI updates (5-10%)

## Best Practices

### 1. Minimize Overhead

- Disable features you don't need
- Use performance mode when possible
- Close unnecessary GUI tabs

### 2. Monitor Performance

- Watch FPS graph
- Check frame times
- Monitor temperatures
- Track GPU/CPU usage

### 3. Adjust Settings

- Start with balanced preset
- Adjust based on bottleneck
- Test different configurations

### 4. System Optimization

- Update GPU drivers
- Close background apps
- Disable overlays
- Use fullscreen mode

## Troubleshooting

### Low FPS

1. Check GPU usage (should be 95-100%)
2. If GPU < 95%, CPU bottleneck
3. If GPU = 100%, GPU bottleneck
4. Adjust quality settings accordingly

### High Latency

1. Disable frame generation
2. Reduce quality preset
3. Enable "Low Latency Mode" in GPU driver
4. Use "Performance" power mode

### Stuttering

1. Check frame time graph (should be smooth)
2. If spikes, check background processes
3. If periodic, check thermal throttling
4. If random, check VRAM usage

### High Temperature

1. Check case airflow
2. Clean dust
3. Reduce target temperature
4. Lower quality preset

### Memory Issues

1. Check VRAM usage
2. Reduce resolution
3. Disable unused features
4. Close other applications

## Advanced Tuning

### Custom Profiles

(Coming in v0.5.0)

- Save/load configurations
- Per-game profiles
- Automatic switching

### Fine-Grained Control

(Coming in v0.5.0)

- Individual feature toggles
- Custom thermal curves
- Advanced upscaling options

---

**Need help?** Open an issue on GitHub!
