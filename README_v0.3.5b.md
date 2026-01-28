# 🚀 PartMart Boost v0.3.5b - Debug и простое добавление игр!

## ✨ ЧТО НОВОГО

### 🔧 Debug режим ВКЛЮЧЕН
- ✅ Теперь видно почему метрики не показываются
- ✅ Подробные логи в консоли
- ✅ Данные GPU/RAM/CPU видны

### ➕ ПРОСТОЕ ДОБАВЛЕНИЕ ИГР
- ✅ Кнопка "➕ Добавить игру" в UI
- ✅ Простая форма с 2 полями
- ✅ Кнопка "📁 Обзор" для выбора .exe
- ✅ Автоматическое создание профиля
- ✅ Подсказки прямо в UI

### 🎨 НАЧАЛО СВОЕГО UI
- ✅ Красивые диалоги
- ✅ Кастомные кнопки
- ✅ Красно-черный стиль

## 🚀 КАК ОБНОВИТЬ

```bash
cd "U:\Users\admir\Downloads\pmb beta\pmb"
git pull origin main
start_app.bat
```

## 🎮 КАК ДОБАВИТЬ ИГРУ (ТЕПЕРЬ ПРОЩЕ!)

### Способ 1: Через UI (САМЫЙ ПРОСТОЙ!)

1. **Открой PartMart Boost**
2. **Перейди на вкладку "🎮 Игры"**
3. **Нажми "➕ Добавить игру"**

4. **Заполни форму:**
   - 🏷️ **Название игры**: `Escape From Tarkov`
   - 💾 **Имя .exe**: `EscapeFromTarkov.exe`
   - 🔥 **Приоритет**: Выбери (рекомендуем "Высокий")

5. **Нажми "✅ Добавить игру"**

6. **Нажми "🔄 Обновить" или перезапусти**

🎉 **ГОТОВО!**

### 💡 КАК НАЙТИ ИМЯ .exe

#### Способ 1: Через Task Manager
1. 🎮 **Запусти игру**
2. ⌨️ **Ctrl+Shift+Esc** (открыть Task Manager)
3. 📊 **Details** → найди процесс игры
4. 📋 **Скопируй имя** (например "EscapeFromTarkov.exe")

#### Способ 2: Через кнопку "📁 Обзор"
1. В диалоге добавления игры нажми "📁 Обзор"
2. Найди .exe файл игры
3. Имя автоматически подставится!

## 📊 ПОЧЕМУ МЕТРИКИ НЕ ПОКАЗЫВАЮТ?

### Теперь вы увидите причину в консоли!

**Пример debug вывода:**
```bash
[SystemMonitor] Initialized (debug=ON)
[DEBUG] Raw GPU data keys: ['name', 'temperature', 'load', 'clock']
[DEBUG] GPU name: NVIDIA GeForce GTX 1660
[DEBUG] Mapped GPU - temp=65, load=45, clock=1800
[DEBUG] RAM keys: ['total', 'used', 'percent']
[DEBUG] RAM - 8.5/16.0 GB (53%)
[DEBUG] CPU keys: ['name', 'load', 'count']
[DEBUG] CPU - load=35%, cores=6
```

### Возможные причины:

1. **GPU температура = 0**
   - Нужны admin права ИЛИ PyNVML
   - Решение: Запусти от администратора

2. **RAM/CPU = 0**
   - psutil не установлен
   - Решение: `pip install psutil`

3. **Все = 0**
   - MonitorManager не инициализирован
   - Решение: Смотри debug логи

## 🎨 СВОЙ UI - ЧТО ДОБАВЛЕНО

### ✅ Диалог добавления игр
- Красивый стиль
- Подсказки в placeholders
- Валидация ввода
- Help карточка

### ✅ Кнопки приоритета
- Toggle buttons
- Визуальный выбор
- Авто-снятие выбора

### 🔜 В разработке:
- Custom progress bars
- Custom cards
- Custom charts
- Анимации

## 📊 ЧТО ДОЛЖНО ПОКАЗЫВАТЬ

### ✅ В консоли:
```bash
[SystemMonitor] Initialized (debug=ON)  # Debug включен!
[OK] Game Profiles system loaded
[OK] Loaded profile: Escape From Tarkov
[DEBUG] GPU name: ...
[DEBUG] Mapped GPU - temp=XX, load=XX
[DEBUG] RAM - X.X/XX.X GB
[DEBUG] CPU - load=XX%
```

### ✅ В UI:
- 🌡️ GPU Temperature: **XX°C** (НЕ "--")
- 🧠 RAM Usage: **XX%** (НЕ "--")
- 💻 CPU Load: **XX%** (НЕ "--")
- 🎮 Вкладка Игры с кнопкой "➕ Добавить"

## 🐛 Troubleshooting

### Проблема: Метрики "--"
**Решение:**
1. Смотри консоль - там будет причина
2. Запусти от admin
3. Проверь `pip install psutil`

### Проблема: Не могу добавить игру
**Решение:**
1. Используй кнопку "➕ Добавить игру"
2. Имя .exe должно быть ТОЧНЫМ
3. Используй "📁 Обзор" для поиска

### Проблема: Игра не определяется
**Решение:**
1. Проверь имя .exe в Task Manager
2. Перезапусти PartMart Boost
3. Запусти игру заново

## 📈 Changelog v0.3.5b

### Added
- ➕ Простое добавление игр через UI
- 📁 Кнопка "Обзор" для .exe файлов
- 💡 Help карточка в UI
- 🔧 Debug режим по умолчанию
- 🔄 Кнопка "Обновить" для перезагрузки профилей

### Fixed
- 🔧 Подробные логи для отладки метрик
- 🔧 Error handling с traceback
- 🔧 Безопасная обработка None

### Changed
- 🔄 Версия 0.3.5b
- 🎨 Начало своего UI

## 💚 ТЕПЕРЬ УДОБНЕЕ!

**Главные улучшения:**
- ✅ Debug показывает проблемы
- ✅ Добавление игр в 2 клика
- ✅ Красивый UI

🎮 **Просто и понятно для рядового пользователя!**

---

**PartMart Team**  
Version: 0.3.5b  
Date: 2026-01-28 08:25 GMT

Commits:
- [Debug mode ON + easy game UI](https://github.com/vitorpixel-6436/partmart-boost)
