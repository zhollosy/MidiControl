import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from ._theme import D70_LED_ON


class QMCDial(QWidget):
    """Qt Midi Controller Custom-Painted Rotary Knob"""

    valueChanged = pyqtSignal(int)

    # Arc range: 225° start to -45° (270° sweep, dead zone at bottom)
    ARC_START = 225
    ARC_SPAN = 270

    stepped = pyqtSignal(int)  # relative delta (+1/-1) for endless mode

    def __init__(self, parent=None, label="", min_val=0, max_val=127, endless=False):
        super().__init__(parent)

        self._min = min_val
        self._max = max_val
        self._value = 0
        self._endless = endless
        self._angle = 0.0  # current rotation angle for endless mode
        self._dragging = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        self._knob_area = _KnobArea(self)
        layout.addWidget(self._knob_area, 1)

        self._value_label = QLabel("0")
        self._value_label.setObjectName("value_label")
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._value_label)

        self._name_label = QLabel(label)
        self._name_label.setObjectName("name_label")
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._name_label)

    @property
    def endless(self):
        return self._endless

    @endless.setter
    def endless(self, val):
        self._endless = val
        self._knob_area.update()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if not self._endless:
            val = max(self._min, min(self._max, val))
        if val != self._value:
            self._value = val
            self._value_label.setText(str(val))
            self._knob_area.update()
            self.valueChanged.emit(val)

    def step(self, delta):
        """Apply a relative step (for endless mode). Emits stepped signal."""
        self._angle = (self._angle + delta * 15) % 360
        self._knob_area.update()
        self.stepped.emit(delta)

    def sizeHint(self):
        return QSize(80, 110)


class _KnobArea(QWidget):
    """Internal knob painting and mouse handling area."""

    def __init__(self, dial: QMCDial):
        super().__init__(dial)
        self._dial = dial
        self._last_y = 0
        self.setMinimumSize(40, 40)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        side = min(self.width(), self.height()) - 4
        x = (self.width() - side) // 2
        y = (self.height() - side) // 2
        rect = QtCore.QRectF(x, y, side, side)
        center = rect.center()
        radius = side / 2

        # Knob body
        grad = QtGui.QRadialGradient(center, radius)
        grad.setColorAt(0.0, QtGui.QColor("#606060"))
        grad.setColorAt(0.7, QtGui.QColor("#3a3a3a"))
        grad.setColorAt(1.0, QtGui.QColor("#2a2a2a"))
        painter.setBrush(QtGui.QBrush(grad))
        painter.setPen(QtGui.QPen(QtGui.QColor("#222"), 1.5))
        painter.drawEllipse(rect)

        # Value arc
        val_ratio = (self._dial._value - self._dial._min) / max(1, self._dial._max - self._dial._min)
        span = int(-val_ratio * QMCDial.ARC_SPAN * 16)
        arc_rect = rect.adjusted(3, 3, -3, -3)
        painter.setPen(QtGui.QPen(QtGui.QColor(D70_LED_ON), 2.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(arc_rect.toRect(), QMCDial.ARC_START * 16, span)

        # Position indicator line
        angle_deg = QMCDial.ARC_START - val_ratio * QMCDial.ARC_SPAN
        angle_rad = math.radians(angle_deg)
        inner_r = radius * 0.35
        outer_r = radius * 0.85
        x1 = center.x() + inner_r * math.cos(angle_rad)
        y1 = center.y() - inner_r * math.sin(angle_rad)
        x2 = center.x() + outer_r * math.cos(angle_rad)
        y2 = center.y() - outer_r * math.sin(angle_rad)
        painter.setPen(QtGui.QPen(QtGui.QColor("#eee"), 2))
        painter.drawLine(QtCore.QPointF(x1, y1), QtCore.QPointF(x2, y2))

        painter.end()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._dial._dragging = True
            self._last_y = e.pos().y()

    def mouseMoveEvent(self, e):
        if self._dial._dragging:
            dy = self._last_y - e.pos().y()
            self._last_y = e.pos().y()
            sensitivity = max(1, (self._dial._max - self._dial._min) / self.height())
            self._dial.value = self._dial._value + int(dy * sensitivity)

    def mouseReleaseEvent(self, e):
        self._dial._dragging = False

    def wheelEvent(self, e):
        delta = 1 if e.angleDelta().y() > 0 else -1
        self._dial.value = self._dial._value + delta


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication, QHBoxLayout
    from ._theme import D70_BODY
    app = QApplication(sys.argv)
    w = QWidget()
    w.setStyleSheet(f"background-color: {D70_BODY};")
    lay = QHBoxLayout(w)
    d = QMCDial(label="Value")
    d.value = 64
    lay.addWidget(d)
    d2 = QMCDial(label="Data")
    d2.value = 100
    lay.addWidget(d2)
    w.show()
    sys.exit(app.exec())
