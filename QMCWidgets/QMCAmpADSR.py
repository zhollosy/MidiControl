from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from typing import overload


class PointData(QtCore.QPoint):
    def __init__(self, time=0, value=0):
        super().__init__(time, value)
        self.time = time
        self.value = value
    
    @property
    def time(self):
        return self.x
    
    @time.setter
    def time(self, value):
        self.setX(value)

    @property
    def value(self):
        return self.x
    
    @value.setter
    def value(self, value):
        self.setX(value)


class QCurveData(QtGui.QPolygon):
    """ Curve data stored in QPolygon and some features more
        aa = QCurveData()
        aa.addPoint(0,0,'start')
        aa.addPoint(1,1,'attack')
        aa.attack
    """
    def __init__(self):
        super(QCurveData, self).__init__()
        self.max_height = 128
        self.point_names = []

        self.target_size = QtCore.QSize(127, 127)

        self._check_point_names()
        # self.print_data()

    def addPoint(self, x: int, y: int, name: str = None):
        pt = QtCore.QPoint(x, y)
        self.append(pt)
        self._append_point_name(name)

    @overload
    def addSegment(self, x: int, y: int, name: str = None): ...

    @overload
    def addSegment(self, pt: QtCore.QPoint, name: str = None): ...

    def addSegment(self, *args, name: str = None):
        pt = args[0] if isinstance(args[0], QtCore.QPoint) else None
        x  = args[0] if isinstance(args[0], int) else None
        y  = args[1] if len(args) > 1 and isinstance(args[1], int) else None
        name = args[-1] if isinstance(args[-1], str) else name

        last = QtCore.QPoint() if self.isEmpty() else self.last()

        if x is not None and y is not None:
            self.addPoint(last.x() + x,
                          last.y() + y,
                          name)
        elif pt is not None:
            self.addPoint(last.x() + pt.x(),
                          last.y() + pt.y(),
                          name)
        else:
            raise TypeError('Add segments by two integers or a QPoint !!')

    def getPointByName(self, name: str):
        if name in self.point_names:
            i = self.point_names.index(name)
            return self[i]

    def print_data(self):
        print('----', self.size())
        for i in range(self.size()):
            print(i, f"{self.point_names[i]:<10}", self.point(i))

    def _append_point_name(self, name: str = None):
        if name:
            self.point_names.append(name)
            setattr(self, name, self.getPointByName(name))
        else:
            i = len(self.point_names)
            point_name = f'point_{i:02d}'
            self.point_names.append(point_name)

    def _rename_attr(self, old_name: str, new_name: str):
        i = self.point_names.index(old_name)
        self.point_names[i] = new_name

        delattr(self, old_name)
        setattr(self, new_name, self.getPointByName(new_name))

    def _check_point_names(self):
        if self.size() == len(self.point_names):
            return
        for i in range(len(self.point_names), self.size()+1):
            self._append_point_name()

    def stretchedTo(self, target_size: QtCore.QSize):
        scale_w = target_size.width() / self.boundingRect().width()
        scale_h = target_size.height() / self.max_height
        trs = QtGui.QTransform()
        trs.scale(scale_w, scale_h)
        return trs.map(self)

    def stretched(self):
        scale_w = self.target_size.width() / self.boundingRect().width()
        scale_h = self.target_size.height() / self.max_height
        trs = QtGui.QTransform()
        trs.scale(scale_w, scale_h)
        return trs.map(self)


class CurveView(QWidget):
    pass


