from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QDialog, QLineEdit, QLabel, QDateEdit \
    , QCheckBox, QDialogButtonBox, QPushButton \
    , QVBoxLayout, QFormLayout, QHBoxLayout, QGroupBox \
    , QFrame

# from DataBase.label_names import PAY_TYPE_HOSPITAL1, PAY_TYPE_HOSPITAL2, PAYIN_DEPARTMENT_HOSPITAL, PAYIN_KEY_HOSPITAL, \
#     DATE_TIME, DATE_TIME1, \
#     PAYIN_KEY_PHARMACY, PAYOUT_KEY_PHARMACY, PAYIN_DEPARTMENT_PHARMACY, PAY_TYPE_PHARMACY1, \
#     PAY_TYPE_PHARMACY2
import pandas as pd
from utility.utility_functions import make_nested_dict
from utility.date_time import DATE_TIME1, DATE_FMT_DMY
from mysql_tools.tables_and_headers import WATCHLIST_DB_HEADER


class add_watchlist_stock(QDialog):

    def __init__(self, ref_no,agency="", dbsave=True, parent=None):
        super(add_watchlist_stock, self).__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Adding New stock")
        self.ref_no = ref_no
        # self.new_stock_addition = new_stock_addition
        self.dbsave = dbsave

        # self.setWindowIcon(QIcon('icons/icon.ico'))
        self.setGeometry(450, 100, 320, 220)
        self.setFixedSize(self.size())

        self.UI()
        self.show()

    def UI(self):
        self.widgets()
        self.layouts()

    def widgets(self):
        self.save_db = True
        self.titleText = QLabel("Add New stock")
        self.equityEntry = QLineEdit()
        self.equityEntry.setPlaceholderText("Enter Equity Symbol (Eg. SBI, ITC, etc)")

        self.trade_dateEntry = QDateEdit(self)
        self.trade_dateEntry.setDate(QDate.currentDate())
        self.trade_dateEntry.setDisplayFormat(DATE_TIME1)

        self.remarksEntry = QLineEdit()
        self.remarksEntry.setPlaceholderText("Type your remarks ..")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.resets = QPushButton("Reset")
        self.resets.clicked.connect(self.clearAll)
        self.buttonBox.addButton(self.resets, QDialogButtonBox.ResetRole)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.saveDB = QCheckBox("Update to Database")
        self.saveDB.setChecked(self.dbsave)
        self.saveDB.setDisabled(False)
        self.saveDB.stateChanged.connect(self.state_changed)

        # self.equityEntry.setText("SBIN")
        # self.remarksEntry.setText("test")

    def state_changed(self, state):
        if state == Qt.Checked:
            self.save_db = True
        else:
            self.save_db = False

    def accept(self):
        equity = self.equityEntry.text()
        tdate = self.trade_dateEntry.text()
        new_stock_addition = make_nested_dict()
        for key in WATCHLIST_DB_HEADER:
            new_stock_addition[key] = None

        if self.remarksEntry.text() == "":
            comment = "na"
        else:
            comment = self.remarksEntry.text()

        new_stock_addition = make_nested_dict()
        for key in WATCHLIST_DB_HEADER:
            new_stock_addition[key]=None

        new_stock_addition['id'] = 0
        new_stock_addition['ref_number'] = self.ref_no
        new_stock_addition['buy_date'] = pd.to_datetime(tdate,
                                                      format=DATE_FMT_DMY)
        new_stock_addition['equity'] = equity.upper()
        new_stock_addition['remarks'] =comment

        self.output = new_stock_addition,self.save_db
        super(add_watchlist_stock, self).accept()

    def clearAll(self):
        self.agencyEntry.setCurrentIndex(0)
        self.equityEntry.setText("")
        self.trade_dateEntry.setDate(QDate.currentDate())
        self.trade_dateEntry.setDisplayFormat(DATE_TIME1)
        self.trade_priceEntry.setText("")
        self.quantityEntry.setText("")
        self.chargesEntry.setText("")
        self.remarksEntry.setText("")

    def get_inp(self):
        return self.output

    def layouts(self):
        self.mainLayout = QVBoxLayout()
        self.mainTopLayout = QVBoxLayout()
        self.topLayout = QFormLayout()
        self.bottomLayout = QHBoxLayout()
        self.topFrame = QFrame()

        self.topGroupBox = QGroupBox("Stock Information")
        self.bottomGroupBox = QGroupBox("Control")
        self.topLayout.addRow(QLabel("Trade Date: "), self.trade_dateEntry)
        self.topLayout.addRow(QLabel("Equity: "), self.equityEntry)
        self.topLayout.addRow(QLabel("Remarks: "), self.remarksEntry)

        self.bottomLayout.addWidget(self.buttonBox)
        self.topGroupBox.setLayout(self.topLayout)
        self.bottomGroupBox.setLayout(self.bottomLayout)
        self.mainTopLayout.addWidget(self.topGroupBox)
        self.mainTopLayout.addWidget(self.saveDB)
        self.mainTopLayout.addWidget(self.bottomGroupBox)

        self.mainLayout.addLayout(self.mainTopLayout)
        self.setLayout(self.mainLayout)

def main():
    from PyQt5.QtWidgets import QApplication
    import sys
    # from utility.utility_functions import gen_id
    APP = QApplication(sys.argv)
    ref_no = 1
    print(ref_no)
    new_stock_addition = make_nested_dict()
    # window = add_new_stock(ref_no, new_stock_addition)
    newBill_inp = add_watchlist_stock(ref_no, new_stock_addition)
    if newBill_inp.exec_() == newBill_inp.Accepted:
        newBill_row = newBill_inp.get_inp()
        print(newBill_row)
    # window=set_defaults(" "," ")
    sys.exit(APP.exec_())


if __name__ == '__main__':
    main()
