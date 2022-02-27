# https://srinikom.github.io/pyside-docs/PySide/QtGui/QMessageBox.html
# https://gist.github.com/jsexauer/f2bb0cc876828b54f2ed
# import datetime
# import logging
# logger = logging.get#logger(__name__)
from datetime import datetime
import sys
import pandas as pd
from PyQt5.QtCore import Qt, QPoint, pyqtSlot, QTimer, QDateTime
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QTableView, QLabel, QMessageBox \
    , QVBoxLayout, QHBoxLayout, QGroupBox \
    , QGridLayout, QWidget, QAbstractItemView \
    , QHeaderView, QSplitter, QMenu, QAction

from mysql_tools.mysql_crud import mysql_table_crud
from mysql_tools.tables_and_headers import CURRENT_HOLDINGS_DB_TABLE_NAME, CURRENT_HOLDING_DB_HEADER
# from babel.numbers import format_currency
# from DataBase.mysql_crud import mysql_table_crud
# from GuiWidgets.gui_widgets_for_payin_new import new_Bill_payin as new_bill_payin
# from GuiWidgets.gui_widgets_for_payin_edit import edit_Bill_payin as edit_bill_payin
# from GuiWidgets.gui_widgets_for_payout_new import new_Bill_payout as new_bill_payout
# from GuiWidgets.gui_widgets_for_payout_edit import edit_Bill_payout as edit_Bill_payout
# from GuiWidgets.gui_widgets_read_name_mobile_no import get_name_mobile_no
#
# from DataBase.create_rk_db import search_data_by_given_options_payin, search_data_by_given_options_payout
# from DataBase.label_names import HEADER_PHARMACY_PAYIN, PHARAMACY_BILL_PAYIN_PREFIX, PHARAMACY_BILL_PAYOUT_PREFIX \
#     , HEADER_PHARMACY_PAYOUT, DEBIT_TITLE, CREDIT_TITLE, HEADER_PHARMACY_PAYOUT_DISAPLY, DATE_TIME, DATE_FMT_YMD, \
#     DATE_FMT_DMY \
#     , BILL_MODIFY_TYPE, HEADER_PHARMACY_PAYIN_DISAPLY, PAYIN_PHARMACY_TABLE_HEADER, PAYOUT_PHARMACY_TABLE_HEADER
#
# from DataBase.utilities import make_nested_dict, parse_str, TABLE_HEADER_FONT, TABLE_FONT, DUMMY_SPACE_FONT \
#     , RECEIPT_SUMMARY_TOTAL_FONT, RECEIPT_SUMMARY_LABEL_FONT \
#     , SUMMARY_GBOX_TITLE, PAYMENT_SUMMARY_TOTAL_FONT, PAYMENT_SUMMARY_LABEL_FONT \
#     , SUMMARY_RECPT_TITLE_COLOR, SUMMARY_PAYMT_TITLE_COLOR, SUMMARY_CASHBALANCE_TITLE_COLOR \
#     , CASH_BALANCE_SUMMARY_LABEL_FONT, CASH_BALANCE_SUMMARY_TOTAL_FONT

from utility.tableViewModel import pandasModel  # ,FloatDelegate
# from DataBase.ItemModel import ItemModelLineChart
# from DataBase.tableViewModel1 import pandasModel
# from DataBase.tableViewModel2 import PandasTableModel as  pandasModel
# from DataBase.label_names import DBNAME
import dateparser


class TimerMessageBox(QMessageBox):
    def __init__(self, timeout=3, titles="Wait..", displayInfo="Please Wait...", parent=None):
        super(TimerMessageBox, self).__init__(parent)
        self.msg = displayInfo
        self.ttl = titles
        self.setWindowTitle(self.ttl)
        self.time_to_wait = timeout
        self.setText(f"{self.msg} \n wait (closing automatically in {timeout} seconds.)")
        self.setStandardButtons(QMessageBox.NoButton)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

    def changeContent(self):
        self.setText(f"{self.msg} \n  wait (closing automatically in {self.time_to_wait} seconds.)")
        self.time_to_wait -= 1
        if self.time_to_wait <= 0:
            self.close()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()


