__author__ = 'Mikhael'


from PyQt4 import QtCore
from PyQt4.QtGui import *
import sys
from time import sleep


class QObj(QtCore.QObject):
    """
    'Virtual' class for emitting signals
    """
    def __init__(self):
        super(QtCore.QObject, self).__init__()
        pass


class GraphicItemISA(QGraphicsItem):
    def __init__(self, pkmItem, qObj):
        super(GraphicItemISA, self).__init__()
        self.isaItem = pkmItem
        self.type = self.isaItem.type
        self.qObj = qObj
        self.x = self.isaItem.mapPosition[0]
        self.y = self.isaItem.mapPosition[1]
        self.rectF = QtCore.QRectF(-10 + self.x, -10 + self.y, 20, 20)

    def boundingRect(self):
        return self.rectF

    def paint(self, painter=None, style=None, widget=None):
        x = self.x
        y = self.y
        # painter.scale(2, 2)
        if self.type == '01':
            painter.translate(x, y)
            painter.rotate(self.isaItem.orientation)
            painter.translate(-x, -y)
            painter.fillRect(-20 + x, -10 + y, 40, 20, QtCore.Qt.white)
            painter.fillRect(-20 + x, -10 + y, 4, 2, QtCore.Qt.blue)
            if self.isaItem.state == 'Right':
                painter.fillRect(-20 + x, y, 40, 10, QtCore.Qt.darkGreen)
            elif self.isaItem.state == 'Left':
                painter.fillRect(-20 + x, -10 + y, 40, 10, QtCore.Qt.red)
            else:
                painter.fillRect(-10 + x, -5 + y, 20, 10, QtCore.Qt.blue)
            painter.fillRect(-20 + x, -10 + y, 4, 2, QtCore.Qt.blue)
        elif self.type == '02':
            # TODO painting wigwags
            pass
        elif self.type == '03':
            if not self.isaItem.state['int0']:
                painter.setBrush(QBrush(QtCore.Qt.darkGreen))
                painter.setPen(QPen(QtCore.Qt.NoPen))
            else:
                painter.setBrush(QBrush(QtCore.Qt.yellow))
                painter.setPen(QPen(QtCore.Qt.NoPen))
            painter.drawEllipse(self.rectF)
        elif self.type == '04':
            painter.fillRect(-25 + x, -15 + y, 50, 30, QtCore.Qt.white)
            painter.fillRect(-15 + x, -5 + y, 30, 10, QtCore.Qt.blue)
            if self.isaItem.state == 'Left':
                painter.fillRect(-25 + x, -15 + y, 50, 10, QtCore.Qt.darkGreen)
                painter.fillRect(-25 + x, -5 + y, 50, 10, QtCore.Qt.white)
                painter.fillRect(-25 + x, 5 + y, 50, 10, QtCore.Qt.darkGreen)
            elif self.isaItem.state == 'Right':
                painter.fillRect(-25 + x, -15 + y, 50, 30, QtCore.Qt.white)
                painter.fillRect(-25 + x, -5 + y, 50, 10, QtCore.Qt.red)
                painter.fillRect(-5 + x, -15 + y, 10, 30, QtCore.Qt.red)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            cmd = ''
            if self.isaItem.type == '01':
                cmd = self.isaItem.switch()
                sys.stdout.write('Switcher ' + str(self.isaItem.deviceNo) + ' switched to ' + str(self.isaItem.state) + unicode('<br>'))
                self.qObj.emit(QtCore.SIGNAL("map_signal"), cmd)
            elif self.type == '02':
                pass
            elif self.type == '03':
                # TODO commands wigwags
                pass
            elif self.type == '04':
                cmd = self.isaItem.switch()
                sys.stdout.write('Multiswitcher ' + str(self.isaItem.deviceNo) + ' switched to ' + str(self.isaItem.state) + unicode('<br>'))
                self.qObj.emit(QtCore.SIGNAL("map_signal"), cmd)
            if self.isaItem.type == '01':
                sleep(0.5)
                cmd = self.isaItem.powerOff()
                self.qObj.emit(QtCore.SIGNAL("map_signal"), cmd)


class GraphicsSceneISA(QGraphicsScene):
    def __init__(self, parent=None):
        super(GraphicsSceneISA, self).__init__(parent)

    # def mousePressEvent(self, event):
    #     if event.buttons() == QtCore.Qt.RightButton:
    #         print 'Position of click: ' + str(event.scenePos()) + '<br\>'


class GraphicsViewISA(QGraphicsView):
    def __init__(self, parent=None):
        super(GraphicsViewISA, self).__init__(parent)
        self.parent = parent