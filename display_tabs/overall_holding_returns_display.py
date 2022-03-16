import pandas as pd

from PyQt5 import QtWebEngineWidgets
from PyQt5.QtCore import Qt, QPoint, pyqtSlot, QTimer, QDateTime
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QWidget, QListWidget, QMenu, QAction, QTableView, QLabel, QMessageBox, \
    QVBoxLayout, QHBoxLayout, QGroupBox, \
    QGridLayout, QAbstractItemView, \
    QHeaderView, QSplitter, QFileDialog

# from babel.numbers import format_currency
import datetime
import yfinance as yf


from mysql_tools.mysql_crud import mysql_table_crud
from mysql_tools.tables_and_headers import CURRENT_HOLDINGS_DB_TABLE_NAME,  \
    SOLD_HOLDING_DB_HEADER, SOLD_HOLDINGS_DB_TABLE_NAME, BANK_TRANSACTIONS_DB_TABLE_NAME, BANK_TRANSACTIONS_DB_HEADER
from utility.libnames import PATH_TO_DATABASE_CURRENT_HOLDINGS
from mysql_tools.tables_and_headers import CURRENT_HOLDING_LIST_DISPLAY, CURRENT_HOLDING_DB_TO_DISPLAY, \
    SOLD_HOLDINGS_LIST_DISPLAY, SOLD_HOLDING_DB_TO_DISPLAY, BANK_TRANSACTIONS_LIST_DISPLAY, \
    BANK_TRANSACTIONS_DB_TO_DISPLAY,TOTAL_HOLDINGS_DB_TABLE_NAME,TOTAL_HOLDINGS_DB_HEADER

# from DataBase.label_names import HEADER_PHARMACY_PAYIN, \
#     DEBIT_TITLE, SAMPLE_TABLE_MEDICAL, DATE_FMT_DMY, DATE_FMT_YMD, \
#     BILL_MODIFY_TYPE, DATE_TIME, STATEMENT_EXCEL_PREFIX, \
#     PHARAMACY_BILL_PAYIN_PREFIX, PAYIN_PHARMACY_TABLE_HEADER
#
# from DataBase.utilities import make_nested_dict, parse_str, TABLE_HEADER_FONT, TABLE_FONT, DUMMY_SPACE_FONT \
#     , RECEIPT_SUMMARY_TOTAL_FONT, RECEIPT_SUMMARY_LABEL_FONT \
#     , SUMMARY_GBOX_TITLE, PAYMENT_SUMMARY_TOTAL_FONT, PAYMENT_SUMMARY_LABEL_FONT \
#     , SUMMARY_RECPT_TITLE_COLOR, SUMMARY_PAYMT_TITLE_COLOR, SUMMARY_CASHBALANCE_TITLE_COLOR \
#     , CASH_BALANCE_SUMMARY_LABEL_FONT, CASH_BALANCE_SUMMARY_TOTAL_FONT
#
# from GuiWidgets.gui_widgets_read_name_mobile_no import get_name_mobile_no
# from GuiWidgets.gui_widgets_for_payin_new import new_Bill_payin as new_bill_payin
# from GuiWidgets.gui_widgets_for_payin_edit import edit_Bill_payin as edit_bill_payin
# from DataBase.utilities import parse_str
import dateparser
import copy
import os
# from DataBase.mysql_crud import mysql_table_crud
from utility.tableViewModel import pandasModel
from utility.fonts_style import TABLE_HEADER_FONT, TABLE_FONT
from mysql_tools.tables_and_headers import TOTAL_HOLDINGS_CALC_HEADER,TOTAL_HOLDINGS_EXTRA_HEADER
from utility.utility_functions import reduce_mem_usage, symbol_date_range_string, date_symbol_split, gen_id,\
    symbol_date_string,create_current_holdings_csv_file_names,create_sold_holdings_csv_file_names,symbol_date_split,\
    create_current_holdings_csv_file_names,make_nested_dict
from utility.date_time import DATE_TIME, DATE_FMT_YMD, DATE_FMT_DMY

from display_tabs.utility_display_tab import get_current_holdings_history,get_sold_holdings_history,get_current_holdings_history_mp

from os.path import expanduser

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

global DEFAULT_PATH
usr_path = expanduser("~")
DEFAULT_PATH = f"{usr_path}/Desktop/"


