from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt


class CurveData(object):
    def __init__(self, number_of_segments):
        super().__init__()

        self.width = 255
        self.height = 127

        self._num_pt = number_of_segments + 1
        self._curve_pts = [[0,0]] * self._num_pt
        self._curve_pts.append( [self.width, 0] )

    def __getitem__(self, item):
        return self._curve_pts[item]

    def __setitem__(self, key, value):
        print('set val')
        self._curve_pts[key] = value

    def __len__(self):
        return len(self._curve_pts)

    def __delitem__(self, key):
        del self._curve_pts[key]

    # @property
    # def width(self):
    #     t = [p[0] for p in self._curve_pts]
    #     return sum(t)


class CurveData_ADSR(CurveData):
    def __init__(self):
        super().__init__(4)
        self.max_value = 127
        self.height_ratio = 127 / self.height

        self[0] = [0,0]
        self.attack_time = 20
        self.attack_level = 127
        self.decay_time = 20
        self.sustain_level = 80
        self.release_time = 20

    @property
    def attack_time(self):
        return self[1][0]

    @attack_time.setter
    def attack_time(self, val):
        self[1][0] = val

    @property
    def attack_level(self):
        return self[1][1]

    @attack_level.setter
    def attack_level(self, val):
        self[1][1] = val

    @property
    def sustain_time(self):
        st = self.width - self.attack_time - self.decay_time - self.release_time
        return st

    @property
    def attack_pt(self):
        return QtCore.QPoint( *self[1] )

    @property
    def decay_pt(self):
        pt_x = self.attack_pt.x() + self.decay_time
        pt_y = self.sustain_level
        return QtCore.QPoint( pt_x, pt_y )

    @property
    def sustain_pt(self):
        pt_x = self.decay_pt.x() + self.sustain_time
        pt_y = self.sustain_level
        return QtCore.QPoint( pt_x, pt_y )

    @property
    def release_pt(self):
        pt_x = self.width
        pt_y = 0
        return QtCore.QPoint( pt_x, pt_y )

    @property
    def attack_crv(self):
        pt_1 = QtCore.QPoint( *self[0] )   #TODO: use self[0] as start point
        pt_2 = self.attack_pt
        return QtCore.QLine(pt_1, pt_2)

    @property
    def decay_crv(self):
        pt_1 = self.attack_pt
        pt_2 = self.decay_pt
        return QtCore.QLine( pt_1, pt_2 )

    @property
    def sustain_crv(self):
        pt_1 = self.decay_pt
        pt_2 = self.sustain_pt
        return QtCore.QLine(pt_1, pt_2)

    @property
    def release_crv(self):
        pt_1 = self.sustain_pt
        pt_2 = self.release_pt
        return QtCore.QLine(pt_1, pt_2)


class QMCAmpADSR(QWidget):
    """Qt Midi Controller Amplifier/ADSR"""

    def __init__(self, *args, **kwargs):
        super().__init__()

        self._curve_data = CurveData_ADSR()

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

    @property
    def attack_time(self):
        return QtCore.QPoint(self._curve_data.attack_time)

    @property
    def attack_level(self):
        return QtCore.QPoint(self._curve_data.attack_level)

    @property
    def decay_time(self):
        return self._curve_data.decay_time

    @property
    def sustain_time(self):
        return self._curve_data.sustain_time

    @property
    def sustain_level(self):
        return self._curve_data.sustain_level

    @property
    def release_time(self):
        return self._curve_data.release_time

    @attack_time.setter
    def attack_time(self, val):
        self._curve_data.attack_time = val

    @attack_level.setter
    def attack_level(self, val):
        self._curve_data.attack_level = val

    @decay_time.setter
    def decay_time(self, val):
        self._curve_data.decay_time = val

    @sustain_level.setter
    def sustain_level(self, val):
        self._curve_data.sustain_level = val

    @release_time.setter
    def release_time(self, val):
        self._curve_data.release_time = val


    def sizeHint(self):
        return QtCore.QSize(100, 50)

    def paintEvent(self, e):
        geom = self.geometry()
        self._curve_data.width = geom.width()
        self._curve_data.height = geom.height()

        # background
        self.drawBackground()

        # adsr curve
        self.drawLine(self._curve_data.attack_crv)  # attack
        self.drawLine(self._curve_data.decay_crv)  # attack
        self.drawLine(self._curve_data.sustain_crv)  # attack
        self.drawLine(self._curve_data.release_crv)  # attack

        # adsr points
        self.drawPoint(self._curve_data.attack_pt)  # attack
        self.drawPoint(self._curve_data.decay_pt)  # attack
        self.drawPoint(self._curve_data.sustain_pt)  # attack
        self.drawPoint(self._curve_data.release_pt)  # attack

    def drawLine(self, crv, color=Qt.black, width=2, pattern=Qt.SolidLine):
        painter = QtGui.QPainter(self)
        # painter.scale(self.geometry().width()/self.width, self.geometry().height()/self.height)
        painter.translate(0, self.geometry().height())
        painter.scale( 1, -1 )
        # painter.setViewport(0, 0, self.geometry().width(), self.geometry().height())
        painter.setBrush(QtGui.QBrush(color, Qt.SolidPattern))
        painter.setPen(QtGui.QPen(color, width, pattern))
        painter.drawLine(crv)
        painter.end()

    def drawPoint(self, pt, color=Qt.black, width=10, pattern=Qt.SolidLine):
        painter = QtGui.QPainter(self)
        painter.translate(0, self.geometry().height())
        painter.scale( 1, -1 )
        painter.setBrush(QtGui.QBrush(color, Qt.SolidPattern))
        painter.setPen(QtGui.QPen(color, width, pattern))
        painter.drawPoint(pt)
        painter.end()

    def drawBackground(self):
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(Qt.black, 5, Qt.SolidLine))
        painter.setBrush(QtGui.QBrush(Qt.green, Qt.SolidPattern))
        painter.drawRect(0, 0, self.geometry().width(), self.geometry().height())

