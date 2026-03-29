"""Capture screenshots of all QMC widgets for documentation."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

app = QApplication(sys.argv)

DOC_DIR = os.path.dirname(__file__)
STYLE = "background-color: #3a3a3a; color: #d0d0d0;"
QSS_PATH = os.path.join(DOC_DIR, '..', 'QMCSurfaces', 'RolandD70.qss')
with open(QSS_PATH, 'r', encoding='utf-8') as f:
    D70_QSS = f.read()


def capture(widget, filename, pad=4):
    """Render widget to PNG."""
    widget.setStyleSheet(STYLE + D70_QSS)
    widget.show()
    widget.adjustSize()
    app.processEvents()
    app.processEvents()
    pixmap = widget.grab()
    path = os.path.join(DOC_DIR, filename)
    pixmap.save(path)
    widget.close()
    print(f"  Saved {filename}")


# ── QMCSlider ──
from QMCWidgets.QMCSlider import QMCSlider

# Default slider
w = QWidget()
lay = QHBoxLayout(w)
lay.setContentsMargins(8, 8, 8, 8)
s = QMCSlider(label="Volume", default=80)
lay.addWidget(s)
capture(w, "QMCSlider.png")

# Slider with options
w = QWidget()
lay = QHBoxLayout(w)
lay.setContentsMargins(8, 8, 8, 8)
lay.setSpacing(12)
s1 = QMCSlider(label="Default", default=64)
s2 = QMCSlider(label="Wide", default=100, groove_width=20, indicator_color="#d0d0d0")
s3 = QMCSlider(label="Top Lbl", default=40, indicator_color="#ff6622",
               label_position='top', value_position='bottom')
s4 = QMCSlider(default=80, groove_width=20, indicator_color="#d0d0d0",
               show_label=False, show_value=False)
lay.addWidget(s1)
lay.addWidget(s2)
lay.addWidget(s3)
lay.addWidget(s4)
capture(w, "QMCSlider_variants.png")

# ── QMCSliderGroup ──
from QMCWidgets.QMCSliderGroup import QMCSliderGroup

# Group with labels and ticks
w = QWidget()
w.setFixedSize(200, 220)
lay = QHBoxLayout(w)
lay.setContentsMargins(8, 8, 8, 8)
grp = QMCSliderGroup(labels=["Vol", "C1", "Bright"], label_position='top',
                      ticks=True, compact=True, tick_color='#d0d0d0')
for val in [100, 64, 64]:
    grp.addSlider(QMCSlider(default=val, indicator_color="#d0d0d0",
                            groove_width=20, show_label=False, show_value=False))
lay.addWidget(grp)
capture(w, "QMCSliderGroup.png")

# Group with title bar
w = QWidget()
w.setFixedSize(200, 220)
lay = QHBoxLayout(w)
lay.setContentsMargins(8, 8, 8, 8)
grp2 = QMCSliderGroup(top_label="TONE PALETTE", ticks=True)
for i in range(1, 5):
    grp2.addSlider(QMCSlider(label=str(i), default=64, indicator_color="#ff6622"))
lay.addWidget(grp2)
capture(w, "QMCSliderGroup_title.png")

# ── QMCButton ──
from QMCWidgets.QMCButton import QMCButton

w = QWidget()
lay = QHBoxLayout(w)
lay.setContentsMargins(8, 8, 8, 8)
lay.setSpacing(6)
lay.addWidget(QMCButton(text="Play"))
b_toggle = QMCButton(text="Solo", toggleable=True)
lay.addWidget(b_toggle)
b_on = QMCButton(text="Mute", toggleable=True)
b_on.setOn(True)
lay.addWidget(b_on)
capture(w, "QMCButton.png")

# Button variants — LED options and frame light
w = QWidget()
lay = QHBoxLayout(w)
lay.setContentsMargins(8, 8, 8, 8)
lay.setSpacing(6)
b1 = QMCButton(text="LED Btm", toggleable=True, led_position='bottom')
b1.setOn(True)
lay.addWidget(b1)
b2 = QMCButton(text="Wide LED", toggleable=True, led_size=0.5)
b2.setOn(True)
lay.addWidget(b2)
b3 = QMCButton(text="Green", toggleable=True, led_color='#00cc44',
               led_off_color='#003300', edge_light=True)
b3.setOn(True)
lay.addWidget(b3)
b4 = QMCButton(text="No Edge", toggleable=True, led_color='#00cc44',
               led_off_color='#003300')
b4.setOn(True)
lay.addWidget(b4)
capture(w, "QMCButton_variants.png")

# ── QMCDial ──
from QMCWidgets.QMCDial import QMCDial

w = QWidget()
lay = QHBoxLayout(w)
lay.setContentsMargins(8, 8, 8, 8)
lay.setSpacing(12)
d1 = QMCDial(label="Value")
d1.value = 64
d2 = QMCDial(label="Data Entry", endless=True)
lay.addWidget(d1)
lay.addWidget(d2)
capture(w, "QMCDial.png")

# ── QMCBendModWheel ──
from QMCWidgets.QMCBendModWheel import QMCBendModWheel

# 3:1 (default/spring)
w = QWidget()
lay = QHBoxLayout(w)
lay.setContentsMargins(8, 8, 8, 8)
lay.setSpacing(12)
bm1 = QMCBendModWheel(aspect_ratio=3)
bm1.setFixedSize(200, 140)
bm2 = QMCBendModWheel(aspect_ratio=2)
bm2.setFixedSize(140, 140)
bm3 = QMCBendModWheel(aspect_ratio=1)
bm3.setFixedSize(120, 140)
lay.addWidget(bm1)
lay.addWidget(bm2)
lay.addWidget(bm3)
capture(w, "QMCBendModWheel.png")

# ── QMCKeyboard ──
from QMCWidgets.QMCKeyboard import QMCKeyboard

w = QWidget()
lay = QHBoxLayout(w)
lay.setContentsMargins(4, 4, 4, 4)
kb = QMCKeyboard(start_note=48, end_note=84)
kb.setFixedSize(500, 100)
lay.addWidget(kb)
capture(w, "QMCKeyboard.png")

# ── QMCGroup ──
from QMCWidgets.QMCGroup import QMCGroup
from PyQt6.QtWidgets import QHBoxLayout as QHBox

# Header on top, buttons horizontal
w = QWidget()
lay = QHBoxLayout(w)
lay.setContentsMargins(8, 8, 8, 8)
grp = QMCGroup(title="CONTROL")
h_lay = QHBox()
h_lay.setSpacing(4)
h_lay.addWidget(QMCButton(text="Play"))
h_lay.addWidget(QMCButton(text="Edit"))
b = QMCButton(text="Solo", toggleable=True)
b.setOn(True)
h_lay.addWidget(b)
grp.setContentLayout(h_lay)
lay.addWidget(grp)
capture(w, "QMCGroup.png")

# Header on bottom
w = QWidget()
lay = QHBoxLayout(w)
lay.setContentsMargins(8, 8, 8, 8)
grp2 = QMCGroup(title="SECTION", header_position='bottom')
h_lay2 = QHBox()
h_lay2.setSpacing(4)
h_lay2.addWidget(QMCButton(text="Int 1", toggleable=True))
h_lay2.addWidget(QMCButton(text="Int 2", toggleable=True))
h_lay2.addWidget(QMCButton(text="Int 3", toggleable=True))
grp2.setContentLayout(h_lay2)
lay.addWidget(grp2)
capture(w, "QMCGroup_bottom.png")

print("\nAll screenshots captured.")
