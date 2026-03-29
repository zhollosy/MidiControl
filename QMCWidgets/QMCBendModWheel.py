from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPointF, QRectF, QTimer
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QLinearGradient


class QMCBendModWheel(QWidget):
    """2-axis joystick: horizontal Bender (X) and vertical Modulation (Y).

    The stick rests at bottom-center by default.
    *spring_back* returns the stick to rest position on mouse release.
    *aspect_ratio* controls the pad shape: 3 (wide), 2, or 1 (square).
    """

    benderChanged = pyqtSignal(int)       # -64 … +63
    modulationChanged = pyqtSignal(int)    #   0 … 127

    # Bender range
    BEND_MIN = -64
    BEND_MAX = 63

    # Modulation range
    MOD_MIN = 0
    MOD_MAX = 127

    def __init__(self, parent=None, *, spring_back=False, aspect_ratio=3):
        super().__init__(parent)

        self._bender = 0          # center
        self._modulation = 0      # bottom
        self._spring_back = spring_back
        self._aspect_ratio = max(1, min(3, aspect_ratio))
        self._dragging = False

        # Spring animation
        self._spring_timer = QTimer(self)
        self._spring_timer.setInterval(16)  # ~60 fps
        self._spring_timer.timeout.connect(self._spring_step)

        # Visual constants
        self._pad_margin = 6
        self._stick_radius = 8

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(0)

        # Pad area (labels painted inside relative to pad_rect)
        self._pad = _PadArea(self)
        layout.addWidget(self._pad, 1)

    # ── Properties ──

    @property
    def bender(self):
        return self._bender

    @bender.setter
    def bender(self, val):
        val = max(self.BEND_MIN, min(self.BEND_MAX, int(val)))
        if val != self._bender:
            self._bender = val
            self.benderChanged.emit(val)
            self._pad.update()

    @property
    def modulation(self):
        return self._modulation

    @modulation.setter
    def modulation(self, val):
        val = max(self.MOD_MIN, min(self.MOD_MAX, int(val)))
        if val != self._modulation:
            self._modulation = val
            self.modulationChanged.emit(val)
            self._pad.update()

    @property
    def spring_back(self):
        return self._spring_back

    @spring_back.setter
    def spring_back(self, enabled):
        self._spring_back = bool(enabled)

    @property
    def aspect_ratio(self):
        return self._aspect_ratio

    @aspect_ratio.setter
    def aspect_ratio(self, ratio):
        self._aspect_ratio = max(1, min(3, ratio))
        self.updateGeometry()
        self._pad.update()

    # ── Spring animation ──

    def _spring_step(self):
        changed = False
        # Bender springs to 0
        if self._bender != 0:
            if abs(self._bender) <= 2:
                self._bender = 0
            else:
                self._bender = int(self._bender * 0.7)
            self.benderChanged.emit(self._bender)
            changed = True
        # Modulation springs to 0
        if self._modulation != 0:
            if self._modulation <= 2:
                self._modulation = 0
            else:
                self._modulation = int(self._modulation * 0.7)
            self.modulationChanged.emit(self._modulation)
            changed = True
        if changed:
            self._pad.update()
        else:
            self._spring_timer.stop()

    # ── Mouse handling (delegated from _PadArea) ──

    def _pad_pressed(self, pos):
        self._dragging = True
        self._spring_timer.stop()
        self._update_from_pad_pos(pos)

    def _pad_moved(self, pos):
        if self._dragging:
            self._update_from_pad_pos(pos)

    def _pad_released(self):
        self._dragging = False
        if self._spring_back:
            self._spring_timer.start()

    def _update_from_pad_pos(self, pos):
        pad_rect = self._pad.pad_rect()
        # Normalize X: -1..+1, Y: 0..1 (bottom=0, top=1)
        nx = (pos.x() - pad_rect.center().x()) / (pad_rect.width() / 2)
        ny = 1.0 - (pos.y() - pad_rect.top()) / pad_rect.height()
        nx = max(-1.0, min(1.0, nx))
        ny = max(0.0, min(1.0, ny))

        self.bender = int(round(nx * self.BEND_MAX)) if nx >= 0 else int(round(-nx * self.BEND_MIN))
        self.modulation = int(round(ny * self.MOD_MAX))

    def sizeHint(self):
        h = 160
        w = int(h * self._aspect_ratio) + 8
        return QSize(w, h)


