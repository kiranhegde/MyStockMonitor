from PyQt5.QtCore import Qt, QRegExp, QDateTime, QDate
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtWidgets import QDialog, QLineEdit, QLabel, QComboBox, QDateTimeEdit, QDateEdit \
    , QCheckBox, QDialogButtonBox, QMessageBox, QPushButton \
    , QVBoxLayout, QFormLayout, QHBoxLayout, QGroupBox \
    , QGridLayout, QFrame

# from DataBase.label_names import PAY_TYPE_HOSPITAL1, PAY_TYPE_HOSPITAL2, PAYIN_DEPARTMENT_HOSPITAL, PAYIN_KEY_HOSPITAL, \
#     DATE_TIME, DATE_TIME1, \
#     PAYIN_KEY_PHARMACY, PAYOUT_KEY_PHARMACY, PAYIN_DEPARTMENT_PHARMACY, PAY_TYPE_PHARMACY1, \
#     PAY_TYPE_PHARMACY2

from utility.utility_functions import make_nested_dict, parse_str
from utility.libnames import AGENCY_LIST, EXCHANGE_LIST
from utility.date_time import DATE_TIME1


class sell_selected_stock(QDialog):

    # def __init__(self,con,cur,agency=""):
    def __init__(self, stock_data, dbsave=False, parent=None):
        super(sell_selected_stock, self).__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Sell stock")
        # self.ref_no = ref_no
        # self.new_stock_addition = new_stock_addition
        self.stock_data = stock_data
        self.dbsave = dbsave
        if dbsave:
            self.dbsave = True

        self.removeCurrent = False

        # self.setWindowIcon(QIcon('icons/icon.ico'))
        self.setGeometry(450, 100, 350, 450)
        self.setFixedSize(self.size())

        self.UI()
        self.show()

    def UI(self):
        self.fetch_data()
        self.widgets()
        self.layouts()

    def fetch_data(self):
        # ['id', 'ref_number', 'agency', 'exchange', 'equity', 'buy_date', 'avg_price',
        #                              'quantity', 'remarks']
        self.ref_number = self.stock_data['ref_number']
        self.agency = self.stock_data['agency']
        self.xchange = self.stock_data['exchange']
        self.equity = self.stock_data['equity']
        self.buy_date = self.stock_data['buy_date']
        self.avg_price = str(self.stock_data['avg_price'])
        self.quantity = str(self.stock_data['quantity'])
        self.charges = "0"
        self.comment = self.stock_data['remarks']

    def widgets(self):
        self.save_db = False
        self.titleText = QLabel("Add New stock")
        self.agencyEntry = QLineEdit()
        self.agencyEntry = QComboBox()
        self.agencyEntry.addItems(AGENCY_LIST)
        if self.xchange in AGENCY_LIST:
            indx = self.exchangeEntry.findText(self.xchange)
            self.exchangeEntry.setCurrentIndex(indx)
        self.agencyEntry.setDisabled(True)
        # self.agencyEntry.setPlaceholderText("Enter name of agency (Eg. Kotak, Zerodha, etc)")
        # self.exchangeEntry=QLineEdit()
        # self.exchangeEntry.setPlaceholderText("Enter name of exchange(Eg. BSE,NSE, etc)")
        self.exchangeEntry = QComboBox()
        self.exchangeEntry.addItems(EXCHANGE_LIST)
        if self.agency in EXCHANGE_LIST:
            indx = self.exchangeEntry.findText(self.agency)
            self.exchangeEntry.setCurrentIndex(indx)

        self.equityEntry = QLineEdit()
        self.equityEntry.setPlaceholderText("Enter Equity Symbol (Eg. SBI, ITC, etc)")
        self.equityEntry.setText(self.equity)
        self.equityEntry.setDisabled(True)

        self.buy_dateEntry = QDateEdit(self)
        self.buy_dateEntry.setDate(self.buy_date)
        self.buy_dateEntry.setDisplayFormat(DATE_TIME1)
        self.buy_dateEntry.setEnabled(False)

        self.buy_priceEntry = QLineEdit()
        self.buy_priceEntry.setText(self.avg_price)
        self.buy_priceEntry.setEnabled(False)

        self.buy_quantityEntry = QLineEdit()
        self.buy_quantityEntry.setText(self.quantity)
        self.buy_quantityEntry.setEnabled(False)

        self.sell_dateEntry = QDateEdit(self)
        self.sell_dateEntry.setDate(QDate.currentDate())
        self.sell_dateEntry.setDisplayFormat(DATE_TIME1)

        self.sell_priceEntry = QLineEdit()
        self.sell_priceEntry.setPlaceholderText("Enter average sale price")
        reg_ex_float = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator_float = QRegExpValidator(reg_ex_float, self.sell_priceEntry)
        self.sell_priceEntry.setValidator(input_validator_float)
        self.sell_priceEntry.textChanged.connect(self.check_price)

        self.sell_quantityEntry = QLineEdit()
        reg_ex_int = QRegExp("[1-9][0-9]*")
        input_validator_int = QRegExpValidator(reg_ex_int, self.sell_quantityEntry)
        self.sell_quantityEntry.setValidator(input_validator_int)
        # self.quantityEntry.setText("0")
        self.sell_quantityEntry.textChanged.connect(self.check_quantity)
        self.sell_quantityEntry.setPlaceholderText("Enter quantity of stocks")

        self.chargesEntry = QLineEdit()
        self.chargesEntry.setPlaceholderText("Enter total charges(Eg. stt+gst+brockerage")
        reg_ex_float1 = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator_float1 = QRegExpValidator(reg_ex_float1, self.chargesEntry)
        self.chargesEntry.setValidator(input_validator_float1)
        self.chargesEntry.textChanged.connect(self.check_charges)
        self.chargesEntry.setText(self.charges)

        self.remarksEntry = QLineEdit()
        self.remarksEntry.setPlaceholderText("Type your remarks ..")
        self.remarksEntry.setText(self.comment)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # self.resets = QPushButton("Reset")
        # self.resets.clicked.connect(self.clearAll)
        # self.buttonBox.addButton(self.resets, QDialogButtonBox.ResetRole)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.saveDB = QCheckBox("Update to Database")
        if self.dbsave:
            self.saveDB.setChecked(True)
            self.saveDB.setDisabled(True)
        else:
            self.saveDB.stateChanged.connect(self.state_changed_db)

        self.deleteHolding = QCheckBox("Delete from current holding")
        if self.removeCurrent:
            self.deleteHolding.setChecked(True)
            self.deleteHolding.setDisabled(True)
        else:
            self.deleteHolding.stateChanged.connect(self.state_changed_current)

        # self.equityEntry.setText("SBI")
        # self.trade_priceEntry.setText("1")
        # self.quantityEntry.setText("1")
        # self.chargesEntry.setText("1")
        # self.remarksEntry.setText("test")

    def layouts(self):
        self.mainLayout = QVBoxLayout()
        self.mainTopLayout = QVBoxLayout()
        self.topLayout = QFormLayout()
        self.bottomLayout = QHBoxLayout()
        self.topFrame = QFrame()

        self.topGroupBox = QGroupBox("Stock Information")
        # self.bottomGroupBox = QGroupBox("Control")
        self.bottomGroupBox = QGroupBox()

        self.topLayout.addRow(QLabel("Agency: "), self.agencyEntry)
        self.topLayout.addRow(QLabel("Exchange: "), self.exchangeEntry)
        self.topLayout.addRow(QLabel("Equity: "), self.equityEntry)
        self.topLayout.addRow(QLabel("Buy Date: "), self.buy_dateEntry)
        self.topLayout.addRow(QLabel("Average Buy Price: "), self.buy_priceEntry)
        self.topLayout.addRow(QLabel("Buy Quantity: "), self.buy_quantityEntry)
        self.topLayout.addRow(QLabel("Sale Date: "), self.sell_dateEntry)
        self.topLayout.addRow(QLabel("Average Sale Price: "), self.sell_priceEntry)
        self.topLayout.addRow(QLabel("Sale Quantity: "), self.sell_quantityEntry)
        self.topLayout.addRow(QLabel("Charges (if any): "), self.chargesEntry)
        self.topLayout.addRow(QLabel("Remarks: "), self.remarksEntry)
        self.bottomLayout.addWidget(self.buttonBox)
        self.topGroupBox.setLayout(self.topLayout)
        self.bottomGroupBox.setLayout(self.bottomLayout)
        self.mainTopLayout.addWidget(self.topGroupBox)
        self.mainTopLayout.addWidget(self.saveDB)
        self.mainTopLayout.addWidget(self.deleteHolding)
        self.mainTopLayout.addWidget(self.bottomGroupBox)

        self.mainLayout.addLayout(self.mainTopLayout)
        self.setLayout(self.mainLayout)

    def state_changed_db(self, state):
        if state == Qt.Checked:
            self.save_db = True
        else:
            self.save_db = False

    def state_changed_current(self, state):
        if state == Qt.Checked:
            self.removeCurrent = True
        else:
            self.removeCurrent = False

    def check_price(self):
        # if type(self.pay2.text()) ==
        price = parse_str(self.sell_priceEntry.text())
        if price == "":
            pass
        elif isinstance(price, str):
            QMessageBox.warning(self, "Check Price !!!",
                                " Price should be a number")
            self.reset_value(1)

    def check_charges(self):
        # if type(self.pay2.text()) ==
        charges = parse_str(self.chargesEntry.text())
        if charges == "":
            pass
        elif isinstance(charges, str):
            QMessageBox.warning(self, "Check Charges  !!!",
                                " Charges should be a number")
            self.reset_value(3)

    def check_quantity(self):
        # if type(self.pay2.text()) ==
        quantity = parse_str(self.sell_quantityEntry.text())
        if quantity == "":
            pass
        # elif isinstance(quantity, int) or isinstance(quantity, float):
        #     if self.quantityEntry.currentText() == "None":
        #         QMessageBox.warning(self, " Invalid Payment method !!!",
        #                             " Please select correct \n Payment method")
        #         # self.reset_pay(2)
        elif isinstance(quantity, str):
            QMessageBox.warning(self, "Quantity  Incorrect !!!",
                                " Quantity should be a number")
            self.reset_value(2)

    def reset_value(self, key):
        if key == 1:
            self.sell_priceEntry.setText("")
        if key == 2:
            self.sell_quantityEntry.setText("")
        if key == 3:
            self.chargesEntry.setText("")

    def accept(self):
        # self.output="hi"
        agency = self.agencyEntry.currentText()
        xchange = self.exchangeEntry.currentText()
        equity = self.equityEntry.text()
        sale_date = self.sell_dateEntry.text()
        sale_price = self.sell_priceEntry.text()
        sale_quantity = self.sell_quantityEntry.text()

        if sale_price == "":
            QMessageBox.critical(self, " Stock sale price missing !!!",
                                 " Stock price cannot be empty ..")
            return
        if sale_quantity == "":
            QMessageBox.critical(self, " Stock sale quantity missing !!!",
                                 " Stock quantity cannot be empty ..")
            return

        if self.chargesEntry.text() == "":
            chargesEntry = "na"
        else:
            chargesEntry = self.chargesEntry.text()

        if self.remarksEntry.text() == "":
            comment = "na"
        else:
            comment = self.remarksEntry.text()

        self.output = agency, xchange, equity, sale_date, sale_price, sale_quantity, chargesEntry, comment, self.save_db, self.removeCurrent
        super(sell_selected_stock, self).accept()

    def clearAll(self):
        # self.agencyEntry.setText("")
        self.agencyEntry.setCurrentIndex(0)
        self.exchangeEntry.setCurrentIndex(0)
        # self.exchangeEntry.setText("")
        self.equityEntry.setText("")
        self.trade_dateEntry.setDate(QDate.currentDate())
        self.trade_dateEntry.setDisplayFormat(DATE_TIME1)
        self.trade_priceEntry.setText("")
        self.quantityEntry.setText("")
        self.chargesEntry.setText("")
        self.remarksEntry.setText("")

    def get_inp(self):
        return self.output

# def main():
#     from PyQt5.QtWidgets import QApplication
#     import sys
#     # from utility.utility_functions import gen_id
#     APP = QApplication(sys.argv)
#     ref_no = 1
#     print(ref_no)
#     new_stock_addition = make_nested_dict()
#     # window = add_new_stock(ref_no, new_stock_addition)
#     newBill_inp = add_new_stock(ref_no, new_stock_addition)
#     if newBill_inp.exec_() == newBill_inp.Accepted:
#         newBill_row = newBill_inp.get_inp()
#         print(newBill_row)
#     # window=set_defaults(" "," ")
#     sys.exit(APP.exec_())
#
#
# if __name__ == '__main__':
#     main()
