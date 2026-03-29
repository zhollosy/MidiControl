from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRect, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient


class _CustomSlider(QWidget):
    """Fully custom-painted vertical slider with controllable groove geometry."""

    valueChanged = pyqtSignal(int)

    HANDLE_HEIGHT = 20
    HANDLE_EXTEND = 4   # how far handle extends beyond groove on each side
    GROOVE_MARGIN_V = 10  # top/bottom margin so handle doesn't clip
    GROOVE_EXTEND_V = 6  # extra visual groove beyond travel range

    def __init__(self, parent=None, min_val=0, max_val=127, default=0,
                 indicator_color=None, groove_width=8):
        super().__init__(parent)

        self._min = min_val
        self._max = max_val
        self._value = default
        self._groove_width = groove_width
        self._indicator_color = QColor(indicator_color) if indicator_color else None
        self._dragging = False
        self._drag_offset = 0

        total_w = self._groove_width + 2 * self.HANDLE_EXTEND
        self.setFixedWidth(total_w)
        self.setMinimumHeight(60)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    def groove_rect(self):
        """Return the visual groove QRect in local widget coordinates."""
        gx = (self.width() - self._groove_width) // 2
        gy = self.GROOVE_MARGIN_V - self.GROOVE_EXTEND_V
        gh = self.height() - 2 * (self.GROOVE_MARGIN_V - self.GROOVE_EXTEND_V)
        return QRect(gx, gy, self._groove_width, gh)

    def _travel_range(self):
        """Return (top_y, bottom_y) for the handle travel area."""
        top = self.GROOVE_MARGIN_V
        bottom = self.height() - self.GROOVE_MARGIN_V
        return top, bottom

    def _handle_rect(self):
        handle_w = self._groove_width + 2 * self.HANDLE_EXTEND
        handle_x = (self.width() - handle_w) // 2
        handle_y = self._value_to_y() - self.HANDLE_HEIGHT // 2
        return QRect(handle_x, handle_y, handle_w, self.HANDLE_HEIGHT)

    def _value_to_y(self):
        top, bottom = self._travel_range()
        if self._max == self._min:
            return top
        ratio = (self._value - self._min) / (self._max - self._min)
        return int(bottom - ratio * (bottom - top))

    def _y_to_value(self, y):
        top, bottom = self._travel_range()
        ratio = (bottom - y) / max(bottom - top, 1)
        ratio = max(0.0, min(1.0, ratio))
        return int(round(self._min + ratio * (self._max - self._min)))

    # ── Properties ──

    def value(self):
        return self._value

    def setValue(self, val):
        val = max(self._min, min(self._max, int(val)))
        if val != self._value:
            self._value = val
            self.valueChanged.emit(val)
            self.update()

    def minimum(self):
        return self._min

    def setMinimum(self, val):
        self._min = val

    def maximum(self):
        return self._max

    def setMaximum(self, val):
        self._max = val

    @property
    def indicator_color(self):
        return self._indicator_color

    @indicator_color.setter
    def indicator_color(self, color):
        self._indicator_color = QColor(color) if color else None
        self.update()

    # ── Painting ──

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        gr = self.groove_rect()
        hr = self._handle_rect()

        # Groove
        p.setPen(QPen(QColor('#080808'), 1))
        p.setBrush(QColor('#0e0e0e'))
        p.drawRoundedRect(QRectF(gr), 3, 3)

        # Handle
        handle_grad = QLinearGradient(hr.left(), 0, hr.right(), 0)
        handle_grad.setColorAt(0.0, QColor('#3a3a3a'))
        handle_grad.setColorAt(0.45, QColor('#4a4a4a'))
        handle_grad.setColorAt(0.55, QColor('#4a4a4a'))
        handle_grad.setColorAt(1.0, QColor('#3a3a3a'))
        p.setPen(QPen(QColor('#333333'), 1))
        p.setBrush(QBrush(handle_grad))
        p.drawRoundedRect(QRectF(hr), 3, 3)

        # Indicator line
        if self._indicator_color:
            cy = hr.center().y()
            p.setPen(QPen(self._indicator_color, 2))
            p.drawLine(hr.left() + 3, cy, hr.right() - 3, cy)

        p.end()

    # ── Mouse interaction ──

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            hr = self._handle_rect()
            if hr.contains(event.pos()):
                self._dragging = True
                self._drag_offset = event.pos().y() - self._value_to_y()
            else:
                self.setValue(self._y_to_value(int(event.pos().y())))
                self._dragging = True
                self._drag_offset = 0

    def mouseMoveEvent(self, event):
        if self._dragging:
            y = int(event.pos().y()) - self._drag_offset
            self.setValue(self._y_to_value(y))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    def wheelEvent(self, event):
        delta = 1 if event.angleDelta().y() > 0 else -1
        self.setValue(self._value + delta)

    def sizeHint(self):
        w = self._groove_width + 2 * self.HANDLE_EXTEND
        return QSize(w, 200)


