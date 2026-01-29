#!/usr/bin/env python3
"""Minimal UI Abstraction Layer

Version: 0.3.5d (package 3.9a, stage 5/5)

Lightweight UI factory to reduce PyQt6 dependency.

Package 3.9a Stage 5: New minimal UI layer for optimization.

Features:
- Lazy loading of PyQt6
- Centralized imports
- Minimal memory footprint
- Easy to add fallback (tkinter)
- Factory pattern
"""
import sys
from typing import Optional, Callable, Any, Dict


class UIFactory:
    """Minimal UI factory to reduce PyQt6 dependency
    
    Benefits:
    - Lazy loading: PyQt6 loaded only when UI needed
    - Centralized: All PyQt6 imports in one place
    - Minimal: Import only what's used
    - Extensible: Easy to add tkinter fallback
    - Fast: Faster startup, lower memory
    
    Usage:
        ui = UIFactory()
        button = ui.create_button("Click Me")
        label = ui.create_label("Hello")
        layout = ui.create_layout('vertical')
    """
    
    _instance: Optional['UIFactory'] = None
    
    def __init__(self):
        self._pyqt6_loaded = False
        self._widgets: Dict[str, Any] = {}
        self._layouts: Dict[str, Any] = {}
        print("[UIFactory] Initialized (PyQt6 not loaded yet)")
    
    @classmethod
    def get_instance(cls) -> 'UIFactory':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _ensure_pyqt6_widgets(self):
        """Lazy load PyQt6 widgets only when needed"""
        if not self._pyqt6_loaded:
            try:
                from PyQt6.QtWidgets import (
                    QWidget, QPushButton, QLabel, QCheckBox,
                    QVBoxLayout, QHBoxLayout, QGroupBox,
                    QLineEdit, QTextEdit, QComboBox,
                    QSlider, QProgressBar
                )
                from PyQt6.QtCore import Qt
                
                # Store widget classes
                self._widgets['QWidget'] = QWidget
                self._widgets['QPushButton'] = QPushButton
                self._widgets['QLabel'] = QLabel
                self._widgets['QCheckBox'] = QCheckBox
                self._widgets['QLineEdit'] = QLineEdit
                self._widgets['QTextEdit'] = QTextEdit
                self._widgets['QComboBox'] = QComboBox
                self._widgets['QSlider'] = QSlider
                self._widgets['QProgressBar'] = QProgressBar
                self._widgets['QGroupBox'] = QGroupBox
                
                # Store layout classes
                self._layouts['QVBoxLayout'] = QVBoxLayout
                self._layouts['QHBoxLayout'] = QHBoxLayout
                
                # Store Qt constants
                self._widgets['Qt'] = Qt
                
                self._pyqt6_loaded = True
                print("[UIFactory] PyQt6 widgets loaded")
            
            except ImportError as e:
                print(f"[UIFactory] PyQt6 not available: {e}")
                # Could fall back to tkinter here
                raise
    
    def is_available(self) -> bool:
        """Check if PyQt6 is available"""
        try:
            self._ensure_pyqt6_widgets()
            return True
        except ImportError:
            return False
    
    def create_widget(self, parent=None) -> Any:
        """Create basic widget"""
        self._ensure_pyqt6_widgets()
        return self._widgets['QWidget'](parent)
    
    def create_button(self, text: str = "", callback: Optional[Callable] = None, parent=None) -> Any:
        """Create button with minimal PyQt6 usage
        
        Args:
            text: Button text
            callback: Click callback function
            parent: Parent widget
        
        Returns:
            QPushButton instance
        """
        self._ensure_pyqt6_widgets()
        btn = self._widgets['QPushButton'](text, parent)
        if callback:
            btn.clicked.connect(callback)
        return btn
    
    def create_label(self, text: str = "", parent=None) -> Any:
        """Create label with minimal PyQt6 usage
        
        Args:
            text: Label text
            parent: Parent widget
        
        Returns:
            QLabel instance
        """
        self._ensure_pyqt6_widgets()
        return self._widgets['QLabel'](text, parent)
    
    def create_checkbox(self, text: str = "", checked: bool = False, parent=None) -> Any:
        """Create checkbox
        
        Args:
            text: Checkbox text
            checked: Initial state
            parent: Parent widget
        
        Returns:
            QCheckBox instance
        """
        self._ensure_pyqt6_widgets()
        cb = self._widgets['QCheckBox'](text, parent)
        cb.setChecked(checked)
        return cb
    
    def create_line_edit(self, text: str = "", placeholder: str = "", parent=None) -> Any:
        """Create line edit (text input)
        
        Args:
            text: Initial text
            placeholder: Placeholder text
            parent: Parent widget
        
        Returns:
            QLineEdit instance
        """
        self._ensure_pyqt6_widgets()
        edit = self._widgets['QLineEdit'](text, parent)
        if placeholder:
            edit.setPlaceholderText(placeholder)
        return edit
    
    def create_text_edit(self, text: str = "", read_only: bool = False, parent=None) -> Any:
        """Create text edit (multiline)
        
        Args:
            text: Initial text
            read_only: Read-only mode
            parent: Parent widget
        
        Returns:
            QTextEdit instance
        """
        self._ensure_pyqt6_widgets()
        edit = self._widgets['QTextEdit'](text, parent)
        edit.setReadOnly(read_only)
        return edit
    
    def create_combo_box(self, items: list = None, parent=None) -> Any:
        """Create combo box (dropdown)
        
        Args:
            items: List of items
            parent: Parent widget
        
        Returns:
            QComboBox instance
        """
        self._ensure_pyqt6_widgets()
        combo = self._widgets['QComboBox'](parent)
        if items:
            combo.addItems(items)
        return combo
    
    def create_slider(self, orientation: str = 'horizontal', min_val: int = 0, 
                     max_val: int = 100, value: int = 50, parent=None) -> Any:
        """Create slider
        
        Args:
            orientation: 'horizontal' or 'vertical'
            min_val: Minimum value
            max_val: Maximum value
            value: Initial value
            parent: Parent widget
        
        Returns:
            QSlider instance
        """
        self._ensure_pyqt6_widgets()
        Qt = self._widgets['Qt']
        orient = Qt.Orientation.Horizontal if orientation == 'horizontal' else Qt.Orientation.Vertical
        slider = self._widgets['QSlider'](orient, parent)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(value)
        return slider
    
    def create_progress_bar(self, min_val: int = 0, max_val: int = 100, value: int = 0, parent=None) -> Any:
        """Create progress bar
        
        Args:
            min_val: Minimum value
            max_val: Maximum value
            value: Initial value
            parent: Parent widget
        
        Returns:
            QProgressBar instance
        """
        self._ensure_pyqt6_widgets()
        pb = self._widgets['QProgressBar'](parent)
        pb.setMinimum(min_val)
        pb.setMaximum(max_val)
        pb.setValue(value)
        return pb
    
    def create_group_box(self, title: str = "", parent=None) -> Any:
        """Create group box
        
        Args:
            title: Group title
            parent: Parent widget
        
        Returns:
            QGroupBox instance
        """
        self._ensure_pyqt6_widgets()
        return self._widgets['QGroupBox'](title, parent)
    
    def create_layout(self, layout_type: str = 'vertical') -> Any:
        """Create layout
        
        Args:
            layout_type: 'vertical' or 'horizontal'
        
        Returns:
            QVBoxLayout or QHBoxLayout instance
        """
        self._ensure_pyqt6_widgets()
        if layout_type == 'vertical':
            return self._layouts['QVBoxLayout']()
        else:
            return self._layouts['QHBoxLayout']()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get UI factory statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            'pyqt6_loaded': self._pyqt6_loaded,
            'widgets_cached': len(self._widgets),
            'layouts_cached': len(self._layouts),
        }


# Singleton instance
_ui_factory = None

def get_ui_factory() -> UIFactory:
    """Get global UI factory instance"""
    global _ui_factory
    if _ui_factory is None:
        _ui_factory = UIFactory()
    return _ui_factory
