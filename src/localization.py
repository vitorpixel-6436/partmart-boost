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
            'home': 'Home',
            'gpu_control': 'GPU Control',
            'ram_tuner': 'RAM Tuner',
            'settings': 'Settings',
            'preferences': 'Preferences',
            'about': 'About',
            
            # Metrics
            'gpu_temperature': 'GPU Temperature',
            'ram_usage': 'RAM Usage',
            'cpu_load': 'CPU Load',
            
            # System info
            'system_metrics': 'SYSTEM METRICS',
            'clock': 'Clock',
            'load': 'Load',
            
            # Actions
            'gpu_optimization': 'GPU optimization',
            'xmp_and_cleanup': 'XMP and memory cleanup',
            
            # Quick Boost
            'quick_boost': 'QUICK BOOST',
            'quick_boost_confirm': 'Optimize system?\n\nWill perform:\n• RAM cleanup\n• Process priority optimization',
            'optimization_complete': 'Optimization complete!\n\nCheck metrics for changes.',
            'optimization_failed': 'Failed to perform optimization',
            
            # Placeholders
            'coming_soon': 'Coming Soon',
            'loading': 'Loading...',
            
            # Messages
            'error': 'Error',
            'success': 'Success',
            'warning': 'Warning',
            
            # CPU
            'cpu_cores': '{count} cores',
            
            # About
            'about_text': 'PartMart Boost v{version}\n\nModern GPU/RAM optimization tool\nfor PartMart PCs\n\n© 2026 PartMart\nhttps://github.com/vitorpixel-6436/partmart-boost',
            
            # Settings Dialog
            'language': 'Language',
            'select_language': 'Interface language',
            'ml_optimizer': 'ML Optimizer',
            'enable_ml': 'Enable AI-powered optimization',
            'ml_warning': '⚠️ Beta feature: Uses up to 50MB RAM. Learns optimal settings from your system locally (no internet required).',
            'performance': 'Performance',
            'update_interval': 'Update interval',
            'save': 'Save',
            'cancel': 'Cancel',
        },
        'ru': {
            # Window
            'window_title': 'PartMart Boost v{version}',
            
            # Navigation
            'home': 'Главная',
            'gpu_control': 'Управление GPU',
            'ram_tuner': 'Настройка RAM',
            'settings': 'Настройки',
            'preferences': 'Настройки',
            'about': 'О программе',
            
            # Metrics
            'gpu_temperature': 'Температура GPU',
            'ram_usage': 'Использование RAM',
            'cpu_load': 'Загрузка CPU',
            
            # System info
            'system_metrics': 'СИСТЕМНЫЕ ПОКАЗАТЕЛИ',
            'clock': 'Частота',
            'load': 'Загрузка',
            
            # Actions
            'gpu_optimization': 'Оптимизация видеокарты',
            'xmp_and_cleanup': 'XMP и очистка памяти',
            
            # Quick Boost
            'quick_boost': 'БЫСТРЫЙ БУСТ',
            'quick_boost_confirm': 'Оптимизировать систему?\n\nБудет выполнено:\n• Очистка RAM\n• Оптимизация приоритетов процессов',
            'optimization_complete': 'Оптимизация завершена!\n\nПроверьте изменения в метриках.',
            'optimization_failed': 'Не удалось выполнить оптимизацию',
            
            # Placeholders
            'coming_soon': 'Скоро',
            'loading': 'Загрузка...',
            
            # Messages
            'error': 'Ошибка',
            'success': 'Успешно',
            'warning': 'Предупреждение',
            
            # CPU
            'cpu_cores': '{count} ядер' if '{count}' != '1' else '{count} ядро',
            
            # About
            'about_text': 'PartMart Boost v{version}\n\nСовременный инструмент оптимизации GPU/RAM\nдля компьютеров PartMart\n\n© 2026 PartMart\nhttps://github.com/vitorpixel-6436/partmart-boost',
            
            # Settings Dialog
            'language': 'Язык',
            'select_language': 'Язык интерфейса',
            'ml_optimizer': 'ML Оптимизатор',
            'enable_ml': 'Включить оптимизацию на основе ИИ',
            'ml_warning': '⚠️ Beta-функция: Использует до 50MB RAM. Изучает оптимальные настройки локально (интернет не требуется).',
            'performance': 'Производительность',
            'update_interval': 'Интервал обновления',
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
    print(f"Settings: {loc.get('settings')}")
    print(f"ML: {loc.get('ml_optimizer')}")
    
    loc.set_language('ru')
    print(f"\nRussian: {loc.get('window_title', version='0.3.4')}")
    print(f"Settings: {loc.get('settings')}")
    print(f"ML: {loc.get('ml_optimizer')}")
    
    # Auto-detect
    auto_loc = Localization()
    print(f"\nAuto-detected: {auto_loc.get_current_language()}")
