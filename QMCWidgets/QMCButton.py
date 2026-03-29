from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRectF, QPointF
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QLinearGradient,
                         QRadialGradient)


class _ButtonBody(QWidget):
    """Thin hardware-style button strip with embedded LED slit."""

    BODY_HEIGHT = 12

    def __init__(self, parent=None, show_led=False, led_size=0.2,
                 led_position='top', led_color='#cc0000', led_off_color='#330000',
                 edge_light=False):
        super().__init__(parent)
        self._show_led = show_led
        self._led_size = max(0.1, min(1.0, led_size))
        self._led_position = led_position
        self._led_color = QColor(led_color)
        self._led_off_color = QColor(led_off_color)
        self._edge_light = edge_light
        self._is_on = False
        self._pressed = False
        self.setFixedHeight(self.BODY_HEIGHT)

    def paintEvent(self, event):
        p = QPainter(self)
        w = self.width()
        h = self.height()
        rect = QRectF(0, 0, w, h)

        # Body — sharp gradient: lighter top, darker bottom
        if self._pressed:
            body_color = QColor("#1e1e1e")
        else:
            body_grad = QLinearGradient(0, 0, 0, h)
            body_grad.setColorAt(0.0, QColor("#666666"))
            body_grad.setColorAt(0.05, QColor("#4a4a4a"))
            body_grad.setColorAt(0.3, QColor("#2a2a2a"))
            body_grad.setColorAt(1.0, QColor("#111111"))
            body_color = body_grad

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(body_color))
        p.drawRect(rect)

        # Border
        border_color = QColor("#333333")
        if self._edge_light:
            border_color = self._led_color
        p.setPen(QPen(border_color, 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(rect.adjusted(0.5, 0.5, -0.5, -0.5))

        # LED slit
        if self._show_led:
            led_w = max(4, w * self._led_size)
            led_x1 = (w - led_w) / 2
            led_x2 = led_x1 + led_w

            if self._led_position == 'top':
                led_y = 3
            else:
                led_y = h - 3

            led_center = QPointF(w / 2, led_y)

            if self._is_on:
                led_color = self._led_color
                # Glow
                p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                r, g, b = led_color.red(), led_color.green(), led_color.blue()
                glow = QRadialGradient(led_center, led_w * 0.9)
                glow.setColorAt(0.0, QColor(r, g, b, 100))
                glow.setColorAt(0.4, QColor(r, g, b, 40))
                glow.setColorAt(1.0, QColor(r, g, b, 0))
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(glow))
                p.drawEllipse(led_center, led_w * 0.8, led_w * 0.5)
                p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            else:
                led_color = self._led_off_color

            p.setPen(QPen(led_color, 2))
            p.drawLine(QPointF(led_x1, led_y), QPointF(led_x2, led_y))

        p.end()


class QMCButton(QWidget):
    """Qt Midi Controller hardware-style button with label above and LED slit.

    Parameters:
        text:          Button label text (displayed above the body).
        toggleable:    Enable toggle mode.
        led:           Show LED slit when toggleable.
        led_size:      LED width as fraction of button width (0.1-1.0).
        led_position:  'top' or 'bottom' — where the LED slit sits.
        led_color:     LED on color (default red).
        led_off_color: LED off color.
        edge_light:   Tint border with LED color.
    """

    clicked = pyqtSignal()
    toggled = pyqtSignal(bool)

    BUTTON_WIDTH = 54

    def __init__(self, parent=None, text="", toggleable=False, led=True,
                 led_size=0.2, led_position='top', led_color='#cc0000',
                 led_off_color='#330000', edge_light=False):
        super().__init__(parent)

        self._toggleable = toggleable
        self._show_led = led and toggleable

        self.setFixedWidth(self.BUTTON_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        # Label above button
        self._label = QLabel(text)
        self._label.setObjectName("button_label")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

        # Thin button body
        self._body = _ButtonBody(
            show_led=self._show_led, led_size=led_size,
            led_position=led_position, led_color=led_color,
            led_off_color=led_off_color, edge_light=edge_light)
        layout.addWidget(self._body)

    # ── Properties ──

    @property
    def is_on(self):
        return self._body._is_on

    def setOn(self, state: bool):
        self._body._is_on = state
        self._body.update()

    @property
    def text(self):
        return self._label.text()

    @text.setter
    def text(self, val):
        self._label.setText(val)

    # ── Mouse interaction ──

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._body._pressed = True
            self._body.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._body._pressed = False
            if self.rect().contains(event.pos()):
                if self._toggleable:
                    self._body._is_on = not self._body._is_on
                    self.toggled.emit(self._body._is_on)
                self.clicked.emit()
            self._body.update()

    def sizeHint(self):
        return QSize(self.BUTTON_WIDTH, 36)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout
    app = QApplication(sys.argv)
    w = QWidget()
    w.setStyleSheet("background-color: #3a3a3a; color: #d0d0d0;")
    lay = QHBoxLayout(w)
    lay.addWidget(QMCButton(text="Play"))
    lay.addWidget(QMCButton(text="Edit", toggleable=True, led_position='bottom'))
    b = QMCButton(text="Solo", toggleable=True, led_size=0.4)
    lay.addWidget(b)
    b2 = QMCButton(text="Mute", toggleable=True, edge_light=True)
    b2.setOn(True)
    lay.addWidget(b2)
    w.show()
    sys.exit(app.exec())
