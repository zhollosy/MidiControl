from PyQt6.QtWidgets import QWidget
from PyQt6 import QtWidgets
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from ._theme import *

# Black key positions within an octave (C=0)
_BLACK_POSITIONS = {1, 3, 6, 8, 10}  # C#, D#, F#, G#, A#
_NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')


class QMCKeyboard(QWidget):
    """Qt Midi Controller Piano Keyboard with configurable note range"""

    noteOn = pyqtSignal(int, int)        # (note, velocity)
    noteOff = pyqtSignal(int)            # (note,)
    aftertouch = pyqtSignal(int, int)    # (note, pressure 0-127)

    def __init__(self, parent=None, start_note=28, end_note=103,
                 white_key_width=18, white_key_height=90,
                 aftertouch_pixels=64):
        super().__init__(parent)

        self._start_note = start_note
        self._end_note = end_note
        self._white_key_width = white_key_width
        self._white_key_height = white_key_height
        self._aftertouch_pixels = aftertouch_pixels
        self._active_notes = set()
        self._pressed_note = -1
        self._press_y = 0
        self._aftertouch_value = 0

        self._white_rects = []  # (note, QRect)
        self._black_rects = []  # (note, QRect)
        self._build_key_rects()

        self.setMouseTracking(True)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )

    @staticmethod
    def is_black_key(note):
        return (note % 12) in _BLACK_POSITIONS

    @staticmethod
    def note_name(note):
        octave = (note // 12) - 1
        return f"{_NOTE_NAMES[note % 12]}{octave}"

    def _white_keys_in_range(self):
        return [n for n in range(self._start_note, self._end_note + 1)
                if not self.is_black_key(n)]

    def _build_key_rects(self):
        self._white_rects = []
        self._black_rects = []

        white_keys = self._white_keys_in_range()
        if not white_keys:
            return

        w = self.width() or (len(white_keys) * self._white_key_width)
        h = self.height() or self._white_key_height
        ww = w / len(white_keys)
        bw = ww * 0.6
        bh = h * 0.6

        # Map each white key to its x position
        white_x = {}
        for i, note in enumerate(white_keys):
            x = int(i * ww)
            x_next = int((i + 1) * ww)
            white_x[note] = x
            self._white_rects.append((note, QtCore.QRect(x, 0, x_next - x, h)))

        # Black keys sit between their adjacent white keys
        for note in range(self._start_note, self._end_note + 1):
            if not self.is_black_key(note):
                continue
            prev_white = note - 1
            while prev_white >= self._start_note and self.is_black_key(prev_white):
                prev_white -= 1
            if prev_white in white_x:
                x = int(white_x[prev_white] + ww - bw / 2)
                self._black_rects.append((note, QtCore.QRect(x, 0, int(bw), int(bh))))

    def _note_at_pos(self, pos):
        # Check black keys first (they are on top)
        for note, rect in self._black_rects:
            if rect.contains(pos):
                return note
        for note, rect in self._white_rects:
            if rect.contains(pos):
                return note
        return -1

    def paintEvent(self, e):
        if not self._white_rects:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # White keys
        for note, rect in self._white_rects:
            if note in self._active_notes:
                grad = QtGui.QLinearGradient(QtCore.QPointF(rect.topLeft()), QtCore.QPointF(rect.bottomLeft()))
                grad.setColorAt(0.0, QtGui.QColor("#7799bb"))
                grad.setColorAt(0.3, QtGui.QColor(D70_KEY_PRESSED))
                grad.setColorAt(1.0, QtGui.QColor("#4a6a88"))
            else:
                grad = QtGui.QLinearGradient(QtCore.QPointF(rect.topLeft()), QtCore.QPointF(rect.bottomLeft()))
                grad.setColorAt(0.0, QtGui.QColor("#ffffff"))
                grad.setColorAt(0.05, QtGui.QColor("#f8f8f8"))
                grad.setColorAt(0.8, QtGui.QColor("#e0e0e0"))
                grad.setColorAt(0.95, QtGui.QColor("#c8c8c8"))
                grad.setColorAt(1.0, QtGui.QColor("#b0b0b0"))
            painter.setBrush(QtGui.QBrush(grad))
            painter.setPen(QtGui.QPen(QtGui.QColor(D70_KEY_BORDER), 1))
            painter.drawRect(rect)
            # Glossy highlight along left edge
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 90), 1))
            painter.drawLine(rect.left() + 1, rect.top() + 1,
                             rect.left() + 1, rect.bottom() - 2)

        # Black keys
        for note, rect in self._black_rects:
            if note in self._active_notes:
                grad = QtGui.QLinearGradient(QtCore.QPointF(rect.topLeft()), QtCore.QPointF(rect.bottomLeft()))
                grad.setColorAt(0.0, QtGui.QColor("#556677"))
                grad.setColorAt(0.4, QtGui.QColor(D70_KEY_PRESSED))
                grad.setColorAt(1.0, QtGui.QColor("#334455"))
            else:
                grad = QtGui.QLinearGradient(QtCore.QPointF(rect.topLeft()), QtCore.QPointF(rect.bottomLeft()))
                grad.setColorAt(0.0, QtGui.QColor("#444444"))
                grad.setColorAt(0.1, QtGui.QColor("#2a2a2a"))
                grad.setColorAt(0.7, QtGui.QColor("#181818"))
                grad.setColorAt(0.9, QtGui.QColor("#0a0a0a"))
                grad.setColorAt(1.0, QtGui.QColor("#222222"))
            painter.setBrush(QtGui.QBrush(grad))
            painter.setPen(QtGui.QPen(QtGui.QColor("#000"), 1))
            painter.drawRect(rect)
            # Glossy highlight along top and left edge
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 50), 1))
            painter.drawLine(rect.left() + 1, rect.top() + 1,
                             rect.right() - 1, rect.top() + 1)
            painter.drawLine(rect.left() + 1, rect.top() + 1,
                             rect.left() + 1, rect.bottom() - 4)

        painter.end()

    def _velocity_from_pos(self, pos, note):
        """Map vertical click position within the key to velocity 1-127."""
        # Find the key rect
        rects = self._black_rects if self.is_black_key(note) else self._white_rects
        for n, rect in rects:
            if n == note:
                ratio = (pos.y() - rect.top()) / max(rect.height(), 1)
                ratio = max(0.0, min(1.0, ratio))
                return max(1, int(round(ratio * 127)))
        return 100

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            note = self._note_at_pos(e.pos())
            if note >= 0:
                self._pressed_note = note
                self._press_y = e.pos().y()
                self._aftertouch_value = 0
                self._active_notes.add(note)
                vel = self._velocity_from_pos(e.pos(), note)
                self.noteOn.emit(note, vel)
                self.update()

    def mouseMoveEvent(self, e):
        if self._pressed_note >= 0:
            note = self._note_at_pos(e.pos())
            if note != self._pressed_note and note >= 0:
                # Moved to a different key
                self._active_notes.discard(self._pressed_note)
                self.noteOff.emit(self._pressed_note)
                self._pressed_note = note
                self._press_y = e.pos().y()
                self._aftertouch_value = 0
                self._active_notes.add(note)
                vel = self._velocity_from_pos(e.pos(), note)
                self.noteOn.emit(note, vel)
                self.update()
            else:
                # Same key — calculate aftertouch from downward drag
                dy = e.pos().y() - self._press_y
                if dy > 0:
                    pressure = min(127, int(round(dy / self._aftertouch_pixels * 127)))
                    if pressure != self._aftertouch_value:
                        self._aftertouch_value = pressure
                        self.aftertouch.emit(self._pressed_note, pressure)

    def mouseReleaseEvent(self, e):
        if self._pressed_note >= 0:
            if self._aftertouch_value > 0:
                self.aftertouch.emit(self._pressed_note, 0)
                self._aftertouch_value = 0
            self._active_notes.discard(self._pressed_note)
            self.noteOff.emit(self._pressed_note)
            self._pressed_note = -1
            self.update()

    def setNoteOn(self, note):
        self._active_notes.add(note)
        self.update()

    def setNoteOff(self, note):
        self._active_notes.discard(note)
        self.update()

    @property
    def start_note(self):
        return self._start_note

    @property
    def end_note(self):
        return self._end_note

    def resizeEvent(self, e):
        self._build_key_rects()

    def sizeHint(self):
        white_count = len(self._white_keys_in_range())
        return QSize(white_count * self._white_key_width + 1,
                     self._white_key_height)

    def minimumSizeHint(self):
        return QSize(200, 60)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # D-70: 76 keys, E1 (28) to G7 (103)
    kb = QMCKeyboard(start_note=28, end_note=103)
    kb.setWindowTitle("QMCKeyboard - 76 keys")
    kb.noteOn.connect(lambda n, v: print(f"NoteOn: {QMCKeyboard.note_name(n)} vel={v}"))
    kb.noteOff.connect(lambda n: print(f"NoteOff: {QMCKeyboard.note_name(n)}"))
    kb.aftertouch.connect(lambda n, p: print(f"Aftertouch: {QMCKeyboard.note_name(n)} pressure={p}"))
    kb.show()
    sys.exit(app.exec())
