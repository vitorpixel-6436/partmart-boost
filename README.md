# PartMart Boost v0.3.5e

**Gaming Performance Optimizer** with **Liquid Glass UI** 🎮✨

**Version:** 0.3.5e (Package 3.9a, Stage 7.8a)  
**Status:** Production Ready ✅

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🌟 New in v0.3.5e - Liquid Glass UI!

**MASSIVE UI/UX OVERHAUL!** 🎨

PartMart Boost now features a **stunning modern interface** inspired by:

- 🍎 **Apple** - Liquid Glass effects, frosted blur, smooth transitions
- 🎮 **Steam** - Beautiful game cards, library grid view
- 🎵 **Spotify** - Clean, minimalist, modern design
- 🔴 **MSI** - Aggressive red/black aesthetic, gaming vibes

### Visual Highlights

✅ **Glassmorphism** - Frosted glass panels with blur  
✅ **Game Cards** - Soft rounded tiles with hover effects  
✅ **Smooth Animations** - Fade, slide, scale transitions  
✅ **MSI Colors** - Signature red (#E30613) + deep blacks  
✅ **Modern Typography** - Segoe UI, bold headers  
✅ **Status Indicators** - Pulsing colored dots  
✅ **Performance Dashboard** - Real-time metrics display  

**Before:** Basic PyQt6 widgets 😕  
**After:** Gorgeous Liquid Glass interface! 🤩

---

## 🚀 Quick Start

### Requirements

```bash
python >= 3.9
PyQt6 >= 6.0
psutil
nvidia-ml-py3
```

### Installation

```bash
# Clone repository
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost

# Install dependencies
pip install -r requirements.txt

# Launch
python launcher.py
```

### Launch Options

```
1. Modern GUI ⭐ RECOMMENDED - New Liquid Glass UI
2. Legacy GUI - Old basic design
3. CLI Mode - Terminal interface
```

**Select option 1** to experience the beautiful new UI! 🌟

---

## 🎨 UI Showcase

### Modern Main Window

```
┌──────────────────────────────────────────────────┐
│  PartMart Boost                            v0.3.5e  │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌────────────── GLASS PANEL ──────────────┐  │
│  │  ● Running  |  CPU: 45%  |  RAM: 60%        │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  Game Library                                    │
│                                                  │
│  ╭────────╮  ╭────────╮  ╭────────╮  ╭────────╮  │
│  │  GTA V  │  │  CS2  │  │  EFT  │  │  PUBG │  │  Soft
│  │ Running │  │ Ready  │  │ Ready  │  │ Ready │  │  Rounded
│  ╰────────╯  ╰────────╯  ╰────────╯  ╰────────╯  │  Cards!
│   (Hover for red glow effect!)                  │
│                                                  │
│  [🔴 Start Monitoring]  [Settings]               │
│                                                  │
│  40+ Games Supported  •  FSR 3.x Ready            │
└──────────────────────────────────────────────────┘
```

### Design Elements

**Colors:**
- 🔴 MSI Red: `#E30613`
- ⚫ Deep Black: `#0A0A0A`
- 🔘 Glass: `rgba(20, 20, 20, 0.75)`
- ⚪ White Text: `#FFFFFF`

**Effects:**
- ✨ Glassmorphism panels
- 🔆 Hover glow (red)
- 💨 Smooth animations
- 🟢 Pulsing status dots

**Typography:**
- **Headers:** Segoe UI Bold 32px
- **Body:** Segoe UI Regular 13px
- **Metrics:** Segoe UI Bold 24px

---

## ✨ Features

### Core Features

✅ **Real-time Performance Monitoring**
- CPU, GPU, RAM usage
- Per-game metrics
- FPS tracking
- Temperature monitoring

✅ **Game Detection**
- 40+ supported games
- Auto-detection
- Process monitoring
- Custom game profiles

✅ **FSR 3.x Integration**
- Frame generation
- AMD FidelityFX
- DLL injection
- Quality presets

✅ **Auto-Injection**
- Launch detection
- Automatic FSR injection
- Profile-based settings
- Safe injection

### UI Features (New!)

✅ **Liquid Glass Theme**
- Frosted glass panels
- Translucent backgrounds
- Blur effects
- MSI color palette

✅ **Game Cards**
- Beautiful tile layout
- Hover effects
- Status indicators
- Performance metrics

✅ **Smooth Animations**
- Fade transitions
- Slide effects
- Scale animations
- 60fps smooth

✅ **Modern Controls**
- Animated buttons
- Glass panels
- Status dots
- Clean layout

---

## 📚 Documentation

### User Guides

- [Installation Guide](docs/INSTALLATION.md)
- [User Guide](docs/USER_GUIDE.md)
- [Quick Start](docs/QUICK_START.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

### Developer Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- **[Stage 7.8a - Liquid Glass UI](docs/STAGE_7.8a_LIQUID_GLASS_UI.md)** ⭐
- [API Reference](docs/API.md)

### Changelog

- [Stage 7.8a](docs/STAGE_7.8a_LIQUID_GLASS_UI.md) - Liquid Glass UI
- [Stage 7.7d](docs/STAGE_7.7d_COMPLETE.md) - Game Profiles + Auto-Injection
- [Stage 7.7c](docs/STAGE_7.7c_COMPLETE.md) - Real Monitoring
- [Hotfixes](docs/HOTFIX_7.7d_4.md) - Latest fixes

---

## 🛠️ Tech Stack

### UI Framework

- **PyQt6** - Modern Qt6 bindings
- **Custom Widgets** - Beautiful components
- **QSS Styling** - Advanced stylesheets
- **QPainter** - Custom rendering

### Design System

- **Glassmorphism** - Apple-inspired effects
- **MSI Colors** - Gaming aesthetic
- **Smooth Animations** - 60fps transitions
- **Responsive Layout** - Adaptive design

### Monitoring

- **psutil** - System metrics
- **nvidia-ml-py3** - GPU monitoring
- **Custom detectors** - Game detection

---

## 📝 Project Structure

```
partmart-boost/
├── src/
│   ├── ui/
│   │   ├── themes/
│   │   │   ├── liquid_glass.py     # ⭐ Main theme
│   │   │   └── msi_colors.py        # ⭐ Color system
│   │   ├── widgets/
│   │   │   ├── game_card.py         # ⭐ Game tiles
│   │   │   ├── glass_panel.py       # ⭐ Glass containers
│   │   │   ├── modern_button.py     # ⭐ Buttons
│   │   │   └── status_indicator.py  # ⭐ Status dots
│   │   └── animations/
│   │       ├── fade.py              # ⭐ Fade effects
│   │       ├── slide.py             # ⭐ Slide transitions
│   │       └── scale.py             # ⭐ Scale animations
│   ├── gui/
│   │   ├── modern_main_window.py  # ⭐ New beautiful window
│   │   └── main_window.py         # Old legacy window
│   ├── core/
│   ├── monitoring/
│   ├── detection/
│   └── fsr/
├── docs/
│   └── STAGE_7.8a_LIQUID_GLASS_UI.md  # ⭐ UI Documentation
├── launcher.py          # ⭐ Updated launcher
├── VERSION.txt          # 0.3.5e
└── README.md
```

---

## 🎯 Roadmap

### Stage 7.8b (Next) - UI Integration

- [ ] Integrate real monitoring data
- [ ] Performance graphs and charts
- [ ] Settings panel redesign
- [ ] Game profile editor UI
- [ ] FSR controls interface

### Stage 7.9 - Advanced Features

- [ ] Custom profiles per game
- [ ] Benchmark mode
- [ ] Screenshot comparison
- [ ] Overlay HUD

### Stage 8.0 - Polish

- [ ] Light theme variant
- [ ] Customizable colors
- [ ] User preferences
- [ ] Localization

---

## 🤝 Contributing

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

---

## 📝 License

MIT License - see [LICENSE](LICENSE)

---

## 👏 Credits

**Design Inspiration:**
- Apple macOS (Liquid Glass effects)
- Steam (Game library)
- Spotify (Modern design)
- MSI (Gaming aesthetic)

**Developed with:**
- Python 3.9+
- PyQt6
- Love for beautiful UIs ❤️

---

**PartMart Boost v0.3.5e** - Now with **Liquid Glass UI**! 🌟

**Launch the Modern GUI and experience the beauty!** 🚀