class holdings_returns_display(QWidget):
    def __init__(self, plot_all_returns_history,**mysql_data):
        super().__init__()
        # self.setWindowTitle("Balance test")
        # self.usr = usr
        # self.my_access = access
        # self.market_value_history = market_value_history
        # self.transactions_detail_df = transactions_detail_df
        # self.overall_holdings = overall_holdings
        self.plot_all_returns_history = plot_all_returns_history
        self.db_cfg = mysql_data
        self.UI()

    def UI(self):
        self.connect_to_tables()

        self.transactions_detail_df = self.transaction_history()
        self.overall_holdings = self.get_overall_holdings_details()
        print(self.overall_holdings.to_string())
        # mask = self.overall_holdings['equity'] == "ADANIGREEN"
        # df=self.overall_holdings[mask].copy()
        # df.sort_values(by="date", ascending=True, inplace=True)
        # print(df.to_string())
        # exit()
        self.market_value_history=self.overall_return()
        # self.overall_holdings = self.get_all_holdings_info()
        # self.overall_return_history()
        # exit()
        self.widgets()
        self.layouts()

    def connect_to_tables(self):
        self.transctions_details = mysql_table_crud(db_table=BANK_TRANSACTIONS_DB_TABLE_NAME,
                                                    db_header=BANK_TRANSACTIONS_DB_HEADER,
                                                    **self.db_cfg)

        self.total_holdings_details = mysql_table_crud(db_table=TOTAL_HOLDINGS_DB_TABLE_NAME,
                                                       db_header=TOTAL_HOLDINGS_DB_HEADER,
                                                           **self.db_cfg)

    def transaction_history(self):
        transactions_df = self.get_all_transaction_details()
        transactions_df.sort_values(by="Date", ascending=True, inplace=True)
        transactions_df["Date"] = pd.to_datetime(transactions_df["Date"])
        start_date = transactions_df["Date"].min()
        col_list = transactions_df.columns.to_list()
        start_date = pd.to_datetime(start_date)
        end_date = datetime.datetime.now().date()
        date_range = [pd.date_range(start_date, end_date, freq='D')]
        df = pd.DataFrame(index=date_range, columns=col_list)
        df.fillna(0, inplace=True)
        df.rename_axis("Date", inplace=True)
        df.drop(["Date", 'Agency'], axis=1, inplace=True)
        df.reset_index(inplace=True)
        transactions_df = pd.concat([transactions_df, df]).groupby(['Date']).sum().reset_index()
        transactions_df['Cumulative_Amount'] = transactions_df['Amount'].cumsum()

        return transactions_df

    def get_overall_holdings_details(self):
        data = self.total_holdings_details.read_row_by_column_values(order="order by date asc")
        all_holding_df = pd.DataFrame(data)
        # reading only current holdings
        all_holding_df.sort_values(by=['equity'], ascending=True, inplace=True)
        # adding fees per stock
        all_holding_df.loc[:, 'price'] = all_holding_df.loc[:, 'price'] + all_holding_df.loc[:, 'fees'] / all_holding_df.loc[:, 'quantity']
        ticker_list = all_holding_df['equity'].to_list()
        ticker_list = sorted(list(set(ticker_list)))

        for hdr in TOTAL_HOLDINGS_CALC_HEADER:
            if hdr not in all_holding_df.columns.to_list():
                all_holding_df[hdr] = 0.0

        i = 0
        for ticker in ticker_list:
            i += 1
            mask = all_holding_df['equity'] == ticker
            calc_df = self.calc_overall_trading_summary(all_holding_df[mask].copy())

            for idx, row in calc_df.iterrows():
                mask_row = all_holding_df['ref_number'] == row['ref_number']
                for col in TOTAL_HOLDINGS_EXTRA_HEADER:
                    all_holding_df.loc[mask_row, col] = row[col]
                all_holding_df.loc[mask_row, 'avg_price'] = row['avg_price']

        all_holding_df.sort_values(by=['date'], ascending=True, inplace=True)
        # drop_columns = ['id', 'remarks', 'ref_number', 'agency']
        drop_columns = ['id', 'remarks','agency']
        all_holding_df.drop(drop_columns, axis=1, inplace=True)
        all_holding_df['cml_gain_loss'] = all_holding_df['gain_loss'].cumsum()

        # print(all_holding_df.head(3).to_string())

        # if i == 3:
        # exit()

        return all_holding_df

    def calc_overall_trading_summary(self, df):
        df = df.sort_values(by=['date'], ascending=True).copy()
        # print(df.to_string())
        # df.loc[:, 'price'] = df.loc[:, 'price']+ df.loc[:, 'fees'] / df.loc[:, 'quantity']
        df.loc[:, 'transact_val'] = df.loc[:, 'quantity'] * df.loc[:, 'price']

        value_list = {'quantity': 0, 'price':0,'cml_units': 0, 'prev_cost': 0, 'transact_val': 0, 'cml_cost': 0, 'avg_price': 0}
        i = 0
        for idx, row in df.iterrows():
            date = row['date']
            type = row['type']
            quantity = row['quantity']
            transact_val = row['transact_val']
            avg_price = row['avg_price']
            # price = row['price']
            # prev_units = row['quantity']
            # cml_units = row['cml_units']
            # prev_cost = row['prev_cost']

            if i == 0:
                df.loc[idx, ('prev_units')] = 0
                df.loc[idx, ('cml_units')] = quantity

                value_list['prev_units'] = 0
                value_list['cml_units'] = quantity
                value_list['prev_cost'] = 0

                df.loc[idx, ('cml_cost')] = transact_val
                df.loc[idx, ('prev_cost')] = 0
                if type == "Buy":
                    df.loc[idx, ('cashflow')] = -transact_val
                if type == "Sale":
                    df.loc[idx, ('cashflow')] = transact_val

                value_list['quantity'] = quantity
                value_list['transact_val'] = transact_val
                value_list['cml_cost'] = transact_val
                value_list['avg_price'] = avg_price
                value_list['prev_cost'] = 0

            else:
                prev_unit_new = value_list['quantity']
                value_list['prev_units'] = prev_unit_new
                value_list['quantity'] = prev_unit_new - quantity
                df.loc[idx, ('prev_units')] = prev_unit_new

                # print(value_list)
                if type == "Buy":
                    cml_units_new = value_list['cml_units'] + quantity
                    prev_cost_new = value_list['avg_price'] * prev_unit_new
                    cml_cost_new = avg_price * cml_units_new

                    value_list['cml_units'] = cml_units_new
                    value_list['prev_cost'] = prev_cost_new
                    value_list['cml_units'] = cml_units_new

                    df.loc[idx, ('cashflow')] = -transact_val
                    df.loc[idx, ('cml_units')] = cml_units_new
                    df.loc[idx, ('prev_cost')] = prev_cost_new
                    df.loc[idx, ('cml_cost')] = cml_cost_new

                    # -------------------------------------------
                    value_list['quantity'] = prev_unit_new + quantity
                    value_list['avg_price'] = avg_price

                if type == "Sell":
                    cml_units_new = value_list['cml_units'] - quantity
                    prev_cost_new = value_list['avg_price'] * prev_unit_new
                    cml_cost_new = avg_price * cml_units_new

                    value_list['cml_units'] = cml_units_new
                    value_list['prev_cost'] = prev_cost_new
                    value_list['cml_units'] = cml_units_new

                    df.loc[idx, ('cashflow')] = transact_val
                    df.loc[idx, ('cml_units')] = cml_units_new
                    df.loc[idx, ('prev_cost')] = prev_cost_new
                    df.loc[idx, ('cml_cost')] = cml_cost_new
                    # df.loc[idx, ('gain_loss')] = quantity * (price - avg_price)
                    # df.loc[idx, ('yield')] = price / avg_price - 1.0

                    # -------------------------------------------
                    value_list['quantity'] = prev_unit_new - quantity
                    value_list['avg_price'] = avg_price
            i += 1

        # print(df.to_string())
        # calculating avg. cum val data
        value_list = { 'prev_units': 0, 'cml_units': 0,'avg_price': 0}
        i = 0
        for idx, row in df.iterrows():
            date = row['date']
            type = row['type']
            quantity = row['quantity']
            price = row['price']
            prev_units = row['quantity']
            cml_units = row['cml_units']
            avg_price = row['avg_price']

            if i == 0:
                value_list['prev_units'] = prev_units
                value_list['cml_units'] = cml_units
                value_list['avg_price'] = avg_price
            else:
                # print(value_list)
                if type == "Buy":
                    cml_units_old = value_list['cml_units']
                    # prev_units_old = value_list['prev_units']
                    avg_price_old = value_list['avg_price']

                    nr=cml_units_old*avg_price_old+quantity*price
                    dr=cml_units_old+quantity
                    avg_price = nr/dr
                    cml_cost_new = avg_price*cml_units
                    prev_cost_new = avg_price_old*prev_units

                    df.loc[idx, ('prev_cost')] = prev_cost_new
                    df.loc[idx, ('cml_cost')] = cml_cost_new
                    df.loc[idx, ('avg_price')] = avg_price

                    value_list['prev_units'] = prev_units
                    value_list['cml_units'] = cml_units
                    value_list['avg_price'] = avg_price

                if type == "Sell":
                    cml_units_old = value_list['cml_units']
                    # prev_units_old = value_list['prev_units']
                    avg_price_old = value_list['avg_price']
                    avg_price = avg_price_old
                    cml_cost_new = avg_price * cml_units
                    prev_cost_new = avg_price_old * prev_units

                    df.loc[idx, ('prev_cost')] = prev_cost_new
                    df.loc[idx, ('cml_cost')] = cml_cost_new
                    df.loc[idx, ('avg_price')] = avg_price

                    value_list['prev_units'] = prev_units
                    value_list['cml_units'] = cml_units
                    value_list['avg_price'] = avg_price

                    df.loc[idx, ('gain_loss')] = quantity * (price - avg_price)
                    df.loc[idx, ('yield')] = price / avg_price - 1.0
            i += 1

        # print(df.to_string())

        # print("-------->")
        # print(df.to_string())
        # exit()
        return df

    def extract_current_holdings_history(self,current_holding_data_df):
        # return get_current_holdings_history(current_holding_data_df)
        current_holdings_csv_file_names = create_current_holdings_csv_file_names(current_holding_data_df)
        return get_current_holdings_history_mp(current_holdings_csv_file_names)

    def extract_sold_holdings_history(self,sold_holding_data_df):
        sold_holdings_csv_file_names = create_current_holdings_csv_file_names(sold_holding_data_df)
        return get_sold_holdings_history(sold_holdings_csv_file_names)
        # return get_sold_holdings_history(sold_holding_data_df)

    def overall_return(self):
        market_value_history = pd.DataFrame()
        mask = self.overall_holdings["current_holding"] == True
        current_holding_data_df = self.overall_holdings.loc[mask].copy()
        current_holding_history = self.extract_current_holdings_history(current_holding_data_df)

        for idx, row in current_holding_data_df.iterrows():
            symbol=row['equity']
            buy_date = row['date']
            quantity = int(row['quantity'])
            symbol_buy_date=symbol_date_string(symbol,buy_date)
            df=current_holding_history[symbol_buy_date]

            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            start_date = pd.to_datetime(buy_date)
            # quantity = float(val['quantity'])
            # start_date = pd.to_datetime(val['buy_date']) - datetime.timedelta(0)
            mask1 = df['Date'] >= start_date
            df = df[mask1].copy()
            header_name = ['Open', 'High', 'Low', 'Close', 'Adj Close']
            for col in header_name:
                df[col] = df[col].apply(lambda x: x * quantity)
                df['Volume'] = 1
            df.sort_values(by=['Date'], ascending=True, inplace=True)
            market_value_history = pd.concat([market_value_history, df]).groupby(['Date']).sum().reset_index()
        # https: // stackoverflow.com / questions / 63750988 / using - multiprocessing -with-pandas - to - read - modify - and -write - thousands - csv - files

        # self.plot_all_returns_history=True
        if self.plot_all_returns_history:
            mask1 = self.overall_holdings["current_holding"] == False
            mask2 = self.overall_holdings["type"] == "Sell"
            mask=mask1 & mask2
            sold_holding_data_df = self.overall_holdings.loc[mask].copy()
            sold_holding_history = self.extract_sold_holdings_history(self.overall_holdings)

            for symbol_date_range, path_to_csv_file in sold_holding_history.items():
                symbol, buy_date, sale_date = date_symbol_split(symbol_date_range)
                buy_date=datetime.date.fromisoformat(str(buy_date))
                sale_date=datetime.date.fromisoformat(str(sale_date))
                mask1 = sold_holding_data_df['date'] == sale_date
                mask2 = sold_holding_data_df['equity'] == symbol
                mask = mask1   & mask2
                sold_df=sold_holding_data_df[mask]

                for idx, row in sold_df.iterrows():
                    quantity = int(row['quantity'])
                    df = sold_holding_history[symbol_date_range]
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                    mask1 = df['Date'] >= pd.to_datetime(buy_date)
                    mask2 = df['Date'] <= pd.to_datetime(sale_date)
                    mask = mask1 & mask2
                    df = df[mask].copy()
                    header_name = ['Open', 'High', 'Low', 'Close', 'Adj Close']
                    for col in header_name:
                        df[col] = df[col].apply(lambda x: x * quantity)
                        df['Volume'] = 1
                    df.sort_values(by=['Date'], ascending=True, inplace=True)
                    market_value_history = pd.concat([market_value_history, df]).groupby(
                        ['Date']).sum().reset_index()

        # print(self.market_value_history.head(10).to_string())
        # print(self.return_history['Close'].sum())
        #     # https: // www.analyticsvidhya.com / blog / 2020 / 05 / datetime - variables - python - pandas /
        # # df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
        return market_value_history


    def widgets(self):
        # holding_df = self.get_all_holdings_details()
        # sold_stocks_df = self.get_all_sold_holdings_details()
        # self.transactions_df = self.get_all_transaction_details()

        # self.holdingModel, self.holdingTable = self.tableViewDataModel(holding_df)
        # self.holdingModel.sort(0, Qt.DescendingOrder)
        #
        # self.sold_stock_Model, self.sold_stockTable = self.tableViewDataModel(sold_stocks_df)
        # self.sold_stock_Model.sort(0, Qt.DescendingOrder)
        #
        # self.trans_Model, self.transTable = self.tableViewDataModel(self.transactions_df)
        # self.trans_Model.sort(1, Qt.DescendingOrder)
        #
        # self.transactions_df.sort_values(by='Date', inplace=True)
        # # print(self.transactions_df.to_string())
        #
        # sold_stocks_df["Profit"] = (sold_stocks_df["Sale Price"] - sold_stocks_df["Buy Price"]) * sold_stocks_df[
        #     "Sale Quantity"]
        #
        # sold_stocks_df.sort_values(by="Equity", inplace=True)
        # # print(sold_stocks_df.to_string())
        #
        # # print(sold_stocks_df.to_string())
        # mask1 = sold_stocks_df["Profit"] >= 0
        # mask2 = sold_stocks_df["Profit"] < 0
        # print(f"-Ve Gain = ", round(sold_stocks_df.loc[mask2, 'Profit'].sum()), 1)
        # print(f"+Ve Gain = ", round(sold_stocks_df.loc[mask1, 'Profit'].sum()), 1)
        # print(f"Total Gain = {round(sold_stocks_df['Profit'].sum(), 1)}")
        # print(f"Max Gain = {round(sold_stocks_df['Profit'].max(), 1)}")
        # print(f"Max loss = {round(sold_stocks_df['Profit'].min(), 1)}")
        # print(f"Total Investment = {round(self.transactions_df['Amount'].sum(), 1)}")
        #
        # print("Holding date:", holding_df["Buy Date"].min(), holding_df["Buy Date"].max())
        # print("Sold date:", sold_stocks_df["Buy Date"].min(), sold_stocks_df["Buy Date"].max())
        # print("Sold date:", sold_stocks_df["Sale Date"].min(), sold_stocks_df["Sale Date"].max())
        # print("Date:", self.transactions_df["Date"].min(), self.transactions_df["Date"].max())
        # # print(self.transactions_df.to_string())

        self.data_plot_browser = QtWebEngineWidgets.QWebEngineView(self)
        # print(self.holding_df.to_string())
        # self.holdingTable.installEventFilter(self)
        # self.holdingTable.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.holdingTable.customContextMenuRequested.connect(self.rightClickMenuPayIn)

    def get_all_transaction_details(self):
        data = self.transctions_details.read_row_by_column_values()
        transaction_df = pd.DataFrame(data)
        col_name = list(transaction_df.columns)
        col_drop_list = []
        for hdr_name in col_name:
            if hdr_name not in BANK_TRANSACTIONS_LIST_DISPLAY:
                col_drop_list.append(hdr_name)

        col_hdr_list = []
        for hdr_name in BANK_TRANSACTIONS_LIST_DISPLAY:
            col_hdr_list.append(BANK_TRANSACTIONS_DB_TO_DISPLAY[hdr_name])

        transaction_df.drop(col_drop_list, axis=1, inplace=True)
        transaction_df.columns = col_hdr_list

        return transaction_df

    def get_all_sold_holdings_details(self):
        data = self.sold_stocks_details.read_row_by_column_values()
        symbol_df = pd.DataFrame(data)
        col_name = list(symbol_df.columns)
        col_drop_list = []
        for hdr_name in col_name:
            if hdr_name not in SOLD_HOLDINGS_LIST_DISPLAY:
                col_drop_list.append(hdr_name)

        col_hdr_list = []
        for hdr_name in SOLD_HOLDINGS_LIST_DISPLAY:
            col_hdr_list.append(SOLD_HOLDING_DB_TO_DISPLAY[hdr_name])

        symbol_df.drop(col_drop_list, axis=1, inplace=True)
        symbol_df.columns = col_hdr_list

        return symbol_df

    def get_all_holdings_details(self):
        data = self.holdings_details.read_row_by_column_values()
        symbol_df = pd.DataFrame(data)
        col_name = list(symbol_df.columns)
        col_drop_list = []
        for hdr_name in col_name:
            if hdr_name not in CURRENT_HOLDING_LIST_DISPLAY:
                col_drop_list.append(hdr_name)

        col_hdr_list = []
        for hdr_name in CURRENT_HOLDING_LIST_DISPLAY:
            col_hdr_list.append(CURRENT_HOLDING_DB_TO_DISPLAY[hdr_name])

        symbol_df.drop(col_drop_list, axis=1, inplace=True)
        symbol_df.columns = col_hdr_list

        return symbol_df

    def layouts(self):
        self.mainLayout = QHBoxLayout()
        self.horizontalSplitter = QSplitter(Qt.Horizontal)
        self.leftVsplitter = QSplitter(Qt.Vertical)
        self.rightVsplitter = QSplitter(Qt.Vertical)
        self.rightBottomLayout = QHBoxLayout()

        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()
        self.leftTopGroupBox = QGroupBox("Current Holdings")
        self.rightTopGroupBox = QGroupBox("Script Information")

        # self.summary_payin = QGridLayout()
        # self.summary_payin.setContentsMargins(0, 0, 0, 0)
        # self.summary_payin.setSpacing(20)
        #
        # self.summary_payin.addWidget(self.dummy, 0, 0)
        # self.summary_payin.addWidget(self.cash_payin_total_LABEL, 1, 0)
        # self.summary_payin.addWidget(self.dummy, 2, 0)
        #
        # self.summary_payin.addWidget(self.dummy, 0, 1)
        # self.summary_payin.addWidget(self.cash_payin, 1, 1, Qt.AlignLeft)
        # self.summary_payin.addWidget(self.dummy, 2, 1)
        #
        # self.summary_payin.addWidget(self.dummy, 0, 2)
        # self.summary_payin.addWidget(self.credit_card_total_LABEL, 1, 2, Qt.AlignLeft)
        # self.summary_payin.addWidget(self.dummy, 2, 2)
        #
        # self.summary_payin.addWidget(self.dummy, 0, 3)
        # self.summary_payin.addWidget(self.credit_card_total, 1, 3, Qt.AlignLeft)
        # self.summary_payin.addWidget(self.dummy, 2, 3)
        #
        # self.summary_payin.addWidget(self.dummy, 0, 4)
        # self.summary_payin.addWidget(self.debit_card_total_LABEL, 1, 4)
        # self.summary_payin.addWidget(self.dummy, 2, 4)
        #
        # self.summary_payin.addWidget(self.dummy, 0, 5)
        # self.summary_payin.addWidget(self.debit_card_total, 1, 5, Qt.AlignLeft)
        # self.summary_payin.addWidget(self.dummy, 2, 5)
        #
        # self.summary_payin.addWidget(self.dummy, 0, 6)
        # self.summary_payin.addWidget(self.eft_payin_total_LABEL, 1, 6)
        # self.summary_payin.addWidget(self.dummy, 2, 6)
        #
        # self.summary_payin.addWidget(self.dummy, 0, 7)
        # self.summary_payin.addWidget(self.eft_payin_total, 1, 7, Qt.AlignLeft)
        # self.summary_payin.addWidget(self.dummy, 2, 7)
        #
        # self.summary_payin.addWidget(self.dummy, 0, 8)
        # self.summary_payin.addWidget(self.credit_note_total_LABEL, 1, 8)
        # self.summary_payin.addWidget(self.dummy, 2, 8)
        #
        # self.summary_payin.addWidget(self.dummy, 0, 9)
        # self.summary_payin.addWidget(self.credit_note_total, 1, 9, Qt.AlignLeft)
        # self.summary_payin.addWidget(self.dummy, 2, 9)
        #
        # self.summary_cash_balance = QGridLayout()
        # self.summary_cash_balance.addWidget(self.total_unpaid_Label, 0, 1)
        # self.summary_cash_balance.addWidget(self.total_unpaid_clearedLabel, 1, 1)
        # self.summary_cash_balance.addWidget(self.cash_balanceLabel, 2, 1)
        #
        # self.summary_cash_balance.addWidget(self.total_unpaid_amount, 0, 2)
        # self.summary_cash_balance.addWidget(self.total_cleared_amount, 1, 2)
        # self.summary_cash_balance.addWidget(self.overall_balance, 2, 2)
        #
        # self.overallsummaryGroupBox = QGroupBox(f"{DEBIT_TITLE} Summary")
        # self.overallsummaryGroupBox.setLayout(self.summary_payin)
        # self.overallsummaryGroupBox3 = QGroupBox('Balance Summary')
        # self.overallsummaryGroupBox3.setLayout(self.summary_cash_balance)
        #
        # self.overallsummaryGroupBox.setFont(SUMMARY_GBOX_TITLE)
        # self.overallsummaryGroupBox.setStyleSheet(SUMMARY_RECPT_TITLE_COLOR)
        # self.overallsummaryGroupBox3.setFont(SUMMARY_GBOX_TITLE)
        # self.overallsummaryGroupBox3.setStyleSheet(SUMMARY_CASHBALANCE_TITLE_COLOR)

        # self.rightBottomLayout.addWidget(self.overallsummaryGroupBox, 70)
        # self.rightBottomLayout.addWidget(self.overallsummaryGroupBox3, 30)

        # self.rightBottomWidget = QWidget()
        # self.rightBottomWidget.setLayout(self.rightBottomLayout)

        # self.leftLayout.addWidget(self.holdingTable)
        # ncol = self.holdingModel.columnCount()
        # row_data = []
        # for col in range(ncol):
        #     val = self.holdingTable.model().index(0, col).data()
        #     row_data.append(val)

        # self.plot_graphs()
        self.plot_market_valuation()
        self.rightLayout.addWidget(self.data_plot_browser)

        fnt_GBox = QFont()
        fnt_GBox.setPointSize(10)
        fnt_GBox.setBold(True)
        fnt_GBox.setFamily("Arial")
        self.leftTopGroupBox.setLayout(self.leftLayout)
        self.rightTopGroupBox.setLayout(self.rightLayout)
        self.leftTopGroupBox.setFont(fnt_GBox)
        self.leftTopGroupBox.setStyleSheet('QGroupBox:title {color: blue;}')
        self.rightTopGroupBox.setFont(fnt_GBox)
        self.rightTopGroupBox.setStyleSheet('QGroupBox:title {color: red;}')

        self.leftVsplitter.addWidget(self.leftTopGroupBox)
        self.rightVsplitter.addWidget(self.rightTopGroupBox)
        # self.rightVsplitter.addWidget(self.rightBottomWidget)
        self.rightVsplitter.setStretchFactor(0, 97)
        self.rightVsplitter.setStretchFactor(1, 3)

        self.horizontalSplitter.addWidget(self.leftVsplitter)
        self.horizontalSplitter.addWidget(self.rightVsplitter)
        self.horizontalSplitter.setStretchFactor(0, 10)
        self.horizontalSplitter.setStretchFactor(1, 90)
        self.horizontalSplitter.setContentsMargins(0, 0, 0, 0)
        self.horizontalSplitter.handle(0)

        self.mainLayout.addWidget(self.data_plot_browser)
        self.setLayout(self.mainLayout)

    def plot_market_valuation(self):
        # import pandas as pd
        # df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

        self.transactions_detail_df.sort_values(by="Date", ascending=True, inplace=True)

        fig = make_subplots(rows=2, cols=1,
                            # column_widths=[0.6, 0.4],
                            row_heights=[0.91, 0.1],
                            # specs=[[{}, {}]],
                            vertical_spacing=0.01,
                            shared_xaxes=True)

        fig.update_layout(margin=go.layout.Margin(
            l=80,  # left margin
            r=0,  # right margin
            b=30,  # bottom margin
            t=80  # top margin
        ))

        # add moving averages to df
        self.market_value_history['MA20'] = self.market_value_history['Close'].rolling(window=20, min_periods=1).mean()
        self.market_value_history['MA50'] = self.market_value_history['Close'].rolling(window=50, min_periods=1).mean()
        self.market_value_history['MA100'] = self.market_value_history['Close'].rolling(window=100, min_periods=1).mean()
        self.market_value_history['MA200'] = self.market_value_history['Close'].rolling(window=200, min_periods=1).mean()

        fig.add_trace(go.Candlestick(x=self.market_value_history['Date'],
                                     open=self.market_value_history['Open'],
                                     high=self.market_value_history['High'],
                                     low=self.market_value_history['Low'],
                                     close=self.market_value_history['Close'],
                                     name='Unrealised Gain/Loss[Rs]',
                                     showlegend=True))
        fig.add_trace(go.Scatter(x=self.market_value_history['Date'],
                                 y=self.market_value_history['MA20'],
                                 opacity=0.7,
                                 line=dict(color='black', width=2),
                                 name='SMA 20'))
        fig.add_trace(go.Scatter(x=self.market_value_history['Date'],
                                 y=self.market_value_history['MA50'],
                                 opacity=0.7,
                                 line=dict(color='blue', width=2),
                                 name='SMA 50'))
        fig.add_trace(go.Scatter(x=self.market_value_history['Date'],
                                 y=self.market_value_history['MA100'],
                                 opacity=0.7,
                                 line=dict(color='green', width=2),
                                 name='SMA 100'))
        fig.add_trace(go.Scatter(x=self.market_value_history['Date'],
                                 y=self.market_value_history['MA200'],
                                 opacity=0.7,
                                 line=dict(color='red', width=2),
                                 name='SMA 200'))

        fig.add_trace(go.Scatter(x=self.transactions_detail_df['Date'],
                                 y=self.transactions_detail_df['Cumulative_Amount'],
                                 opacity=0.7,
                                 mode='markers+lines',
                                 line=dict(color='red', width=3),
                                 marker=dict(color='LightSkyBlue', size=1, line=dict(color='blue', width=0.1)),
                                 name='Invesment[Rs]'))

        fig.add_trace(go.Scatter(x=self.overall_holdings['date'],
                                 y=self.overall_holdings['cml_gain_loss'],
                                 opacity=0.7,
                                 mode='markers+lines',
                                 line=dict(color='green', width=3),
                                 marker=dict(color='LightSkyBlue', size=3, line=dict(color='LightSkyBlue', width=0.2)),
                                 name='Realised Gain/Loss[Rs]'))

        colors = ['green' if row['gain_loss'] >= 0 else 'red' for index, row in self.overall_holdings.iterrows()]
        fig.add_trace(go.Bar(x=self.overall_holdings['date'],
                             y=self.overall_holdings['gain_loss'],
                             marker_color=colors,
                             text="Realised Gain/Loss[Rs]",
                             name='Realised Gain/Loss[Rs]',
                             ), row=2, col=1)

        # build complete timeline from start date to end date
        dt_all = pd.date_range(start=self.market_value_history.index[0], end=self.market_value_history.index[-1])
        # retrieve the dates that ARE in the original datset
        dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(self.market_value_history.index)]
        # print(dt_obs)
        # define dates with missing values
        dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]

        fig.update_layout(showlegend=True,
                          xaxis_rangeslider_visible=False,
                          xaxis_rangebreaks=[dict(values=dt_breaks)])

        # update y-axis label
        fig.update_yaxes(title_text="Market Value [Rs.]", showgrid=True, row=1, col=1)
        fig.update_yaxes(title_text=f"INR[Rs]", showgrid=True, row=2, col=1)
        # fig.update_yaxes(title_text="MACD", showgrid=True, row=3, col=1)
        # fig.update_yaxes(title_text="RSI", row=4, col=1)

        # hide dates with no values
        fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])
        # remove rangeslider
        # fig.update_layout(xaxis_rangeslider_visible=False)
        # # add chart title
        title_str="Summary of Holdings"
        data_info="Current Portfolio"
        if self.plot_all_returns_history:
            data_info = "Historic Portfolio"
        title_str=f"{title_str}({data_info})"
        fig.update_layout(title=title_str)
        # fig.layout.annotations[1].update(y=0.05)
        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))

        fig.update(layout_xaxis_rangeslider_visible=False)
        self.data_plot_browser.setHtml(fig.to_html(include_plotlyjs='cdn'))

    def plot_market_valuation1(self):
        # import pandas as pd
        # df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

        self.transactions_detail_df.sort_values(by="Date", ascending=True, inplace=True)

        # print(self.transactions_df.to_string())
        invested = {
            'x': self.transactions_detail_df["Date"],
            'y': self.transactions_detail_df["Cumulative_Amount"],
            'type': 'scatter',
            'mode': 'markers+lines',
            'line': {
                'width': 3,
                'color': 'red'
            },
            'marker': {
                'color': 'LightSkyBlue',
                'size': 3,
                'line': {
                    'color': 'blue',
                    'width': 0.5
                }
            },
            # 'name': 'Moving Average of 200 periods'
            'name': 'Invesment[Rs]'
        }

        gain_loss1 = {
            'x': self.overall_holdings["date"],
            'y': self.overall_holdings["cml_gain_loss"],
            'type': 'scatter',
            'mode': 'markers+lines',
            'line': {
                'width': 3,
                'color': 'green'
            },
            'marker': {
                'color': 'LightSkyBlue',
                'size': 3,
                'line': {
                    'color': 'blue',
                    'width': 0.5
                }
            },
            'name': 'Realised Gain/Loss[Rs]'
        }

        gain_loss = {
            'x': self.overall_holdings["date"],
            'y': self.overall_holdings["gain_loss"],
            'type': 'bar',
            # 'mode': 'markers+lines',
            # 'line': {
            #     'width': 3,
            #     'color': 'blue'
            # },
            # 'marker': {
            #     'color': 'LightSkyBlue',
            #     'size': 3,
            #     'line': {
            #         'color': 'blue',
            #         'width': 0.5
            #     }
            # },
            'name': 'Realised Gain/Loss[Rs]'
        }

        market_value = {
            'x': self.market_value_history['Date'],
            'open': self.market_value_history['Open'],
            'close': self.market_value_history['Close'],
            'high': self.market_value_history['High'],
            'low': self.market_value_history['Low'],
            'type': 'candlestick',
            'name': 'Unrealised Gain/Loss[Rs]'
        }

        data = [market_value, invested, gain_loss]
        # Config graph layout
        layout = go.Layout({
            'title': {
                'text': "Returns",
                'font': {
                    'size': 18
                }
            }
        })
        fig = go.Figure(data=data, layout=layout)
        # fig.add_hline(y=price, line_width=2, line_dash="dash", line_color="red")
        # fig.add_hline(y=price, line_width=2, line_color="red")
        fig.update_xaxes(title_text='Day')
        fig.update_yaxes(title_text='Market Value[Rs.]')
        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))

        # # fig = go.Figure(data=go.Ohlc(x=self.return_history['Date'],
        # fig = go.Figure(data=go.Candlestick(x=self.all_holding_history['Date'],
        #                                     open=self.all_holding_history['Open'],
        #                                     high=self.all_holding_history['High'],
        #                                     low=self.all_holding_history['Low'],
        #                                     close=self.all_holding_history['Close']))
        # fig.add_l(y=price, line_width=2, line_color="red")
        # fig.show()
        fig.update(layout_xaxis_rangeslider_visible=False)
        self.data_plot_browser.setHtml(fig.to_html(include_plotlyjs='cdn'))

    def plot_graphs(self, price=100, symbol="DMART"):

        # df = px.data.tips()
        # fig = px.box(df, x="day", y="total_bill", color="smoker")
        # fig.update_traces(quartilemethod="exclusive")  # or "inclusive", or "linear" by default
        # self.data_plot_browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        # path_to_symbol=f"{symbol}.NS"
        cwd = os.getcwd()
        # symbol = f"{symbol}.NS"
        path_to_csv_file = os.path.join(cwd, 'database', f"{symbol}_history.csv")
        if os.path.isfile(path_to_csv_file):
            df = pd.DataFrame(pd.read_csv(path_to_csv_file))
            # df.reset_index(inplace=True)
            # print(df.head().to_string())
            for i in ['Open', 'Close', 'High', 'Low']:
                df[i] = df[i].astype('float64')

            set1 = {
                'x': df.Date,
                'open': df.Open,
                'close': df.Close,
                'high': df.High,
                'low': df.Low,
                'type': 'candlestick',
            }

            # finding the moving average of 20 periods
            avg_20 = df.Close.rolling(window=20, min_periods=1).mean()

            # finding the moving average of 50 periods
            avg_50 = df.Close.rolling(window=50, min_periods=1).mean()

            # finding the moving average of 50 periods
            avg_100 = df.Close.rolling(window=100, min_periods=1).mean()

            # finding the moving average of 200 periods
            avg_200 = df.Close.rolling(window=200, min_periods=1).mean()

            set2 = {
                'x': df.Date,
                'y': avg_20,
                'type': 'scatter',
                'mode': 'lines',
                'line': {
                    'width': 2,
                    'color': 'blue'
                },
                # 'name': 'Moving Average of 20 periods'
                'name': '20 SMA'
            }

            set3 = {
                'x': df.Date,
                'y': avg_50,
                'type': 'scatter',
                'mode': 'lines',
                'line': {
                    'width': 2,
                    'color': 'red'
                },
                # 'name': 'Moving Average of 50 periods'
                'name': '50 SMA'
            }
            set4 = {
                'x': df.Date,
                'y': avg_100,
                'type': 'scatter',
                'mode': 'lines',
                'line': {
                    'width': 2,
                    'color': 'green'
                },
                # 'name': 'Moving Average of 100 periods'
                'name': '100 SMA'
            }

            set5 = {
                'x': df.Date,
                'y': avg_200,
                'type': 'scatter',
                'mode': 'lines',
                'line': {
                    'width': 2,
                    'color': 'black'
                },
                # 'name': 'Moving Average of 200 periods'
                'name': '200 SMA'
            }

            data = [set1, set2, set3, set4, set5]
            # Config graph layout
            layout = go.Layout({
                'title': {
                    'text': symbol,
                    'font': {
                        'size': 18
                    }
                }
            })
            fig = go.Figure(data=data, layout=layout)
            # fig.add_hline(y=price, line_width=2, line_dash="dash", line_color="red")
            fig.add_hline(y=price, line_width=2, line_color="red")
            fig.update_xaxes(title_text='Day')
            fig.update_yaxes(title_text='Price[Rs.]')
            fig.update_layout(legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ))
            # fig.update_traces(quartilemethod="linear")  # or "inclusive", or "linear" by default
            self.data_plot_browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
            # self.data_plot_browser.setHtml(fig.to_html())
            # fig.show()

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



    def calculate_sum(self):
        credit_card = "{:.{}f}".format(self.df_reception_payin["CreditCard"].sum(), 3)
        debit_card = "{:.{}f}".format(self.df_reception_payin["DebitCard"].sum(), 3)
        cash_payin = "{:.{}f}".format(self.df_reception_payin["Cash"].sum(), 3)
        unpaid = "{:.{}f}".format(self.df_reception_payin["Unpaid"].sum(), 3)
        eft_payin = "{:.{}f}".format(self.df_reception_payin["EFT"].sum(), 3)
        credit_notes = "{:.{}f}".format(self.df_reception_payin["CreditNote"].sum(), 3)

        total_transaction_reciept = float(cash_payin) + float(credit_card) + float(debit_card) + float(
            eft_payin) + float(credit_notes)
        balance_amount = float(unpaid) - float(total_transaction_reciept)

        self.credit_card_total.setText(format_currency(credit_card, 'INR', locale='en_IN'))
        self.debit_card_total.setText(format_currency(debit_card, 'INR', locale='en_IN'))
        self.cash_payin.setText(format_currency(cash_payin, 'INR', locale='en_IN'))
        self.unpaid_total.setText(format_currency(unpaid, 'INR', locale='en_IN'))
        self.eft_payin_total.setText(format_currency(eft_payin, 'INR', locale='en_IN'))
        self.credit_note_total.setText(format_currency(credit_notes, 'INR', locale='en_IN'))

        self.total_unpaid_amount.setText(format_currency(unpaid, 'INR', locale='en_IN'))
        self.total_cleared_amount.setText(format_currency(total_transaction_reciept, 'INR', locale='en_IN'))
        self.overall_balance.setText(format_currency(balance_amount, 'INR', locale='en_IN'))

        self.credit_card_total.setStyleSheet('color: blue')
        self.debit_card_total.setStyleSheet('color: blue')
        self.cash_payin.setStyleSheet('color: blue')
        self.unpaid_total.setStyleSheet('color: blue')
        self.eft_payin_total.setStyleSheet('color: blue')
        self.credit_note_total.setStyleSheet('color: green')

        self.total_unpaid_amount.setStyleSheet('color: red')
        self.total_cleared_amount.setStyleSheet('color: green')
        self.overall_balance.setStyleSheet('color: red')

    @pyqtSlot(QPoint)
    def rightClickMenuHoldings(self, pos):
        indexes = self.sender().selectedIndexes()
        mdlIdx = self.holdingTable.indexAt(pos)
        row = self.holdingTable.currentIndex().row()

        if not mdlIdx.isValid() and len(indexes) != 0:
            # print("return")
            return
        elif len(indexes) == 0 and not mdlIdx.isValid():
            # print("new..")
            self.menu_payin = QMenu(self)
            historyAct = QAction(QIcon(""), "History", self, triggered=self.plot_history)
            # CloseBalanceAct = QAction(QIcon(""), "Clear Balance and Close a/c", self, triggered=self.clear_and_close)
            # newAct.setShortcut(QKeySequence("Ctrl+N"))
            editStk = self.menu_payin.addAction(historyAct)
            # editStk = self.menu_payin.addAction(CloseBalanceAct)

        else:
            self.menu_payin = QMenu(self)
            # newAct = QAction(QIcon(""), "New", self, triggered=self.newBill_payin)
            # newAct.setShortcut(QKeySequence("Ctrl+N"))
            historyAct = QAction(QIcon(""), "History", self, triggered=self.plot_history)
            # replaceAct = QAction(QIcon(""), "New", self, triggered=self.replaceBill_payin)
            # replaceAct = QAction(QIcon(""), "Edit", self, triggered=self.replaceBill_payin)
            # duelistAct = QAction(QIcon(""), "Register Unpaid", self, triggered=self.move_to_unpaid_payin)
            # deleteAct = QAction(QIcon(""), "Delete", self, triggered=self.deleteBill)
            # CloseBalanceAct = QAction(QIcon(""), "Clear Balance and Close a/c", self, triggered=self.clear_and_close)
            # remAct.setStatusTip('Delete stock from database')
            # showAct = QAction(QIcon(""), 'Show', self, triggered=self.showBill)
            # addAct = self.menu_payin.addAction(newAct)
            editStk = self.menu_payin.addAction(historyAct)
            # editStk = self.menu_payin.addAction(replaceAct)
            # editStk = self.menu_payin.addAction(duelistAct)
            # editStk = self.menu_payin.addAction(CloseBalanceAct)
            # if self.my_access == "Administrator":
            # dispStk = self.menu_payin.addAction(deleteAct)
            # avgStk = self.menu_payin.addAction(showAct)
            self.menu_payin.addSeparator()

        self.menu_payin.exec_(self.sender().viewport().mapToGlobal(pos))



    # BILL_MODIFY_TYPE = ["Update", "Replace"]
    def plot_history(self):
        # fetch data from mysql
        index = self.holdingTable.currentIndex().row()
        ncol = self.holdingModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(index, col).data()
            row_data.append(val)

        # print(row_data)
        self.plot_graphs(price=row_data[2], symbol=row_data[0])

