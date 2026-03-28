import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QFrame, QLabel)
from PyQt6.QtCore import Qt, QSize

from QMCWidgets.QMCSlider import QMCSlider
from QMCWidgets.QMCButton import QMCButton
from QMCWidgets.QMCDial import QMCDial
from QMCWidgets.QMCGroup import QMCGroup
from QMCWidgets.QMCKeyboard import QMCKeyboard

_QSS_PATH = os.path.join(os.path.dirname(__file__), "RolandD70.qss")


class QMCSurfaceD70(QWidget):
    """Roland D-70 Super LA Synthesis — Surface Controller"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Roland D-70 Super LA Synthesis")
        self._load_stylesheet()
        self._setup_ui()

    def _load_stylesheet(self):
        with open(_QSS_PATH, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        # ── Logo bar ──
        logo_bar = QHBoxLayout()
        logo_label = QLabel("Roland")
        logo_label.setObjectName("logo_label")
        model_label = QLabel("D-70  SUPER LA SYNTHESIS")
        model_label.setObjectName("model_label")
        logo_bar.addWidget(logo_label)
        logo_bar.addWidget(model_label)
        logo_bar.addStretch()
        main_layout.addLayout(logo_bar)

        # ── Top panel (controls) ──
        top_panel = QHBoxLayout()
        top_panel.setSpacing(4)

        top_panel.addWidget(self._build_master_section())
        top_panel.addWidget(self._build_sliders_section())
        top_panel.addWidget(self._build_display_section(), 1)
        top_panel.addWidget(self._build_control_section())
        top_panel.addWidget(self._build_tone_zone_section())
        top_panel.addWidget(self._build_navigation_section())
        top_panel.addWidget(self._build_memory_section())
        top_panel.addWidget(self._build_value_section())

        main_layout.addLayout(top_panel)

        # ── Bottom panel (keyboard) ──
        bottom_panel = QHBoxLayout()
        bottom_panel.setSpacing(4)

        # Pitch bend placeholder
        bend_slider = QMCSlider(label="Bend", min_val=-64, max_val=63, default=0)
        bend_slider.setFixedWidth(50)
        bottom_panel.addWidget(bend_slider)

        # 76-key keyboard (E1=28 to G7=103)
        self.keyboard = QMCKeyboard(start_note=28, end_note=103)
        bottom_panel.addWidget(self.keyboard)

        main_layout.addLayout(bottom_panel)

    # ── Section builders ──

    def _build_master_section(self):
        grp = QMCGroup(title="MASTER")
        self.master_volume = QMCSlider(label="Volume", default=100)
        grp.addWidget(self.master_volume)
        return grp

    def _build_sliders_section(self):
        grp = QMCGroup(title="SLIDERS")
        layout = QHBoxLayout()
        layout.setSpacing(2)
        self.slider_c1 = QMCSlider(label="C1", default=64)
        self.slider_brightness = QMCSlider(label="Bright", default=64)
        layout.addWidget(self.slider_c1)
        layout.addWidget(self.slider_brightness)
        self.tone_palette_sliders = []
        for i in range(1, 5):
            s = QMCSlider(label=str(i), default=64)
            self.tone_palette_sliders.append(s)
            layout.addWidget(s)
        grp.setContentLayout(layout)
        return grp

    def _build_display_section(self):
        grp = QMCGroup(title="DISPLAY")
        # LCD placeholder
        lcd = QFrame()
        lcd.setObjectName("lcd_display")
        lcd.setFixedSize(280, 80)
        lcd_label = QLabel("Roland D-70", lcd)
        lcd_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lcd_label.setGeometry(0, 0, 280, 80)

        # Function buttons below LCD
        f_row = QHBoxLayout()
        for name in ("F1", "F2", "F3", "F4", "F5"):
            f_row.addWidget(QMCButton(text=name))

        layout = QVBoxLayout()
        layout.addWidget(lcd)
        layout.addLayout(f_row)
        layout.addStretch()
        grp.setContentLayout(layout)
        return grp

    def _build_control_section(self):
        grp = QMCGroup(title="CONTROL")
        grid = QGridLayout()
        grid.setSpacing(2)

        row0 = ["Play", "Edit", "PCM Card", "Solo"]
        row1 = ["Porta", "Release", "Cutoff", "Reso", "Attack"]
        row2 = ["Level", "Pan", "Tuning"]
        row3 = ["ToneDisp", "MIDI", "EFX/CTRL"]

        for col, name in enumerate(row0):
            grid.addWidget(QMCButton(text=name), 0, col)
        for col, name in enumerate(row1):
            grid.addWidget(QMCButton(text=name, toggleable=True), 1, col)
        for col, name in enumerate(row2):
            grid.addWidget(QMCButton(text=name, toggleable=True), 2, col)
        for col, name in enumerate(row3):
            grid.addWidget(QMCButton(text=name), 3, col)

        grp.setContentLayout(grid)
        return grp

    def _build_tone_zone_section(self):
        grp = QMCGroup(title="TONE / ZONE")
        grid = QGridLayout()
        grid.setSpacing(2)

        for i in range(1, 5):
            grid.addWidget(QMCButton(text=f"Zone {i}", toggleable=True), 0, i - 1)

        misc = ["Part", "User"]
        for col, name in enumerate(misc):
            grid.addWidget(QMCButton(text=name, toggleable=True), 1, col)

        grp.setContentLayout(grid)
        return grp

    def _build_navigation_section(self):
        grp = QMCGroup(title="NAVIGATION")
        grid = QGridLayout()
        grid.setSpacing(2)

        grid.addWidget(QMCButton(text="Exit"), 0, 0)
        grid.addWidget(QMCButton(text="\u25b2"), 0, 1)  # ▲
        grid.addWidget(QMCButton(text="DEC"), 0, 2)
        grid.addWidget(QMCButton(text="\u25c4"), 1, 0)  # ◄
        grid.addWidget(QMCButton(text="\u25bc"), 1, 1)  # ▼
        grid.addWidget(QMCButton(text="\u25ba"), 1, 2)  # ►
        grid.addWidget(QMCButton(text="INC"), 1, 3)
        grid.addWidget(QMCButton(text="Cmd"), 2, 0)
        grid.addWidget(QMCButton(text="Write"), 2, 1)
        grid.addWidget(QMCButton(text="Enter"), 2, 2)

        grp.setContentLayout(grid)
        return grp

    def _build_memory_section(self):
        grp = QMCGroup(title="MEMORY")
        grid = QGridLayout()
        grid.setSpacing(2)

        # Mode row
        for col, name in enumerate(["Perf", "Patch", "Tone"]):
            grid.addWidget(QMCButton(text=name, toggleable=True), 0, col)

        # Source row
        for col, name in enumerate(["A", "B", "INT", "CARD"]):
            grid.addWidget(QMCButton(text=name, toggleable=True), 1, col)

        # Bank row
        for i in range(1, 9):
            grid.addWidget(QMCButton(text=str(i)), 2, i - 1)

        grp.setContentLayout(grid)
        return grp

    def _build_value_section(self):
        grp = QMCGroup(title="VALUE")
        self.value_dial = QMCDial(label="Data Entry")
        self.value_dial.value = 64
        grp.addWidget(self.value_dial)
        return grp

    def sizeHint(self):
        return QSize(1400, 500)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setStyle('windowsvista')
    surface = QMCSurfaceD70()
    surface.show()
    sys.exit(app.exec())
