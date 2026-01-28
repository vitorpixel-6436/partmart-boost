# Hybrid Upscaler Setup Guide

**Version:** 0.4.0-alpha  
**Date:** 2026-01-28

---

## 📚 Overview

Universal Upscaler System with multiple backends:

⭐ **FSR 3.1** (AMD FidelityFX Super Resolution)  
⭐ **XeSS 2.1** (Intel Xe Super Sampling)  
⭐ **Software Fallback** (Lanczos4)

Works on **NVIDIA, AMD, and Intel GPUs**!

---

## 🚀 Quick Start (Software Fallback)

Works **immediately** without any DLLs:

```python
from upscaler import UniversalUpscaler, QualityMode, FrameData
import numpy as np

# 1. Create upscaler
upscaler = UniversalUpscaler()
upscaler.initialize()  # Auto-detects GPU, loads best available backend

# 2. Create context
context = upscaler.create_context(
    input_resolution=(1920, 1080),
    output_resolution=(3840, 2160),
    quality_mode=QualityMode.QUALITY
)

# 3. Upscale frames
frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
frame_data = FrameData(color=frame)

upscaled, metrics = context.upscale(frame_data)

print(f"Backend: {metrics.backend.name}")  # SOFTWARE
print(f"Time: {metrics.upscale_time_ms:.2f}ms")
print(f"FPS: {metrics.fps:.1f}")

# 4. Cleanup
upscaler.shutdown()
```

---

## 📦 Installing Real FSR 3.1

### Step 1: Download AMD FSR 3.1 SDK

**Official Source:**
```
https://github.com/GPUOpen-Effects/FidelityFX-FSR3
```

### Step 2: Extract DLL

**Windows:**
- Find: `bin/ffx_fsr3_x64.dll`
- Or: `ffx_fsr31_x64.dll`

**Linux:**
- Find: `lib/libffx_fsr3.so`
- Or: `lib/libffx_fsr31.so`

### Step 3: Place DLL

Copy to one of these locations:

```
partmart-boost/
├── libs/                ⭐ RECOMMENDED
│   └── ffx_fsr3_x64.dll
├── dlls/
│   └── ffx_fsr3_x64.dll
└── src/
```

**Linux:**
```bash
# System-wide (optional)
sudo cp libffx_fsr3.so /usr/local/lib/
sudo ldconfig
```

### Step 4: Test

```python
from upscaler import UniversalUpscaler

upscaler = UniversalUpscaler()
upscaler.initialize()

# Should see:
# ✅ FSR 3.1 available
# ⭐ Selected: FSR 3.1 (AMD FidelityFX)
```

---

## 📦 Installing Real XeSS 2.1

### Step 1: Download Intel XeSS 2.1 SDK

**Official Source:**
```
https://github.com/intel/xess
```

**Or Intel Developer Zone:**
```
https://www.intel.com/content/www/us/en/developer/topic-technology/gamedev/xess2.html
```

### Step 2: Extract DLL

**Windows:**
- Find: `bin/libxess.dll`
- Or: `xess.dll`

**Linux:**
- Find: `lib/libxess.so`

### Step 3: Place DLL

```
partmart-boost/
├── libs/                ⭐ RECOMMENDED
│   ├── ffx_fsr3_x64.dll
│   └── libxess.dll
└── dlls/
```

### Step 4: Test

```python
from upscaler import UniversalUpscaler

upscaler = UniversalUpscaler()
upscaler.initialize()

# Should see:
# ✅ XeSS 2.1 available
```

---

## 📊 Backend Selection Logic

### Auto-Detection (Default):

```python
upscaler = UniversalUpscaler()
upscaler.initialize()  # AUTO mode

# Priority:
# 1. FSR 3.1 (if DLL found)
# 2. XeSS 2.1 (if FSR not available)
# 3. Software (always available)
```

### Manual Selection:

```python
from upscaler import UniversalUpscaler, UpscalerBackend

# Force FSR 3.1
upscaler = UniversalUpscaler()
upscaler.initialize(preferred_backend=UpscalerBackend.FSR3)

# Force XeSS 2.1
upscaler.initialize(preferred_backend=UpscalerBackend.XESS)

# Force Software
upscaler.initialize(preferred_backend=UpscalerBackend.SOFTWARE)
```

### Runtime Swap:

```python
# Start with auto
upscaler = UniversalUpscaler()
upscaler.initialize()

print(f"Current: {upscaler.get_active_backend().name}")

# Swap to different backend
upscaler.swap_backend(UpscalerBackend.XESS)

print(f"New: {upscaler.get_active_backend().name}")
```

---

## 🎯 GPU Compatibility

### FSR 3.1:

| GPU | Upscaling | Frame Gen | Quality |
|-----|-----------|-----------|----------|
| **NVIDIA GTX 10+** | ✅ | ✅ | ★★★★ |
| **NVIDIA RTX 20+** | ✅ | ✅ | ★★★★ |
| **AMD RX 400+** | ✅ | ✅ | ★★★★ |
| **AMD RX 6000+** | ✅ | ✅ | ★★★★★ |
| **Intel Arc** | ✅ | ✅ | ★★★★ |

### XeSS 2.1:

| GPU | Upscaling | Frame Gen | Quality |
|-----|-----------|-----------|----------|
| **Intel Arc** | ✅ (HW) | ✅ | ★★★★★ |
| **Intel iGPU** | ✅ (HW) | ✅ | ★★★★ |
| **NVIDIA GTX 10+** | ✅ (DP4a) | ✅ | ★★★★ |
| **AMD RX 5000+** | ✅ (DP4a) | ✅ | ★★★★ |

