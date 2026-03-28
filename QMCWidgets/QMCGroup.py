from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLayout
from PyQt6.QtCore import Qt, QSize


class QMCGroup(QWidget):
    """Qt Midi Controller Section Group with styled header strip"""

    def __init__(self, parent=None, title=""):
        super().__init__(parent)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # Header strip
        self._header = QLabel(title)
        self._header.setObjectName("group_header")
        self._header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._header.setFixedHeight(22)
        self._main_layout.addWidget(self._header)

        # Content area
        self._content = QWidget()
        self._content.setObjectName("group_content")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(4, 4, 4, 4)
        self._content_layout.setSpacing(4)
        self._main_layout.addWidget(self._content, 1)

    @property
    def title(self):
        return self._header.text()

    @title.setter
    def title(self, val):
        self._header.setText(val)

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
