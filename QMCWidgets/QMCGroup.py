from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QPen, QColor


class _GroupHeader(QWidget):
    """Header strip with text and continuous line spacers on both sides.

    line_align='baseline' — line at the baseline of the text (for top headers).
    line_align='ascent'   — line at the ascent of the text (for bottom headers).
    """

    def __init__(self, text, line_align='baseline', parent=None):
        super().__init__(parent)
        self._text = text
        self._line_align = line_align
        self.setObjectName("group_header")
        self.setFixedHeight(22)

    def paintEvent(self, event):
        p = QPainter(self)
        fm = p.fontMetrics()
        text_w = fm.horizontalAdvance(self._text)
        total_w = self.width()
        gap = 6
        margin = 6

        text_x = (total_w - text_w) // 2
        text_y = (self.height() + fm.ascent() - fm.descent()) // 2

        # Text
        p.setPen(QColor('#d0d0d0'))
        p.drawText(text_x, text_y, self._text)

        # Line position
        if self._line_align == 'baseline':
            ly = text_y + fm.descent()
        else:
            ly = text_y - fm.ascent()

        line_pen = QPen(QColor('#555555'), 1)
        p.setPen(line_pen)

        left_end = text_x - gap
        right_start = text_x + text_w + gap

        if left_end > margin:
            p.drawLine(margin, ly, left_end, ly)
        if right_start < total_w - margin:
            p.drawLine(right_start, ly, total_w - margin, ly)

        p.end()


class QMCGroup(QWidget):
    """Qt Midi Controller Section Group with styled header strip.

    Parameters:
        title:           Header text.
        header_position: 'top' or 'bottom' — where the header sits.
    """

    def __init__(self, parent=None, title="", header_position='top'):
        super().__init__(parent)

        self._header_position = header_position

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # Header strip
        line_align = 'baseline' if header_position == 'top' else 'ascent'
        self._header = _GroupHeader(title, line_align=line_align)

        # Content area
        self._content = QWidget()
        self._content.setObjectName("group_content")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(4, 4, 4, 4)
        self._content_layout.setSpacing(4)

        if header_position == 'top':
            self._main_layout.addWidget(self._header)
            self._main_layout.addWidget(self._content, 1)
        else:
            self._main_layout.addWidget(self._content, 1)
            self._main_layout.addWidget(self._header)

    @property
    def title(self):
        return self._header._text

    @title.setter
    def title(self, val):
        self._header._text = val
        self._header.update()

    @property
    def content_layout(self):
        return self._content_layout

    def addWidget(self, widget):
        self._content_layout.addWidget(widget)

    def setContentLayout(self, layout: QLayout):
        # Remove old layout from content widget
        old = self._content.layout()
        if old is not None:
            while old.count():
                old.takeAt(0)
            from PyQt6.QtWidgets import QWidget as _QW
            _QW().setLayout(old)
        self._content.setLayout(layout)
        self._content_layout = layout

    def sizeHint(self):
        return QSize(100, 150)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication, QHBoxLayout
    from ._theme import D70_BODY
    from .QMCButton import QMCButton
    app = QApplication(sys.argv)
    w = QWidget()
    w.setStyleSheet(f"background-color: {D70_BODY};")
    lay = QHBoxLayout(w)
    grp = QMCGroup(title="CONTROL")
    grp.addWidget(QMCButton(text="Play"))
    grp.addWidget(QMCButton(text="Edit"))
    grp.addWidget(QMCButton(text="Solo", toggleable=True))
    lay.addWidget(grp)
    w.show()
    sys.exit(app.exec())
