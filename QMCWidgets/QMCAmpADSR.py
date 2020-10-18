import self as self
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from typing import overload


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

        self.targetSize = QtCore.QSize(127, 127)

        self.segments = [[0, 0]] * segment_num
        self._curve_pts = [[0, 0]] * (segment_num+1)

    def __getitem__(self, i):
        t_all = [p[0] for p in self.segments]
        t = t_all[:i]
        res = sum(t), self.segments[i - 1][1]
        res_scaled = (res[0] * self.targetSize.width()/sum(t_all),
                      res[1] * self.targetSize.height()/self.height_max)
        return res_scaled

    def __setitem__(self, key, value):
        self._curve_pts[key] = value

    def __len__(self):
        return len(self._curve_pts)

    def __delitem__(self, key):
        del self._curve_pts[key]
        del self.segments[key]

    def setSegment(self, i, delta_time, level):
        self.segments[i] = [delta_time, level]

    def line(self, i):
        return self[1], self[i+1]

    @property
    def width(self):
        return self[-1][0]


class QCurveData(QtGui.QPolygon):
    """ Curve data stored in QPolygon and some features more
        aa = QCurveData()
        aa.addPoint(0,0,'start')
        aa.addPoint(1,1,'attack')
        aa.attack
    """
    def __init__(self):
        super(QCurveData, self).__init__()
        self.point_names = []

        self._check_point_names()
        self.print_data()

    def addPoint(self, x: int, y: int, name:str=None):
        pt = QtCore.QPoint(x, y)
        self.append(pt)
        self._append_point_name(name)

    def addSegment(self, x: int, y: int, name:str=None):
        self.addPoint(self.last().x() + x,
                      self.last().y() + y,
                      name)

    def getPointByName(self, name:str):
        if name in self.point_names:
            i = self.point_names.index(name)
            return self[i]

    def print_data(self):
        print('----', self.size())
        for i in range(self.size()):
            print(i, f"{self.point_names[i]:<10}", self.point(i))

    def _append_point_name(self, name:str=None):
        if name:
            self.point_names.append(name)
            i = self.size() - 1
            setattr(self, name, self.getPointByName(name))
        else:
            i = len(self.point_names)
            point_name = f'point_{i:02d}'
            self.point_names.append(point_name)

    def _rename_attr(self, old_name:str, new_name:str):
        i = self.point_names.index(old_name)
        self.point_names[i] = new_name

        delattr(self, old_name)
        setattr(self, new_name, self.getPointByName(new_name))

    def _check_point_names(self):
        if self.size() == len(self.point_names): return
        for i in range(len(self.point_names), self.size()+1):
            self._append_point_name()



