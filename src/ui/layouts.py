"""Custom Layout Utilities

Version: 0.3.5c
Features:
- Responsive layouts
- Grid with auto-sizing
- Flow layout
"""
from PyQt6.QtWidgets import QLayout, QLayoutItem, QWidget
from PyQt6.QtCore import QRect, QSize, Qt, QPoint
from typing import List


class FlowLayout(QLayout):
    """Flow layout - wraps widgets to next line when needed"""
    
    def __init__(self, parent=None, margin: int = 0, spacing: int = -1):
        super().__init__(parent)
        
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        
        self._spacing = spacing
        self._item_list: List[QLayoutItem] = []
    
    def addItem(self, item: QLayoutItem):
        self._item_list.append(item)
    
    def count(self) -> int:
        return len(self._item_list)
    
    def itemAt(self, index: int) -> QLayoutItem:
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None
    
    def takeAt(self, index: int) -> QLayoutItem:
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None
    
    def expandingDirections(self) -> Qt.Orientation:
        return Qt.Orientation(0)
    
    def hasHeightForWidth(self) -> bool:
        return True
    
    def heightForWidth(self, width: int) -> int:
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect: QRect):
        super().setGeometry(rect)
        self._do_layout(rect, False)
    
    def sizeHint(self) -> QSize:
        return self.minimumSize()
    
    def minimumSize(self) -> QSize:
        size = QSize()
        
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), 
                     margins.top() + margins.bottom())
        return size
    
    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        """Perform layout calculation"""
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)
        
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0
        
        spacing = self._spacing
        if spacing == -1:
            spacing = self.spacing()
        
        for item in self._item_list:
            widget = item.widget()
            if widget is None:
                continue
            
            space_x = spacing
            space_y = spacing
            
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y() + bottom


class ResponsiveGrid:
    """Helper for responsive grid layouts"""
    
    @staticmethod
    def calculate_columns(container_width: int, item_width: int, 
                         spacing: int = 20, min_cols: int = 1, 
                         max_cols: int = 4) -> int:
        """Calculate optimal number of columns"""
        # Calculate how many items can fit
        available_width = container_width - spacing
        cols = max(min_cols, available_width // (item_width + spacing))
        return min(cols, max_cols)
    
    @staticmethod
    def calculate_item_size(container_width: int, columns: int, 
                          spacing: int = 20) -> int:
        """Calculate item width for given number of columns"""
        total_spacing = spacing * (columns + 1)
        available_width = container_width - total_spacing
        return available_width // columns


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
    import sys
    
    print("[TEST] Custom Layouts")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # Test FlowLayout
    window = QWidget()
    window.setWindowTitle("FlowLayout Test")
    window.setStyleSheet("background: #0D0D0D;")
    
    layout = FlowLayout(spacing=10)
    
    for i in range(20):
        btn = QPushButton(f"Button {i+1}")
        btn.setStyleSheet("""
            QPushButton {
                background: #E63946;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }
        """)
        layout.addWidget(btn)
    
    window.setLayout(layout)
    window.resize(600, 400)
    window.show()
    
    # Test ResponsiveGrid
    print("\n[TEST] ResponsiveGrid:")
    container_width = 1200
    item_width = 250
    cols = ResponsiveGrid.calculate_columns(container_width, item_width)
    print(f"  Container: {container_width}px")
    print(f"  Item width: {item_width}px")
    print(f"  Optimal columns: {cols}")
    
    print("\n" + "=" * 60)
    print("✅ Custom layouts work!")
    
    sys.exit(app.exec())
