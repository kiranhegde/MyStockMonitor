from PyQt5.QtCore import Qt, QRegExp, QDateTime, QDate
from PyQt5.QtGui import QIcon, QRegExpValidator, QFont
from PyQt5.QtWidgets import QDialog, QLineEdit, QLabel, QComboBox, QDateTimeEdit, QDateEdit \
    , QCheckBox, QDialogButtonBox, QMessageBox, QPushButton \
    , QVBoxLayout, QFormLayout, QHBoxLayout, QGroupBox \
    , QGridLayout, QFrame,QSpacerItem,QSizePolicy

from utility.date_time import DATE_TIME1
from utility.utility_functions import weighted_average,parse_str

class average_stocks(QDialog):

    # def __init__(self,con,cur,agency=""):
    def __init__(self, stock_data, parent=None):
        super(average_stocks, self).__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Weighted Average of Stocks")
        # self.con=con
        # self.cur=cur
        self.stock_data = stock_data
        self.dbsave = False

        # self.setWindowIcon(QIcon('icons/icon.ico'))
        self.setGeometry(450, 150, 450, 450)
        self.setFixedSize(self.size())

        self.UI()
        self.show()

    def UI(self):
        self.fetch_data()
        # self.default_paramters()
        self.widgets()
        self.layouts()

    def fetch_data(self):
        self.ref_number = self.stock_data['ref_number']
        self.agency = self.stock_data['agency']
        self.equity = self.stock_data['equity']
        self.buy_date = self.stock_data['date']
        self.avg_price = str(self.stock_data['avg_price'])
        self.quantity = str(self.stock_data['quantity'])
        self.charges = str(self.stock_data['fees'])
        self.comment = self.stock_data['remarks']

    def widgets(self):
        fnt = QFont()
        fnt.setPointSize(12)
        fnt.setBold(True)
        fnt.setFamily("Arial")

        self.save_db = False
        self.titleText = QLabel("Stock Averaging")
        # self.agencyEntry=QLineEdit()
        # self.agencyEntry.setText(self.agency)
        # self.agencyEntry.setReadOnly(1)
        # self.agencyEntry.setDisabled(True)
        # self.exchangeEntry=QLineEdit()
        # self.exchangeEntry.setText(self.xchange)
        # self.exchangeEntry = QLineEdit()
        # self.exchangeEntry.setText(self.xchange)
        # self.exchangeEntry.setDisabled(True)

        self.equityEntry = QLineEdit()
        self.equityEntry.setText(self.equity)
        self.equityEntry.setDisabled(True)

        self.trade_dateEntry = QDateEdit(self)
        self.trade_dateEntry.setDate(self.buy_date)
        self.trade_dateEntry.setDisplayFormat(DATE_TIME1)
        self.trade_dateEntry.setDisabled(True)

        self.trade_priceEntry = QLineEdit()
        self.trade_priceEntry.setText(self.avg_price)
        self.trade_priceEntry.setDisabled(True)

        self.quantityEntry = QLineEdit()
        self.quantityEntry.setText(self.quantity)
        self.quantityEntry.setDisabled(True)

        self.current_priceEntry = QLineEdit()
        self.current_priceEntry.setPlaceholderText("Enter current price")
        reg_ex_int = QRegExp("[1-9][0-9]*")
        input_validator_int = QRegExpValidator(reg_ex_int, self.current_priceEntry)
        self.current_priceEntry.setValidator(input_validator_int)
        # self.quantityEntry.setText("0")
        self.current_priceEntry.textChanged.connect(self.check_quantity)

        self.current_quantityEntry = QLineEdit()
        self.current_quantityEntry.setPlaceholderText("Enter current quantity of stocks")
        reg_ex_int = QRegExp("[1-9][0-9]*")
        input_validator_int = QRegExpValidator(reg_ex_int, self.current_quantityEntry)
        self.current_quantityEntry.setValidator(input_validator_int)
        # self.quantityEntry.setText("0")
        self.current_quantityEntry.textChanged.connect(self.check_quantity)
        self.current_price = 0
        self.current_quantity = 0

        self.chargesEntry = QLineEdit()
        self.chargesEntry.setPlaceholderText("Enter total charges(Eg. stt+gst+brockerage")
        reg_ex_float1 = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator_float1 = QRegExpValidator(reg_ex_float1, self.chargesEntry)
        self.chargesEntry.setValidator(input_validator_float1)
        self.chargesEntry.textChanged.connect(self.check_charges)
        self.chargesEntry.setText("0")

        self.remarksEntry = QLineEdit()
        self.remarksEntry.setPlaceholderText("Type your remarks ..")
        self.remarksEntry.setText("")

        self.saveDB = QCheckBox("Update to Database")
        if self.dbsave:
            self.saveDB.setChecked(True)
            self.saveDB.setDisabled(True)
        else:
            self.saveDB.stateChanged.connect(self.state_changed_db)

        self.avg_priceEntry = QLabel()
        self.avg_priceEntry.setFont(fnt)
        self.avg_priceEntry.setText("Average Price: ")
        self.totalQEntry = QLabel()
        self.totalQEntry.setFont(fnt)
        self.totalQEntry.setText("Total  stock: ")
        self.delta_Entry = QLabel()
        self.delta_Entry.setFont(fnt)
        self.delta_Entry.setText("Gain/Loss per stock: ")

        self.overalldelta_Entry = QLabel()
        self.overalldelta_Entry.setFont(fnt)
        self.overalldelta_Entry.setText("Overall Gain/Loss : ")

        self.total_priceEntry = QLabel()
        self.total_priceEntry.setFont(fnt)
        self.total_priceEntry.setText("Total Price: ")

        self.avg_priceEntry.setStyleSheet('color: blue')
        self.totalQEntry.setStyleSheet('color: blue')
        self.delta_Entry.setStyleSheet('color: blue')
        self.overalldelta_Entry.setStyleSheet('color: blue')
        self.total_priceEntry.setStyleSheet('color: blue')

        # self.exchangeEntry.setPlaceholderText("Enter name of exchange(Eg. BSE,NSE, etc)")
        self.equityEntry.setPlaceholderText("Enter Equity name (Eg. SBI, ITC, etc)")
        # self.trade_dateEntry.setDate(QDate.currentDate())
        self.trade_dateEntry.setDisplayFormat("dd/MM/yyyy")
        # self.settle_dateEntry.setDate(QDate.currentDate())

        self.trade_priceEntry.setPlaceholderText("Enter trade price")
        self.quantityEntry.setPlaceholderText("Enter quantity of stocks")
        # self.remarksEntry.setPlaceholderText("Type your remarks ..")
        # https: // www.programcreek.com / python / example / 108071 / PyQt5.QtWidgets.QDialogButtonBox
        # self.buttonBox=QDialogButtonBox(QDialogButtonBox.Ok |QDialogButtonBox.Reset |QDialogButtonBox.Cancel)
        # self.buttonBox=QDialogButtonBox(QDialogButtonBox.Ok |QDialogButtonBox.Cancel)
        # self.buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # self.resets=QPushButton("Reset")
        # self.resets.clicked.connect(self.clearAll)
        self.calcAvg = QPushButton("Calculate")
        self.calcAvg.clicked.connect(self.get_avg)
        # self.addBtn=QPushButton("Submit")
        # self.addBtn.clicked.connect(self.add_stock)
        # self.clrBtn = QPushButton("Clear")
        # self.clrBtn.clicked.connect(self.clear_stock)
        # self.buttonBox.addButton(self.resets,QDialogButtonBox.ResetRole)
        self.buttonBox.addButton(self.calcAvg, QDialogButtonBox.ResetRole)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        # self.buttonBox.clear.connect(self.clearAll)
        self.spaceItem = QSpacerItem(150, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # self.saveDB=QCheckBox("Update to database")
        # self.saveDB=QCheckBox("Update to Database:")
        # self.saveDB.stateChanged.connect(self.state_changed)

        # if self.agency0:
        #     self.agencyEntry.setText(self.agency0)
        # self.exchangeEntry.setText("NSE")
        # self.equityEntry.setText("SBI")
        # self.trade_priceEntry.setText("200")
        # self.quantityEntry.setText("100")

    def state_changed_db(self, state):
        if state == Qt.Checked:
            self.save_db = True
        else:
            self.save_db = False

    def check_price(self):
        # if type(self.pay2.text()) ==
        price = parse_str(self.current_priceEntry.text())
        if price == "":
            pass
        elif isinstance(price, str):
            QMessageBox.warning(self, "Check Price !!!",
                                " Price should be a number")
            self.reset_value(1)

    def check_quantity(self):
        # if type(self.pay2.text()) ==
        quantity = parse_str(self.current_quantityEntry.text())
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

    def check_charges(self):
        # if type(self.pay2.text()) ==
        charges = parse_str(self.chargesEntry.text())
        if charges == "":
            pass
        elif isinstance(charges, str):
            QMessageBox.warning(self, "Check Charges  !!!",
                                " Charges should be a number")
            self.reset_value(3)

    def accept(self):
        pass

    def reset_value(self, key):
        if key == 1:
            self.current_priceEntry.setText("")
        if key == 2:
            self.current_quantityEntry.setText("")
        if key == 3:
            self.chargesEntry.setText("")

    def get_avg(self):
        # print("#", self.quantity)
        # print("#", self.price)
        # print("#", self.current_priceEntry.text())
        # print("#",self.current_quantityEntry.text())
        # print("#",self.current_priceEntry.text())
        q1 = parse_str(self.quantity)
        q2 = parse_str(self.current_quantityEntry.text())
        p1 = parse_str(self.avg_price)
        p2 = parse_str(self.current_priceEntry.text())
        charges = parse_str(self.chargesEntry.text())

        if p2 == "":
            QMessageBox.critical(self, " Stock current price missing !!!",
                                 " Stock price cannot be empty ..")
            return
        if q2 == "":
            QMessageBox.critical(self, " Stock current quantity missing !!!",
                                 " Stock quantity cannot be empty ..")
            return

        if charges == "":
           charges = 0.0

        if q2 == "":
            q2 = 0
        if p2 == "":
            p2 = 0.0

        charges = float(charges) / float(q2)
        p2=p2+charges

        price=[p1,p2]
        quantity=[q1,q2]
        avg_price=weighted_average(values=price,weights=quantity)
        print(avg_price)

        totalstock = q1 + q2
        # delta=round(avg-p1,3)
        delta = round(p2 - avg_price, 3)
        total = round(p2 * q2, 3)
        overallPL = round(totalstock * delta, 3)

        self.avg_priceEntry.setText("Average Price: " + str(avg_price))
        self.totalQEntry.setText("Total  stock: " + str(totalstock))
        self.delta_Entry.setText("Gain/Loss per stock: " + str(delta))
        self.overalldelta_Entry.setText("Overall Gain/Loss : " + str(overallPL))
        self.total_priceEntry.setText("Total Price: " + str(total))




    def layouts(self):
        self.mainLayout=QVBoxLayout()
        self.mainTopLayout=QVBoxLayout()
        self.topLayout=QFormLayout()
        self.bottomLayout=QHBoxLayout()
        self.topFrame=QFrame()

        # self.symbolLabel = QLabel("Equity symbol")
        # self.symbolEntry = QLineEdit()
        # self.intervalLabel = QLabel("Time Interval")
        # self.intervalEntry = QLineEdit()


        self.topGroupBox=QGroupBox("Stock Information")
        # self.bottomGroupBox=QGroupBox("Control")
        self.bottomGroupBox=QGroupBox()

        # self.topLayout.addRow(QLabel("Agency: "),self.agencyEntry)
        # self.topLayout.addRow(QLabel("Exchange: "),self.exchangeEntry)
        self.topLayout.addRow(QLabel("Equity: "),self.equityEntry)
        self.topLayout.addRow(QLabel("Trade Date: "),self.trade_dateEntry)
        # self.topLayout.addRow(QLabel("Settlement Date: "),self.settle_dateEntry)
        self.topLayout.addRow(QLabel("Average Price: "),self.trade_priceEntry)
        self.topLayout.addRow(QLabel("Quantity: "),self.quantityEntry)
        self.topLayout.addRow(QLabel("Current Price: "), self.current_priceEntry)
        self.topLayout.addRow(QLabel("Current Quantity: "), self.current_quantityEntry)
        self.topLayout.addRow(QLabel("Charges (if any): "), self.chargesEntry)
        self.topLayout.addRow(QLabel("Remarks: "), self.remarksEntry)
        self.topLayout.addWidget(self.avg_priceEntry)
        self.topLayout.addWidget(self.totalQEntry)
        self.topLayout.addWidget(self.delta_Entry)
        self.topLayout.addWidget(self.overalldelta_Entry)
        self.topLayout.addWidget(self.total_priceEntry)

        # self.topLayout.addRow(self.avg_priceEntry)
        # self.topLayout.addRow(QLabel("Brockerage per unit: "),self.unit_brockEntry)
        # self.topLayout.addRow(QLabel("GST on Brockerage: "),self.gst_brockEntry)
        # self.topLayout.addRow(QLabel("STT on Share: "),self.stt_Entry)
        # self.topLayout.addRow(QLabel("Income Tax: "),self.it_Entry)
        # self.topLayout.addRow(QLabel("Remarks: "),self.remarksEntry)

        # self.topLayout.addItem(self.spaceItem)
        # self.topLayout.addRow(QLabel("Update to Database: "),self.saveDB)

        # self.bottomLayout.addWidget(self.addBtn)
        # self.bottomLayout.addWidget(self.clrBtn)
        # self.topLayout.addWidget(self.saveDB)
        self.bottomLayout.addWidget(self.buttonBox)
        self.topGroupBox.setLayout(self.topLayout)
        self.bottomGroupBox.setLayout(self.bottomLayout)

        # self.topFrame.setLayout(self.topLayout)
        #self.topGroupBox.add setLayout(self.topLayout)
        # self.bottomGroupBox.setLayout(self.bottomLayout)
        self.mainTopLayout.addWidget(self.topGroupBox)
        self.mainTopLayout.addWidget(self.saveDB)
        self.mainTopLayout.addWidget(self.bottomGroupBox)
        self.mainLayout.addLayout(self.mainTopLayout)
        self.setLayout(self.mainLayout)