"""Capture ADSR and ADBSR widget screenshots for documentation."""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import QMCWidgets


def capture():
    app = QApplication(sys.argv)
    app.setStyle('windowsvista')

    # ADSR (standard)
    adsr = QMCWidgets.QMCAmpADSR()
    adsr.setFixedSize(500, 260)
    adsr.attack_time = 60
    adsr.attack_level = 127
    adsr.decay_time = 70
    adsr.sustain_level = 55
    adsr.release_time = 80
    adsr.curve_label.setText('ADSR Amplifier')
    adsr.show()

    # ADBSR (with breakpoint) - matching reference diagram
    adbsr = QMCWidgets.QMCAmpADSR(breakpoint=True)
    adbsr.setFixedSize(500, 260)
    adbsr.attack_time = 50
    adbsr.attack_level = 127
    adbsr.breakpoint_time = 50
    adbsr.breakpoint_level = 80
    adbsr.decay_time = 50
    adbsr.sustain_level = 55
    adbsr.release_time = 70
    adbsr.curve_label.setText('ADBSR Amplifier')
    adbsr.show()

    def grab():
        adsr.grab().save('doc/QMCAmpADSR.png')
        adbsr.grab().save('doc/QMCAmpADBSR.png')
        print('Saved doc/QMCAmpADSR.png')
        print('Saved doc/QMCAmpADBSR.png')
        app.quit()

    QTimer.singleShot(500, grab)
    app.exec()


if __name__ == '__main__':
    capture()