class my_holdings(QWidget):
    def __init__(self, start_end_time, **mysql_data):
        super().__init__()
        # self.setWindowTitle("Investment")
        # self.setGeometry(450,150,750,600)
        # self.mysql_login = mysql_data[0]
        # self.mysql_passwd = mysql_data[1]
        # self.mysql_dbname = mysql_data[2]
        # self.mysql_hostname = mysql_data[3]
        # self.mysql_port =  mysql_data[4]

        self.bill_count = 0
        self.bill_count_payout = 0
        # self.usr = usrName
        self.start_end_time = start_end_time
        self.db_cfg = mysql_data
        # self.check = check
        # self.search_options = search_options
        self.UI()
        # self.showMaximized()
        # self.show()

    def UI(self):
        self.connect_to_tables()
        # self.widgets()
        # self.layouts()

    def connect_to_tables(self):

        self.payin_table = mysql_table_crud(db_table=CURRENT_HOLDINGS_DB_TABLE_NAME,
                                            db_header=CURRENT_HOLDING_DB_HEADER,
                                            **self.db_cfg)
        data = self.payin_table.read_row_by_column_values()
        # print(self.payin_table.table_view(data))

        # print(data)

        # self.payout_table = mysql_table_crud(db_table=PHARAMACY_BILL_PAYOUT_PREFIX,
        #                                      db_header=PAYOUT_PHARMACY_TABLE_HEADER,
        #                                      **self.db_cfg)
        #
        # mydata0 = search_data_by_given_options_payin(PHARAMACY_BILL_PAYIN_PREFIX, self.start_end_time[0],
        #                                              self.start_end_time[1],
        #                                              self.search_options)
        # mydata1 = search_data_by_given_options_payout(PHARAMACY_BILL_PAYOUT_PREFIX, self.start_end_time[0],
        #                                               self.start_end_time[1],
        #                                               self.search_options)
        #
        # # print(mydata0)
        # self.df_reception_payin = self.read_mysql_payin(mydata0)
        # self.df_reception_payout = self.read_mysql_payout(mydata1)

    def read_mysql_payin(self, mydata):
        rk_db, mssg = self.payin_table.db_connection()
        df_all = pd.read_sql(mydata, con=rk_db)
        df_all.columns = HEADER_PHARMACY_PAYIN
        df_display = df_all.drop(columns=['ID', 'User', 'Edit Info', "Mobile Number"])
        self.bill_count = len(df_display)
        return df_display

    def read_mysql_payout(self, mydata):
        rk_db, mssg = self.payin_table.db_connection()
        df_all = pd.read_sql(mydata, con=rk_db)
        df_all.columns = HEADER_PHARMACY_PAYOUT
        df_display = df_all.drop(columns=['ID', 'User', 'Edit Info', "Mobile Number"])
        self.bill_count_payout = len(df_display)
        return df_display

    def msg_info_db_read(self):
        msg = TimerMessageBox(4, "DB Read", "Reading database ...")
        # msg = QMessageBox.information(self, "Success !!!", "Database access complete..")
        msg.exec_()

    def quit_now(self):
        sys.exit(0)

    def widgets(self):

        self.dummy = QLabel('                 ')
        self.cash_payin_total_LABEL = QLabel('  Cash    :')
        self.creditnote_total_LABEL = QLabel('   Credit Note :')
        self.unpaid_total_LABEL = QLabel('   Unpaid        :')
        self.credit_card_total_LABEL = QLabel('   Credit Card :')
        self.debit_card_total_LABEL = QLabel('   Debit  Card :')
        self.eft_payin_total_LABEL = QLabel('   EFT         :')
        self.extra_payin_total_LABEL = QLabel('  Old Balance(Extra)  :')

        self.cash_payout_total_LABEL = QLabel('  Total Cash :')
        self.eft_payout_total_LABEL = QLabel('  EFT        :')

        self.dummy.setFont(DUMMY_SPACE_FONT)
        self.credit_card_total_LABEL.setFont(RECEIPT_SUMMARY_LABEL_FONT)
        self.debit_card_total_LABEL.setFont(RECEIPT_SUMMARY_LABEL_FONT)
        self.cash_payin_total_LABEL.setFont(RECEIPT_SUMMARY_LABEL_FONT)
        self.eft_payin_total_LABEL.setFont(RECEIPT_SUMMARY_LABEL_FONT)
        self.unpaid_total_LABEL.setFont(RECEIPT_SUMMARY_LABEL_FONT)
        self.creditnote_total_LABEL.setFont(RECEIPT_SUMMARY_LABEL_FONT)
        self.extra_payin_total_LABEL.setFont(RECEIPT_SUMMARY_LABEL_FONT)

        self.cash_payout_total_LABEL.setFont(PAYMENT_SUMMARY_LABEL_FONT)
        self.eft_payout_total_LABEL.setFont(PAYMENT_SUMMARY_LABEL_FONT)

        self.credit_card_total = QLabel("0")
        self.debit_card_total = QLabel("0")
        self.cash_payin_total = QLabel("0")
        self.eft_payin_total = QLabel("0")
        self.extra_payin_total = QLabel("0")
        self.unpaid_total = QLabel("0")
        self.creditnote_payin_totalCash = QLabel("0")

        self.credit_card_total.setFont(RECEIPT_SUMMARY_TOTAL_FONT)
        self.debit_card_total.setFont(RECEIPT_SUMMARY_TOTAL_FONT)
        self.cash_payin_total.setFont(RECEIPT_SUMMARY_TOTAL_FONT)
        self.eft_payin_total.setFont(RECEIPT_SUMMARY_TOTAL_FONT)
        self.unpaid_total.setFont(RECEIPT_SUMMARY_TOTAL_FONT)
        self.creditnote_payin_totalCash.setFont(RECEIPT_SUMMARY_TOTAL_FONT)
        self.extra_payin_total.setFont(RECEIPT_SUMMARY_TOTAL_FONT)

        self.cash_payout_total = QLabel("0")
        self.eft_payout_total = QLabel("0")

        self.cash_payout_total.setFont(PAYMENT_SUMMARY_TOTAL_FONT)
        self.eft_payout_total.setFont(PAYMENT_SUMMARY_TOTAL_FONT)

        self.total_transaction_receiptLabel = QLabel("     Total Transaction(Reciept): ")
        self.total_transaction_paymentLabel = QLabel("     Total Transaction(Payment): ")
        self.cash_balanceLabel = QLabel("     Available Cash: ")

        self.total_transaction_receipt = QLabel("0")
        self.total_transaction_payment = QLabel("0")
        self.cash_balance = QLabel("0")

        self.total_transaction_receiptLabel.setFont(CASH_BALANCE_SUMMARY_LABEL_FONT)
        self.total_transaction_paymentLabel.setFont(CASH_BALANCE_SUMMARY_LABEL_FONT)
        self.cash_balanceLabel.setFont(CASH_BALANCE_SUMMARY_LABEL_FONT)

        self.total_transaction_receipt.setFont(CASH_BALANCE_SUMMARY_TOTAL_FONT)
        self.total_transaction_payment.setFont(CASH_BALANCE_SUMMARY_TOTAL_FONT)
        self.cash_balance.setFont(CASH_BALANCE_SUMMARY_TOTAL_FONT)

        self.payinModel, self.payinTable = self.tableViewDataModel(self.df_reception_payin)
        self.payinModel.sort(1, Qt.AscendingOrder)
        # self.payinTable.setSortingEnabled(True)
        if self.check:
            self.payinTable.installEventFilter(self)
            self.payinTable.setContextMenuPolicy(Qt.CustomContextMenu)
            self.payinTable.customContextMenuRequested.connect(self.rightClickMenuPayIn)
            # self.payinTable.horizontalHeader().setStretchLastSection(True)
        # else:
        #
        #     self.payinTable.customContextMenuRequested.connect(self.rightClickMenuPayIn_opt)

        self.payoutModel, self.payoutTable = self.tableViewDataModel(self.df_reception_payout)
        self.payoutModel.sort(1, Qt.AscendingOrder)
        # self.payoutTable.setSortingEnabled(True)
        self.payoutTable.installEventFilter(self)
        if self.check:
            self.payoutTable.setContextMenuPolicy(Qt.CustomContextMenu)
            self.payoutTable.customContextMenuRequested.connect(self.rightClickMenuPayOut)
            # self.payoutTable.horizontalHeader().setStretchLastSection(True)
        # else:
        #     self.payinTable.customContextMenuRequested.connect(self.rightClickMenuPayout_opt)

        self.calculate_sum()

    def layouts(self):
        self.mainLayout = QVBoxLayout()
        self.horizontalSplitter = QSplitter(Qt.Horizontal)
        self.leftVsplitter = QSplitter(Qt.Vertical)
        self.rightVsplitter = QSplitter(Qt.Vertical)
        self.BottomLayout = QHBoxLayout()

        self.summary_payin = QGridLayout()
        self.summary_payin.setContentsMargins(0, 0, 0, 0)
        self.summary_payin.setSpacing(20)

        self.summary_payin.addWidget(self.dummy, 0, 0)
        self.summary_payin.addWidget(self.cash_payin_total_LABEL, 1, 0)
        self.summary_payin.addWidget(self.creditnote_total_LABEL, 2, 0)
        self.summary_payin.addWidget(self.unpaid_total_LABEL, 3, 0)
        self.summary_payin.addWidget(self.dummy, 4, 0)
        # self.summary_payin.setHorizontalSpacing()

        self.summary_payin.addWidget(self.dummy, 0, 1)
        self.summary_payin.addWidget(self.cash_payin_total, 1, 1, Qt.AlignLeft)
        self.summary_payin.addWidget(self.creditnote_payin_totalCash, 2, 1, Qt.AlignLeft)
        self.summary_payin.addWidget(self.unpaid_total, 3, 1, Qt.AlignLeft)
        self.summary_payin.addWidget(self.dummy, 4, 1)

        self.summary_payin.addWidget(self.dummy, 0, 2)
        self.summary_payin.addWidget(self.credit_card_total_LABEL, 1, 2)
        self.summary_payin.addWidget(self.debit_card_total_LABEL, 2, 2)
        self.summary_payin.addWidget(self.eft_payin_total_LABEL, 3, 2)
        self.summary_payin.addWidget(self.dummy, 4, 2)

        self.summary_payin.addWidget(self.dummy, 0, 3)
        self.summary_payin.addWidget(self.credit_card_total, 1, 3)
        self.summary_payin.addWidget(self.debit_card_total, 2, 3)
        self.summary_payin.addWidget(self.eft_payin_total, 3, 3)
        self.summary_payin.addWidget(self.dummy, 4, 3)

        self.summary_payin.addWidget(self.dummy, 0, 4)
        self.summary_payin.addWidget(self.extra_payin_total_LABEL, 1, 4)
        self.summary_payin.addWidget(self.dummy, 2, 4)
        self.summary_payin.addWidget(self.dummy, 3, 4)
        self.summary_payin.addWidget(self.dummy, 4, 4)

        self.summary_payin.addWidget(self.dummy, 0, 5)
        self.summary_payin.addWidget(self.extra_payin_total, 1, 5)
        self.summary_payin.addWidget(self.dummy, 2, 5)
        self.summary_payin.addWidget(self.dummy, 3, 5)
        self.summary_payin.addWidget(self.dummy, 4, 5)

        self.summary_payout = QGridLayout()
        self.summary_payout.setContentsMargins(0, 0, 0, 0)
        self.summary_payout.setSpacing(20)

        self.summary_payout.addWidget(self.dummy, 0, 0)
        self.summary_payout.addWidget(self.cash_payout_total_LABEL, 1, 0)
        self.summary_payout.addWidget(self.dummy, 2, 0)
        self.summary_payout.addWidget(self.eft_payout_total_LABEL, 3, 0)
        self.summary_payout.addWidget(self.dummy, 4, 0)
        # self.summary_payin.setHorizontalSpacing()

        self.summary_payout.addWidget(QLabel('            '), 0, 1)
        self.summary_payout.addWidget(self.cash_payout_total, 1, 1)
        self.summary_payout.addWidget(QLabel('              '), 2, 1)
        self.summary_payout.addWidget(self.eft_payout_total, 3, 1)
        self.summary_payout.addWidget(QLabel('            '), 4, 1)

        self.summary_cash_balance = QGridLayout()
        self.summary_cash_balance.addWidget(self.total_transaction_receiptLabel, 0, 1)
        self.summary_cash_balance.addWidget(self.total_transaction_paymentLabel, 1, 1)
        self.summary_cash_balance.addWidget(self.cash_balanceLabel, 2, 1)

        self.summary_cash_balance.addWidget(self.total_transaction_receipt, 0, 2)
        self.summary_cash_balance.addWidget(self.total_transaction_payment, 1, 2)
        self.summary_cash_balance.addWidget(self.cash_balance, 2, 2)

        self.overallsummaryGroupBox = QGroupBox(f"{DEBIT_TITLE} Summary")
        self.overallsummaryGroupBox.setLayout(self.summary_payin)
        self.overallsummaryGroupBox2 = QGroupBox(f"{CREDIT_TITLE} Summary")
        self.overallsummaryGroupBox2.setLayout(self.summary_payout)
        self.overallsummaryGroupBox3 = QGroupBox('Cash Balance')
        self.overallsummaryGroupBox3.setLayout(self.summary_cash_balance)

        self.overallsummaryGroupBox.setFont(SUMMARY_GBOX_TITLE)
        self.overallsummaryGroupBox.setStyleSheet(SUMMARY_RECPT_TITLE_COLOR)
        self.overallsummaryGroupBox2.setFont(SUMMARY_GBOX_TITLE)
        self.overallsummaryGroupBox2.setStyleSheet(SUMMARY_PAYMT_TITLE_COLOR)
        self.overallsummaryGroupBox3.setFont(SUMMARY_GBOX_TITLE)
        self.overallsummaryGroupBox3.setStyleSheet(SUMMARY_CASHBALANCE_TITLE_COLOR)

        self.BottomLayout.addWidget(self.overallsummaryGroupBox, 50)
        self.BottomLayout.addWidget(self.overallsummaryGroupBox2, 30)
        self.BottomLayout.addWidget(self.overallsummaryGroupBox3, 20)

        self.BottomWidget = QWidget()
        self.BottomWidget.setLayout(self.BottomLayout)

        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()
        self.leftTopGroupBox = QGroupBox(DEBIT_TITLE)
        self.rightTopGroupBox = QGroupBox(CREDIT_TITLE)

        fnt_GBox = QFont()
        fnt_GBox.setPointSize(14)
        fnt_GBox.setBold(True)
        fnt_GBox.setFamily("Arial")
        self.leftTopGroupBox.setFont(fnt_GBox)
        self.leftTopGroupBox.setStyleSheet('QGroupBox:title {color: green;}')
        self.rightTopGroupBox.setFont(fnt_GBox)
        self.rightTopGroupBox.setStyleSheet('QGroupBox:title {color: red;}')

        self.leftLayout.addWidget(self.payinTable)
        self.leftLayout.setContentsMargins(0, 0, 0, 0)
        self.rightLayout.addWidget(self.payoutTable)
        self.rightLayout.setContentsMargins(0, 0, 0, 0)

        self.leftTopGroupBox.setLayout(self.leftLayout)
        self.rightTopGroupBox.setLayout(self.rightLayout)

        self.leftVsplitter.addWidget(self.leftTopGroupBox)
        self.rightVsplitter.addWidget(self.rightTopGroupBox)

        self.horizontalSplitter.addWidget(self.leftVsplitter)
        self.horizontalSplitter.addWidget(self.rightVsplitter)
        self.horizontalSplitter.setStretchFactor(0, 3)
        self.horizontalSplitter.setStretchFactor(1, 2)
        self.horizontalSplitter.setContentsMargins(0, 0, 0, 0)
        # self.horizontalSplitter.handle(0)
        self.horizontalSplitter.handle(0)

        self.mainLayout.addWidget(self.horizontalSplitter, 94)
        self.mainLayout.addWidget(self.BottomWidget, 6)

        self.setLayout(self.mainLayout)

    def tableViewDataModel(self, data):

        # print(data.dtypes)
        # print(data.head(5).to_string())
        #
        # data['Date'] = pd.to_datetime(data['Date'], format="%d-%m-%y %H:%M:%S")
        # data['Date'] = data['Date'].dt.strftime("%d-%m-%y %H:%M:%S")
        # data.style.format({"Date": lambda t: t.strftime("%d-%m-%y %H:%M:%S")})
        # print(data.dtypes)
        Tview = QTableView()

        # fnt1 = QFont()
        # fnt1.setPointSize(10)
        # fnt1.setBold(True)
        # fnt1.setFamily("Arial")
        #
        # fnt2 = QFont()
        # fnt2.setPointSize(9)
        # # fnt2.setBold(True)
        # fnt2.setFamily("Arial")

        # https: // forum.qt.io / topic / 109144 / tableview -        not -updated - after - calling - datachanged / 11
        # self.model = pandasModel()
        # data.tableView.setModel(self.model)

        # size policy
        # Tview.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # Tview.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)(display doesnot fit to screen)
        #
        Tview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        Tview.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Tview.setWordWrap(True)

        Tview.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        Tview.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        Tview.setAlternatingRowColors(True)
        Tview.setSortingEnabled(True)
        Tview.setShowGrid(True)
        Tview.verticalHeader().setVisible(False)
        Tview.verticalHeader().hide()

        """
            Forbid resizing(speeds up)
        """
        header = Tview.horizontalHeader()
        header.setFont(TABLE_HEADER_FONT)
        header.setStyleSheet("color: blue;")
        Tview.setFont(TABLE_FONT)
        Tview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        Tmodel = pandasModel(data)
        # Tmodel.setHorizontalHeaderLabels(header_list)
        Tview.setModel(Tmodel)

        return Tmodel, Tview

    @pyqtSlot(QPoint)
    def rightClickMenuPayIn(self, pos):
        indexes = self.sender().selectedIndexes()
        mdlIdx = self.payinTable.indexAt(pos)
        row = self.payinTable.currentIndex().row()

        if not mdlIdx.isValid() and len(indexes) != 0:
            # print("return")
            return
        elif len(indexes) == 0 and not mdlIdx.isValid():
            # print("new..")
            self.menu_payin = QMenu(self)
            newAct = QAction(QIcon(""), "New", self, triggered=self.newBill_payin)
            # newAct.setShortcut(QKeySequence("Ctrl+N"))
            addAct = self.menu_payin.addAction(newAct)

        else:
            self.menu_payin = QMenu(self)
            newAct = QAction(QIcon(""), "New", self, triggered=self.newBill_payin)
            # newAct.setShortcut(QKeySequence("Ctrl+N"))
            # updateAct = QAction(QIcon(""), "Update", self, triggered=self.updateBill_payin)
            replaceAct = QAction(QIcon(""), "Edit", self, triggered=self.replaceBill_payin)
            duelistAct = QAction(QIcon(""), "Register Unpaid", self, triggered=self.move_to_unpaid_payin)
            deleteAct = QAction(QIcon(""), "Delete", self, triggered=self.deleteBill)
            # remAct.setStatusTip('Delete stock from database')
            # showAct = QAction(QIcon(""), 'Show', self, triggered=self.showBill)
            addAct = self.menu_payin.addAction(newAct)
            # editStk = self.menu_payin.addAction(updateAct)
            editStk = self.menu_payin.addAction(replaceAct)
            editStk = self.menu_payin.addAction(duelistAct)
            dispStk = self.menu_payin.addAction(deleteAct)
            # avgStk = self.menu_payin.addAction(showAct)
            self.menu_payin.addSeparator()

        self.menu_payin.exec_(self.sender().viewport().mapToGlobal(pos))

    def move_to_unpaid_payin(self):
        # print("Moving to unpaid list")

        abc = self.payin_table.read_row_by_column_values(criteria=f"pay_unpaid>0 and mobile_no is not null")
        list_of_unpaid = []
        for item in abc:
            id = f"{item['patient_name']}_{item['mobile_no']}"
            list_of_unpaid.append(id)
        list_of_unpaid.append("Others")

        # fetch data from mysql
        index = self.payinTable.currentIndex().row()
        ncol = self.payinModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.payinTable.model().index(index, col).data()
            row_data.append(val)

        date_time = datetime.strptime(row_data[1], DATE_FMT_DMY)
        date_time = datetime.strftime(date_time, DATE_FMT_YMD)
        date_time_bill_no = f"date_time = '{date_time}'  and  bill_no = '{row_data[0]}'"
        row_data_db = self.payin_table.read_row_by_column_values(criteria=date_time_bill_no)[0]
        # print(row_data_db)
        mob_no = row_data_db['mobile_no']
        if mob_no:
            # print(f"mob:{mob_no}")
            QMessageBox.information(self, 'Aborted !!',
                                    f'A bill already registered  with mobile number {mob_no}')
            return

        if row_data_db['pay_unpaid'] == 0:
            QMessageBox.information(self, 'Incorrect !!',
                                    f'There is no unpaid amount in selected  transaction/bill..')
        else:
            # process data
            # row_data_db = row_data_db[0]
            id = row_data_db['id']
            billNo = row_data_db['bill_no']
            date0 = str(row_data_db['date_time'])
            old_biller = row_data_db['user']
            pname = row_data_db['patient_name']
            mobile_number = 123456789
            headers = self.payin_table.db_header
            name_mobile_inp = get_name_mobile_no(pname)
            if name_mobile_inp.exec_() == name_mobile_inp.Accepted:
                pnameNew, mobile_number = name_mobile_inp.get_inp()
                if pnameNew.strip() == "":
                    pnameNew = pname
                # print(pnameNew, mobile_number)
                new_id = f"{pnameNew}_{mobile_number}"
                if new_id not in list_of_unpaid:
                    row_data_db['mobile_no'] = mobile_number.strip()
                    row_data_db['patient_name'] = pnameNew.strip()
                    set_list = ""
                    for k, v in row_data_db.items():
                        if k != 'id':
                            set_list = f"{set_list},{k}='{v}'"
                    set_list = set_list[1:]
                    messge = self.payin_table.update_rows_by_column_values(set_argument=set_list, criteria=f"id='{id}'")
                    # print(messge)
                    #
                    # print(type(self.df_reception_payin))
                    # print(self.df_reception_payin.columns)

                    mask1 = self.df_reception_payin["Bill Number"] == billNo
                    mask2 = self.df_reception_payin["Date"] == date0
                    index = self.df_reception_payin[mask1 & mask2].index
                    # self.df_reception_payin.drop(index, axis=0, inplace=True)
                    # print(index)
                    # print(self.df_reception_payin.iloc[index])
                    self.df_reception_payin.loc[index, ["Patient Name"]] = pnameNew
                    self.payinModel.update(self.df_reception_payin, key="New")
                    self.payinModel.layoutChanged.emit()
                    self.payinTable.clearSelection()
                else:
                    QMessageBox.information(self, 'Aborted !!',
                                            f'A bill already registered by the name {new_id}')

    def newBill_payin(self):

        bill_no_list = self.df_reception_payin["Bill Number"].to_list()
        bill_no_list = list(map(int, bill_no_list))
        # print(len(bill_no_list))
        if len(bill_no_list) == 0:
            bill_no_max = 0
        else:
            bill_no_max = max(bill_no_list)

        newBillGen = make_nested_dict()
        for key in PAYIN_PHARMACY_TABLE_HEADER:
            newBillGen[key] = None

        newBill_inp = new_bill_payin(bill_no_max, bill_no_list, newBillGen, pharmacy=True)
        if newBill_inp.exec_() == newBill_inp.Accepted:
            newBill_row, bill_count = newBill_inp.get_inp()
            dateNow = str(QDateTime.currentDateTime().toString(DATE_TIME))
            newBill_row['id'] = 0
            newBill_row['bill_no'] = parse_str(bill_count)
            newBill_row['date_time'] = dateparser.parse(dateNow)
            newBill_row['user'] = self.usr
            newBill_row['edit_info'] = self.usr
            # newBill_row['mobile_no'] = ""
            df_row = pd.DataFrame([newBill_row])
            listt = list(newBill_row.values())
            vals_tuple = [tuple(listt)]
            df_row.columns = HEADER_PHARMACY_PAYIN
            df_row = df_row.drop(columns=['ID', 'User', 'Edit Info', "Mobile Number"])
            messge = self.payin_table.insert_row_by_column_values(row_val=vals_tuple)

            # QMessageBox.information(self, 'New bill !!',f'{messge}')

            self.df_reception_payin = pd.concat([df_row, self.df_reception_payin]).reset_index(drop=True)
            self.payinModel.update(self.df_reception_payin, key="New")
            self.payinModel.layoutChanged.emit()
            self.payinTable.clearSelection()
            # self.payinModel(self.df_reception_payin)

            # # tableviewmodel
            # nrow = self.payinModel.rowCount()
            # # print("#",rows)
            # # data = pd.DataFrame(data=new_row)
            # self.df_reception_payin.loc[nrow] = list(new_row)
            # self.payinModel.appendRowData(new_row)

            self.calculate_sum()

    # BILL_MODIFY_TYPE = ["Update", "Replace"]
    def updateBill_payin(self):
        self.modify_payin_bill(BILL_MODIFY_TYPE[0])

    def replaceBill_payin(self):
        self.modify_payin_bill(BILL_MODIFY_TYPE[1])

    def modify_payin_bill(self, updateType):

        bill_no_list = self.df_reception_payin["Bill Number"].to_list()
        bill_no_list = list(map(int, bill_no_list))
        # print(len(bill_no_list))
        if len(bill_no_list) == 0:
            bill_no_max = 0
        else:
            bill_no_max = max(bill_no_list)

        # fetch data from mysql
        index = self.payinTable.currentIndex().row()
        ncol = self.payinModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.payinTable.model().index(index, col).data()
            row_data.append(val)

        date_time = datetime.strptime(row_data[1], DATE_FMT_DMY)
        date_time = datetime.strftime(date_time, DATE_FMT_YMD)

        date_time_bill_no = f"date_time = '{date_time}'  and  bill_no = '{row_data[0]}'"
        row_data_db = self.payin_table.read_row_by_column_values(criteria=date_time_bill_no)[0]

        # process data
        # row_data_db = list(row_data_db[0])
        # print(row_data_db)
        id = row_data_db['id']
        billNo = row_data_db['bill_no']
        date0 = str(row_data_db['date_time'])
        old_biller = row_data_db['user']

        # print("$", row_data_db)
        amount_prev = f"Rs:{row_data_db['pay_cash']},CC:{row_data_db['pay_credit_card']},DC:{row_data_db['pay_debit_card']},EFT:{row_data_db['pay_eft']}"

        # row_data_db.pop(11)
        # row_data_db.pop(2)
        # row_data_db.pop(0)

        editBill_inp = edit_bill_payin(row_data_db, bill_no_list, updateType, pharmacy=True)
        if editBill_inp.exec_() == editBill_inp.Accepted:
            newBill_row, bill_count = editBill_inp.get_inp()
            # print("#",newBill_row)
            if updateType == BILL_MODIFY_TYPE[1]:
                message = self.payin_table.delete_row_by_column_values(criteria=date_time_bill_no)
                # QMessageBox.information(self, 'Replaced !!',
                #                         f'Selected  transaction information replaced with latest data')
                # print(query)
                # print("delete",message)

            # keys = list(newBill_row.keys())
            # keys.insert(0, "id")
            # keys.insert(1, "bill_no")
            # keys.insert(2, "user")
            # keys.insert(11, "edit_info")
            # kys = list(keys)

            dateNow = str(QDateTime.currentDateTime().toString(DATE_TIME))
            # print(date0)
            # print(dateNow)
            editInfo = f"{self.usr},Time{date0}:{old_biller}={amount_prev}"
            newBill_row['id'] = 0
            newBill_row['bill_no'] = parse_str(bill_count)
            newBill_row['date_time'] = dateparser.parse(dateNow)
            newBill_row['user'] = self.usr
            newBill_row['edit_info'] = editInfo

            # vals = list(newBill_row.values())
            # vals.insert(0, 0)
            # vals.insert(1, bill_count)
            # vals.insert(2, self.usr)
            # vals.insert(11, self.usr)
            # vals.pop(3)
            # vals.insert(3, dateNow)
            #
            # vals[11] = editInfo
            #
            # vals = tuple(vals)
            # vals_tuple = vals
            # # print(vals_tuple)

            # new_row = list(vals)
            # new_row.pop(11)
            # new_row.pop(2)
            # new_row.pop(0)
            # new_row.pop(1)
            # new_row.insert(1, dateNow)

            # new_row[0] = parse_str(new_row[0])
            # print(type(newBill_row))

            df_row = pd.DataFrame([newBill_row])
            # print(df_row.iloc[0])
            # listt= list(df_row.iloc[0])
            listt = list(newBill_row.values())

            # print(type(listt))
            vals_tuple = [tuple(listt)]
            # print(vals_tuple)
            df_row.columns = HEADER_PHARMACY_PAYIN
            df_row = df_row.drop(columns=['ID', 'User', 'Edit Info', "Mobile Number"])

            # print(df_row.to_string())
            # print(self.df_reception_payin.to_string())

            # print(type(df_row['date_time']))
            # print(df_row['date_time'])

            # row_dict = make_nested_dict()
            # for k, v in zip(HEADER_RECPT_PAYIN_DISAPLY, new_row):
            #     row_dict[k] = [v]            #
            # df_row = pd.DataFrame(row_dict)
            self.df_reception_payin = pd.concat([df_row, self.df_reception_payin]).reset_index(drop=True)

            # if updateType == "Update":
            #                     payin.insert_row_by_column_values(row_val=row_val)
            # vals_tuple=tuple([0, 3, 'kiran', '2021-06-06 17:50:38', 's', 'OPD', 5.0, 5.0, 0.0, 0.0, 0.0,'kiran,Time2021-06-06 16:46:41:kiran=Rs:1.0,CC:0.0,DC:0.0,EFT:0.0', 'a'])

            messge = self.payin_table.insert_row_by_column_values(row_val=vals_tuple)
            # print("insert=>",messge)

            if updateType == BILL_MODIFY_TYPE[1]:
                mask1 = self.df_reception_payin["Bill Number"] == billNo
                mask2 = self.df_reception_payin["Date"] == date0
                index = self.df_reception_payin[mask1 & mask2].index
                self.df_reception_payin.drop(index, axis=0, inplace=True)

            self.payinModel.update(self.df_reception_payin, key=updateType)
            self.payinModel.layoutChanged.emit()
            self.payinTable.clearSelection()

            # # tableviewmodel
            # # rows = self.payinModel.rowCount()
            # self.df_reception_payin.loc[index] = list(new_row)
            # self.payinModel.sort(1, Qt.AscendingOrder)
            # self.payinModel.appendRowData(new_row)
            self.calculate_sum()

    def deleteBill(self):
        bill_no_list = self.df_reception_payin["Bill Number"].to_list()
        bill_no_list = list(map(int, bill_no_list))
        # print(len(bill_no_list))
        if len(bill_no_list) == 0:
            bill_no_max = 0
        else:
            bill_no_max = max(bill_no_list)

        # fetch data from mysql
        index = self.payinTable.currentIndex().row()
        ncol = self.payinModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.payinTable.model().index(index, col).data()
            row_data.append(val)

        date_time = datetime.strptime(row_data[1], DATE_FMT_DMY)
        date_time = datetime.strftime(date_time, DATE_FMT_YMD)
        date_time_bill_no = f"date_time = '{date_time}'  and  bill_no = '{row_data[0]}'"
        row_data_db = self.payin_table.read_row_by_column_values(criteria=date_time_bill_no)[0]
        # print(row_data_db)
        # process data
        # row_data_db = row_data_db[0]
        id = row_data_db['id']
        billNo = row_data_db['bill_no']
        date0 = str(row_data_db['date_time'])
        old_biller = row_data_db['user']

        msgBox = QMessageBox()
        msgBox.setWindowTitle("Warning")
        msgBox.setText(f"Are you sure to delete transaction information with Serial number {billNo} ?")
        msgBox.setInformativeText(f"Transaction  information will be \npermanatly removed from the database !")
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        buttonY = msgBox.button(QMessageBox.Yes)
        buttonY = msgBox.button(QMessageBox.Yes)
        # buttonY.setText('Evet')
        # buttonN = box.button(QtGui.QMessageBox.No)
        # buttonN.setText('Iptal')
        msgBox.exec_()

        if msgBox.clickedButton() == buttonY:
            message = self.payin_table.delete_row_by_column_values(criteria=date_time_bill_no)
            mask1 = self.df_reception_payin["Bill Number"] == billNo
            mask2 = self.df_reception_payin["Date"] == date0
            index = self.df_reception_payin[mask1 & mask2].index
            self.df_reception_payin.drop(index, axis=0, inplace=True)
            self.payinModel.update(self.df_reception_payin, key="Delete")
            self.payinModel.layoutChanged.emit()
            self.payinTable.clearSelection()
            QMessageBox.information(self, 'Deleted !!',
                                    f'Selected  transaction (Serial No:{billNo}) has been deleted')
        else:
            # msgBox = QMessageBox()
            # msgBox.setWindowTitle("Aborted")
            # msgBox.setText("Selected  transaction (Serial No: " + billNo + ") has not been deleted")
            # msgBox.setIcon(QMessageBox.Information)
            # msgBox.exec_()
            QMessageBox.information(self, 'Aborted !!',
                                    f'Selected  transaction (Serial No:{billNo}) has not been deleted')

        self.calculate_sum()

    def showBill(self):
        pass

    @pyqtSlot(QPoint)
    def rightClickMenuPayOut(self, pos):
        indexes = self.sender().selectedIndexes()
        mdlIdx = self.payoutTable.indexAt(pos)
        row = self.payoutTable.currentIndex().row()

        if not mdlIdx.isValid() and len(indexes) != 0:
            return
        elif len(indexes) == 0 and not mdlIdx.isValid():
            self.menu = QMenu(self)
            newAct = QAction(QIcon(""), "New", self, triggered=self.newBill_payout)
            addAct = self.menu.addAction(newAct)
        else:
            self.menu = QMenu(self)
            newAct = QAction(QIcon(""), "New", self, triggered=self.newBill_payout)
            # updateAct = QAction(QIcon(""), "Update", self, triggered=self.updateBill_payout)
            replaceAct = QAction(QIcon(""), "Edit", self, triggered=self.replaceBill_payout)
            deleteAct = QAction(QIcon(""), "Delete", self, triggered=self.deleteBill_payout)
            # showAct = QAction(QIcon(""), 'Show', self, triggered=self.showBill_payout)
            addAct = self.menu.addAction(newAct)
            # editStk = self.menu.addAction(updateAct)
            editStk = self.menu.addAction(replaceAct)
            dispStk = self.menu.addAction(deleteAct)
            # avgStk = self.menu.addAction(showAct)
            self.menu.addSeparator()
        self.menu.exec_(self.sender().viewport().mapToGlobal(pos))

    def newBill_payout(self):

        newBillGen = make_nested_dict()
        for key in PAYOUT_PHARMACY_TABLE_HEADER:
            newBillGen[key] = None

        newBill_inp = new_bill_payout(self.bill_count_payout, newBillGen, pharmacy=True)
        if newBill_inp.exec_() == newBill_inp.Accepted:
            newBill_row = newBill_inp.get_inp()
            self.bill_count_payout = self.bill_count_payout + 1
            dateNow = str(QDateTime.currentDateTime().toString(DATE_TIME))
            newBill_row['id'] = 0
            newBill_row['bill_no'] = parse_str(self.bill_count_payout)
            newBill_row['date_time'] = dateparser.parse(dateNow)
            newBill_row['user'] = self.usr
            newBill_row['edit_info'] = self.usr
            df_row = pd.DataFrame([newBill_row])
            listt = list(newBill_row.values())

            # print(listt)
            vals_tuple = [tuple(listt)]
            df_row.columns = HEADER_PHARMACY_PAYOUT
            df_row = df_row.drop(columns=['ID', 'User', 'Edit Info', "Mobile Number"])
            messge = self.payout_table.insert_row_by_column_values(row_val=vals_tuple)

            self.df_reception_payout = pd.concat([df_row, self.df_reception_payout]).reset_index(drop=True)
            # self.payoutTable.model().insertRow(0)
            self.payoutModel.update(self.df_reception_payout, key="New")
            self.payoutModel.layoutChanged.emit()
            # self.payoutTable.clearSelection()

            self.calculate_sum()

    # BILL_MODIFY_TYPE = ["Update", "Replace"]
    def updateBill_payout(self):
        self.modify_payout_bill(BILL_MODIFY_TYPE[0])

    def replaceBill_payout(self):
        self.modify_payout_bill(BILL_MODIFY_TYPE[1])

    def modify_payout_bill(self, updateType):
        row_no = self.payoutTable.currentIndex().row()
        ncol = self.payoutModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.payoutTable.model().index(row_no, col).data()
            row_data.append(val)

        date_time = datetime.strptime(row_data[1], DATE_FMT_DMY)
        date_time = datetime.strftime(date_time, DATE_FMT_YMD)
        date_time_bill_no = f"date_time = '{date_time}'  and  bill_no = '{row_data[0]}'"
        row_data_db = self.payout_table.read_row_by_column_values(criteria=date_time_bill_no)[0]

        # print("$",row_data_db)
        id = row_data_db['id']
        billNo = row_data_db['bill_no']
        date0 = str(row_data_db['date_time'])
        old_biller = row_data_db['user']
        amount_prev = f"Rs:{row_data_db['pay_cash']},EFT:{row_data_db['pay_eft']}"

        editBill_inp = edit_Bill_payout(row_data_db, updateType, pharmacy=True)
        if editBill_inp.exec_() == editBill_inp.Accepted:
            newBill_row = editBill_inp.get_inp()
            # print(newBill_row)
            if updateType == BILL_MODIFY_TYPE[1]:
                message = self.payout_table.delete_row_by_column_values(criteria=date_time_bill_no)

            dateNow = str(QDateTime.currentDateTime().toString(DATE_TIME))
            editInfo = f"{self.usr},Time{date0}:{old_biller}={amount_prev}"
            newBill_row['id'] = 0
            newBill_row['bill_no'] = parse_str(billNo)
            newBill_row['date_time'] = dateparser.parse(dateNow)
            newBill_row['user'] = self.usr
            newBill_row['edit_info'] = editInfo

            df_row = pd.DataFrame([newBill_row])
            listt = list(newBill_row.values())
            # print(type(listt))
            vals_tuple = [tuple(listt)]
            # print(vals_tuple)
            df_row.columns = HEADER_PHARMACY_PAYOUT

            df_row = df_row.drop(columns=['ID', 'User', 'Edit Info', "Mobile Number"])
            self.df_reception_payout = pd.concat([df_row, self.df_reception_payout]).reset_index(drop=True)

            # if updateType == "Update":
            messge = self.payout_table.insert_row_by_column_values(row_val=vals_tuple)

            if updateType == BILL_MODIFY_TYPE[1]:
                mask1 = self.df_reception_payout["Serial Number"] == billNo
                mask2 = self.df_reception_payout["Date"] == date0
                index = self.df_reception_payout[mask1 & mask2].index
                self.df_reception_payout.drop(index, axis=0, inplace=True)
                # self.payoutTable.model().removeRow(row_no)

            self.payoutModel.update(self.df_reception_payout, key=updateType)
            self.payoutModel.layoutChanged.emit()
            self.payoutTable.clearSelection()

            self.calculate_sum()

    def deleteBill_payout(self):
        bill_no_list = self.df_reception_payout["Serial Number"].to_list()
        bill_no_list = list(map(int, bill_no_list))
        # print(len(bill_no_list))
        if len(bill_no_list) == 0:
            bill_no_max = 0
        else:
            bill_no_max = max(bill_no_list)

        # fetch data from mysql
        row_no = self.payoutTable.currentIndex().row()
        ncol = self.payoutModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.payoutTable.model().index(row_no, col).data()
            row_data.append(val)

        date_time = datetime.strptime(row_data[1], DATE_FMT_DMY)
        date_time = datetime.strftime(date_time, DATE_FMT_YMD)
        date_time_bill_no = f"date_time = '{date_time}'  and  bill_no = '{row_data[0]}'"
        row_data_db = self.payout_table.read_row_by_column_values(criteria=date_time_bill_no)[0]

        # process data
        id = row_data_db['id']
        billNo = row_data_db['bill_no']
        date0 = str(row_data_db['date_time'])
        old_biller = row_data_db['user']

        msgBox = QMessageBox()
        msgBox.setWindowTitle("Warning")
        msgBox.setText(f"Are you sure to delete transaction information with Serial number {billNo} ?")
        msgBox.setInformativeText(f"Transaction  information will be \npermanatly removed from the database !")
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        buttonY = msgBox.button(QMessageBox.Yes)
        buttonY = msgBox.button(QMessageBox.Yes)
        # buttonY.setText('Evet')
        # buttonN = box.button(QtGui.QMessageBox.No)
        # buttonN.setText('Iptal')
        msgBox.exec_()

        if msgBox.clickedButton() == buttonY:
            message = self.payout_table.delete_row_by_column_values(criteria=date_time_bill_no)

            mask1 = self.df_reception_payout["Serial Number"] == billNo
            mask2 = self.df_reception_payout["Date"] == date0
            index = self.df_reception_payout[mask1 & mask2].index
            self.df_reception_payout.drop(index, axis=0, inplace=True)
            # print("#",len(self.payoutTable))
            # self.payoutTable.model().removeRow(row_no)
            self.payoutModel.layoutChanged.emit()
            self.payoutTable.clearSelection()
            self.payoutTable.model().update(self.df_reception_payout, key="Delete")

            QMessageBox.information(self, 'Deleted !!',
                                    f'Selected  transaction (Serial No:{billNo}) has been deleted')
        else:
            # msgBox = QMessageBox()
            # msgBox.setWindowTitle("Aborted")
            # msgBox.setText("Selected  transaction (Serial No: " + billNo + ") has not been deleted")
            # msgBox.setIcon(QMessageBox.Information)
            # msgBox.exec_()
            QMessageBox.information(self, 'Aborted !!',
                                    f'Selected  transaction (Serial No:{billNo}) has not been deleted')

        self.calculate_sum()

    def showBill_payout(self):
        pass

    def calculate_sum(self):
        # df_pharmacy=pd.DataFrame()
        df_pharmacy = self.df_reception_payin[self.df_reception_payin['Department'].str.contains("Pharmacy")]
        df_extra = self.df_reception_payin[self.df_reception_payin['Department'].str.contains("Extra Balance")]
        # print(df_pharmacy.to_string())
        # print()
        credit_card = "{:.{}f}".format(self.df_reception_payin["CreditCard"].sum(), 3)
        debit_card = "{:.{}f}".format(self.df_reception_payin["DebitCard"].sum(), 3)
        cash_payin = "{:.{}f}".format(self.df_reception_payin["Cash"].sum(), 3)
        unpaid = "{:.{}f}".format(self.df_reception_payin["Unpaid"].sum(), 3)
        eft_payin = "{:.{}f}".format(self.df_reception_payin["EFT"].sum(), 3)
        credit_notes = "{:.{}f}".format(self.df_reception_payin["CreditNote"].sum(), 3)
        # print(df_extra.to_string())
        col_list = ["Cash", "CreditCard", "DebitCard", "EFT"]
        extra_cash = 0.0
        for col in col_list:
            extra_cash = extra_cash + df_extra[col].sum(axis=0)
        extra_cash = "{:.{}f}".format(extra_cash, 3)
        # print(extra_cash)
        # df_extra['Sum'] = df_extra.iloc[col_list].sum()
        # print(df_extra.to_string())
        # extra_cash = 0  # "{:.{}f}".format(df_extra['Sum'].sum(axis=0), 3)
        pharmacy_cash = "{:.{}f}".format(df_pharmacy["Cash"].sum(), 3)
        # extra_cash = "{:.{}f}".format(df_extra["Cash", "CreditCard", "DebitCard", "EFT"].sum(axis=1), 3)

        cash_payout = "{:.{}f}".format(self.df_reception_payout["Cash"].sum(), 3)
        eft_payout = "{:.{}f}".format(self.df_reception_payout["EFT"].sum(), 3)

        # print(self.df_reception_payout.to_string())
        # print(credit_notes)
        cash_balanceFinal = float(cash_payin) - float(cash_payout) - float(credit_notes)
        total_transaction_reciept = float(cash_payin) + float(credit_card) + float(debit_card) + float(
            eft_payin) - float(credit_notes)
        total_transaction_payment = float(cash_payout) + float(eft_payout)

        # print(cash_balanceFinal,total_transaction_reciept)

        self.credit_card_total.setText(format_currency(credit_card, 'INR', locale='en_IN'))
        self.debit_card_total.setText(format_currency(debit_card, 'INR', locale='en_IN'))
        self.cash_payin_total.setText(format_currency(cash_payin, 'INR', locale='en_IN'))
        self.unpaid_total.setText(format_currency(unpaid, 'INR', locale='en_IN'))
        self.eft_payin_total.setText(format_currency(eft_payin, 'INR', locale='en_IN'))
        self.creditnote_payin_totalCash.setText(format_currency(credit_notes, 'INR', locale='en_IN'))
        self.extra_payin_total.setText(format_currency(extra_cash, 'INR', locale='en_IN'))

        self.cash_payout_total.setText(format_currency(cash_payout, 'INR', locale='en_IN'))
        self.eft_payout_total.setText(format_currency(eft_payout, 'INR', locale='en_IN'))

        self.total_transaction_receipt.setText(format_currency(total_transaction_reciept, 'INR', locale='en_IN'))
        self.total_transaction_payment.setText(format_currency(total_transaction_payment, 'INR', locale='en_IN'))
        self.cash_balance.setText(format_currency(cash_balanceFinal, 'INR', locale='en_IN'))

        self.credit_card_total.setStyleSheet('color: blue')
        self.debit_card_total.setStyleSheet('color: blue')
        self.cash_payin_total.setStyleSheet('color: blue')
        self.unpaid_total.setStyleSheet('color: red')
        self.eft_payin_total.setStyleSheet('color: blue')
        self.extra_payin_total.setStyleSheet('color: blue')

        self.cash_payout_total.setStyleSheet('color: blue')
        self.eft_payout_total.setStyleSheet('color: blue')

        self.cash_balance.setStyleSheet('color: green')
        self.total_transaction_receipt.setStyleSheet('color: green')
        self.total_transaction_payment.setStyleSheet('color: red')
        self.creditnote_payin_totalCash.setStyleSheet('color: green')
        self.creditnote_payin_totalCash.setStyleSheet('color: green')

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     model = pandasModel(df)
#     view = QTableView()
#     view.setModel(model)
#     view.resize(800, 600)
#     view.show()
#     sys.exit(app.exec_())
