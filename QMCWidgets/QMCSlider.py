from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QSize


class QMCSlider(QWidget):
    """Qt Midi Controller Vertical Fader/Slider"""

    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None, label="", min_val=0, max_val=127, default=0):
        super().__init__(parent)

        self._label_text = label

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        self._value_label = QLabel(str(default))
        self._value_label.setObjectName("value_label")
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._value_label)

        self._slider = QSlider(Qt.Orientation.Vertical)
        self._slider.setMinimum(min_val)
        self._slider.setMaximum(max_val)
        self._slider.setValue(default)
        layout.addWidget(self._slider, 1)

        self._name_label = QLabel(label)
        self._name_label.setObjectName("name_label")
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._name_label)

        self._slider.valueChanged.connect(self._on_value_changed)

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
    from ._theme import D70_BODY
    app = QApplication(sys.argv)
    w = QWidget()
    w.setStyleSheet(f"background-color: {D70_BODY};")
    lay = QHBoxLayout(w)
    for name in ("Volume", "C1", "Bright", "1", "2", "3", "4"):
        lay.addWidget(QMCSlider(label=name, default=64))
    w.show()
    sys.exit(app.exec())
