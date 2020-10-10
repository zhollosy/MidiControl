import sys
from PyQt5.QtWidgets import *
# from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

import QMCWidgets

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.title = "Midi Control Widgets"
        self.top = 0
        self.left = 0
        self.width = 680
        self.height = 500

        layoutH_main = QHBoxLayout()

        self.ADSR_Widget = QMCWidgets.QMCAmpADSR()
        layoutH_main.addWidget(self.ADSR_Widget)

        widgets = [
            QDial,
            QLCDNumber,
            QLabel,
            QProgressBar,
            QPushButton,
            QSlider]

        for w in widgets:
            layoutH_main.addWidget(w())

        widget = QWidget()
        widget.setLayout(layoutH_main)

        self.setCentralWidget(widget)

    def InitWindow(self):
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.move(300, 300)


def main():

    app = QApplication(sys.argv)

    w = MainWindow()
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()