class _PadArea(QWidget):
    """Internal: the paintable joystick pad area with labels."""

    LABEL_HEIGHT = 16  # space reserved for each label

    def __init__(self, owner: QMCBendModWheel):
        super().__init__(owner)
        self._owner = owner
        self.setMouseTracking(True)

    def pad_rect(self) -> QRectF:
        m = self._owner._pad_margin
        # Reserve space for top and bottom labels
        top_offset = self.LABEL_HEIGHT * 2 + 4  # two lines of text + gap
        bottom_offset = self.LABEL_HEIGHT + 4
        avail = QRectF(self.rect()).adjusted(m, top_offset, -m, -bottom_offset)
        # Enforce aspect ratio within available space
        target_ratio = self._owner._aspect_ratio
        current_ratio = avail.width() / max(avail.height(), 1)
        if current_ratio > target_ratio:
            new_w = avail.height() * target_ratio
            avail = QRectF(avail.center().x() - new_w / 2, avail.top(),
                           new_w, avail.height())
        elif current_ratio < target_ratio:
            new_h = avail.width() / target_ratio
            avail = QRectF(avail.left(), avail.center().y() - new_h / 2,
                           avail.width(), new_h)
        # Clamp so labels always have room
        min_top = top_offset
        max_bottom = self.height() - bottom_offset
        if avail.top() < min_top:
            avail.moveTop(min_top)
        if avail.bottom() > max_bottom:
            avail.setHeight(max_bottom - avail.top())
        return avail

    def _stick_pos(self) -> QPointF:
        pr = self.pad_rect()
        bender = self._owner._bender
        mod = self._owner._modulation

        # X: map -64..63 to left..right
        if bender >= 0:
            nx = bender / QMCBendModWheel.BEND_MAX
        else:
            nx = -bender / QMCBendModWheel.BEND_MIN
        # Y: map 0..127 to bottom..top
        ny = mod / QMCBendModWheel.MOD_MAX

        x = pr.center().x() + nx * (pr.width() / 2)
        y = pr.bottom() - ny * pr.height()
        return QPointF(x, y)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pr = self.pad_rect()

        # Pad background
        bg = QLinearGradient(pr.topLeft(), pr.bottomLeft())
        bg.setColorAt(0.0, QColor(20, 30, 40))
        bg.setColorAt(1.0, QColor(8, 14, 22))
        p.setPen(QPen(QColor(60, 60, 60), 1))
        p.setBrush(QBrush(bg))
        p.drawRoundedRect(pr, 4, 4)

        # Crosshair lines (center-x, bottom-y as rest indicators)
        crosshair_pen = QPen(QColor(50, 80, 110), 1, Qt.PenStyle.DotLine)
        p.setPen(crosshair_pen)
        cx = pr.center().x()
        p.drawLine(QPointF(cx, pr.top()), QPointF(cx, pr.bottom()))
        p.drawLine(QPointF(pr.left(), pr.bottom()), QPointF(pr.right(), pr.bottom()))

        # Stick
        sp = self._stick_pos()
        # Shadow
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 80))
        sr = self._owner._stick_radius
        p.drawEllipse(sp + QPointF(1, 1), sr, sr)
        # Stick body
        stick_grad = QLinearGradient(
            sp.x() - sr, sp.y() - sr, sp.x() + sr, sp.y() + sr)
        stick_grad.setColorAt(0.0, QColor(140, 140, 140))
        stick_grad.setColorAt(0.5, QColor(90, 90, 90))
        stick_grad.setColorAt(1.0, QColor(60, 60, 60))
        p.setBrush(QBrush(stick_grad))
        p.setPen(QPen(QColor(80, 80, 80), 1))
        p.drawEllipse(sp, sr, sr)
        # Highlight dot
        p.setBrush(QColor(180, 180, 180, 100))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(sp + QPointF(-2, -2), 3, 3)

        # Labels — aligned to pad_rect edges
        p.setPen(QColor('#d0d0d0'))
        fm = p.fontMetrics()

        # Top label: "MODULATION" + "▲"
        mod_text = "MODULATION"
        arrow_text = "\u25b2"
        mod_w = fm.horizontalAdvance(mod_text)
        arrow_w = fm.horizontalAdvance(arrow_text)
        label_cx = pr.center().x()
        mod_y = pr.top() - 4
        p.drawText(QPointF(label_cx - mod_w / 2, mod_y - fm.height()), mod_text)
        p.drawText(QPointF(label_cx - arrow_w / 2, mod_y), arrow_text)

        # Bottom label: "◄   BENDER   ►"
        bend_text = "\u25c4   BENDER   \u25ba"
        bend_w = fm.horizontalAdvance(bend_text)
        bend_y = pr.bottom() + fm.ascent() + 4
        p.drawText(QPointF(label_cx - bend_w / 2, bend_y), bend_text)

        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._owner._pad_pressed(event.position())

    def mouseMoveEvent(self, event):
        self._owner._pad_moved(event.position())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._owner._pad_released()


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication, QHBoxLayout
    app = QApplication(sys.argv)
    w = QWidget()
    w.setStyleSheet("background-color: #3a3a3a; color: #d0d0d0;")
    lay = QHBoxLayout(w)

    pad_3_1 = QMCBendModWheel(aspect_ratio=3, spring_back=True)
    pad_2_1 = QMCBendModWheel(aspect_ratio=2)
    pad_1_1 = QMCBendModWheel(aspect_ratio=1)

    lay.addWidget(pad_3_1)
    lay.addWidget(pad_2_1)
    lay.addWidget(pad_1_1)

    w.setWindowTitle("QMCBendModWheel Test")
    w.resize(700, 300)
    w.show()
    sys.exit(app.exec())
