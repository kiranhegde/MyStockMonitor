# from PyQt5.QtWidgets import QApplication, QTableView
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant

from datetime import date


# from PyQt5.QtWidgets import
# from PyQt5.QtGui import

# import operator
# from DataBase.label_names import DATE_TIME
# import datetime
# https://stackoverflow.com/questions/44603119/how-to-display-a-pandas-data-frame-with-pyqt5-pyside2
# https://www.qtcentre.org/threads/62807-PyQt-QTableView-displying-100-000-000-rows
# https://stackoverflow.com/questions/43915108/qtablewidget-insert-row-crashes-the-application-python
# https://www.programmersought.com/article/13974875038/
# https://www.zeolearn.com/magazine/getting-started-guis-with-python-pyqt-qthread-class
# https://github.com/datalyze-solutions/pandas-qt/blob/master/pandasqt/models/DataFrameModel.py

# https://forum.qt.io/topic/60110/qtablemanager-removing-all-rows-crashes-application-with-bad-access/3
# https://www.mfitzp.com/forum/t/add-some-explanation-on-sorting-a-qtableview/221/3
# https://codereview.stackexchange.com/questions/125622/insert-new-row-to-a-qtableview-by-double-clicking-the-last-row
# https://www.mfitzp.com/tutorials/modelview-architecture/
# https://stackoverflow.com/questions/61320830/adding-dynamic-data-to-sublcassed-qabstracttablemodel

# class memoize:
#     # from http://avinashv.net/2008/04/python-decorators-syntactic-sugar/
#     def __init__(self, function):
#         self.function = function
#         self.memoized = {}
#
#     def __call__(self, *args):
#         try:
#             return self.memoized[args]
#         except KeyError:
#             self.memoized[args] = self.function(*args)
#             return self.memoized[args]
#
#
#
# class FloatDelegate(QItemDelegate):
#     def __init__(self, decimals, parent=None):
#         QItemDelegate.__init__(self, parent=parent)
#         self.nDecimals = decimals
#
#     def paint(self, painter, option, index):
#         value = index.model().data(index, Qt.EditRole)
#         try:
#             number = float(value)
#             painter.drawText(option.rect, Qt.AlignLeft, "{:.{}f}".format(number, self.nDecimals))
#         except :
#             QItemDelegate.paint(self, painter, option, index)


class pandasModel(QAbstractTableModel):
    def __init__(self, data):
        super(pandasModel, self).__init__()
        self._data = data
        # print("Input Data Type--------------------->",type(data))

    # def appendRowData(self, data):
    #     self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
    #     self._data.append(data)
    #     self.endInsertRows()

    # def data(self, index, role=Qt.EditRole):
    #     if role in (Qt.DisplayRole, Qt.EditRole):
    #         return self._data.iloc[index.row()][index.column()]
    # https: // stackoverflow.com / questions / 24122306 / custom - tableview - model for -pandas - dataframe
    def update(self, data, key="edit"):
        self._data = data
        # self.layoutChanged.emit()
        # self.clearSelection()
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    # def insertRows(self, row, rows=1, index=QModelIndex()):
    #     print("Inserting at row: {row}")
    #     self.beginInsertRows(QModelIndex(), row, row + rows - 1)
    #     for row in range(rows):
    #         self.items.insert(row + row, "New Item %s" % self.added)
    #         self.added += 1
    #     self.endInsertRows()
    #     return True

    # https://stackoverflow.com/questions/53838343/pyqt5-extremely-slow-scrolling-on-qtableview-with-pandas
    # @memoize
    def data(self, index, role=Qt.DisplayRole):
        # https://www.learnpyqt.com / tutorials / qtableview - modelviews - numpy - pandas /
        if index.isValid():
            if role == Qt.DisplayRole:
                val = self._data.iloc[index.row(), index.column()]
                # value = parse_str(val)
                value = str(val)

                if isinstance(val, date):
                    # Render time to DD-MM-YYYY.
                    return val.strftime("%d-%m-%Y")

                if isinstance(value, float) and index.column() != 0 and index.column() != 1:
                    # Render float to 2 dp
                    return "%.2f" % value

                if isinstance(value, str):
                    # Render strings with quotes
                    return "%s" % value

                if isinstance(value, int):
                    # Render strings with quotes
                    return "%d" % value

        return None

    def rowCount(self, index=None):
        # print(len(self._data.index))
        return len(self._data.index)

    def columnCount(self, index=None):
        # len(self._data.columns)
        return len(self._data.columns)

    # def headerData(self, section: int, orientation: Qt.Orientation, role: int):
    #     # https: // stackoverflow.com / questions / 63012839 / how - to - quickly - fill - a - qtableview - model - with-data - in -pyqt
    #     if role == Qt.DisplayRole:
    #         colname=self._data.columns.tolist()[section]
    #         if orientation == Qt.Horizontal:
    #             # print("1",colname)
    #             return str(colname)
    #         else:
    #             # print("2", section)
    #             return str(colname)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self._data.columns.tolist()[section])
        return QVariant()

    def sort(self, column, order):
        # print(self._data.columns.tolist())
        colname = self._data.columns.tolist()[column]
        # print(colname,order)
        self.layoutAboutToBeChanged.emit()
        self._data.sort_values(colname, ascending=order == Qt.DescendingOrder, inplace=True)
        self._data.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()
