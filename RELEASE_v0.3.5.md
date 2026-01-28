# 🚀 PartMart Boost v0.3.5 - Stable Release

## 📋 Что исправлено

### ✅ GPU метрики теперь работают!
- **Исправлено**: GPU данные показывали "0" или "--"
- **Причина**: Несовпадение ключей между GPU монитором и wrapper
- **Решение**: Добавлен умный маппинг ключей
- **Теперь показывает**: Температуру, загрузку, частоту, память

### ✅ Убрана CSS ошибка
- **Исправлено**: "Unknown property transform" в терминале
- **Причина**: PyQt6 не поддерживает CSS transform
- **Решение**: Убрано свойство transform из кнопок

### ✅ Версия обновлена везде
- **Версия**: 0.3.5
- **Обновлено**: main_window.py, system_monitor.py
- **Стабильность**: Не разгоняемся с версиями

## 🎮 Как добавить игровые профили

### Шаг 1: Создать профиль игры

```bash
cd "U:\Users\admir\Downloads\pmb beta\pmb\config\profiles"
copy example_game.json eft.json
```

### Шаг 2: Отредактировать профиль

Открой `eft.json` в текстовом редакторе:

```json
{
  "game_name": "Escape From Tarkov",
  "enabled": true,
  "executable_names": [
    "EscapeFromTarkov.exe",
    "EFT.exe"
  ],
  
  "priority": "high",
  "affinity": "auto",
  
  "gpu": {
    "enabled": true,
    "power_limit": 100,
    "temp_limit": 85,
    "fan_curve": "aggressive"
  },
  
  "ram": {
    "enabled": true,
    "cleanup_before_launch": true,
    "reserved_mb": 4096
  },
  
  "windows": {
    "game_mode": true,
    "fullscreen_optimizations": false,
    "hags": true,
    "game_bar": false
  }
}
```

### Шаг 3: Узнать имя .exe файла

**Способ 1 - Task Manager:**
1. Запусти игру
2. Открой Task Manager (Ctrl+Shift+Esc)
3. Вкладка "Details"
4. Найди процесс игры
5. Скопируй имя (например "GTA5.exe")

**Способ 2 - Папка игры:**
1. Открой папку с игрой
2. Найди .exe файл
3. Скопируй полное имя

### Шаг 4: Добавить в профиль

```json
"executable_names": [
  "EscapeFromTarkov.exe",  // Основной
  "EFT.exe",               // Альтернативный
  "tarkov.exe"             // На всякий случай
]
```

### Шаг 5: Включить профиль

```json
"enabled": true
```

### Шаг 6: Перезапустить PartMart Boost

```bash
cd "U:\Users\admir\Downloads\pmb beta\pmb"
start_app.bat
```

## 🎮 Примеры профилей для твоих игр

### Escape From Tarkov
```json
{
  "game_name": "Escape From Tarkov",
  "enabled": true,
  "executable_names": [
    "EscapeFromTarkov.exe"
  ],
  "priority": "high",
  "ram": {
    "enabled": true,
    "cleanup_before_launch": true,
    "reserved_mb": 4096
  }
}
```

### GTA 5
```json
{
  "game_name": "GTA 5",
  "enabled": true,
  "executable_names": [
    "GTA5.exe",
    "GTAVLauncher.exe"
  ],
  "priority": "high",
  "gpu": {
    "enabled": true,
    "power_limit": 100
  }
}
```

### Minecraft
```json
{
  "game_name": "Minecraft Java",
  "enabled": true,
  "executable_names": [
    "javaw.exe",
    "java.exe"
  ],
  "priority": "high",
  "ram": {
    "enabled": true,
    "reserved_mb": 8192
  }
}
```

## 🔧 Настройки профиля

### Priority (приоритет процесса)
- `"realtime"` - Максимальный (осторожно!)
- `"high"` - Высокий (рекомендуется)
- `"above_normal"` - Выше среднего
- `"normal"` - Обычный

### Affinity (привязка к ядрам)
- `"auto"` - Автоматически
- `"performance_cores"` - Только P-cores
- `"all_cores"` - Все ядра

### GPU Settings
```json
"gpu": {
  "enabled": true,           // Включить GPU оптимизацию
  "power_limit": 100,        // Лимит мощности (90-110%)
  "temp_limit": 85,          // Лимит температуры (°C)
  "fan_curve": "aggressive" // Профиль вентиляторов
}
```

### RAM Settings
```json
"ram": {
  "enabled": true,               // Включить RAM оптимизацию
  "cleanup_before_launch": true, // Очистить перед запуском
  "reserved_mb": 4096           // Зарезервировать (MB)
}
```

### Windows Settings
```json
"windows": {
  "game_mode": true,                  // Windows Game Mode
  "fullscreen_optimizations": false, // FSO (часто лагает)
  "hags": true,                       // Hardware Scheduling
  "game_bar": false                   // Xbox Game Bar (выкл)
}
```

## 📊 Что показывает программа сейчас

### ✅ Работает:
- GPU Temperature (если доступна)
- GPU Name
- GPU Load
- GPU Clock
- GPU Memory
- RAM Usage (процент и GB)
- CPU Load (процент)
- CPU Cores/Threads
- CPU Name

### ⚠️ Может быть недоступно:
- GPU Temperature (без PyNVML или admin прав)
- CPU Temperature (только Linux)
- GPU Fan Speed (зависит от карты)

