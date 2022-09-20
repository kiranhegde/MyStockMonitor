import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QPoint, pyqtSlot
from PyQt5.QtCore import Qt, QRegExp, QDate
from PyQt5.QtGui import QIcon, QRegExpValidator
import pandas as pd

from babel.numbers import format_currency
# from Purchase.purchase import  make_nested_dict0,get_nested_dist_value,parse_str,table_sort_color
# from db_management import read_all_transaction,save_transactionDB,delTransDB,gen_id
from utility.utility_functions import make_nested_dict, get_nested_dist_value, parse_str, gen_id, \
    extablish_db_connection
from mysql_tools.tables_and_headers import BANK_TRANSACTIONS_DB_TO_DISPLAY, \
    BANK_TRANSACTIONS_DB_TABLE_NAME, BANK_TRANSACTIONS_DB_HEADER, BANK_TRANSACTIONS_DISPLAY,BANK_TRANSACTIONS_HEADER
from mysql_tools.mysql_crud import mysql_table_crud
from share.libnames import AGENCY_LIST,TRANS_TYPE_LIST
from utility.tableViewModel import pandasModel
from utility.fonts_style import TABLE_HEADER_FONT, TABLE_FONT
from utility.date_time import DATE_TIME1,DATE_FMT_DMY


class show_transactions(QDialog):

    def __init__(self, parent=None, **mysql_data):
        super(show_transactions, self).__init__().__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)

        # self.setWindowTitle("Balance test")
        self.db_cfg = mysql_data

        self.setWindowTitle("Transaction Details")
        # self.setWindowIcon(QIcon('icons/icon.ico'))
        self.setGeometry(350, 350, 1150, 600)
        # self.setFixedSize(self.size())
        # self.stock_id=stock_id
        # self.stock_info=stock_info
        self.UI()
        self.show()
        # self.showMaximized()

    def UI(self):
        # self.table_header_info()
        self.connect_to_db_tables()
        self.transactions_df = self.transaction_history()
        # print(self.transactions_df.head(10).to_string())
        # exit()

        self.widgets()
        self.layouts()

    def connect_to_db_tables(self):
        self.transctions_details = mysql_table_crud(db_table=BANK_TRANSACTIONS_DB_TABLE_NAME,
                                                    db_header=BANK_TRANSACTIONS_DB_HEADER,
                                                    **self.db_cfg)

    def transaction_history(self):
        transactions_df = self.get_all_transaction_details()
        # data = self.transctions_details.read_row_by_column_values()
        # transactions_df = pd.DataFrame(data)
        transactions_df.sort_values(by="Date", ascending=True, inplace=True)
        transactions_df["Date"] = pd.to_datetime(transactions_df["Date"])
        # start_date = transactions_df["Date"].min()
        # col_list = transactions_df.columns.to_list()
        # start_date = pd.to_datetime(start_date)
        # end_date = datetime.datetime.now().date()
        #
        # date_range = [pd.date_range(start_date, end_date, freq='D')]
        # df = pd.DataFrame(index=date_range, columns=col_list)
        #
        # df.fillna(0, inplace=True)
        # df.rename_axis("Date", inplace=True)
        # df.drop(["Date", 'Agency'], axis=1, inplace=True)
        # df.reset_index(inplace=True)
        # # print(df.head(3).to_string())
        # # print(df.tail(3).to_string())
        # # print(df.info())
        # # print(transactions_df.info())
        # transactions_df = pd.concat([transactions_df, df]).groupby(['Date']).sum().reset_index()
        # # print(transactions_df.isna().any())
        # # exit()
        # transactions_df['Cumulative_Amount'] = transactions_df['Amount'].cumsum()
        #
        # # print(transactions_df.to_string())
        return transactions_df

    def get_all_transaction_details(self):
        data = self.transctions_details.read_row_by_column_values()
        transaction_df = pd.DataFrame(data)
        col_name = list(transaction_df.columns)
        col_drop_list = []
        for hdr_name in col_name:
            if hdr_name not in BANK_TRANSACTIONS_DISPLAY:
                col_drop_list.append(hdr_name)

        col_hdr_list = []
        for hdr_name in BANK_TRANSACTIONS_DISPLAY:
            col_hdr_list.append(BANK_TRANSACTIONS_DB_TO_DISPLAY[hdr_name])

        transaction_df.drop(col_drop_list, axis=1, inplace=True)
        transaction_df.columns = col_hdr_list

        return transaction_df

    def tableViewDataModel(self, data):

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

    def widgets(self):
        # self.data_plot_browser = QtWebEngineWidgets.QWebEngineView(self)
        # self.current_holding_data_df.columns = CURRENT_HOLDINGS_HEADER_DISPLAY_LIST
        self.transactionsModel, self.transactionsTable = self.tableViewDataModel(self.transactions_df)
        self.transactionsModel.sort(2, Qt.AscendingOrder)
        self.transactionsTable.installEventFilter(self)
        # self.holdingTable.hideColumn(0)
        self.transactionsTable.setColumnHidden(0,True)
        self.transactionsTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.transactionsTable.customContextMenuRequested.connect(self.rightClickMenu)

        self.agencyName="Summary"

    def layouts(self):
        # pass
        self.mainLayout = QVBoxLayout()
        self.horizontalSplitter = QSplitter(Qt.Horizontal)
        self.rightLayout = QVBoxLayout()
        self.rightWidget = QWidget()

        # self.agency_summaryLayout = QGridLayout()
        # self.agency_summaryLayout.addWidget(self.agencyName, 0, 0)
        # self.agency_summaryLayout.addWidget(QLabel('Total Transaction : '), 0, 1)
        # self.agency_summaryLayout.addWidget(self.agencyInvestmt, 0, 2)

        # self.summaryGroupBox = QGroupBox("Agency")
        # self.summaryGroupBox.setLayout(self.agency_summaryLayout)

        # self.leftTopGroupBox = QGroupBox("Agency List")
        # self.leftLayout = QVBoxLayout()
        # self.leftLayout.addWidget(self.List_of_agency)
        # self.leftTopGroupBox.setLayout(self.leftLayout)

        self.rightTopGroupBox = QGroupBox("Transactions")
        self.rightTopLayout = QVBoxLayout()
        self.rightTopLayout.addWidget(self.transactionsTable)
        self.rightTopGroupBox.setLayout(self.rightTopLayout)

        self.rightLayout.addWidget(self.rightTopGroupBox, 100)
        # self.rightLayout.addWidget(self.summaryGroupBox, 5)
        # self.rightWidget.setLayout(self.rightLayout)

        # self.horizontalSplitter.addWidget(self.leftTopGroupBox)
        # self.horizontalSplitter.addWidget(self.rightWidget)
        # self.horizontalSplitter.setStretchFactor(0, 10)
        # self.horizontalSplitter.setStretchFactor(1, 90)
        # self.horizontalSplitter.setContentsMargins(0, 0, 0, 0)
        # self.horizontalSplitter.handle(0)

        # self.mainLayout.addWidget(self.rightWidget)
        self.setLayout(self.rightLayout)

    def tabulatePayment(self):

        Table = QTableWidget()
        Table.setColumnCount(self.col_disp)
        j = 0
        for i in self.index_disp:
            hname = str(self.headerName[i])
            Table.setHorizontalHeaderItem(j, QTableWidgetItem(hname))
            j = j + 1

        Table.setAlternatingRowColors(True)
        header = Table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSelectionMode(QAbstractItemView.SingleSelection)
        header.setStretchLastSection(True)
        Table.setFont(QFont("Times", 9))
        Table.setSortingEnabled(False)
        header.setFont(QFont("Times", 12))
        Table.setSelectionBehavior(QAbstractItemView.SelectRows)
        Table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        Table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # stockTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)

        return Table

    def get_stock_info(self, agency, invoice):

        if invoice != "":
            invoice = int(invoice)
            agency = str(agency)
            agencyStock = get_nested_dist_value(self.transInfoz, agency)
            searchCase = get_nested_dist_value(agencyStock, invoice)

            # print("--", searchCase)

            return searchCase

    @pyqtSlot(QPoint)
    def rightClickMenu(self, pos):
        # indexes = self.sender().selectedIndexes()
        # mdlIdx = self.transactionList.indexAt(pos)
        # # print("position",pos)
        # if not mdlIdx.isValid():
        #     return
        #
        # # self.case=self.stockList.itemFromIndex(mdlIdx)
        # # print("Case :"+str(self.case.text()))
        # row = self.transactionList.currentRow()
        # # self.invoice = int(self.stockList.item(row, 0).text())
        # # print("#"+str(self.invoice))

        indexes = self.sender().selectedIndexes()
        mdlIdx = self.transactionsTable.indexAt(pos)
        row = self.transactionsTable.currentIndex().row()

        if not mdlIdx.isValid() and len(indexes) != 0:
            # print("return")
            return


        self.menu = QMenu(self)
        remAct = QAction(QIcon(""), "Delete Transaction", self, triggered=self.delTrans)
        dbremAct = QAction(QIcon(""), "Delete Transaction DB", self, triggered=self.del_transDB)
        # saveAct = QAction(QIcon(""), "Save", self, triggered=self.saveStock)
        addAct = QAction(QIcon(""), "Add Transaction", self, triggered=self.new_trans)
        # remAct.setStatusTip('Delete stock from database')
        updateAct = QAction(QIcon(""), 'Update Transaction', self, triggered=self.update_trans)
        # refreshAct = QAction(QIcon(""), 'Refresh', self, triggered=self.refresh_Stock)
        # dispAct = QAction(QIcon(""), 'Show', self, triggered=self.show_Stock)
        # soldAct = QAction(QIcon(""), 'Sold', self, triggered=self.stock_sold)
        addAct = self.menu.addAction(addAct)
        editStk = self.menu.addAction(updateAct)
        # dispStk = self.menu.addAction(dispAct)
        # saveStk = self.menu.addAction(saveAct)
        remStk = self.menu.addAction(remAct)
        dbremStk = self.menu.addAction(dbremAct)
        # refrStk = self.menu.addAction(refreshAct)
        # self.menu.addSeparator()
        # soldStk = self.menu.addAction(soldAct)

        self.menu.exec_(self.sender().viewport().mapToGlobal(pos))

    def new_trans(self):
        # agency = parse_str(self.List_of_agency.currentItem().text())
        ref_no = gen_id(**self.db_cfg)
        tr_inp = add_new_trans(ref_no)
        if tr_inp.exec_() == tr_inp.Accepted:
            new_trans_addition, save_db = tr_inp.get_inp()
            df_row = pd.DataFrame([new_trans_addition])
            df_row.columns = BANK_TRANSACTIONS_HEADER
            # print(BANK_TRANSACTIONS_DB_TO_DISPLAY)
            # print(df_row)
            self.transactions_df = pd.concat([df_row, self.transactions_df]).reset_index(drop=True)
            self.transactionsModel.update(self.transactions_df)
            if save_db:
                # date_time = datetime.datetime.strptime(new_trans_addition['transaction_date'], DATE_FMT_DMY)
                # new_trans_addition['transaction_date'] = date_time.date()
                listt = list(new_trans_addition.values())
                vals_tuple = [tuple(listt)]
                messge = self.transctions_details.insert_row_by_column_values(row_val=vals_tuple)

    def update_trans(self):
        index = self.transactionsTable.currentIndex().row()
        ncol = self.transactionsModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.transactionsTable.model().index(index, col).data()
            row_data.append(val)

        edit_stock = make_nested_dict()
        for key in BANK_TRANSACTIONS_DB_HEADER:
            edit_stock[key] = None

        new_case=False
        search_item = f"id = {row_data[0]}"
        try:
            row_data_db = self.transctions_details.read_row_by_column_values(criteria=search_item)[0]
        except:
            new_case = True
            row_data_db = make_nested_dict()
            for key in BANK_TRANSACTIONS_DB_HEADER:
                row_data_db[key] = None
            row_data_db['id'] = row_data[0]
            row_data_db['agency'] = row_data[1]
            row_data_db['transaction_date'] = pd.to_datetime(row_data[2], format=DATE_FMT_DMY)
            row_data_db['transaction_id'] = row_data[3]
            row_data_db['amount'] = row_data[4]
            row_data_db['from_bank'] = row_data[5]
            row_data_db['to_bank'] = row_data[6]
            row_data_db['remarks'] = row_data[7]
            # QMessageBox.warning(self, "Transaction not in database","It could be new data which is not saved to database")
            # return

        if row_data_db['id'] != '':
            editBill_inp = edit_selected_trans(row_data_db)
            if editBill_inp.exec_() == editBill_inp.Accepted:
                edit_trans_details, save_db = editBill_inp.get_inp()
                # print(self.transactions_df.columns.tolist())

                mask1 = self.transactions_df["ID"] == row_data_db['id']
                for k, v in edit_trans_details.items():
                    key = BANK_TRANSACTIONS_DB_TO_DISPLAY[k]
                    if key in self.transactions_df.columns.values.tolist() and key != 'Id':
                        self.transactions_df.loc[mask1, key] = edit_trans_details[k]

                self.transactionsModel.update(self.transactions_df)
                self.transactionsModel.layoutChanged.emit()
                self.transactionsTable.clearSelection()

                if save_db:
                    if new_case:
                        # date_time = datetime.datetime.strptime(row_data_db['transaction_date'], DATE_FMT_DMY)
                        # new_trans_addition['transaction_date'] = date_time.date()
                        listt = list(row_data_db.values())
                        vals_tuple = [tuple(listt)]
                        messge = self.transctions_details.insert_row_by_column_values(row_val=vals_tuple)
                    else:
                        set_list = ""
                        # date_time = datetime.datetime.strptime(edit_trans_details['transaction_date'], DATE_FMT_DMY)
                        # edit_trans_details['transaction_date'] = date_time.date()
                        for k, v in edit_trans_details.items():
                            if k != 'id':
                                set_list = f"{set_list},{k}='{v}'"
                        set_list = set_list[1:]
                        messge = self.transctions_details.update_rows_by_column_values(set_argument=set_list,
                                                                                          criteria=f"id='{row_data_db['id']}'")
                    # print(messge)



    def del_transDB(self):
        # fetch data from mysql
        index = self.transactionsTable.currentIndex().row()
        ncol = self.transactionsModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.transactionsTable.model().index(index, col).data()
            row_data.append(val)

        if row_data[0] != '':
            search_item = f"id = {row_data[0]}"
            try:
                row_data_db = self.transctions_details.read_row_by_column_values(criteria=search_item)[0]
            except:
                QMessageBox.warning(self, "Transaction not in database",
                                    "It could be new data which is not saved to database")
                return

            msgBox = QMessageBox()
            msgBox.setWindowTitle("Warning")
            msgBox.setText(f"Are you sure to delete transaction {row_data_db['amount']} data of ID {row_data_db['transaction_id']} ?")
            msgBox.setInformativeText(f"Transaction information will be \npermanatly removed from the database !")
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
                message = self.transctions_details.delete_row_by_column_values(criteria=search_item)
                print(message)
                mask1 = self.transactions_df["ID"] == int(row_data[0])
                index = self.transactions_df[mask1].index
                self.transactions_df.drop(index, axis=0, inplace=True)
                self.transactionsModel.update(self.transactions_df)
                self.transactionsModel.layoutChanged.emit()
                self.transactionsTable.clearSelection()
                QMessageBox.information(self, 'Deleted !!',
                                        f'Selected  transaction (ID {row_data_db["transaction_id"]}) has been deleted')
            else:
                QMessageBox.information(self, 'Aborted !!',
                                        f'Selected  transaction (ID {row_data_db["transaction_id"]}) has not been deleted')

            # self.calculate_sum()
        else:
            QMessageBox.information(self, 'Insufficient data !!',
                                    f'Insufficient data in selected equity..')

    def delTrans(self):
        index = self.transactionsTable.currentIndex().row()
        ncol = self.transactionsModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.transactionsTable.model().index(index, col).data()
            row_data.append(val)

        if row_data[0] != '':
            row_data_db = make_nested_dict()
            for key in BANK_TRANSACTIONS_DB_HEADER:
                row_data_db[key] = None
            row_data_db['id'] = row_data[0]
            row_data_db['agency'] = row_data[1]
            row_data_db['transaction_date'] = pd.to_datetime(row_data[2], format=DATE_FMT_DMY)
            row_data_db['transaction_id'] = row_data[3]
            row_data_db['amount'] = row_data[4]
            row_data_db['from_bank'] = row_data[5]
            row_data_db['to_bank'] = row_data[6]
            row_data_db['remarks'] = row_data[7]

            msgBox = QMessageBox()
            msgBox.setWindowTitle("Warning")
            msgBox.setText(
                f"Are you sure to delete transaction {row_data_db['amount']} data of ID {row_data_db['transaction_id']} ?")
            # msgBox.setInformativeText(f"Transaction information will be \npermanatly removed from the database !")
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
                # message = self.transctions_details.delete_row_by_column_values(criteria=search_item)
                mask1 = self.transactions_df["ID"] == int(row_data[0])
                index = self.transactions_df[mask1].index
                self.transactions_df.drop(index, axis=0, inplace=True)
                self.transactionsModel.update(self.transactions_df)
                self.transactionsModel.layoutChanged.emit()
                self.transactionsTable.clearSelection()
                QMessageBox.information(self, 'Deleted !!',
                                        f'Selected  transaction (ID {row_data_db["transaction_id"]}) has been deleted')
            else:
                QMessageBox.information(self, 'Aborted !!',
                                        f'Selected  transaction (ID {row_data_db["transaction_id"]}) has not been deleted')

            # self.calculate_sum()
        else:
            QMessageBox.information(self, 'Insufficient data !!',
                                    f'Insufficient data in selected equity..')

    def store_trans(self):

        transInfoz = make_nested_dict()
        transInfoz.clear()

        for key, value in self.paymentDB.items():
            for k1, val1 in value.items():
                rowList = list(val1)
                # print("#",key,k1,rowList)
                # 'id', 'agency', 'TransactionDate', 'TransactionAmount', 'TransactionID', 'FromBank', 'ToBank', 'Remarks'
                transInfoz[key][k1]['id'] = k1
                transInfoz[key][k1]['agency'] = key
                transInfoz[key][k1]['TransactionDate'] = rowList[0]
                transInfoz[key][k1]['TransactionAmount'] = rowList[2]
                transInfoz[key][k1]['TransactionID'] = rowList[1]
                transInfoz[key][k1]['FromBank'] = rowList[3]
                transInfoz[key][k1]['ToBank'] = rowList[4]
                transInfoz[key][k1]['Remarks'] = rowList[5]

        return transInfoz

    def load_agency(self, agency):
        # List of stock brocker agencies
        List_of_agency = QListWidget()
        for itm in agency:
            # print(itm)
            List_of_agency.addItem(itm)

        return List_of_agency

    def get_trans(self, item):
        # https://www.tutorialexample.com/pyqt-table-add-row-data-dynamically-a-beginner-guide-pyqt-tutorial/

        agncy = item.text()
        self.transactionList.setRowCount(0)
        self.agencyName.setText(agncy)

        stockz = get_nested_dist_value(self.transInfoz, agncy)
        one_stock = make_nested_dict()
        one_stock.clear()

        for key, val in stockz.items():
            row_number = self.transactionList.rowCount()
            self.transactionList.setRowCount(row_number + 1)
            one_stock = val

            new_table = []
            new_table.clear()
            for info in self.stock_disp_key:
                data = one_stock[info]
                new_table.append(data)

            # print(new_table)
            new_table = tuple(new_table)
            # print(new_table)

            self.add_update_disp(row_number, new_table, agncy, False)

        self.transactionList.setSortingEnabled(True)
        table_sort_color(self.transactionList, self.sort_colmn_by_index, self.Red_colmn_by_index,
                         self.Green_colmn_by_index, self.sort_date_column, 2)

        self.calculate_tr_sum()

        return

    def add_update_disp(self, row, row_data, agency, do_sum):

        for column_number, data in enumerate(row_data):
            # print(data,type(parse_str(data)))
            newItem = QTableWidgetItem()

            # data = parse_str(data)
            # newItem.setData(Qt.DisplayRole, data)
            self.transactionList.setSortingEnabled(False)
            # self.transactionList.setItem(row, column_number, newItem)

            if column_number in self.sort_date_column:
                # format_str='%d/%m/%Y'
                # val = datetime.datetime.strptime(value, "%d/%m/%Y")
                date = QDate.fromString(data, 'dd/MM/yyyy')
                newItem.setData(Qt.DisplayRole, date)
                self.transactionList.setItem(row, column_number, newItem)
                # print(newItem, column_number, self.sort_date_column, date)
            else:
                val = parse_str(data)
                newItem.setData(Qt.DisplayRole, val)
                # if j ==12:
                #     print(i,j,val,type(val))
                self.transactionList.setItem(row, column_number, newItem)
                self.transactionList.setEditTriggers(QTableWidget.NoEditTriggers)

            # print(data,type(data))
        # exit()
        self.transactionList.setSortingEnabled(True)

        # if do_sum:
        #     self.calculate_sum(agency)

    def calculate_tr_sum(self, agency=""):

        if not agency:
            item = self.List_of_agency.currentItem()
            agency = str(item.text())

        tranz = self.transInfoz[agency]
        net_invetment = 0.0
        net_extra = 0.0

        for key, value in tranz.items():
            net_invetment = net_invetment + parse_str(value['TransactionAmount'])

        agencyInvestmt = "{:.{}f}".format(net_invetment, 3)
        self.agencyInvestmt.setText(format_currency(agencyInvestmt, 'INR', locale='en_IN'))
        self.agencyInvestmt.setStyleSheet('color: blue')

        return


