from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt


class PointData(QtCore.QPoint):
    def __init__(self, time=0, value=0):
        super().__init__(time, value)
        self.time = time
        self.value = value


class CurveData(object):
    def __init__(self, segment_num):
        super().__init__()

        self.segment_time_max = 127
        self.height_max = 127

        self.targetSize = QtCore.QSize(127.0, 127.0)

        self.segments = [[0,0]] * segment_num
        self._curve_pts = [[0,0]] * (segment_num+1)

    def __getitem__(self, i):
        t_all = [p[0] for p in self.segments]
        t = t_all[:i]
        res = sum(t), self.segments[i - 1][1]
        res_scaled = res[0] * self.targetSize.width()/sum(t_all),\
                     res[1] * self.targetSize.height()/self.height_max
        return res_scaled

    def __setitem__(self, key, value):
        print('set val', key, value)
        self._curve_pts[key] = value

    def __len__(self):
        return len(self._curve_pts)

    def __delitem__(self, key):
        del self._curve_pts[key]
        del self.segments[key]

    def setSegment(self, i, time, level):
        self.segments[i] = [time, level]

    @property
    def line(self, i):
        return self[1], self[i+1]

    @property
    def width(self):
        return self[-1][0]


class CurveData_ADSR(CurveData):
    segment_num = 4
    max_level = 127

    def __init__(self):
        super().__init__(CurveData_ADSR.segment_num)
        # self.height_ratio = 127 / self.height

        self.attack = 20, 127
        self.decay = 35
        self.sustain = 80
        self.release = 20

    # region PROPS
    @property
    def attack(self) -> [int, int]:
        return self.segments[0]

    @attack.setter
    def attack(self, val):
        self.setSegment(0, *val)

    @property
    def decay(self) -> int:
        return self.segments[1][0]

    @decay.setter
    def decay(self, val):
        self.setSegment(1, val, self.sustain)

    @property
    def sustain(self) -> int:
        return self.segments[2][1]

    @sustain.setter
    def sustain(self, val):
        sustain_time= self.width + self.segment_time_max / self.segment_num
        self.setSegment(2, max(30, sustain_time), val)

    @property
    def release(self) -> int:
        return self.segments[3][0]

    @release.setter
    def release(self, val):
        self.setSegment(3, val, 0)
    # endregion

    # region POINTS
    @property
    def start_pt(self):
        return QtCore.QPoint( 0, 0 )

    @property
    def attack_pt(self):
        return QtCore.QPoint( *self[1] )

    @property
    def decay_pt(self):
        return QtCore.QPoint( *self[2] )

    @property
    def sustain_pt(self):
        return QtCore.QPoint( *self[3] )

    @property
    def release_pt(self):
        return QtCore.QPoint( *self[4] )
    # endregion

    # region CURVES
    @property
    def attack_crv(self):
        pt_1 = self.start_pt
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
    # endregion

class CurveView(QWidget):
    pass