### ❌ Пока не работает:
- GPU Control (разгон, fan curve)
- RAM Tuner (XMP, cleaning)
- Game Profiles (модуль есть, но UI пустой)

## 🚀 Как запустить

### 1. Скачать обновление
```bash
cd "U:\Users\admir\Downloads\pmb beta\pmb"
git pull origin main
```

### 2. Запустить
```bash
start_app.bat
```

### 3. Проверить логи
Если что-то не работает - смотри терминал:
```bash
[OK] GPU Monitor: ...  # Должен быть OK
[OK] CPU Monitor: ...  # Должен быть OK
[OK] RAM Monitor: ...  # Должен быть OK
```

## 🐛 Troubleshooting

### Метрики показывают "--"

**Решение 1: Запустить от администратора**
```bash
Правой кнопкой на start_app.bat → Запустить от имени администратора
```

**Решение 2: Проверить мониторы**
```bash
cd src
python system_monitor.py
```

Должно показать:
```
[GPU Data]
  Name: NVIDIA ...
  Temperature: XX°C
  Load: XX%
  ...
```

### Игра не определяется

**Проблема**: Неправильное имя .exe

**Решение**:
1. Запусти игру
2. Открой Task Manager
3. Найди процесс игры в "Details"
4. Скопируй ТОЧНОЕ имя в профиль
5. Перезапусти PartMart Boost

**Проблема**: Профиль не включен

**Решение**:
```json
"enabled": true  // Не false!
```

**Проблема**: Нет файла профиля

**Решение**:
1. Скопируй `example_game.json`
2. Переименуй в название игры
3. Отредактируй
4. Перезапусти

### CSS ошибка "transform"

✅ **Исправлено в v0.3.5!**

Если всё равно видишь - скачай обновление:
```bash
git pull origin main
```

## 📈 Sovereignty Score: 50/100

**Что это?**
Показатель независимости от внешних библиотек:
- 100 = только нативные API (максимальная производительность)
- 50 = гибрид (psutil + native)
- 0 = только библиотеки

**Для Windows - 50/100 это нормально!**

## 🔄 Changelog

### [0.3.5] - 2026-01-28 08:05 GMT

#### Fixed
- 🔧 GPU метрики: Исправлен маппинг ключей (temperature, clock, load)
- 🔧 CSS ошибка: Убрано свойство `transform` из стилей
- 🔧 Версия: Обновлена везде на 0.3.5
- 🔧 Debug: Добавлен debug режим в SystemMonitor

#### Added
- 📚 Example game profile с инструкциями
- 📚 Подробный README для игровых профилей
- 📚 Примеры профилей (EFT, GTA 5, Minecraft)

#### Changed
- 🔄 SystemMonitor: Умный маппинг ключей GPU
- 🔄 UI: Убран transform из Quick Boost кнопки

## 📝 TODO для следующих версий

### v0.3.6 (Next)
- [ ] GPU Control виджет (разгон, fan)
- [ ] RAM Tuner виджет (XMP, cleanup)
- [ ] Games виджет (список, управление)
- [ ] Системные трей-иконка

### v0.4.0 (Major)
- [ ] Полный набор игровых профилей (50+ игр)
- [ ] Автоопределение игр через Steam/Epic
- [ ] Статистика FPS
- [ ] Графики производительности

### v0.5.0 (Custom UI)
- [ ] Web-based UI (Flask + HTML/CSS/JS)
- [ ] Современный дизайн
- [ ] Анимации и эффекты
- [ ] Темная/светлая тема

## 💡 Советы

### Для максимальной производительности:
1. **Запускай от администратора** - доступ к GPU/CPU данным
2. **Создай профили игр** - автооптимизация при запуске
3. **Используй Quick Boost** - быстрая оптимизация системы
4. **Отключи Xbox Game Bar** - освободит ресурсы
5. **Включи HAGS** - Hardware Accelerated GPU Scheduling

### Для стабильности:
1. **Не используй "realtime" priority** - может зависнуть система
2. **Оставь reserve RAM 2-4GB** - для системы
3. **Следи за температурой GPU** - не выше 85°C

## 🆘 Поддержка

### Если проблема не решена:
1. 🐛 **GitHub Issue**: https://github.com/vitorpixel-6436/partmart-boost/issues
2. 📧 **Email**: vitorleitye6436@gmail.com
3. 📝 **Приложи**:
   - Весь вывод терминала
   - Скриншот UI
   - Версию Python: `python --version`
   - GPU модель
   - OS: Windows/Linux

## 🎯 Разработчики

**PartMart Team**  
Version: 0.3.5  
Date: 2026-01-28 08:05 GMT

Commits:
- [49b0de0](https://github.com/vitorpixel-6436/partmart-boost/commit/49b0de00d65c54cd8201de396453e5822818c2a1) - Fix CSS and version
- [8a30474](https://github.com/vitorpixel-6436/partmart-boost/commit/8a30474ed2e936eaad3698f1572def386e578738) - Fix GPU mapping
- [3f05fbc](https://github.com/vitorpixel-6436/partmart-boost/commit/3f05fbc8010b6ce0c256e83b9ea4753769d103aa) - Add game profile example

---

🎮 **Готово к игре!** Теперь можно добавлять свои профили и наслаждаться оптимизацией!
