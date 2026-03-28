from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from ._theme import *


class QMCButton(QWidget):
    """Qt Midi Controller Styled Push Button with optional LED indicator"""

    clicked = pyqtSignal()
    toggled = pyqtSignal(bool)

    LED_RADIUS = 4

    def __init__(self, parent=None, text="", toggleable=False, led=True):
        super().__init__(parent)

        self._toggleable = toggleable
        self._show_led = led and toggleable
        self._is_on = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 8 if self._show_led else 2, 2, 2)
        layout.setSpacing(0)

        self._button = QPushButton(text)
        self._button.setCheckable(toggleable)
        self._button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #555, stop:0.1 {D70_BTN_FACE}, stop:1 #3a3a3a);
                color: {D70_TEXT};
                border: 1px solid {D70_BTN_BORDER};
                border-radius: 3px;
                padding: 4px 8px;
                font: 8pt 'Consolas';
            }}
            QPushButton:pressed {{
                background: {D70_BTN_PRESSED};
                border: 1px solid #333;
            }}
            QPushButton:checked {{
                background: {D70_BTN_PRESSED};
                border: 1px solid {D70_LED_ON};
            }}
        """)
        layout.addWidget(self._button)

        self._button.clicked.connect(self._on_clicked)

    def _on_clicked(self):
        if self._toggleable:
            self._is_on = self._button.isChecked()
            self.toggled.emit(self._is_on)
            self.update()
        self.clicked.emit()

    @property
    def is_on(self):
        return self._is_on

    def setOn(self, state: bool):
        self._is_on = state
        self._button.setChecked(state)
        self.update()

    @property
    def text(self):
        return self._button.text()

    @text.setter
    def text(self, val):
        self._button.setText(val)

    def paintEvent(self, e):
        super().paintEvent(e)
        if not self._show_led:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        color = QtGui.QColor(D70_LED_ON if self._is_on else D70_LED_OFF)
        painter.setBrush(QtGui.QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        cx = self.width() // 2
        cy = 5
        painter.drawEllipse(QtCore.QPoint(cx, cy), self.LED_RADIUS, self.LED_RADIUS)
        painter.end()

    def sizeHint(self):
        return QSize(60, 36 if not self._show_led else 42)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication, QHBoxLayout
    app = QApplication(sys.argv)
    w = QWidget()
    w.setStyleSheet(f"background-color: {D70_BODY};")
    lay = QHBoxLayout(w)
    lay.addWidget(QMCButton(text="Play"))
    lay.addWidget(QMCButton(text="Edit"))
    lay.addWidget(QMCButton(text="Solo", toggleable=True))
    lay.addWidget(QMCButton(text="Mute", toggleable=True, led=True))
    w.show()
    sys.exit(app.exec())
