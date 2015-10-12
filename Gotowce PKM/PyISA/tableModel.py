__author__ = 'mikhael'
import operator
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class TableModel(QAbstractTableModel):
    """
    Table model of PKM Objects
    """
    def __init__(self, data, headerData, parent=None):
        """
        :data: a list PKMObjects
        :headerData: a list of strings
        """
        QAbstractTableModel.__init__(self, parent)
        self.tableData = data
        self.headerData = headerData

    def rowCount(self, parent):
        return len(self.tableData)

    def columnCount(self, parent):
        if self.tableData:
            return len(self.tableData[0].getTableData())
        else:
            return 0

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.tableData[index.row()].getTableData()[
            index.column()])

    def changeData(self):
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))


    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerData[col])
        return QVariant()

    def flags(self, index):
        flags = super(self.__class__, self).flags(index)

        flags |= Qt.ItemIsEditable
        flags |= Qt.ItemIsSelectable
        flags |= Qt.ItemIsEnabled
        flags |= Qt.ItemIsDragEnabled
        flags |= Qt.ItemIsDropEnabled

        return flags

    def sort(self, colNum, order):
        """
        Sort table by given column number.
        :colNum: number of column
        :order: ascending/descending Qt.DescendingOrder
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        # Zone sorting
        if colNum == 0:
            self.tableData = sorted(self.tableData, cmp=lambda x, y: cmp(
                                    x.zone, y.zone))
        # Address sorting
        elif colNum == 1:
            self.tableData = sorted(self.tableData)
        # Status sorting -- disabled
        elif colNum == 2:
            self.tableData = sorted(self.tableData)
        # Point (x, y) sorting
        elif colNum == 3:
            self.tableData = sorted(self.tableData, cmp=lambda x, y: cmp(
                x.mapPosition[0], y.mapPosition[0]))
        # Description
        elif colNum == 4:
            self.tableData = sorted(self.tableData, cmp=lambda x, y: cmp(
                x.description, y.description))
        if order == Qt.DescendingOrder:
            self.tableData.reverse()
        self.emit(SIGNAL("layoutChanged()"))