class add_new_trans(QDialog):

    # def __init__(self,con,cur,agency=""):
    def __init__(self,ref_no, parent=None):
        super(add_new_trans, self).__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Add Transaction")
        # self.con=con
        # self.cur=cur
        self.dbsave = False
        self.ref_no=ref_no
        # self.agency0 = ""
        # if agency:
        #     self.agency0 = agency
        #
        # if dbsave:
        #     # print("HHHH")
        #     self.dbsave = True

        # self.setWindowIcon(QIcon('icons/icon.ico'))
        self.setGeometry(450, 150, 450, 400)
        self.setFixedSize(self.size())

        self.UI()
        self.show()

    def UI(self):
        # self.get_db()
        # self.get_default_paramters()
        self.widgets()
        self.layouts()

    # def get_db(self):
    #     self.con, self.cur = check_db(db_file)

    # def get_default_paramters(self):
    #     default = default_parameters()
    #     self.brockerage = default[0]
    #     self.gst = default[1]
    #     self.stt = default[2]
    #     self.itax = default[3]

    def widgets(self):
        self.save_db = False
        self.titleText = QLabel("Add New transaction")
        # self.agencyEntry = QLineEdit()
        self.agencyEntry = QComboBox()
        self.agencyEntry.addItems(AGENCY_LIST)
        # self.agencyEntry.setPlaceholderText("Enter name of agency (Eg. Kotak, Zerodha, etc)")
        self.tr_dateEntry = QDateEdit(self)
        self.tr_dateEntry.setDate(QDate.currentDate())
        self.tr_dateEntry.setDisplayFormat(DATE_TIME1)
        self.tr_idEntry = QLineEdit()
        self.tr_idEntry.setPlaceholderText("Enter transaction id")
        self.amountEntry = QLineEdit()
        self.amountEntry.setPlaceholderText("Enter transaction amount")
        reg_ex_float = QRegExp("[0-9]+.?[0-9]{,2}")
        # reg_ex_float = QRegExp(r'[0-9].+')
        input_validator_float = QRegExpValidator(reg_ex_float, self.amountEntry)
        self.amountEntry.setValidator(input_validator_float)
        # self.trade_priceEntry.setText("0.00")
        self.transTypeEntry = QComboBox()
        self.transTypeEntry.addItems(TRANS_TYPE_LIST)
        self.amountEntry.textChanged.connect(self.check_price)
        self.transTypeEntry = QComboBox()
        self.transTypeEntry.addItems(TRANS_TYPE_LIST)
        self.fromBnkEntry = QLineEdit()
        self.fromBnkEntry.setPlaceholderText("source bank")
        self.toBnkEntry = QLineEdit()
        self.toBnkEntry.setPlaceholderText("destination bank")
        self.remarksEntry = QLineEdit()
        self.remarksEntry.setPlaceholderText("Type your remarks ..")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.resets = QPushButton("Reset")
        self.resets.clicked.connect(self.clearAll)
        self.buttonBox.addButton(self.resets, QDialogButtonBox.ResetRole)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.saveDB = QCheckBox("Update to Database:")
        if self.dbsave:
            self.saveDB.setChecked(True)
            self.saveDB.setDisabled(True)
        else:
            self.saveDB.stateChanged.connect(self.state_changed)

        self.fromBnkEntry.setText('SBI')
        self.toBnkEntry.setText('Zerodha,HDFC')
        self.remarksEntry.setText('Investment')
    # def state_changed(self):
    #     if self.save_db:
    #         self.save_db = False
    #     else:
    #         self.save_db = True

    def check_price(self):
        # if type(self.pay2.text()) ==
        price = parse_str(self.amountEntry.text())
        if price == "":
            pass
        elif isinstance(price, str):
            QMessageBox.warning(self, "Check amount !!!",
                                " Amount should be a number")
            self.reset_value(1)

    def reset_value(self, key):
        if key == 1:
            self.amountEntry.setText("")
        if key == 2:
            self.quantityEntry.setText("")
        if key == 3:
            self.chargesEntry.setText("")


    def state_changed(self, state):
        if state == Qt.Checked:
            self.save_db = True
        else:
            self.save_db = False

    def accept(self):
        agency = self.agencyEntry.currentText()
        # if  agency == "Zerodha":
        #     self.toBnkEntry.setText("Zerodha, HDFC")
        # if agency == "Kotak":
        #     self.toBnkEntry.setText("Kotak Mahindra securities ltd")

        # agency = self.agencyEntry.text()
        tdate = self.tr_dateEntry.text()
        amount = float(self.amountEntry.text())
        if self.transTypeEntry.currentText() == 'Debit':
            amount = amount*-1.0
        tr_id = self.tr_idEntry.text()
        bank0 = self.fromBnkEntry.text()
        bank1 = self.toBnkEntry.text()
        comment = self.remarksEntry.text()

        new_trans_addition = make_nested_dict()
        for key in BANK_TRANSACTIONS_DB_HEADER:
            new_trans_addition[key] = None

        new_trans_addition['id']=self.ref_no
        new_trans_addition['agency']=agency
        new_trans_addition['transaction_date']=pd.to_datetime(tdate,format=DATE_FMT_DMY)
        new_trans_addition['transaction_id']=tr_id
        new_trans_addition['amount']=amount
        new_trans_addition['from_bank']=bank0
        new_trans_addition['to_bank']=bank1
        new_trans_addition['remarks']=comment

        self.output = new_trans_addition, self.save_db
        super(add_new_trans, self).accept()

    def clearAll(self):
        self.agencyEntry.setCurrentIndex(0)
        self.tr_dateEntry.setDate(QDate.currentDate())
        self.tr_dateEntry.setDisplayFormat(DATE_TIME1)
        self.amountEntry.setText("")
        self.transTypeEntry.setCurrentIndex(0)
        self.tr_idEntry.setText("")
        self.fromBnkEntry.setText("")
        self.toBnkEntry.setText("")
        self.remarksEntry.setText("")

    def get_inp(self):
        return self.output

    def layouts(self):
        self.mainLayout = QVBoxLayout()
        self.mainTopLayout = QVBoxLayout()
        self.topLayout = QFormLayout()
        self.bottomLayout = QHBoxLayout()
        self.topFrame = QFrame()

        self.topGroupBox = QGroupBox("Transaction Information")
        self.bottomGroupBox = QGroupBox("Control")

        self.topLayout.addRow(QLabel("Agency: "), self.agencyEntry)
        self.topLayout.addRow(QLabel("Transaction Date: "), self.tr_dateEntry)
        self.topLayout.addRow(QLabel("Transaction Amount: "), self.amountEntry)
        self.topLayout.addRow(QLabel("Transaction ID: "), self.tr_idEntry)
        self.topLayout.addRow(QLabel("Transaction Type: "), self.transTypeEntry)
        self.topLayout.addRow(QLabel("From Bank: "), self.fromBnkEntry)
        self.topLayout.addRow(QLabel("To Bank: "), self.toBnkEntry)
        self.topLayout.addRow(QLabel("Remarks: "), self.remarksEntry)

        # self.bottomLayout.addWidget(self.addBtn)
        # self.bottomLayout.addWidget(self.clrBtn)
        self.bottomLayout.addWidget(self.buttonBox)

        self.topGroupBox.setLayout(self.topLayout)
        self.bottomGroupBox.setLayout(self.bottomLayout)

        # self.topFrame.setLayout(self.topLayout)
        # self.topGroupBox.add setLayout(self.topLayout)
        # self.bottomGroupBox.setLayout(self.bottomLayout)
        self.mainTopLayout.addWidget(self.topGroupBox)
        self.mainTopLayout.addWidget(self.saveDB)
        self.mainTopLayout.addWidget(self.bottomGroupBox)

        self.mainLayout.addLayout(self.mainTopLayout)
        self.setLayout(self.mainLayout)