class QMCAmpADSR(QWidget):
    """Qt Midi Controller Amplifier/ADSR"""

    # TODO: Add ghost curve
    # TODO: Shade (gradient) curve area
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.backgroundColor = QtGui.QColor(4, 21, 37)
        self.borderColor = Qt.black
        self.contentBorderColor = QtGui.QColor(74, 86, 100)
        self.lineColor = QtGui.QColor(59, 118, 168)
        self.pointColor = QtGui.QColor(255, 247, 197)
        self.gridColor = QtGui.QColor(74, 86, 100, 127)
        self.background_gradColor_start = QtGui.QColor(74, 86, 100, alpha=0)
        self.background_gradColor_stop = QtGui.QColor(74, 86, 100, alpha=200)

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

        self.curve_label = QLabel(self.tr('ADSR Amplifier'))
        self.curve_label.setMouseTracking(True)
        self.curve_label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.curve_label.setStyleSheet("""
                font: 12pt "Terminal" ;
                color: rgb(255, 255, 255);
        """)

        layout = QHBoxLayout(self)
        layout.addWidget(self.curve_label)
        self.setLayout(layout)

        # adsr as polygon
        self.poly = QCurveData()
        self.poly.addSegment(0, 0, 'start')
        self.poly.addSegment(64, 127, 'attack')
        self.poly.addSegment(64, -64, 'decay')
        self.poly.addSegment(72, 0, 'sustain')
        self.poly.addSegment(63, -63, 'release')

        self.poly.target_size = self.contentsRect().size()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.mouse_pressed = True
        pos = self.contentTransform.map(a0.pos())
        in_range_data = self.inRangeCurvePoint_mapped(pos)
        if not self.pt_dragging and in_range_data['name']:
            print('---------------')
            print(f'Clicked: {in_range_data["name"]}')
            print(pos)
            self.pt_dragging = in_range_data

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        pos = self.contentTransform.map(a0.pos())
        in_range_data = self.inRangeCurvePoint_mapped(pos)

        if in_range_data['name']:
            self.pt_hasFocus = True
            self.focus_pt = in_range_data['coord']
        else:
            # update if hasFocus changed
            if self.pt_hasFocus:
                self.pt_hasFocus = False

        if self.mouse_pressed and self.pt_dragging is not None:
            pos_fixed = [min(self.contentsRect().width(),   max(0, pos.x())),
                         min(127,                           max(0, pos.y()))]
            pos_fixed = QtCore.QPoint(*pos_fixed)
            if self.pt_dragging['name'] == 'attack':
                self.attack_time = pos_fixed.x()
                self.attack_level = pos_fixed.y()
            if self.pt_dragging['name'] == 'decay':
                self.decay_time = max(self.attack_time, pos_fixed.x() - self.attack_time)
                self.sustain_level = pos_fixed.y()
            if self.pt_dragging['name'] == 'sustain':
                self.decay_time = min(127, self.contentsRect().width() - pos_fixed.x())
                self.sustain_level = pos_fixed.y()

        label_data = [str(in_range_data["name"]).capitalize(),
                      pos.x(),
                      pos.y()]
        self.curve_label.setText('{}\n [ {:>3},{:>3} ]'.format(*label_data))
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
        return self.poly.attack.x()

    @property
    def attack_level(self):
        return self.poly.attack.y()

    @property
    def decay_time(self):
        return self.poly.decay.x() - self.poly.attack.x()

    @property
    def sustain_time(self):
        return self.poly.sustain.x() - self.poly.decay.x()

    @property
    def sustain_level(self):
        return self.poly.sustain.y()

    @property
    def release_time(self):
        return self.poly.release.x() - self.poly.sustain.x()
    # endregion

    # region SETTERS
    @attack_time.setter
    def attack_time(self, val):
        self.poly.attack.setX(val)

    @attack_level.setter
    def attack_level(self, val):
        self.poly.attack.setY(val)

    @decay_time.setter
    def decay_time(self, val):
        self.poly.decay.setX(self.attack_time + val)

    @sustain_level.setter
    def sustain_level(self, val):
        self.poly.decay.setY(val)
        self.poly.sustain.setY(val)

    @release_time.setter
    def release_time(self, val):
        self.poly.release.setX(self.sustain_time + val)
    # endregion

    def sizeHint(self):
        return QtCore.QSize(200, 167)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.poly.target_size = self.contentsRect().size()

    def paintEvent(self, e):
        # background
        self.drawBackground()

        # adsr as polygon
        poly_fitted = self.poly.stretched()
        self.drawPoly_background(poly_fitted)
        self.drawOpenPoly(poly_fitted)

        # adsr points
        list(map(self.drawPoint, poly_fitted))

        if self.pt_hasFocus:
            self.drawRectangle(self.focus_pt)

    def drawPoint(self, pt, pattern=Qt.SolidLine):
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

    def drawOpenPoly(self, poly: QtGui.QPolygon, pattern=Qt.SolidLine):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        content = self.contentsMargins()
        painter.translate(content.left(), self.geometry().height() - content.bottom())  # Shift to Content
        painter.scale(1, -1)  # flip

        painter.setPen(QtGui.QPen(self.lineColor, self.lineWidth, pattern))

        pt_pairs = list()
        for i, p in enumerate(poly[:-1]):
            pt_pairs.extend([poly[i], poly[i+1]])
        painter.drawLines(*pt_pairs)

        painter.end()

    def drawPoly_background(self, poly: QtGui.QPolygon, pattern=Qt.SolidLine):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        content = self.contentsMargins()
        painter.translate(content.left(), self.geometry().height()-content.bottom())  # Shift to Content
        painter.scale(1, -1)  # flip

        lin_grad = QtGui.QLinearGradient(poly.boundingRect().bottomLeft(), poly.boundingRect().topLeft())
        lin_grad.setColorAt(0.3, self.background_gradColor_start)
        lin_grad.setColorAt(1.0, self.background_gradColor_stop)

        painter.setBrush(QtGui.QBrush(lin_grad))
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, alpha=0), self.lineWidth, pattern))
        painter.drawPolygon(poly)
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

    def inRangeCurvePoint_mapped(self, pos, proximity=10):
        def mdist(pt): return (pt - pos).manhattanLength()

        pts = list(self.poly.stretched())
        pt_names = "start", "attack", "decay", "sustain", "end"
        offsets = list(map(mdist, pts))

        closest_i = offsets.index(sorted(offsets)[0])

        if offsets[closest_i] < proximity:
            return {'name': pt_names[closest_i],
                    'offset': offsets[closest_i],
                    'coord': pts[closest_i]}
        else:
            return {'name': '',
                    'offset': 9999,
                    'coord': QtCore.QPoint(99999, 99999)}
