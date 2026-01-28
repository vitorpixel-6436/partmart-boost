# 🚀 PartMart Boost v0.3.5a - ПОЛНОСТЬЮ РАБОЧАЯ ВЕРСИЯ!

## ✅ ЧТО ИСПРАВЛЕНО

### 🎮 Игровые профили ТЕПЕРЬ РАБОТАЮТ!
- ✅ Созданы ВСЕ модули: `game_profiles.py`, `game_detector.py`, `optimization_applier.py`
- ✅ Рабочий UI для управления играми
- ✅ Автообнаружение запущенных игр
- ✅ Автоприменение оптимизации
- ✅ Уведомления о применении профиля

### 📊 Метрики РАБОТАЮТ!
- ✅ GPU: температура, загрузка, частота, память
- ✅ RAM: процент, GB, тип
- ✅ CPU: загрузка, ядра, частота
- ✅ Исправлен маппинг ключей

### 🔧 CSS ошибка убрана
- ✅ Удалено `transform` свойство
- ✅ Никаких ошибок в консоли

## 🚀 КАК ЗАПУСТИТЬ

```bash
# 1. Перейти в папку
cd "U:\Users\admir\Downloads\pmb beta\pmb"

# 2. Скачать обновление
git pull origin main

# 3. ЗАПУСТИТЬ!
start_app.bat
```

## 🎮 КАК ДОБАВИТЬ ИГРУ

### Быстрый способ:

1. **Открой Task Manager** (Ctrl+Shift+Esc)
2. **Запусти игру**
3. **Details → найди процесс игры**
4. **Скопируй имя** (например "EscapeFromTarkov.exe")

5. **Создай профиль:**
```bash
cd "U:\Users\admir\Downloads\pmb beta\pmb\config\profiles"
copy example_game.json eft.json
notepad eft.json
```

6. **Измени:**
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

7. **Перезапусти PartMart Boost**

8. **Запусти игру → получишь уведомление!** 🎉

## 📊 ЧТО ПОКАЗЫВАЕТ

### ✅ GPU (если есть PyNVML или admin):
- 🌡️ Температура (XX°C)
- ⚙️ Загрузка (XX%)
- 💻 Частота (XXXX MHz)
- 🧠 Память (XXXX / XXXX MB)
- 🏷️ Имя GPU

### ✅ RAM (всегда работает):
- 📈 Процент (XX%)
- 💾 Использовано / Всего (XX.X / XX.X GB)
- ⚡ Скорость (XXXX MHz)
- 🏷️ Тип (DDR4/DDR5)

### ✅ CPU (всегда работает):
- 📈 Загрузка (XX%)
- 💻 Ядра / Потоки (XX / XX)
- ⚡ Частота (XXXX MHz)
- 🏷️ Имя CPU

### 🎮 Игровые профили:
- ✅ Автообнаружение игр
- ✅ Применение профиля
- ✅ Уведомления
- ✅ UI для управления

## 🎮 ПРИМЕРЫ ПРОФИЛЕЙ

### Escape From Tarkov
```json
{
  "game_name": "Escape From Tarkov",
  "enabled": true,
  "executable_names": ["EscapeFromTarkov.exe"],
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
  "executable_names": ["GTA5.exe"],
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
  "game_name": "Minecraft",
  "enabled": true,
  "executable_names": ["javaw.exe", "java.exe"],
  "priority": "high",
  "ram": {"reserved_mb": 8192}
}
```

## ⚠️ ЕСЛИ МЕТРИКИ ПОКАЗЫВАЮТ "--"

### Решение: Запусти от Администратора
```
Правой кнопкой на start_app.bat → Запустить от имени администратора
```

**Почему?**
- GPU температура требует admin прав без PyNVML
- Некоторые WMI запросы требуют прав

## 🐛 ЕСЛИ ИГРА НЕ ОПРЕДЕЛЯЕТСЯ

### Проверь:

1. **Имя .exe ПРАВИЛЬНОЕ?**
   - Task Manager → Details → точное имя
   - Регистр НЕ важен ("GTA5.exe" = "gta5.exe")

2. **Профиль ВКЛЮЧЕН?**
   ```json
   "enabled": true  // НЕ false!
   ```

3. **Файл существует?**
   ```
   config/profiles/eft.json  // Да, существует
   ```

4. **PartMart Boost перезапущен?**
   - После создания профиля НАДО перезапустить!

## 📊 ЧТО ДОЛЖНО БЫТЬ В КОНСОЛИ

### ✅ НОРМАЛЬНО:
```bash
[OK] Game Profiles system loaded  # Система загружена!
[OK] GPU Monitor: Available: True
[OK] CPU Monitor: Available: True  
[OK] RAM Monitor: Available: True
[MonitorManager] Sovereignty Score: 50/100
[OK] Loaded profile: Escape From Tarkov  # Профиль загружен!
```

### ⚠️ НОРМАЛЬНЫЕ ПРЕДУПРЕЖДЕНИЯ:
```bash
[DEBUG] CPU temp sensor detection failed  # Нормально для Windows
```

### ❌ НЕ ДОЛЖНО БЫТЬ:
```bash
[WARN] Game Profiles not available  # Этого больше НЕТ!
Unknown property transform  # Этого больше НЕТ!
ERROR: Failed to update system data  # Этого больше НЕТ!
```

## 🚀 КАК ЭТО РАБОТАЕТ

1. **Запускаешь PartMart Boost** → загружаются профили
2. **Запускаешь игру** → PartMart обнаруживает .exe
3. **Применяется профиль** → приоритет, RAM, GPU
4. **Получаешь уведомление** 🎉
5. **Играешь** → оптимизация работает
6. **Выходишь из игры** → оптимизация откатывается

## 📈 Changelog v0.3.5a

### Added
- ✅ ПОЛНАЯ система игровых профилей
- ✅ `profiles/game_profiles.py` - управление профилями
- ✅ `profiles/game_detector.py` - обнаружение игр
- ✅ `profiles/optimization_applier.py` - применение оптимизаций
- ✅ `ui/games_widget.py` - UI для игр
- ✅ Уведомления о применении профиля

### Fixed
- 🔧 GPU метрики теперь показываются правильно
- 🔧 RAM и CPU метрики работают
- 🔧 CSS ошибка "transform" убрана
- 🔧 Версия обновлена на 0.3.5a

### Changed
- 🔄 Полностью рабочая версия!

## 💚 РАБОЧАЯ ВЕРСИЯ!

**Теперь ВСЕ РАБОТАЕТ:**
- ✅ Метрики GPU/RAM/CPU
- ✅ Игровые профили
- ✅ Автообнаружение
- ✅ Никаких ошибок

🎮 **Создай профили для своих игр и наслаждайся!**

---

**PartMart Team**  
Version: 0.3.5a  
Date: 2026-01-28 08:14 GMT

Commits:
- [Полная система игровых профилей](https://github.com/vitorpixel-6436/partmart-boost)
- Исправление всех метрик
- Убрана CSS ошибка