class CurveDataADSR(CurveData):
    segment_num = 4
    max_level = 127

    def __init__(self):
        super().__init__(CurveDataADSR.segment_num)

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
        sustain_time = self.width + self.segment_time_max / self.segment_num
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
        return QtCore.QPoint(0, 0)

    @property
    def attack_pt(self):
        return QtCore.QPoint(*self[1])

    @property
    def decay_pt(self):
        return QtCore.QPoint(*self[2])

    @property
    def sustain_pt(self):
        return QtCore.QPoint(*self[3])

    @property
    def release_pt(self):
        return QtCore.QPoint(*self[4])

    @property
    def end_pt(self):
        return QtCore.QPoint(*self[4])
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
        return QtCore.QLine(pt_1, pt_2)

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

    # TODO: Add ghost curve
    # TODO: Shade (gradient) curve area
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._ADSR_curve_data = CurveDataADSR()

        self.backgroundColor = QtGui.QColor(4, 21, 37)
        self.borderColor = Qt.black
        self.contentBorderColor = QtGui.QColor(74, 86, 100)
        self.lineColor = QtGui.QColor(59, 118, 168)
        self.pointColor = QtGui.QColor(255, 247, 197)
        self.gridColor = QtGui.QColor(74, 86, 100, 127)

        self.lineWidth = 3
        self.pointSize = 3
        self.borderWidth = 3
        self.contentBorderWidth = 2

        self.dragDistance = 10
        self.pt_hasFocus = False
        self.focus_pt = QtCore.QPoint()
        self.pt_dragging = None
        self.mouse_pressed = False

        self.setMouseTracking(True)
        self.setContentsMargins(20, 20, 20, 20)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        self.label = QLabel(self.tr('ADSR Amplifier'))
        self.label.setMouseTracking(True)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.label.setStyleSheet("""
                font: 12pt "Terminal" ;
                color: rgb(255, 255, 255);
        """)

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.mouse_pressed = True
        pos = self.contentTransform.map(a0.pos())
        in_range_data = self.inRangeCurvePoint_mapped(pos)
        if not self.pt_dragging and in_range_data['coord']:
            print('---------------')
            print(f'Clicked: {in_range_data["name"]}')
            print(pos)
            self.pt_dragging = in_range_data

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        pos = self.contentTransform.map(a0.pos())
        in_range_data = self.inRangeCurvePoint_mapped(pos)
        self.label.setText(f'{in_range_data["name"].capitalize()}\n [ {pos.x():>3},{pos.y():>3} ]')

        if in_range_data['coord']:
            self.pt_hasFocus = True
            self.focus_pt = in_range_data['coord']
            self.update()
        else:
            # update if hasFocus changed
            if self.pt_hasFocus:
                self.pt_hasFocus = False
                self.update()

        if self.mouse_pressed and self.pt_dragging is not None:
            pos_fixed = [min(self.contentsRect().width(),   max(0, pos.x())),
                         min(127,                           max(0, pos.y()))]
            pos_fixed = QtCore.QPoint(*pos_fixed)
            if self.pt_dragging['name'] == 'attack':
                self._ADSR_curve_data.attack = [pos_fixed.x(), pos_fixed.y()]
                # self.attack_level = pos_fixed.y()
            if self.pt_dragging['name'] == 'decay':
                self.decay_time = max(self.attack_time, pos_fixed.x() - self.attack_time)
                self.sustain_level = pos_fixed.y()
            if self.pt_dragging['name'] == 'sustain':
                self.decay_time = min(127, self.contentsRect().width() - pos_fixed.x())
                self.sustain_level = pos_fixed.y()
            self.update()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.mouse_pressed = False
        self.pt_dragging = None

    @property
    def contentTransform(self):
        content = self.contentsMargins()
        trs = QtGui.QTransform()
        trs.translate(-content.left(), self.geometry().height() - content.bottom())
        trs.scale(1, -1)
        return trs

    # region GETTERS
    @property
    def attack_time(self):
        return self._ADSR_curve_data.attack[0]

    @property
    def attack_level(self):
        return self._ADSR_curve_data.attack[1]

    @property
    def decay_time(self):
        return self._ADSR_curve_data.decay

    @property
    def sustain_time(self):
        return self._ADSR_curve_data.sustain[0]

    @property
    def sustain_level(self):
        return self._ADSR_curve_data.sustain

    @property
    def release_time(self):
        return self._ADSR_curve_data.release[0]
    # endregion

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

        if self.pt_hasFocus:
            self.drawRectangle(self.focus_pt)

    def drawPoint(self, pt, size=9, pattern=Qt.SolidLine):
        painter = QtGui.QPainter(self)

        content = self.contentsMargins()
        painter.translate(content.left(), self.geometry().height()-content.bottom())
        painter.scale(1, -1)

        painter.setPen(QtGui.QPen(self.pointColor, 2, pattern))

        rect = QtCore.QRect(0, 0, self.pointSize, self.pointSize)
        rect.moveCenter(pt)
        painter.drawRect(rect)
        painter.end()

    def drawLine(self, crv, pattern=Qt.SolidLine):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        content = self.contentsMargins()
        painter.translate(content.left(), self.geometry().height()-content.bottom())
        painter.scale(1, -1)

        painter.setPen(QtGui.QPen(self.lineColor, self.lineWidth, pattern))
        painter.drawLine(crv)
        painter.end()

    def drawRectangle(self, center_pt, size=11, pattern=Qt.SolidLine):
        trs = self.contentTransform.inverted()[0]
        center_pt = trs.map(center_pt)

        rect = QtCore.QRect()
        rect.setWidth(size)
        rect.setHeight(size)
        rect.moveCenter(center_pt)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(QtGui.QPen(self.pointColor, 1, pattern))
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

    def inRangeCurvePoint_mapped(self, pos, range=10):
        start_pt = self._ADSR_curve_data.start_pt
        attack_pt = self._ADSR_curve_data.attack_pt
        decay_pt = self._ADSR_curve_data.decay_pt
        sustain_pt = self._ADSR_curve_data.sustain_pt
        end_pt = self._ADSR_curve_data.end_pt

        start_offset = (start_pt - pos).manhattanLength()
        attack_offset = (attack_pt - pos).manhattanLength()
        decay_offset = (decay_pt  - pos).manhattanLength()
        sustain_offset = (sustain_pt - pos).manhattanLength()
        end_offset = (end_pt - pos).manhattanLength()

        data_dicts = ({'name': 'start', 'offset': start_offset, 'coord': start_pt},
                      {'name': 'attack', 'offset': attack_offset, 'coord': attack_pt},
                      {'name': 'decay', 'offset': decay_offset, 'coord': decay_pt},
                      {'name': 'sustain', 'offset': sustain_offset, 'coord': sustain_pt},
                      {'name': 'end', 'offset': end_offset, 'coord': end_pt})

        closest = sorted(data_dicts, key=lambda x: x['offset'])[0]

        if closest['offset'] < range:
            return closest
        else:
            return {'name': '', 'offset': None, 'coord': None}