class QMCAmpADSR(QWidget):
    """Qt Midi Controller Amplifier/ADSR"""

    #TODO: Add ghost curve
    #TODO: Shade (gradient) curve area
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._ADSR_curve_data = CurveData_ADSR()

        self.backgroundColor = QtGui.QColor(4,21,37)
        self.borderColor = Qt.black
        self.contentBorderColor = QtGui.QColor(74,86,100)
        self.lineColor = QtGui.QColor(59,118,168)
        self.pointColor = QtGui.QColor(255,247,197)
        self.gridColor = QtGui.QColor(74,86,100,127)

        self.lineWidth = 3
        self.pointSize = 3
        self.borderWidth = 3
        self.contentBorderWidth = 2

        self.dragDistance = 10

        self.setContentsMargins(20,20,20,20)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        self.label = QLabel(self.tr('ADSR Amplifier'))
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.label.setStyleSheet("""
                font: 12pt "Terminal" ;
                color: rgb(255, 255, 255);
        """)

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        content = self.contentsMargins()
        trs = QtGui.QTransform()
        trs.translate(-content.left(), self.geometry().height() - content.bottom())
        trs.scale(1, -1)
        pos = trs.map(a0.pos())

        attack_offset = (self._ADSR_curve_data.attack_pt - pos).manhattanLength()
        decay_offset  = (self._ADSR_curve_data.decay_pt  - pos).manhattanLength()
        sustain_offset = (self._ADSR_curve_data.sustain_pt - pos).manhattanLength()

        # isAttackClicked = click_offset.manhattanLength() < 10

        data = zip((attack_offset, decay_offset, sustain_offset), ('attack', 'decay', 'sustain'))
        closest = sorted(data, key=lambda x: x[0])[0]

        if closest[0] < 10:
            print ('---------------')
            print(f'Clicked: {closest[1]}')
            print(pos)

    #region GETTERS
    @property
    def attack_time(self):
        return self._ADSR_curve_data.attack[0]

    @property
    def attack_level(self):
        return self._ADSR_curve_data.attack[1]

    @property
    def decay_time(self):
        return self._ADSR_curve_data.decay[0]

    @property
    def sustain_time(self):
        return self._ADSR_curve_data.sustain[0]

    @property
    def sustain_level(self):
        return self._ADSR_curve_data.sustain[1]

    @property
    def release_time(self):
        return self._ADSR_curve_data.release[0]
    #endregion

    # region SETTERS
    @attack_time.setter
    def attack_time(self, val):
        self._ADSR_curve_data.attack[0] = val

    @attack_level.setter
    def attack_level(self, val):
        self._ADSR_curve_data.attack[1] = val

    @decay_time.setter
    def decay_time(self, val):
        self._ADSR_curve_data.decay = val

    @sustain_level.setter
    def sustain_level(self, val):
        self._ADSR_curve_data.sustain = val

    @release_time.setter
    def release_time(self, val):
        self._ADSR_curve_data.release = val
    # endregion


    def sizeHint(self):
        return QtCore.QSize(200, 167)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self._ADSR_curve_data.targetSize = self.contentsRect()


    def paintEvent(self, e):
        # background
        self.drawBackground()

        # adsr curve
        self.drawLine(self._ADSR_curve_data.attack_crv)  # attack
        self.drawLine(self._ADSR_curve_data.decay_crv)  # attack
        self.drawLine(self._ADSR_curve_data.sustain_crv)  # attack
        self.drawLine(self._ADSR_curve_data.release_crv)  # attack

        # adsr points
        self.drawPoint(self._ADSR_curve_data.start_pt)  # attack
        self.drawPoint(self._ADSR_curve_data.attack_pt)  # attack
        self.drawPoint(self._ADSR_curve_data.decay_pt)  # attack
        self.drawPoint(self._ADSR_curve_data.sustain_pt)  # attack
        self.drawPoint(self._ADSR_curve_data.release_pt)  # attack

    def drawLine(self, crv, pattern=Qt.SolidLine):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        content = self.contentsMargins()
        painter.translate(content.left(), self.geometry().height()-content.bottom())
        painter.scale( 1, -1 )

        painter.setPen(QtGui.QPen(self.lineColor, self.lineWidth, pattern))
        painter.drawLine(crv)
        painter.end()

    def drawPoint(self, pt, size=9, pattern=Qt.SolidLine):
        painter = QtGui.QPainter(self)

        content = self.contentsMargins()
        painter.translate(content.left(), self.geometry().height()-content.bottom())
        painter.scale( 1, -1 )

        painter.setPen(QtGui.QPen(self.pointColor, 2, pattern))

        rect = QtCore.QRect(0, 0, self.pointSize, self.pointSize)
        rect.moveCenter(pt)
        painter.drawRect(rect)
        painter.end()

    def drawBackground(self):
        painter = QtGui.QPainter(self)

        painter.setBrush(QtGui.QBrush(self.backgroundColor, Qt.SolidPattern))
        painter.setPen(QtGui.QPen(self.borderColor, self.borderWidth, Qt.SolidLine))
        painter.drawRect(0, 0, self.geometry().width(), self.geometry().height())

        painter.setBrush(QtGui.QBrush(self.backgroundColor, Qt.SolidPattern))
        painter.setPen(QtGui.QPen(self.contentBorderColor, self.contentBorderWidth, Qt.SolidLine))
        painter.drawRect(self.contentsRect())

        painter.setBrush(QtGui.QBrush(self.backgroundColor, Qt.SolidPattern))
        painter.setPen(QtGui.QPen(self.gridColor, 2, Qt.SolidLine))
        grid_pace = QtCore.QPoint(0, int(self.contentsRect().height()/4))
        painter.drawLine(self.contentsRect().bottomLeft() - grid_pace,
                         self.contentsRect().bottomRight() - grid_pace)
        painter.drawLine(self.contentsRect().bottomLeft() - grid_pace*2,
                         self.contentsRect().bottomRight() - grid_pace*2)
        painter.drawLine(self.contentsRect().bottomLeft() - grid_pace*3,
                         self.contentsRect().bottomRight() - grid_pace*3)
        painter.end()

