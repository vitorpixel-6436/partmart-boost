# FSR 3.x Integration Guide

**Version:** 0.3.5d (Package 3.9a, Stage 7.7d)

## AMD FidelityFX Super Resolution 3.x

FSR 3.x is AMD's latest upscaling technology with **frame generation**!

## What's New in FSR 3.x

### FSR 3.0/3.1 Features

1. **Frame Generation** 🚀
   - Generate intermediate frames
   - 2x FPS boost potential
   - AI-powered interpolation

2. **Improved Upscaling**
   - Better image quality
   - Reduced artifacts
   - Enhanced temporal stability

3. **Async Compute**
   - Parallel GPU execution
   - Reduced latency
   - Better performance

4. **HDR Support**
   - Native HDR pipeline
   - Better color accuracy

## FSR 3.x vs FSR 2.x

| Feature | FSR 2.x | FSR 3.x |
|---------|---------|----------|
| Upscaling | ✅ | ✅ |
| Frame Generation | ❌ | ✅ |
| Async Compute | ❌ | ✅ |
| HDR Support | Basic | Native |
| Performance | Good | Better |

## Quality Presets

### Available Presets

1. **Native AA** (100% scale)
   - No upscaling, FSR as anti-aliasing
   - Best quality
   - Lowest FPS gain

2. **Ultra Quality** (77% scale, 1.3x)
   - Minimal quality loss
   - ~30% FPS boost
   - Recommended for 4K

3. **Quality** (67% scale, 1.5x)
   - **Recommended default**
   - Good balance
   - ~50% FPS boost

4. **Balanced** (59% scale, 1.7x)
   - Visible quality trade-off
   - ~70% FPS boost

5. **Performance** (50% scale, 2.0x)
   - Noticeable quality loss
   - ~100% FPS boost (2x)

6. **Ultra Performance** (33% scale, 3.0x)
   - Maximum FPS
   - Significant quality loss
   - For 8K → 4K or extreme cases

### Frame Generation Impact

With frame generation enabled:
- **Additional 2x FPS** on top of upscaling
- Quality preset + FG = ~3x total FPS!
- Ultra Performance + FG = up to 6x FPS!

**Example:**
- Native: 60 FPS
- FSR Quality: 90 FPS (1.5x)
- FSR Quality + FG: **180 FPS** (3x total!)

## Configuration

### Basic Configuration

```python
from core.fsr_manager import get_fsr_manager, FSRPreset, FSRVersion

manager = get_fsr_manager()

# Create FSR 3.1 config with frame generation
config = manager.create_config(
    version=FSRVersion.FSR_3_1,
    preset=FSRPreset.QUALITY,
    frame_generation=True,
    sharpness=0.7
)

# Save for game
manager.save_game_config('Cyberpunk2077', config)
```

### Advanced Configuration

```python
from core.fsr_manager import FSRConfig, FSRVersion, FSRPreset

config = FSRConfig(
    version=FSRVersion.FSR_3_1,
    preset=FSRPreset.BALANCED,
    render_scale=0.59,
    sharpness=0.8,
    
    # Frame generation (FSR 3.x)
    frame_generation=True,
    frame_interpolation=True,
    async_compute=True,
    
    # API
    dx12_mode=True,
    
    # Advanced
    hdr_support=True,
    motion_vector_scale=1.0,
    auto_exposure=True
)
```

## Required DLLs

### For DirectX 12

**Base FSR:**
- `ffx_fsr3_api_dx12_x64.dll`

**Frame Generation:**
- `ffx_framegeneration_dx12_x64.dll`

### For Vulkan

**Base FSR:**
- `ffx_fsr3_api_vk_x64.dll`

**Frame Generation:**
- `ffx_framegeneration_vk_x64.dll`

## Installation

### 1. Download FSR 3.x SDK

Get from AMD GPUOpen:
- https://gpuopen.com/fidelityfx-sdk/

### 2. Install DLLs

```python
manager = get_fsr_manager()
manager.install_fsr_dlls('path/to/fsr/sdk/bin')
```

### 3. Deploy to Game

```python
# Manual deployment
manager.deploy_fsr_to_game(
    'C:/Games/Cyberpunk2077',
    config
)
```

## Game Profiles

### Create Profile

```python
from core.game_profile_manager import get_profile_manager

profile_manager = get_profile_manager()

# Create with default FSR 3.1 settings
profile = profile_manager.create_default_profile(
    'Cyberpunk2077',
    'Cyberpunk2077.exe'
)
```

### Auto-Injection

```python
from core.game_profile_manager import AutoInjectMode

profile.auto_inject = AutoInjectMode.AUTO
profile.auto_inject_delay = 5.0  # seconds

profile_manager.save_profile(profile)
```

## Performance Tips

### Optimal Settings by Resolution

**1080p:**
- Preset: Performance or Balanced
- Frame Gen: Optional
- Expected: 100-150 FPS

**1440p:**
- Preset: Quality or Balanced
- Frame Gen: Recommended
- Expected: 120-180 FPS

**4K:**
- Preset: Ultra Quality or Quality
- Frame Gen: Essential
- Expected: 60-120 FPS

**8K:**
- Preset: Performance or Balanced
- Frame Gen: Essential
- Expected: 30-60 FPS

### GPU Requirements

**Minimum (FSR 3.x):**
- AMD: RX 6000 series
- NVIDIA: RTX 2000 series
- Intel: Arc A-series

**Recommended (Frame Generation):**
- AMD: RX 7000 series
- NVIDIA: RTX 4000 series
- Intel: Arc B-series

## Troubleshooting

### Frame Generation Not Working

1. Check GPU support
2. Ensure FSR 3.x DLLs installed
3. Verify frame generation DLL present
4. Check game API (DX12/Vulkan required)

### Quality Issues

1. Increase render scale
2. Adjust sharpness (0.5-0.8 recommended)
3. Enable auto-exposure
4. Check motion vector quality

### Performance Issues

1. Disable frame generation temporarily
2. Lower quality preset
3. Enable async compute
4. Check for bottlenecks

## Limitations

### Frame Generation

❌ **Not supported:**
- DirectX 11 games
- Older GPUs (pre-2020)
- Some anti-cheat systems

⚠️ **Caveats:**
- May increase input latency
- Artifacts in fast motion
- Requires good base framerate (>60 FPS recommended)

### General

- **Open source:** FSR is open, but integration varies
- **Game support:** Depends on game implementation
- **Anti-cheat:** May be blocked in multiplayer

## Best Practices

### For Single Player Games

✅ Enable frame generation  
✅ Use Quality or Balanced preset  
✅ Adjust sharpness to taste  
✅ Enable async compute  

### For Competitive Multiplayer

⚠️ **Check anti-cheat first!**

❌ Disable frame generation (latency)  
✅ Use Quality or Ultra Quality  
✅ Prioritize responsiveness  
❌ Avoid Ultra Performance  

## Resources

- **AMD FSR SDK:** https://gpuopen.com/fidelityfx-sdk/
- **Documentation:** https://gpuopen.com/fidelityfx-superresolution/
- **Source Code:** https://github.com/GPUOpen-Effects/FidelityFX-FSR
- **Games with FSR:** https://www.amd.com/en/technologies/fidelityfx-super-resolution

---

**FSR 3.x - Open Source Gaming Performance!** 🚀