class edit_selected_trans(QDialog):

    # def __init__(self,con,cur,agency=""):
    def __init__(self, trans_data, parent=None):
        super(edit_selected_trans, self).__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Update Transaction")
        # self.con=con
        # self.cur=cur
        self.trans_data = trans_data

        # self.setWindowIcon(QIcon('icons/icon.ico'))
        self.setGeometry(450, 150, 450, 400)
        self.setFixedSize(self.size())

        self.UI()
        self.show()

    def UI(self):
        self.fetch_data()
        self.widgets()
        self.layouts()

    def fetch_data(self):
        self.agency = self.trans_data['agency']
        self.tr_date = self.trans_data['transaction_date']
        self.tr_id = str(self.trans_data['transaction_id'])
        self.tr_amount = float(self.trans_data['amount'])
        self.tr_type = 'Credit'
        if self.tr_amount < 0.0:
            self.tr_type='Debit'
        self.from_bank = self.trans_data['from_bank']
        self.to_bank = self.trans_data['to_bank']
        self.comment = self.trans_data['remarks']

    def widgets(self):
        self.save_db = False
        self.titleText = QLabel("Update Transaction")
        self.agencyEntry = QLineEdit()
        self.agencyEntry = QComboBox()
        self.agencyEntry.addItems(AGENCY_LIST)
        if self.agency in AGENCY_LIST:
            indx = self.agencyEntry.findText(self.agency)
            self.agencyEntry.setCurrentIndex(indx)
        self.agencyEntry.setPlaceholderText("Enter name of agency (Eg. Kotak, Zerodha, etc)")
        # self.agencyEntry.setText(self.agency)
        self.tr_dateEntry = QDateEdit(self)
        self.tr_dateEntry.setDate(self.tr_date)
        self.tr_dateEntry.setDisplayFormat(DATE_TIME1)
        self.tr_idEntry = QLineEdit()
        self.tr_idEntry.setPlaceholderText("Enter transaction id")
        self.tr_idEntry.setText(self.tr_id)
        self.amountEntry = QLineEdit()
        self.amountEntry.setPlaceholderText("Enter transaction amount")
        self.amountEntry.setText(str(self.tr_amount))
        self.transTypeEntry = QComboBox()
        self.transTypeEntry.addItems(TRANS_TYPE_LIST)
        if self.tr_type in TRANS_TYPE_LIST:
            indx = self.transTypeEntry.findText(self.tr_type)
            self.transTypeEntry.setCurrentIndex(indx)
        self.fromBnkEntry = QLineEdit()
        self.fromBnkEntry.setPlaceholderText("source bank")
        self.fromBnkEntry.setText(self.from_bank)
        self.toBnkEntry = QLineEdit()
        self.toBnkEntry.setPlaceholderText("destination bank")
        self.toBnkEntry.setText(self.to_bank)
        self.remarksEntry = QLineEdit()
        self.remarksEntry.setPlaceholderText("Type your remarks ..")
        self.remarksEntry.setText(self.comment)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.resets = QPushButton("Reset")
        self.resets.clicked.connect(self.clearAll)
        self.buttonBox.addButton(self.resets, QDialogButtonBox.ResetRole)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.saveDB = QCheckBox("Update to Database:")
        self.saveDB.stateChanged.connect(self.state_changed)

        # if self.agency0:
        #     self.agencyEntry.setText(self.agency0)
        #     if  self.agency0 == "Zerodha":
        #         self.toBnkEntry.setText("Zerodha, HDFC")
        #     if self.agency0 == "Kotak":
        #         self.toBnkEntry.setText("Kotak Mahindra securities ltd")

        # self.agencyEntry.setText("Kotak")
        # # self.tr_dateEntry.setText("16/08/2020")
        # # self.tr_dateEntry.setDateTime(QDateTime(QDate(2020, 08, 16)))
        # self.amountEntry.setText("109")
        # self.tr_idEntry.setText("200")
        # self.fromBnkEntry.setText("SBI")
        # self.remarksEntry.setText("Equity")

    def state_changed(self, state):
        if state == Qt.Checked:
            self.save_db = True
        else:
            self.save_db = False

    def accept(self):
        agency = self.agencyEntry.currentText()
        tdate = self.tr_dateEntry.text()
        amount = float(self.amountEntry.text())
        if self.transTypeEntry.currentText() == 'Debit':
            amount = amount*-1.0
        tr_id = self.tr_idEntry.text()
        bank0 = self.fromBnkEntry.text()
        bank1 = self.toBnkEntry.text()
        comment = self.remarksEntry.text()
        new_trans_addition = make_nested_dict()
        for key in BANK_TRANSACTIONS_DB_HEADER:
            new_trans_addition[key] = None

        new_trans_addition['id'] = self.trans_data['id']
        new_trans_addition['agency'] = agency
        new_trans_addition['transaction_date'] = pd.to_datetime(tdate,format=DATE_FMT_DMY)
        new_trans_addition['transaction_id'] = tr_id
        new_trans_addition['amount'] = amount
        new_trans_addition['from_bank'] = bank0
        new_trans_addition['to_bank'] = bank1
        new_trans_addition['remarks'] = comment
        self.output = new_trans_addition, self.save_db
        super(edit_selected_trans, self).accept()

    def clearAll(self):
        self.agencyEntry.setCurrentIndex(0)
        self.tr_dateEntry.setDate(QDate.currentDate())
        self.tr_dateEntry.setDisplayFormat(DATE_TIME1)
        self.amountEntry.setText("")
        self.transTypeEntry.setCurrentIndex(0)
        self.tr_idEntry.setText("")
        self.fromBnkEntry.setText("")
        self.toBnkEntry.setText("")
        self.remarksEntry.setText("")

    def get_inp(self):
        return self.output

    def layouts(self):
        self.mainLayout = QVBoxLayout()
        self.mainTopLayout = QVBoxLayout()
        self.topLayout = QFormLayout()
        self.bottomLayout = QHBoxLayout()
        self.topFrame = QFrame()

        self.topGroupBox = QGroupBox("Transaction Information")
        self.bottomGroupBox = QGroupBox("Control")

        self.topLayout.addRow(QLabel("Agency: "), self.agencyEntry)
        self.topLayout.addRow(QLabel("Transaction Date: "), self.tr_dateEntry)
        self.topLayout.addRow(QLabel("Transaction Amount: "), self.amountEntry)
        self.topLayout.addRow(QLabel("Transaction ID: "), self.tr_idEntry)
        self.topLayout.addRow(QLabel("Transaction Type: "), self.transTypeEntry)
        self.topLayout.addRow(QLabel("From Bank: "), self.fromBnkEntry)
        self.topLayout.addRow(QLabel("To Bank: "), self.toBnkEntry)
        self.topLayout.addRow(QLabel("Remarks: "), self.remarksEntry)

        # self.bottomLayout.addWidget(self.addBtn)
        # self.bottomLayout.addWidget(self.clrBtn)
        self.bottomLayout.addWidget(self.buttonBox)

        self.topGroupBox.setLayout(self.topLayout)
        self.bottomGroupBox.setLayout(self.bottomLayout)

        # self.topFrame.setLayout(self.topLayout)
        # self.topGroupBox.add setLayout(self.topLayout)
        # self.bottomGroupBox.setLayout(self.bottomLayout)
        self.mainTopLayout.addWidget(self.topGroupBox)
        self.mainTopLayout.addWidget(self.saveDB)
        self.mainTopLayout.addWidget(self.bottomGroupBox)

        self.mainLayout.addLayout(self.mainTopLayout)
        self.setLayout(self.mainLayout)


#
# #
def main():
    APP = QApplication(sys.argv)
    db_cfg=extablish_db_connection()
    window = show_transactions(**db_cfg)
    sys.exit(APP.exec_())


if __name__ == '__main__':
    main()
