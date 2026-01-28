"""Internationalization (i18n) system for PartMart Boost"""
import json
import os
from typing import Dict

class Localization:
    """Lightweight localization system"""
    
    SUPPORTED_LANGUAGES = ['en', 'ru']
    DEFAULT_LANGUAGE = 'en'
    
    # Embedded translations (no external files needed)
    TRANSLATIONS = {
        'en': {
            # Window
            'window_title': 'PartMart Boost v{version}',
            
            # Navigation
            'nav_home': 'Home',
            'nav_gpu': 'GPU',
            'nav_ram': 'RAM',
            'nav_settings': 'Settings',
            
            # Metrics
            'metric_gpu_temp': 'GPU Temperature',
            'metric_ram_usage': 'RAM Usage',
            'metric_cpu_load': 'CPU Load',
            
            # System info
            'system_info_title': 'SYSTEM METRICS',
            'gpu_info': 'GPU: {name} | {clock}MHz | {temp}°C | Load {load}%',
            'cpu_info': 'CPU: {cores} cores | Load {load}% | {freq}MHz',
            
            # Actions
            'action_gpu_control': 'GPU Control',
            'action_gpu_desc': 'GPU optimization',
            'action_ram_tuner': 'RAM Tuner',
            'action_ram_desc': 'XMP and memory cleanup',
            
            # Quick Boost
            'quick_boost': 'QUICK BOOST',
            'quick_boost_title': 'Quick Boost',
            'quick_boost_msg': 'Optimize system?\n\nWill perform:\n• RAM cleanup\n• Process priority optimization',
            'quick_boost_success': 'Optimization complete!\n\nCheck metrics for changes.',
            'quick_boost_error': 'Failed to perform optimization:\n{error}',
            
            # GPU Page
            'gpu_control_title': 'GPU CONTROL',
            'gpu_loading': 'Loading GPU info...',
            
            # Placeholders
            'coming_soon': 'Coming Soon',
            
            # Units
            'unit_celsius': '°C',
            'unit_percent': '%',
            'unit_gb': 'GB',
            'unit_mhz': 'MHz',
            
            # Messages
            'loading': 'Loading...',
            'error': 'Error',
            'success': 'Success',
            'warning': 'Warning',
            
            # CPU
            'cpu_cores': '{count} cores',
            'cpu_temp': 'Temp: {temp}°C',
            'cpu_freq': '{freq}MHz',
            
            # Progress
            'load_progress': 'Load: {value}%',
            
            # AI Recommendations
            'ai_temp_high': 'GPU temperature {diff}°C above average',
            'ai_temp_low': 'GPU temperature below average - excellent!',
            'ai_clean_cooling': 'Recommended: Clean cooling system',
            'ai_high_load': 'GPU load high ({load}%)',
            'ai_ram_high': 'RAM loaded at {percent}%',
            'ai_ram_clean': 'Recommended: Memory cleanup',
            'ai_cpu_high': 'CPU load high ({load}%)',
            'ai_check_bg': 'Check background processes',
            'ai_learning': 'Collecting data about your system...',
            'ai_optimal': 'System running optimally',
            'ai_success_count': 'Successful optimizations: {count}',
            
            # Settings Dialog
            'settings_title': 'Settings',
            'language': 'Language',
            'select_language': 'Interface language',
            'auto_detect': 'Auto-detect',
            'language_change_note': 'Changes take effect immediately',
            'language_changed_title': 'Language Changed',
            'language_changed_msg': 'Interface language has been updated.',
            
            'ml_optimizer': 'ML Optimizer (Beta)',
            'enable_ml': 'Enable AI-powered optimization',
            'ml_beta_warning': 'Beta feature: May consume up to 50MB RAM',
            'ml_info': 'Learn optimal settings from your usage',
            'ml_local': 'Works 100% offline',
            'ml_lightweight': 'Uses <50MB RAM',
            'ml_learns': 'Learns from each optimization',
            
            'performance': 'Performance',
            'update_interval': 'Update interval',
            'interval_hint': 'Lower = more updates, higher CPU usage',
            
            'save': 'Save',
            'cancel': 'Cancel',
        },
        'ru': {
            # Window
            'window_title': 'PartMart Boost v{version}',
            
            # Navigation
            'nav_home': 'Главная',
            'nav_gpu': 'GPU',
            'nav_ram': 'RAM',
            'nav_settings': 'Настройки',
            
            # Metrics
            'metric_gpu_temp': 'Температура GPU',
            'metric_ram_usage': 'Использование RAM',
            'metric_cpu_load': 'Загрузка CPU',
            
            # System info
            'system_info_title': 'СИСТЕМНЫЕ ПОКАЗАТЕЛИ',
            'gpu_info': 'GPU: {name} | {clock}МГц | {temp}°C | Загрузка {load}%',
            'cpu_info': 'CPU: {cores} ядер | Загрузка {load}% | {freq}МГц',
            
            # Actions
            'action_gpu_control': 'Управление GPU',
            'action_gpu_desc': 'Оптимизация видеокарты',
            'action_ram_tuner': 'Настройка RAM',
            'action_ram_desc': 'XMP и очистка памяти',
            
            # Quick Boost
            'quick_boost': 'БЫСТРЫЙ БУСТ',
            'quick_boost_title': 'Быстрый буст',
            'quick_boost_msg': 'Оптимизировать систему?\n\nБудет выполнено:\n• Очистка RAM\n• Оптимизация приоритетов процессов',
            'quick_boost_success': 'Оптимизация завершена!\n\nПроверьте изменения в метриках.',
            'quick_boost_error': 'Не удалось выполнить оптимизацию:\n{error}',
            
            # GPU Page
            'gpu_control_title': 'УПРАВЛЕНИЕ GPU',
            'gpu_loading': 'Загрузка информации о GPU...',
            
            # Placeholders
            'coming_soon': 'Скоро',
            
            # Units
            'unit_celsius': '°C',
            'unit_percent': '%',
            'unit_gb': 'ГБ',
            'unit_mhz': 'МГц',
            
            # Messages
            'loading': 'Загрузка...',
            'error': 'Ошибка',
            'success': 'Успешно',
            'warning': 'Предупреждение',
            
            # CPU
            'cpu_cores': '{count} ядер',
            'cpu_temp': 'Темп: {temp}°C',
            'cpu_freq': '{freq}МГц',
            
            # Progress
            'load_progress': 'Загрузка: {value}%',
            
            # AI Recommendations
            'ai_temp_high': 'GPU температура выше средней на {diff}°C',
            'ai_temp_low': 'GPU температура ниже средней - отлично!',
            'ai_clean_cooling': 'Рекомендуется прочистить систему охлаждения',
            'ai_high_load': 'GPU загрузка высокая ({load}%)',
            'ai_ram_high': 'RAM загружен на {percent}%',
            'ai_ram_clean': 'Рекомендуется очистка памяти',
            'ai_cpu_high': 'CPU загрузка высокая ({load}%)',
            'ai_check_bg': 'Проверьте фоновые процессы',
            'ai_learning': 'Сбор данных о вашей системе...',
            'ai_optimal': 'Система работает оптимально',
            'ai_success_count': 'Успешных оптимизаций: {count}',
            
            # Settings Dialog
            'settings_title': 'Настройки',
            'language': 'Язык',
            'select_language': 'Язык интерфейса',
            'auto_detect': 'Автоопределение',
            'language_change_note': 'Изменения применяются немедленно',
            'language_changed_title': 'Язык изменён',
            'language_changed_msg': 'Язык интерфейса обновлён.',
            
            'ml_optimizer': 'ML Оптимизатор (Beta)',
            'enable_ml': 'Включить оптимизацию на основе ИИ',
            'ml_beta_warning': 'Beta-функция: может использовать до 50MB RAM',
            'ml_info': 'Изучает оптимальные настройки из вашего использования',
            'ml_local': 'Работает 100% офлайн',
            'ml_lightweight': 'Использует <50MB RAM',
            'ml_learns': 'Учится на каждой оптимизации',
            
            'performance': 'Производительность',
            'update_interval': 'Интервал обновления',
            'interval_hint': 'Меньше = чаще обновления, выше нагрузка на CPU',
            
            'save': 'Сохранить',
            'cancel': 'Отмена',
        }
    }
    
    def __init__(self, language: str = None):
        """Initialize localization"""
        if language is None:
            language = self._detect_system_language()
        
        self.current_language = language if language in self.SUPPORTED_LANGUAGES else self.DEFAULT_LANGUAGE
        self.translations = self.TRANSLATIONS[self.current_language]
    
    def _detect_system_language(self) -> str:
        """Auto-detect system language"""
        try:
            import locale
            system_lang = locale.getdefaultlocale()[0]
            if system_lang:
                # ru_RU -> ru
                lang_code = system_lang.split('_')[0].lower()
                if lang_code in self.SUPPORTED_LANGUAGES:
                    return lang_code
        except:
            pass
        return self.DEFAULT_LANGUAGE
    
    def get(self, key: str, **kwargs) -> str:
        """Get translated string"""
        text = self.translations.get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except:
                return text
        return text
    
    def set_language(self, language: str):
        """Change language"""
        if language in self.SUPPORTED_LANGUAGES:
            self.current_language = language
            self.translations = self.TRANSLATIONS[language]
            return True
        return False
    
    def get_current_language(self) -> str:
        """Get current language code"""
        return self.current_language

# Global instance
_localization = None

def init_localization(language: str = None):
    """Initialize global localization"""
    global _localization
    _localization = Localization(language)
    return _localization

def get_localization() -> Localization:
    """Get global localization instance"""
    global _localization
    if _localization is None:
        _localization = Localization()
    return _localization

def get_current_language() -> str:
    """Get current language code"""
    return get_localization().get_current_language()

def set_language(language: str):
    """Set global language"""
    loc = get_localization()
    return loc.set_language(language)

def t(key: str, **kwargs) -> str:
    """Shortcut for translation"""
    return get_localization().get(key, **kwargs)

if __name__ == "__main__":
    # Test
    loc = Localization('en')
    print(f"English: {loc.get('window_title', version='0.3.4')}")
    print(f"Settings: {loc.get('settings_title')}")
    print(f"ML: {loc.get('ml_optimizer')}")
    
    loc.set_language('ru')
    print(f"\nRussian: {loc.get('window_title', version='0.3.4')}")
    print(f"Settings: {loc.get('settings_title')}")
    print(f"ML: {loc.get('ml_optimizer')}")
    
    # Auto-detect
    auto_loc = Localization()
    print(f"\nAuto-detected: {auto_loc.get_current_language()}")
