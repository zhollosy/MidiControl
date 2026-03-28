from PyQt6.QtWidgets import QWidget
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from ._theme import *

# Black key positions within an octave (C=0)
_BLACK_POSITIONS = {1, 3, 6, 8, 10}  # C#, D#, F#, G#, A#
_NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')


class QMCKeyboard(QWidget):
    """Qt Midi Controller Piano Keyboard with configurable note range"""

    noteOn = pyqtSignal(int, int)   # (note, velocity)
    noteOff = pyqtSignal(int)       # (note,)

    def __init__(self, parent=None, start_note=28, end_note=103,
                 white_key_width=18, white_key_height=90):
        super().__init__(parent)

        self._start_note = start_note
        self._end_note = end_note
        self._white_key_width = white_key_width
        self._white_key_height = white_key_height
        self._active_notes = set()
        self._pressed_note = -1

        self._white_rects = []  # (note, QRect)
        self._black_rects = []  # (note, QRect)
        self._build_key_rects()

        self.setMouseTracking(True)

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
        ww = self._white_key_width
        wh = self._white_key_height
        bw = int(ww * 0.6)
        bh = int(wh * 0.6)

        # Map each white key to its x position
        white_x = {}
        for i, note in enumerate(white_keys):
            x = i * ww
            white_x[note] = x
            self._white_rects.append((note, QtCore.QRect(x, 0, ww, wh)))

        # Black keys sit between their adjacent white keys
        for note in range(self._start_note, self._end_note + 1):
            if not self.is_black_key(note):
                continue
            # Black key sits to the right of the previous white key
            prev_white = note - 1
            while prev_white >= self._start_note and self.is_black_key(prev_white):
                prev_white -= 1
            if prev_white in white_x:
                x = white_x[prev_white] + ww - bw // 2
                self._black_rects.append((note, QtCore.QRect(x, 0, bw, bh)))

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
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # White keys
        for note, rect in self._white_rects:
            if note in self._active_notes:
                painter.setBrush(QtGui.QBrush(QtGui.QColor(D70_KEY_PRESSED)))
            else:
                painter.setBrush(QtGui.QBrush(QtGui.QColor(D70_KEY_WHITE)))
            painter.setPen(QtGui.QPen(QtGui.QColor(D70_KEY_BORDER), 1))
            painter.drawRect(rect)

        # Black keys
        for note, rect in self._black_rects:
            if note in self._active_notes:
                painter.setBrush(QtGui.QBrush(QtGui.QColor(D70_KEY_PRESSED)))
            else:
                painter.setBrush(QtGui.QBrush(QtGui.QColor(D70_KEY_BLACK)))
            painter.setPen(QtGui.QPen(QtGui.QColor("#000"), 1))
            painter.drawRect(rect)

        painter.end()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            note = self._note_at_pos(e.pos())
            if note >= 0:
                self._pressed_note = note
                self._active_notes.add(note)
                self.noteOn.emit(note, 100)
                self.update()

    def mouseMoveEvent(self, e):
        if self._pressed_note >= 0:
            note = self._note_at_pos(e.pos())
            if note != self._pressed_note and note >= 0:
                self._active_notes.discard(self._pressed_note)
                self.noteOff.emit(self._pressed_note)
                self._pressed_note = note
                self._active_notes.add(note)
                self.noteOn.emit(note, 100)
                self.update()

    def mouseReleaseEvent(self, e):
        if self._pressed_note >= 0:
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

    def sizeHint(self):
        white_count = len(self._white_keys_in_range())
        return QSize(white_count * self._white_key_width + 1,
                     self._white_key_height)

    def minimumSizeHint(self):
        return self.sizeHint()


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # D-70: 76 keys, E1 (28) to G7 (103)
    kb = QMCKeyboard(start_note=28, end_note=103)
    kb.setWindowTitle("QMCKeyboard - 76 keys")
    kb.noteOn.connect(lambda n, v: print(f"NoteOn: {QMCKeyboard.note_name(n)} vel={v}"))
    kb.noteOff.connect(lambda n: print(f"NoteOff: {QMCKeyboard.note_name(n)}"))
    kb.show()
    sys.exit(app.exec())
