# 🔧 РЕФАКТОРИНГ ЧАСТЬ 1: Базовая архитектура + GPU Monitor

## ✅ ЧТО СДЕЛАНО

### 1. Базовый класс `BaseMonitor`

**Файл:** `src/monitors/__init__.py`

**Функции:**
- Абстрактный класс для всех мониторов
- Единый интерфейс (`get_data()`, `get_name()`, `is_available()`)
- Встроенная обработка ошибок
- Graceful degradation (если железо недоступно)

**Методы:**
```python
class BaseMonitor(ABC):
    def _initialize() -> bool          # Инициализация железа
    def get_data() -> Dict[str, Any]   # Получить текущие данные
    def get_name() -> str              # Название железа
    def is_available() -> bool         # Доступен ли монитор
    def get_last_error() -> str        # Последняя ошибка
```

### 2. GPU Monitor (NVIDIA)

**Файл:** `src/monitors/gpu_monitor.py`

**Функции:**
- Чистая реализация на основе `pynvml`
- Поддержка **hotspot temperature** (точнее чем core temp)
- Graceful fallback (если датчики недоступны)
- Удобные helper методы

**Поддерживаемые метрики:**
```python
{
    'name': 'NVIDIA GeForce RTX 3060',
    'temperature': 52,              # Core temp
    'temperature_hotspot': 57,      # Hotspot (точнее!)
    'clock_graphics': 1785,         # MHz
    'clock_memory': 8001,           # MHz
    'load_gpu': 38,                 # %
    'load_memory': 24,              # %
    'power_usage': 125.5,           # W
    'power_limit': 170.0,           # W
    'fan_speed': 45,                # %
    'memory_total': 12288,          # MB
    'memory_used': 3456,            # MB
    'memory_free': 8832             # MB
}
```

**Helper методы:**
```python
monitor.get_temperature(use_hotspot=True)  # Получить температуру
monitor.get_load()                         # Получить загрузку GPU
monitor.get_memory_usage()                 # Получить использование памяти
```

---

## 📊 ПРЕИМУЩЕСТВА НОВОЙ АРХИТЕКТУРЫ

### 1. Модульность
- Каждый монитор в отдельном файле
- Легко добавить AMD GPU, Intel GPU, etc.
- Независимое тестирование

### 2. Отказоустойчивость
```python
monitor = GPUMonitor()
if monitor.is_available():
    data = monitor.get_data()
else:
    print(f"GPU недоступен: {monitor.get_last_error()}")
```

### 3. Graceful Degradation
- Если pynvml не установлен → монитор недоступен (не краш)
- Если GPU нет → монитор недоступен
- Если датчик сломан → None вместо exception

### 4. Точность
- **Hotspot temperature** вместо core (точнее на 5-10°C)
- Совпадает с MSI Afterburner, HWiNFO

---

## 🛠️ ИСПОЛЬЗОВАНИЕ

### Базовый пример:
```python
from monitors.gpu_monitor import GPUMonitor

monitor = GPUMonitor()

if monitor.is_available():
    print(f"GPU: {monitor.get_name()}")
    print(f"Temp: {monitor.get_temperature()}°C")
    print(f"Load: {monitor.get_load()}%")
else:
    print(f"Error: {monitor.get_last_error()}")
```

### Полные данные:
```python
data = monitor.get_data()
for key, value in data.items():
    if value is not None:
        print(f"{key}: {value}")
```

### Интеграция в UI:
```python
class PartMartMainWindow:
    def __init__(self):
        self.gpu_monitor = GPUMonitor()
        
    def _update_gpu_card(self):
        if not self.gpu_monitor.is_available():
            self.gpu_card.set_value("N/A")
            self.gpu_card.set_subtitle("GPU not detected")
            return
        
        temp = self.gpu_monitor.get_temperature(use_hotspot=True)
        load = self.gpu_monitor.get_load()
        
        self.gpu_card.set_value(f"{temp}°C")
        self.gpu_card.set_subtitle(f"Load: {load}%")
        self.gpu_card.set_progress(int(load))
```

---

## ✅ ТЕСТИРОВАНИЕ

### Запустить тест:
```bash
python src/monitors/gpu_monitor.py
```

### Ожидаемый вывод:
```
✅ GPU detected: NVIDIA GeForce RTX 3060

📊 GPU Data:
  name: NVIDIA GeForce RTX 3060
  temperature: 52
  temperature_hotspot: 57
  clock_graphics: 1785
  clock_memory: 8001
  load_gpu: 38
  load_memory: 24
  power_usage: 125.5
  fan_speed: 45
  memory_total: 12288
  memory_used: 3456
  memory_free: 8832

🌡️ Temperature: 57°C
⚡ Load: 38%
🧠 Memory: 3456/12288 MB (28.1%)
```

---

## 🔜 СЛЕДУЮЩИЕ ШАГИ

**ЧАСТЬ 2** (следующий запрос):
- `cpu_monitor.py` - CPU мониторинг
- `ram_monitor.py` - RAM мониторинг

**ЧАСТЬ 3:**
- `error_handler.py` - Централизованная обработка ошибок
- Обновить `system_monitor.py` для использования новых модулей

**ЧАСТЬ 4:**
- ML optimizer (легковесный, опциональный)

---

## 📄 ФАЙЛЫ

```
src/
├── monitors/
│   ├── __init__.py         ✅ BaseMonitor
│   └── gpu_monitor.py      ✅ GPUMonitor (NVIDIA)
├── core/
│   ├── config.py           ✅ Config system
│   └── logger.py           ✅ Logging system
└── localization.py         ✅ i18n system
```

---

## 💡 КЛЮЧЕВЫЕ ПРИНЦИПЫ

1. **Один класс = одна ответственность**
2. **Graceful degradation везде**
3. **Никаких необработанных exception**
4. **Чистый интерфейс** (BaseMonitor)
5. **Легкое тестирование**
