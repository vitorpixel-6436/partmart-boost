# 🚀 Установка PartMart Boost

## 📦 Быстрая установка (Рекомендуется)

```bash
# 1. Скачать проект
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить
python src/main.py
```

**Готово!** Приложение запущено.

---

## ⚠️ Если возникли проблемы

### Проблема 1: Python не найден

```bash
python: command not found
```

**Решение:**
1. Установите Python 3.11+ с [python.org](https://www.python.org/downloads/)
2. При установке обязательно отметьте **"Add Python to PATH"**

### Проблема 2: PyQt6 DLL error (Python 3.14)

```
ImportError: DLL load failed while importing QtCore
```

**Решение:**
```bash
# Переустановите PyQt6
pip uninstall PyQt6 PyQt6-Qt6 -y
pip install PyQt6>=6.8.0 PyQt6-Qt6>=6.8.0
```

### Проблема 3: nvidia-ml-py не устанавливается

**Решение:**
```bash
# Установите по одному
pip install nvidia-ml-py
pip install psutil
pip install PyQt6
pip install wmi
```

---

## 💻 Требования

### Минимальные:
- **Python**: 3.11+ (рекомендуется 3.11 или 3.12)
- **ОС**: Windows 10 (build 19043+) или Windows 11
- **RAM**: 2GB+
- **GPU**: Любая (для NVIDIA больше функций)

### Рекомендуемые:
- **Python**: 3.12.x
- **GPU**: NVIDIA GTX 10xx+ или RTX
- **Интернет**: Не требуется после установки

---

## 🔧 Установка с venv (Опционально)

Если вы хотите изолировать зависимости:

```bash
# 1. Создать venv
python -m venv venv

# 2. Активировать
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить
python src/main.py

# Для выхода:
deactivate
```

---

## 🚀 Быстрый запуск в будущем

После первой установки просто:

```bash
cd partmart-boost
python src/main.py
```

Или создайте ярлык Windows:
1. ПКМ на рабочем столе → Создать ярлык
2. Путь: `python "C:\path\to\partmart-boost\src\main.py"`
3. Рабочая папка: `C:\path\to\partmart-boost`
4. Иконка: `C:\path\to\partmart-boost\assets\icon.ico` (если есть)

---

## 🐛 Ошибки и поддержка

Если возникли проблемы:
1. Проверьте [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Создайте issue: [GitHub Issues](https://github.com/vitorpixel-6436/partmart-boost/issues)
3. Приложите логи из `logs/partmart.log`

---

## ✅ Проверка установки

После запуска вы должны увидеть:
- ✅ Три карточки с метриками (GPU, RAM, CPU)
- ✅ Красные цифры (температуры и проценты)
- ✅ Прогресс-бары с загрузкой
- ✅ Кнопку "БЫСТРЫЙ БУСТ"
- ✅ Автообновление данных каждые 2 секунды

**Если что-то не работает** - сообщите в Issues!
