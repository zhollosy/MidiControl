from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QSizePolicy, QSpacerItem)
from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtGui import QPainter, QPen, QColor


class _LabelBar(QWidget):
    """Label with horizontal line spacers on each side.

    *line_position*: 'bottom' draws lines at the bottom of the spacers,
                     'top' draws lines at the top.
    """

    def __init__(self, text, line_position='bottom', line_color='#555555',
                 parent=None):
        super().__init__(parent)
        self._text = text
        self._line_position = line_position
        self._line_color = QColor(line_color)
        self.setFixedHeight(18)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        fm = p.fontMetrics()
        text_w = fm.horizontalAdvance(self._text)
        total_w = self.width()
        gap = 6

        text_x = (total_w - text_w) // 2
        text_y = (self.height() + fm.ascent() - fm.descent()) // 2

        p.setPen(QColor('#d0d0d0'))
        p.drawText(text_x, text_y, self._text)

        line_pen = QPen(self._line_color, 1)
        p.setPen(line_pen)
        ly = self.height() - 1 if self._line_position == 'bottom' else 0

        left_end = text_x - gap
        right_start = text_x + text_w + gap

        if left_end > 8:
            p.drawLine(8, ly, left_end, ly)
        if right_start < total_w - 8:
            p.drawLine(right_start, ly, total_w - 8, ly)

        p.end()


class _TickOverlay(QWidget):
    """Transparent overlay that paints tick marks between slider grooves."""

    def __init__(self, group, parent=None):
        super().__init__(parent)
        self._group = group
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        widgets = self._group._widgets
        if len(widgets) < 2:
            return

        p = QPainter(self)
        p.setPen(QPen(QColor(self._group._tick_color), 2))

        for i in range(len(widgets) - 1):
            left_groove = widgets[i].groove_rect_in(self._group)
            right_groove = widgets[i + 1].groove_rect_in(self._group)
            left_travel = widgets[i].travel_rect_in(self._group)
            right_travel = widgets[i + 1].travel_rect_in(self._group)

            x1 = left_groove.right() + 5
            x2 = right_groove.left() - 4

            top = max(left_travel.top(), right_travel.top())
            bottom = min(left_travel.bottom(), right_travel.bottom())
            usable = bottom - top

            count = self._group._tick_count
            if count < 2 or usable <= 0:
                continue
            for t in range(count):
                y = top + int(t * usable / (count - 1))
                p.drawLine(x1, y, x2, y)

        p.end()


class QMCSliderGroup(QWidget):
    """A group of QMCSliders with optional labels and tick marks between grooves.

    Parameters:
        labels:         List of label strings rendered in a separate row.
        label_position: 'top' or 'bottom' — where the labels row appears.
        top_label:      Text for the top title bar (lines at bottom of spacers).
        bottom_label:   Text for the bottom title bar (lines at top of spacers).
        ticks:          Draw tick marks between slider grooves.
        tick_count:     Number of tick marks between each slider pair.
        tick_color:     Color of tick marks.
        line_color:     Color of the title bar separator lines.
        compact:        Center sliders with expanding spacers on each side.
    """

    def __init__(self, parent=None, *, labels=None, label_position='top',
                 top_label=None, bottom_label=None,
                 ticks=False, tick_count=9, tick_color='#d0d0d0',
                 line_color='#555555', compact=False):
        super().__init__(parent)
        self._ticks = ticks
        self._tick_count = tick_count
        self._tick_color = tick_color
        self._line_color = line_color
        self._compact = compact
        self._label_texts = labels or []
        self._label_position = label_position

        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(0, 0, 0, 0)
        self._outer.setSpacing(0)

        # Top title bar
        self._top_bar = None
        if top_label:
            self._top_bar = _LabelBar(top_label, line_position='bottom',
                                      line_color=line_color)
            self._outer.addWidget(self._top_bar)

        # Labels row (top position)
        self._labels_row = QHBoxLayout()
        self._labels_row.setContentsMargins(0, 0, 0, 0)
        self._labels_row.setSpacing(0)
        self._labels_widget = QWidget()
        self._labels_widget.setLayout(self._labels_row)
        self._labels_widget.setVisible(bool(self._label_texts))

        if self._label_position == 'top':
            self._outer.addWidget(self._labels_widget)

        # Slider row
        self._slider_row = QHBoxLayout()
        self._slider_row.setContentsMargins(0, 0, 0, 0)
        self._slider_row.setSpacing(0)

        if self._compact:
            self._slider_row.addSpacerItem(
                QSpacerItem(0, 0, QSizePolicy.Policy.Expanding,
                            QSizePolicy.Policy.Minimum))

        self._outer.addLayout(self._slider_row, 1)

        if self._label_position == 'bottom':
            self._outer.addWidget(self._labels_widget)

        # Bottom title bar
        self._bottom_bar = None
        if bottom_label:
            self._bottom_bar = _LabelBar(bottom_label, line_position='top',
                                         line_color=line_color)
            self._outer.addWidget(self._bottom_bar)

        self._widgets = []
        self._label_widgets = []

        # Pre-build label widgets
        for text in self._label_texts:
            lbl = QLabel(text)
            lbl.setObjectName("name_label")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._labels_row.addWidget(lbl)
            self._label_widgets.append(lbl)

        # Tick overlay
        self._tick_overlay = None
        if self._ticks:
            self._tick_overlay = _TickOverlay(self, self)

    def addSlider(self, slider):
        """Add a QMCSlider (or any widget) to the group."""
        # Remove trailing spacer before inserting
        if self._compact and self._widgets:
            last = self._slider_row.itemAt(self._slider_row.count() - 1)
            if last and last.spacerItem():
                self._slider_row.removeItem(last)

        self._slider_row.addWidget(slider)
        self._widgets.append(slider)

        # Re-add trailing spacer
        if self._compact:
            self._slider_row.addSpacerItem(
                QSpacerItem(0, 0, QSizePolicy.Policy.Expanding,
                            QSizePolicy.Policy.Minimum))

    def addGroup(self, group):
        """Add a nested QMCSliderGroup."""
        self.addSlider(group)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._tick_overlay:
            self._tick_overlay.setGeometry(self.rect())
            self._tick_overlay.raise_()


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    from QMCWidgets.QMCSlider import QMCSlider

    app = QApplication(sys.argv)

    w = QWidget()
    w.setStyleSheet("background-color: #2e2e2e; color: #d0d0d0;")

    layout = QHBoxLayout(w)

    grp = QMCSliderGroup(labels=["Volume", "C1", "Bright"],
                         label_position='top',
                         ticks=True, compact=True, tick_color='#d0d0d0')
    for val in [100, 64, 64]:
        grp.addSlider(QMCSlider(default=val, indicator_color="#d0d0d0",
                                groove_width=20,
                                show_label=False, show_value=False))
    layout.addWidget(grp)

    grp2 = QMCSliderGroup(top_label="TONE PALETTE", ticks=True)
    for i in range(1, 5):
        grp2.addSlider(QMCSlider(label=str(i), default=64,
                                 indicator_color="#ff6622"))
    layout.addWidget(grp2)

    w.setWindowTitle("QMCSliderGroup Test")
    w.resize(400, 300)
    w.show()
    sys.exit(app.exec())
