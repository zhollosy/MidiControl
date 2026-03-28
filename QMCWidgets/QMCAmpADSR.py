from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt
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
        self.max_width = None  # Set externally for fixed-width scaling
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

    def indexOfName(self, name: str):
        return self.point_names.index(name) if name in self.point_names else -1

    def getPointByName(self, name: str):
        i = self.indexOfName(name)
        if i >= 0:
            return self.point(i)

    def setPointValue(self, name: str, x: int = None, y: int = None):
        i = self.indexOfName(name)
        if i < 0:
            return
        pt = self.point(i)
        if x is not None:
            pt.setX(x)
        if y is not None:
            pt.setY(y)
        self.setPoint(i, pt)

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
        base_w = self.max_width if self.max_width else self.boundingRect().width()
        scale_w = self.target_size.width() / base_w
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
        self.borderColor = Qt.GlobalColor.black
        self.contentBorderColor = QtGui.QColor(74, 86, 100)
        self.lineColor = QtGui.QColor(59, 118, 168)
        self.pointColor = QtGui.QColor(255, 247, 197)
        self.gridColor = QtGui.QColor(74, 86, 100, 127)
        self.background_gradColor_start = QtGui.QColor(74, 86, 100, 0)
        self.background_gradColor_stop = QtGui.QColor(74, 86, 100, 200)

        self.lineWidth = 3
        self.pointSize = 3
        self.borderWidth = 3
        self.contentBorderWidth = 2

        self.dragDistance = 10
        self.pt_hasFocus = False
        self.focus_pt_index = -1
        self.pt_dragging = None
        self.mouse_pressed = False

        self.setMouseTracking(True)
        self.setContentsMargins(20, 20, 20, 20)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding
        )

        self.curve_label = QLabel(self.tr('ADSR Amplifier'))
        self.curve_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.curve_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.curve_label.setStyleSheet("""
                font: 12pt "Consolas" ;
                color: rgb(255, 255, 255);
        """)

        layout = QHBoxLayout(self)
        layout.addWidget(self.curve_label)
        self.setLayout(layout)

        # adsr as polygon
        # Fixed layout: Attack(max 127) + Decay(max 127) + Sustain(fixed 64) + Release(max 127)
        self.SUSTAIN_TIME = 64
        self.MAX_TIME = 127
        self.MAX_LEVEL = 127

        self.poly = QCurveData()
        self.poly.addSegment(0, 0, 'start')
        self.poly.addSegment(64, 127, 'attack')       # attack_time=64, attack_level=127
        self.poly.addSegment(64, -64, 'decay')         # decay_time=64, sustain_level=63
        self.poly.addSegment(self.SUSTAIN_TIME, 0, 'sustain')  # fixed 64 wide
        self.poly.addSegment(63, -63, 'release')       # release_time=63

        self.poly.max_width = 3 * self.MAX_TIME + self.SUSTAIN_TIME  # 445
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
            self.focus_pt_index = in_range_data['index']
        else:
            if self.pt_hasFocus:
                self.pt_hasFocus = False
                self.focus_pt_index = -1

        if self.mouse_pressed and self.pt_dragging is not None:
            # Convert from stretched content space back to original polygon space
            mw = self.poly.max_width or self.poly.boundingRect().width() or 1
            tw = self.poly.target_size.width() or 1
            th = self.poly.target_size.height() or 1
            orig_x = int(pos.x() * mw / tw)
            orig_y = int(pos.y() * self.poly.max_height / th)
            orig_x = max(0, orig_x)
            orig_y = max(0, min(self.MAX_LEVEL, orig_y))

            if self.pt_dragging['name'] == 'attack':
                self.attack_time = orig_x
                self.attack_level = orig_y

            elif self.pt_dragging['name'] == 'decay':
                self.decay_time = orig_x - self.attack_time
                self.sustain_level = orig_y

            elif self.pt_dragging['name'] == 'sustain':
                self.sustain_level = orig_y

            elif self.pt_dragging['name'] == 'release':
                sustain_x = self.poly.getPointByName('sustain').x()
                self.release_time = orig_x - sustain_x

        name = in_range_data['name']
        if name == 'attack':
            label_text = f'Attack\n [ A:{self.attack_time:>3}, A:{self.attack_level:>3} ]'
        elif name == 'decay':
            label_text = f'Decay\n [ D:{self.decay_time:>3}, S:{self.sustain_level:>3} ]'
        elif name == 'sustain':
            label_text = f'Sustain\n [ S:{self.sustain_level:>3}, R:{self.release_time:>3} ]'
        elif name == 'release':
            label_text = f'Release\n [ R:{self.release_time:>3} ]'
        else:
            label_text = f'[ {pos.x():>3},{pos.y():>3} ]'
        self.curve_label.setText(label_text)
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
        return self.poly.getPointByName('attack').x()

    @property
    def attack_level(self):
        return self.poly.getPointByName('attack').y()

    @property
    def decay_time(self):
        return self.poly.getPointByName('decay').x() - self.attack_time

    @property
    def sustain_level(self):
        return self.poly.getPointByName('sustain').y()

    @property
    def release_time(self):
        return self.poly.getPointByName('release').x() - self.poly.getPointByName('sustain').x()
    # endregion

    # region SETTERS
    @attack_time.setter
    def attack_time(self, val):
        rt = self.release_time
        dt = self.decay_time
        self.poly.setPointValue('attack', x=max(0, min(self.MAX_TIME, val)))
        self.poly.setPointValue('decay', x=self.attack_time + dt)
        self._sync_sustain_x()
        self.poly.setPointValue('release', x=self.poly.getPointByName('sustain').x() + rt)

    @attack_level.setter
    def attack_level(self, val):
        self.poly.setPointValue('attack', y=max(0, min(self.MAX_LEVEL, val)))

    @decay_time.setter
    def decay_time(self, val):
        rt = self.release_time
        val = max(0, min(self.MAX_TIME, val))
        self.poly.setPointValue('decay', x=self.attack_time + val)
        self._sync_sustain_x()
        self.poly.setPointValue('release', x=self.poly.getPointByName('sustain').x() + rt)

    @sustain_level.setter
    def sustain_level(self, val):
        val = max(0, min(self.MAX_LEVEL, val))
        self.poly.setPointValue('decay', y=val)
        self.poly.setPointValue('sustain', y=val)

    @release_time.setter
    def release_time(self, val):
        val = max(0, min(self.MAX_TIME, val))
        self.poly.setPointValue('release', x=self.poly.getPointByName('sustain').x() + val)
    def _sync_sustain_x(self):
        self.poly.setPointValue('sustain', x=self.poly.getPointByName('decay').x() + self.SUSTAIN_TIME)

    def _sync_release_x(self):
        rt = self.release_time
        self.poly.setPointValue('release', x=self.poly.getPointByName('sustain').x() + max(0, rt))
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

        if self.pt_hasFocus and 0 <= self.focus_pt_index < poly_fitted.size():
            self.drawRectangle(poly_fitted.point(self.focus_pt_index))

    def drawPoint(self, pt, pattern=Qt.PenStyle.SolidLine):
        painter = QtGui.QPainter(self)

        content = self.contentsMargins()
        painter.translate(content.left(), self.geometry().height()-content.bottom())
        painter.scale(1, -1)

        painter.setPen(QtGui.QPen(self.pointColor, 2, pattern))


        rect = QtCore.QRect(0, 0, self.pointSize, self.pointSize)
        rect.moveCenter(pt)
        painter.drawRect(rect)
        painter.end()

    def drawLine(self, crv, pattern=Qt.PenStyle.SolidLine):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        content = self.contentsMargins()
        painter.translate(content.left(), self.geometry().height()-content.bottom())
        painter.scale(1, -1)

        painter.setPen(QtGui.QPen(self.lineColor, self.lineWidth, pattern))
        painter.drawLine(crv)
        painter.end()

    def drawOpenPoly(self, poly: QtGui.QPolygon, pattern=Qt.PenStyle.SolidLine):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        content = self.contentsMargins()
        painter.translate(content.left(), self.geometry().height() - content.bottom())  # Shift to Content
        painter.scale(1, -1)  # flip

        painter.setPen(QtGui.QPen(self.lineColor, self.lineWidth, pattern))

        pt_pairs = list()
        for i, p in enumerate(poly[:-1]):
            pt_pairs.extend([poly[i], poly[i+1]])
        painter.drawLines(*pt_pairs)

        painter.end()

    def drawPoly_background(self, poly: QtGui.QPolygon, pattern=Qt.PenStyle.SolidLine):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        content = self.contentsMargins()
        painter.translate(content.left(), self.geometry().height()-content.bottom())  # Shift to Content
        painter.scale(1, -1)  # flip

        lin_grad = QtGui.QLinearGradient(QtCore.QPointF(poly.boundingRect().bottomLeft()), QtCore.QPointF(poly.boundingRect().topLeft()))
        lin_grad.setColorAt(0.3, self.background_gradColor_start)
        lin_grad.setColorAt(1.0, self.background_gradColor_stop)

        painter.setBrush(QtGui.QBrush(lin_grad))
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), self.lineWidth, pattern))
        painter.drawPolygon(poly)
        painter.end()

    def drawRectangle(self, center_pt, size=11, pattern=Qt.PenStyle.SolidLine):
        trs = self.contentTransform.inverted()[0]
        center_pt = trs.map(center_pt)

        rect = QtCore.QRect()
        rect.setWidth(size)
        rect.setHeight(size)
        rect.moveCenter(center_pt)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        painter.setPen(QtGui.QPen(self.pointColor, 1, pattern))
        painter.drawRect(rect)
        painter.end()

    def drawBackground(self):
        painter = QtGui.QPainter(self)

        painter.setBrush(QtGui.QBrush(self.backgroundColor, Qt.BrushStyle.SolidPattern))
        painter.setPen(QtGui.QPen(self.borderColor, self.borderWidth, Qt.PenStyle.SolidLine))
        painter.drawRect(0, 0, self.geometry().width(), self.geometry().height())

        painter.setBrush(QtGui.QBrush(self.backgroundColor, Qt.BrushStyle.SolidPattern))
        painter.setPen(QtGui.QPen(self.contentBorderColor, self.contentBorderWidth, Qt.PenStyle.SolidLine))
        painter.drawRect(self.contentsRect())

        painter.setBrush(QtGui.QBrush(self.backgroundColor, Qt.BrushStyle.SolidPattern))
        painter.setPen(QtGui.QPen(self.gridColor, 2, Qt.PenStyle.SolidLine))
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
        pt_names = ("start", "attack", "decay", "sustain", "release")
        # Draggable points (skip start)
        draggable = (1, 2, 3, 4)  # attack, decay, sustain, release
        offsets = {i: mdist(pts[i]) for i in draggable}

        closest_i = min(offsets, key=offsets.get)

        if offsets[closest_i] < proximity:
            return {'name': pt_names[closest_i],
                    'index': closest_i,
                    'offset': offsets[closest_i],
                    'coord': pts[closest_i]}
        else:
            return {'name': '',
                    'index': -1,
                    'offset': 9999,
                    'coord': QtCore.QPoint(99999, 99999)}