### Software Fallback:

| Hardware | Upscaling | Frame Gen | Quality |
|----------|-----------|-----------|----------|
| **Any CPU** | ✅ | ❌ | ★★★ |

---

## 🔧 Troubleshooting

### Issue: "DLL not found"

**Solution:**
1. Check DLL is in `./libs/` or `./dlls/`
2. Verify DLL architecture (x64 only)
3. Check DLL permissions
4. Try system path: `/usr/local/lib` (Linux)

### Issue: "Backend not available"

**Causes:**
- DLL not found
- Incompatible DLL version
- GPU driver too old

**Solution:**
```python
# Check what's available
from upscaler.backends import FSR3Backend, XeSSBackend

fsr = FSR3Backend()
print(f"FSR available: {fsr.is_available()}")

xess = XeSSBackend()
print(f"XeSS available: {xess.is_available()}")
```

### Issue: Low Performance

**Solutions:**
1. Use Performance quality mode
2. Check GPU usage
3. Update drivers
4. Try different backend

```python
# Performance mode
context = upscaler.create_context(
    input_resolution=(1920, 1080),
    output_resolution=(3840, 2160),
    quality_mode=QualityMode.PERFORMANCE  # Fastest
)
```

---

## 📚 Advanced Usage

### Backend Info:

```python
# Get GPU info
gpu_info = upscaler.get_gpu_info()
print(f"GPU: {gpu_info['name']}")
print(f"Vendor: {gpu_info['vendor']}")
print(f"Memory: {gpu_info['memory_mb']} MB")

# Get active backend
backend = upscaler.get_active_backend()
print(f"Backend: {backend.name}")
```

### Multiple Contexts:

```python
# Different quality modes
context_perf = upscaler.create_context(
    (1920, 1080), (3840, 2160),
    quality_mode=QualityMode.PERFORMANCE
)

context_qual = upscaler.create_context(
    (1920, 1080), (3840, 2160),
    quality_mode=QualityMode.ULTRA_QUALITY
)

# Use based on performance target
if current_fps > 60:
    upscaled, _ = context_qual.upscale(frame)
else:
    upscaled, _ = context_perf.upscale(frame)
```

### With Sharpening:

```python
context = upscaler.create_context(
    input_resolution=(1920, 1080),
    output_resolution=(3840, 2160),
    quality_mode=QualityMode.QUALITY,
    enable_sharpening=True,
    sharpness=0.7  # 0.0-1.0
)
```

---

## 📝 Example: Full Integration

```python
#!/usr/bin/env python3
"""Example: Full upscaler integration"""
import numpy as np
from upscaler import UniversalUpscaler, QualityMode, FrameData

class GameRenderer:
    def __init__(self):
        self.upscaler = UniversalUpscaler()
        self.upscaler.initialize()
        
        # Print info
        gpu = self.upscaler.get_gpu_info()
        backend = self.upscaler.get_active_backend()
        print(f"GPU: {gpu['name']}")
        print(f"Backend: {backend.name}")
        
        # Create context
        self.context = self.upscaler.create_context(
            input_resolution=(1920, 1080),  # Render resolution
            output_resolution=(3840, 2160),  # Display resolution
            quality_mode=QualityMode.QUALITY,
            enable_sharpening=True,
            sharpness=0.6
        )
    
    def render_frame(self):
        # Render at lower resolution
        frame = self.render_scene(1920, 1080)
        
        # Upscale
        frame_data = FrameData(color=frame)
        upscaled, metrics = self.context.upscale(frame_data)
        
        # Display
        self.display(upscaled)
        
        # Print metrics
        print(f"FPS: {metrics.fps:.1f} ({metrics.upscale_time_ms:.2f}ms)")
        
        return upscaled
    
    def render_scene(self, width, height):
        # Your rendering code here
        return np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    
    def display(self, frame):
        # Your display code here
        pass
    
    def cleanup(self):
        self.upscaler.shutdown()

# Usage
renderer = GameRenderer()
for frame_num in range(1000):
    renderer.render_frame()
renderer.cleanup()
```

---

## 🔗 Resources

### Official SDKs:
- **AMD FSR 3.1:** https://github.com/GPUOpen-Effects/FidelityFX-FSR3
- **Intel XeSS 2.1:** https://github.com/intel/xess
- **Intel XeSS Docs:** https://www.intel.com/content/www/us/en/developer/topic-technology/gamedev/xess2.html

### Community:
- **OptiScaler:** https://github.com/optiscaler/OptiScaler
- **GPUOpen:** https://gpuopen.com/fsr/

### Documentation:
- AMD FSR 3.1 Guide
- Intel XeSS Integration Guide
- Performance Optimization Tips

---

## ✅ Checklist

### Minimum (Works Now):
- [x] Python 3.8+
- [x] NumPy
- [x] Software backend

### Recommended:
- [ ] OpenCV (`pip install opencv-python`)
- [ ] FSR 3.1 DLL in `./libs/`
- [ ] XeSS 2.1 DLL in `./libs/`
- [ ] GPU with updated drivers

### Optional:
- [ ] scipy (for advanced filtering)
- [ ] psutil (for monitoring)

---

## 🚀 You're Ready!

```bash
# Test it now:
python -c "from upscaler import UniversalUpscaler; u = UniversalUpscaler(); u.initialize()"
```

**It works immediately with software fallback!**  
**Add DLLs for FSR 3.1 or XeSS 2.1 for best performance!**

---

**Version:** 0.4.0-alpha  
**Updated:** 2026-01-28