class QMCSlider(QWidget):
    """Qt Midi Controller Vertical Fader/Slider"""

    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None, label="", min_val=0, max_val=127,
                 default=0, indicator_color=None, groove_width=None,
                 show_label=True, show_value=True,
                 label_position='bottom', value_position='top'):
        super().__init__(parent)

        self._label_text = label
        gw = groove_width if groove_width is not None else 8

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._name_label = QLabel(label)
        self._name_label.setObjectName("name_label")
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_label.setVisible(show_label)

        self._value_label = QLabel(str(default))
        self._value_label.setObjectName("value_label")
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._value_label.setVisible(show_value)

        self._slider = _CustomSlider(min_val=min_val, max_val=max_val,
                                     default=default,
                                     indicator_color=indicator_color,
                                     groove_width=gw)

        # Top widgets
        if label_position == 'top':
            layout.addWidget(self._name_label, 0, Qt.AlignmentFlag.AlignHCenter)
        if value_position == 'top':
            layout.addWidget(self._value_label, 0, Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(self._slider, 1, Qt.AlignmentFlag.AlignHCenter)

        # Bottom widgets
        if value_position == 'bottom':
            layout.addWidget(self._value_label, 0, Qt.AlignmentFlag.AlignHCenter)
        if label_position == 'bottom':
            layout.addWidget(self._name_label, 0, Qt.AlignmentFlag.AlignHCenter)

        self._slider.valueChanged.connect(self._on_value_changed)

    def groove_rect_in(self, ancestor):
        """Return the groove QRect mapped to ancestor's coordinate space."""
        local_rect = self._slider.groove_rect()
        top_left = self._slider.mapTo(ancestor, local_rect.topLeft())
        return QRect(top_left, local_rect.size())

    def travel_rect_in(self, ancestor):
        """Return the handle travel QRect mapped to ancestor's coordinate space.
        This defines where the indicator line can be positioned."""
        top, bottom = self._slider._travel_range()
        gr = self._slider.groove_rect()
        local_rect = QRect(gr.x(), top, gr.width(), bottom - top)
        top_left = self._slider.mapTo(ancestor, local_rect.topLeft())
        return QRect(top_left, local_rect.size())

    @property
    def indicator_color(self):
        return self._slider.indicator_color

    @indicator_color.setter
    def indicator_color(self, color):
        self._slider.indicator_color = color

    def _on_value_changed(self, val):
        self._value_label.setText(str(val))
        self.valueChanged.emit(val)

    @property
    def value(self):
        return self._slider.value()

    @value.setter
    def value(self, val):
        self._slider.setValue(val)

    def sizeHint(self):
        return QSize(50, 200)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication, QHBoxLayout
    app = QApplication(sys.argv)
    w = QWidget()
    w.setStyleSheet("background-color: #3a3a3a; color: #d0d0d0;")
    lay = QHBoxLayout(w)
    for name in ("Volume", "C1", "Bright", "1", "2", "3", "4"):
        lay.addWidget(QMCSlider(label=name, default=64,
                                indicator_color="#d0d0d0", groove_width=20))
    w.show()
    sys.exit(app.exec())
