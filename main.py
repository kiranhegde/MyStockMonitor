import datetime
import os.path
from pathlib import Path
import shutil
import tarfile
import time
import yfinance as yf

import pandas as pd
from PyQt5.QtCore import Qt, QTimer, QCoreApplication, QProcess
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QAction, QFileDialog, QTabWidget \
    , QMainWindow, QApplication, QMenu

# import PyQt5.sip # required to function exe file
import PyQt5.sip

from PyQt5.QtWidgets import QWidget, QListWidget, QMenu, QAction, QTableView, QLabel, QMessageBox, \
    QVBoxLayout, QHBoxLayout, QGroupBox, \
    QGridLayout, QAbstractItemView, \
    QHeaderView, QSplitter, QFileDialog

from utility.libnames import PDIR, WELCOME, MYSQL_SQLITE_DB, MYSQL_SQLITE_DB_LOGIN, PATH_TO_DATABASE_CURRENT_HOLDINGS, \
    PATH_TO_DATABASE, PATH_TO_DATABASE_BACKUP, PATH_TO_DATABASE_SOLD_HOLDINGS, PATH_TO_DATABASE_SOLD_HOLDINGS_BKP, \
    PATH_TO_DATABASE_CURRENT_HOLDINGS_BKP
from mysql_tools.tables_and_headers import CURRENT_HOLDINGS_DB_TABLE_NAME, SOLD_HOLDINGS_DB_TABLE_NAME, \
    BANK_TRANSACTIONS_DB_TABLE_NAME
from utility.utility_functions import make_nested_dict, date_time_day_start_end
from mysql_tools.mysql_crud import mysql_table_crud
from mysql_tools.tables_and_headers import CURRENT_HOLDINGS_DB_TABLE_NAME, create_current_holdings_table_db_query, \
    create_transaction_table_db_query, create_sold_holdings_table_db_query, create_all_holdings_table_db_query, \
    CURRENT_HOLDING_DB_HEADER, SOLD_HOLDING_DB_HEADER, BANK_TRANSACTIONS_DB_HEADER, TRADE_TYPE, \
    DEFAULTS_DB_HEADER, CURRENT_HOLDING_DB_HEADER, SOLD_HOLDINGS_DB_TABLE_NAME, TOTAL_HOLDINGS_DB_HEADER, \
    BANK_TRANSACTIONS_DB_TABLE_NAME, DEFAULTS_DB_HEADER, SOLD_HOLDINGS_LIST_DISPLAY, SOLD_HOLDING_DB_TO_DISPLAY, \
    TOTAL_HOLDINGS_DB_HEADER, TOTAL_HOLDINGS_DB_TABLE_NAME, TOTAL_HOLDINGS_CALC_HEADER, TOTAL_HOLDINGS_EXTRA_HEADER, \
    CURRENT_HOLDING_LIST_DISPLAY, CURRENT_HOLDING_DB_TO_DISPLAY, BANK_TRANSACTIONS_LIST_DISPLAY, \
    BANK_TRANSACTIONS_DB_TO_DISPLAY
from sqlite3_database.sqlite3_crud import sqlite3_crud
from gui_widgets.gui_widgets_add_mysql_login import update_mysql_login
from gui_widgets.gui_widgets_return_history_data_selection import return_history_range_selection
from display_tabs.current_holding_display import list_of_holdings_display
from display_tabs.overall_holding_returns_display import holdings_returns_display
from utility.fonts_style import FONT1, TABLE_HEADER_FONT, TABLE_FONT
from utility.utility_functions import reduce_mem_usage, symbol_date_range_string, date_symbol_split, gen_id,\
    symbol_date_string,create_current_holdings_csv_file_names,create_sold_holdings_csv_file_names,symbol_date_split
from utility.date_time import DATE_TIME, DATE_FMT_YMD, DATE_FMT_DMY, DATE_FMT_YDM
from utility.tableViewModel import pandasModel


# PEP8 Reformat Code press Ctrl+Alt+L.
# File>Setting>Save Actions -> disable/enable Reformat code
# https://stackoverflow.com/questions/40623605/how-to-stop-pycharm-auto-format-code-after-pasted/56991669

class TimerMessageBox(QMessageBox):
    def __init__(self, timeout=3, titles="Wait..", displayInfo="Please Wait...", parent=None):
        super(TimerMessageBox, self).__init__(parent)
        self.msg = displayInfo
        self.ttl = titles
        self.setWindowTitle(self.ttl)
        self.time_to_wait = timeout
        self.setText(f"{self.msg} \n wait (closing automatically in {timeout} seconds.) ")
        self.setStandardButtons(QMessageBox.NoButton)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()

    def changeContent(self):
        self.setText(f"{self.msg} \n wait (closing automatically in {self.time_to_wait} seconds.) ")
        self.time_to_wait -= 1
        if self.time_to_wait <= 0:
            self.close()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()


class MyMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.welcome = WELCOME
        self.setWindowTitle(self.welcome)
        self.setWindowIcon(QIcon('icons/ksirtet.ico'))
        self.setGeometry(450, 150, 750, 600)
        self.statusBar()
        self.close_now = False
        self.plot_all_returns_history = False
        self.UI()
        # self.setWindowState(Qt.WindowMaximized)
        # self.showNormal()
        # self.showMaximized()
        # self.showFullScreen()

    def UI(self):
        self.check_folders()
        self.check_sqlite_db_info()
        self.extablish_db_connection()
        self.check_db_tables_exists()
        self.connect_to_db_tables()

        # self.transactions_df = self.transaction_history()
        # self.overall_holdings = self.get_all_holdings_info()
        # print(self.overall_holdings.head().to_string())
        # print(self.current_holdings_csv_file_names)
        # print(self.sold_holdings_csv_file_names)

        # ------------------------------------------------
        # -----download stock history-----
        # self.update_database_from_csv()
        # exit()
        # -----download current stock history-----
        # self.update_stock_history()
        #  -----download stock history-----
        # self.update_sold_stock_history()
        # exit()
        # ------------------------------------------------


        # self.get_current_holdings_history()
        # self.get_sold_holdings_history()


        # convert all holdings to new format
        # self.export_all_holdings_to_db()
        # exit()

        # mask1=self.overall_holdings["current_holding"]==True
        # mask2=self.overall_holdings["equity"]=="AFFLE"
        # mask=mask1 & mask2
        # col_names=['ref_number', 'equity', 'date', 'price', 'quantity']
        # self.overall_holdings.sort_values(by=['equity'], ascending=True, inplace=True)
        #
        # df_new=self.overall_holdings.loc[mask1]
        # print(df_new[col_names].to_string())
        # export to excel sheet
        # self.export_all_holdings_to_excel()
        # ------------------------------------------------


        # self.overall_return()
        # exit()

        # print(self.sold_holding_history)

        # self.get_parameter_values()

        # backup_mysql(**self.db_cfg)

        # self.add_columns_name_to_table()
        # self.my_login()
        # print(self.user_list)
        self.toolBarMenu()
        self.toolBar()
        self.tabWidgets()
        # self.get_column_value_count()
        self.widgets()

    # @mysql_db(DB_CFG)
    # def check_mysql(self):
    #     pass


    def connect_to_db_tables(self):
        # self.current_holdings_details_db = mysql_table_crud(db_table=CURRENT_HOLDINGS_DB_TABLE_NAME,
        #                                                     db_header=CURRENT_HOLDING_DB_HEADER,
        #                                                     **self.db_cfg)
        # self.sold_stocks_details_db = mysql_table_crud(db_table=SOLD_HOLDINGS_DB_TABLE_NAME,
        #                                                db_header=SOLD_HOLDING_DB_HEADER,
        #                                                **self.db_cfg)

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
        # print(df.head(3).to_string())
        # print(df.tail(3).to_string())
        # print(df.info())
        # print(transactions_df.info())
        transactions_df = pd.concat([transactions_df, df]).groupby(['Date']).sum().reset_index()
        # print(transactions_df.isna().any())
        # exit()
        transactions_df['Cumulative_Amount'] = transactions_df['Amount'].cumsum()

        # print(transactions_df.to_string())
        return transactions_df

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

    def check_folders(self):
        # https: // stackoverflow.com / questions / 273192 / how - can - i - safely - create - a - nested - directory
        list_of_folders = [PATH_TO_DATABASE, PATH_TO_DATABASE_BACKUP, PATH_TO_DATABASE_CURRENT_HOLDINGS, \
                           PATH_TO_DATABASE_SOLD_HOLDINGS]
        list_of_backup_folders = [PATH_TO_DATABASE_BACKUP, PATH_TO_DATABASE_SOLD_HOLDINGS_BKP,
                                  PATH_TO_DATABASE_CURRENT_HOLDINGS_BKP]

        for folder in list_of_folders:
            # print(folder, os.path.exists(folder))
            if not os.path.exists(folder):
                Path(folder).mkdir(parents=True, exist_ok=True)
            # else:
            #     print(f"{folder} exists..")
        for folder in list_of_backup_folders:
            # print(folder, os.path.exists(folder))
            if not os.path.exists(folder):
                Path(folder).mkdir(parents=True, exist_ok=True)
            # else:
            #     print(f"{folder} exists..")

    def backup_folder(self, src_path, trg_path):
        for src_file in Path(src_path).glob('*.*'):
            filename = os.path.basename(src_file)
            distination = os.path.join(trg_path, filename)
            # shutil.copy(src_file, trg_path)
            shutil.move(src_file, distination)

        # # source = os.path.join(PATH_TO_DATABASE, PATH_TO_DATABASE_CURRENT_HOLDINGS, PATH_TO_DATABASE_SOLD_HOLDINGS)
        # source = os.path.join(PATH_TO_DATABASE, PATH_TO_DATABASE_CURRENT_HOLDINGS)
        # destination = os.path.join(PATH_TO_DATABASE, PATH_TO_DATABASE_BACKUP)
        # # source = os.path.join(root, "Documents and Settings", "rgolwalkar", "Desktop", "Desktop", "Dr Py", "Final_Py")
        # # destination = os.path.join(root, "Documents and Settings", "rgolwalkar", "Desktop", "Desktop", "PyDevResourse")
        # targetBackup = target + time.strftime('%Y%m%d%H%M%S') + 'tar.gz'
        # print(targetBackup)
        # print(source)
        # # tar = tarfile.open(targetBackup, "w:gz")
        # # tar.add(source)
        # # tar.close()

    def get_all_holdings_info(self):
        data = self.total_holdings_details.read_row_by_column_values(order="order by date asc")
        all_holding_df = pd.DataFrame(data)
        all_holding_df.sort_values(by=['equity'], ascending=True, inplace=True)
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
            # print(calc_df.to_string())

            for idx, row in calc_df.iterrows():
                mask_row = all_holding_df['ref_number'] == row['ref_number']
                for col in TOTAL_HOLDINGS_EXTRA_HEADER:
                    all_holding_df.loc[mask_row, col] = row[col]

        all_holding_df.sort_values(by=['date'], ascending=True, inplace=True)
        # drop_columns = ['id', 'remarks', 'ref_number', 'agency']
        drop_columns = ['id', 'remarks','agency']
        all_holding_df.drop(drop_columns, axis=1, inplace=True)
        all_holding_df['cml_gain_loss'] = all_holding_df['gain_loss'].cumsum()

        # print(all_holding_df.head(10).to_string())

        # if i == 3:
        # exit()

        return all_holding_df

    def export_all_holdings_to_excel(self, all_holding_df):

        print(all_holding_df.to_string())
        print(all_holding_df['gain_loss'].sum())

        drop_columns = ['id', 'remarks', 'ref_number', 'agency']
        all_holding_df.drop(drop_columns, axis=1, inplace=True)
        all_holding_df.rename({'equity': 'ticker'}, axis=1, inplace=True)
        path_to_excel = os.path.join(PDIR, PATH_TO_DATABASE, 'transactions.xlsx')

        writer = pd.ExcelWriter(path_to_excel, engine='xlsxwriter')

        # all_holding_df.to_excel(writer, sheet_name="dataframe", index=False)
        all_holding_df.to_excel(writer, index=False)
        writer.save()

    def calc_overall_trading_summary(self, df):
        df = df.sort_values(by=['date'], ascending=True).copy()
        # print(df.to_string())
        df.loc[:, 'transact_val'] = df.loc[:, 'quantity'] * df.loc[:, 'price']
        value_list = {'quantity': 0, 'cml_units': 0, 'prev_cost': 0, 'transact_val': 0, 'cml_cost': 0, 'avg_price': 0}
        i = 0
        for idx, row in df.iterrows():
            date = row['date']
            type = row['type']
            quantity = row['quantity']
            transact_val = row['transact_val']
            avg_price = row['avg_price']
            price = row['price']
            prev_units = row['quantity']
            cml_units = row['cml_units']
            prev_cost = row['prev_cost']

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
                    df.loc[idx, ('gain_loss')] = quantity * (price - avg_price)
                    df.loc[idx, ('yield')] = price / avg_price - 1.0

                    # -------------------------------------------
                    value_list['quantity'] = prev_unit_new - quantity
                    value_list['avg_price'] = avg_price
            i += 1
        # print("-------->")
        # print(df.to_string())
        # exit()
        return df

    def export_all_holdings_to_db(self):
        # print(self.sold_holding_history.keys())
        total_holdings_df = pd.DataFrame(columns=TOTAL_HOLDINGS_DB_HEADER)
        print(total_holdings_df.to_string())
        holding_history = make_nested_dict()
        for key in TOTAL_HOLDINGS_DB_HEADER:
            holding_history[key] = None
        # print(holding_history)
        # ['id', 'ref_number', 'agency', 'exchange', 'equity', 'buy_date', 'buy_price',
        # 'sale_date', 'sale_price', 'sale_quantity', 'remarks']

        data = self.sold_stocks_details_db.read_row_by_column_values(order="order by equity asc")
        sold_holding_df = pd.DataFrame(data)
        for index, row in sold_holding_df.iterrows():
            holding_history['id'] = 0
            holding_history['ref_number'] = gen_id(**self.db_cfg)
            holding_history['date'] = row['buy_date']
            holding_history['type'] = TRADE_TYPE[0]
            holding_history['agency'] = row["agency"]
            # holding_history['exchange'] = row["exchange"]
            holding_history['equity'] = row["equity"]
            holding_history['quantity'] = row["sale_quantity"]
            holding_history['price'] = row["buy_price"]
            holding_history['fees'] = 0
            holding_history['avg_price'] = row["buy_price"]
            holding_history['current_holding'] = False
            holding_history['remarks'] = TRADE_TYPE[0]
            buy_df = pd.DataFrame([holding_history])
            total_holdings_df = pd.concat([buy_df, total_holdings_df]).reset_index(drop=True)

            holding_history['id'] = 0
            holding_history['ref_number'] = gen_id(**self.db_cfg)
            holding_history['date'] = row['sale_date']
            holding_history['type'] = TRADE_TYPE[1]
            holding_history['agency'] = row["agency"]
            # holding_history['exchange'] = row["exchange"]
            holding_history['equity'] = row["equity"]
            holding_history['quantity'] = row["sale_quantity"]
            holding_history['price'] = row["sale_price"]
            holding_history['fees'] = 0
            holding_history['avg_price'] = row["buy_price"]
            holding_history['current_holding'] = False
            holding_history['remarks'] = TRADE_TYPE[1]
            sell_df = pd.DataFrame([holding_history])
            total_holdings_df = pd.concat([sell_df, total_holdings_df]).reset_index(drop=True)

        total_holdings_df.sort_values(by=['date'], ascending=True, inplace=True)
        # ['id', 'ref_number', 'agency', 'exchange', 'equity', 'buy_date', 'avg_price', 'quantity',
        #  'remarks']
        data_current = self.current_holdings_details_db.read_row_by_column_values(order="order by equity asc")
        current_holding_df = pd.DataFrame(data_current)
        for index, row in current_holding_df.iterrows():
            holding_history['id'] = 0
            holding_history['ref_number'] = gen_id(**self.db_cfg)
            holding_history['date'] = row['buy_date']
            holding_history['type'] = TRADE_TYPE[0]
            holding_history['agency'] = row["agency"]
            # holding_history['exchange'] = row["exchange"]
            holding_history['equity'] = row["equity"]
            holding_history['quantity'] = row["quantity"]
            holding_history['price'] = row["avg_price"]
            holding_history['fees'] = 0
            holding_history['avg_price'] = row["avg_price"]
            holding_history['current_holding'] = True
            holding_history['remarks'] = TRADE_TYPE[0]
            buy_df = pd.DataFrame([holding_history])
            total_holdings_df = pd.concat([buy_df, total_holdings_df]).reset_index(drop=True)

        total_holdings_df.sort_values(by=['date'], ascending=True, inplace=True)
        print(total_holdings_df.to_string())

        # writing to database
        for indx, row in total_holdings_df.iterrows():
            row = row.to_dict()
            listt = list(row.values())
            vals_tuple = [tuple(listt)]
            messge = self.total_holdings_details.insert_row_by_column_values(row_val=vals_tuple)
            print(messge)

        exit()

        # for symb, hist_df in self.sold_holding_history.items():
        #     symbol, start_date, end_date = date_symbol_split(symb)
        #     print(symbol, start_date, end_date)
        #     print(hist_df.head().to_string())
        #     exit()



    def create_sold_holdings_csv_file_names(self, df):
        # self.sold_holdings_csv_file_names=make_nested_dict()
        return create_sold_holdings_csv_file_names(df)

    def get_sold_holdings_history(self):
        self.sold_holdings_csv_file_names = self.create_sold_holdings_csv_file_names(self.overall_holdings)

        self.sold_holding_history = make_nested_dict()
        # data = self.sold_stocks_details_db.read_row_by_column_values(order="order by equity asc")
        # search_item = f"current_holding = {False}"
        # data = self.total_holdings_details.read_row_by_column_values(criteria=search_item,
        #                                                              order="order by equity asc")
        # sold_holding_df = pd.DataFrame(data)
        # print(sold_holding_df.to_string())

        mask1 = self.overall_holdings["current_holding"] == False
        symbol_df = self.overall_holdings[mask1].copy()
        symbol_list = sorted(list(set(symbol_df['equity'].to_list())))
        for symbol in symbol_list:
            mask1=self.overall_holdings["current_holding"]==False
            mask2=self.overall_holdings["equity"]== symbol
            mask=mask1 & mask2
            col_list = ['date', 'type', 'quantity', 'prev_units', 'cml_units']
            df=self.overall_holdings.loc[mask,col_list].copy()
            df.sort_values(by=['date'], ascending=True, inplace=True)

            # print(symbol)
            # if symbol == "IRCTC":
            #     print(df.to_string())

            c=0
            cml_units_old=0
            start_date=datetime.date.today()
            end_date=datetime.date.today()
            for index, row in df.iterrows():
                if row['prev_units'] == 0 :
                   start_date = row['date']
                   cml_units_old = row['cml_units']

                if row['cml_units'] < cml_units_old:
                    end_date = row['date']

                if c==0 and row['type'] != 'Buy' : #and start_date != end_date :
                    print( 'start_date',start_date)
                    print( 'end_date',end_date)
                    print(f"Something wrong, before selling a stock must bought {symbol}")
                    print(df.to_string())
                    exit()

                c += 1
                if row['type'] == 'Sell':
                    # print(start_date,end_date, row['type'])
                    symbol_date_range = symbol_date_range_string(symbol, start_date, end_date)
                    # csv_file_name = f"{symbol_date_range}_Xquantiy.csv"
                    csv_file_name = f"{symbol_date_range}.csv"
                    path_to_csv_file = os.path.join(PDIR, PATH_TO_DATABASE_SOLD_HOLDINGS, csv_file_name)
                    if os.path.isfile(path_to_csv_file):
                        df = pd.DataFrame(pd.read_csv(path_to_csv_file))
                        for i in ['Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']:
                            df[i] = df[i].astype('float64')
                            # df[i] = df[i].astype("category")
                        # self.sold_holding_history[symbol_date_range] = reduce_mem_usage(df)
                        self.sold_holding_history[symbol_date_range] = df
                    else:
                        print(path_to_csv_file, 'path missing, downloading the data..')
                        symbol_ns = f"{symbol}.NS"
                        sale_date_1 = datetime.date.fromisoformat(str(end_date)) + datetime.timedelta(days=1)
                        data = yf.download(symbol_ns, start=start_date, end=sale_date_1)
                        data.to_csv(path_to_csv_file)
                        df = pd.DataFrame(pd.read_csv(path_to_csv_file))
                        for i in ['Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']:
                            df[i] = df[i].astype('float64')
                            # df[i] = df[i].astype("category")
                        # self.sold_holding_history[symbol_date_range] = reduce_mem_usage(df)
                        self.sold_holding_history[symbol_date_range] = df

    
    def overall_return(self):

        self.market_value_history = pd.DataFrame()

        # equity_list = self.current_holdings_details_db.read_row_by_column_values(order="order by equity asc")
        # print(equity_list)
        # print("===========>")
        # search_item = f"current_holding = {True}"
        # equity_list = self.total_holdings_details.read_row_by_column_values(criteria=search_item,order="order by equity asc")
        # print(equity_list)

        # mask = self.overall_holdings["current_holding"] == True
        # symbol_df = self.overall_holdings[mask].copy()
        # symbol_list = sorted(list(set(symbol_df['equity'].to_list())))
        for symbol_buy_date in self.current_holdings_csv_file_names.keys():
        # for val in symbol_list:
        #     print(val)
            df = self.current_holding_history[symbol_buy_date]
            print(symbol_buy_date)
            symbol, buy_date=symbol_date_split(symbol_buy_date)
            print(df.head(3).to_string())
            # print(df)
            # exit()
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            start_date = pd.to_datetime(buy_date)
            quantity = float(val['quantity'])
            # start_date = pd.to_datetime(val['buy_date']) - datetime.timedelta(0)
            mask1 = df['Date'] >= start_date
            df = df[mask1].copy()
            header_name = ['Open', 'High', 'Low', 'Close', 'Adj Close']
            for col in header_name:
                df[col] = df[col].apply(lambda x: x * quantity)
                df['Volume'] = 1
            df.sort_values(by=['Date'], ascending=True, inplace=True)
            self.market_value_history = pd.concat([self.market_value_history, df]).groupby(['Date']).sum().reset_index()

        if self.plot_all_returns_history:
            # equity_list = self.sold_stocks_details_db.read_row_by_column_values(order="order by equity asc")
            search_item = f"current_holding = {False}"
            equity_list = self.total_holdings_details.read_row_by_column_values(criteria=search_item,
                                                                                order="order by equity asc")
            for val in equity_list:
                symbol = val['equity']
                buy_date = pd.to_datetime(val['buy_date'])
                sale_date = pd.to_datetime(val['sale_date'])
                quantity = float(val['sale_quantity'])
                symbol_date_range = symbol_date_range_string(symbol, val['buy_date'], val['sale_date'])
                df = self.sold_holding_history[symbol_date_range]
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                mask1 = df['Date'] >= buy_date
                mask2 = df['Date'] <= sale_date
                mask = mask1 & mask2
                df = df[mask].copy()
                header_name = ['Open', 'High', 'Low', 'Close', 'Adj Close']
                for col in header_name:
                    df[col] = df[col].apply(lambda x: x * quantity)
                    df['Volume'] = 1
                df.sort_values(by=['Date'], ascending=True, inplace=True)
                self.market_value_history = pd.concat([self.market_value_history, df]).groupby(['Date']).sum().reset_index()

        # print(self.market_value_history.head(10).to_string())
        # print(self.return_history['Close'].sum())
        #     # https: // www.analyticsvidhya.com / blog / 2020 / 05 / datetime - variables - python - pandas /
        # # df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')


    def get_all_sold_holdings_details(self):
        data = self.sold_stocks_details_db.read_row_by_column_values(order="order by equity asc")
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
        symbol_df.sort_values(by=['Buy Date'], ascending=True, inplace=True)

        return symbol_df

    def get_all_current_holdings_details(self):
        # data = self.sold_stocks_details_db.read_row_by_column_values(order="order by equity asc")
        data = self.current_holdings_details_db.read_row_by_column_values(order="order by equity asc")
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
        symbol_df.sort_values(by=['Buy Date'], ascending=True, inplace=True)

        return symbol_df

    def create_current_holdings_csv_file_names(self, df):
        # self.current_holdings_csv_file_names=make_nested_dict()
        return create_current_holdings_csv_file_names(df)

    def get_current_holdings_history(self):
        self.current_holdings_csv_file_names = self.create_current_holdings_csv_file_names(self.overall_holdings)
        self.current_holding_history = make_nested_dict()
        mask = self.overall_holdings["current_holding"] == True
        symbol_df=self.overall_holdings[mask]

        for index, row in symbol_df.iterrows():
            symbol = row['equity']
            buy_date = row['date']
            symbol_buy_date = symbol_date_string(symbol, buy_date)
            path_to_csv_file = self.current_holdings_csv_file_names[symbol_buy_date]
            # path_to_csv_file = os.path.join(PDIR, PATH_TO_DATABASE_CURRENT_HOLDINGS, f"{symbol}_history.csv")

            if os.path.isfile(path_to_csv_file):
                # print(path_to_csv_file)
                df = pd.DataFrame(pd.read_csv(path_to_csv_file))
                deltatime = datetime.date.today() - datetime.timedelta(5 * 365)
                mask = df['Date'] > str(deltatime)
                # print('----------------before')
                # print(df.memory_usage(deep=True))
                for i in ['Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']:
                    df[i] = df[i].astype('float64')
                    # df[i] = df[i].astype("category")
                # print('----------------after')
                # df = reduce_mem_usage(df)
                # print(df.memory_usage(deep=True))
                df = df.loc[mask].copy()
                self.current_holding_history[symbol_buy_date] = reduce_mem_usage(df)
                # print(df.head(4).to_string())
            else:
                print(path_to_csv_file, 'path missing')
                symbol_ns = f"{symbol}.NS"
                data = yf.download(symbol_ns)
                # print(symbol, path_to_csv_file)
                data.to_csv(path_to_csv_file)
                df = pd.DataFrame(pd.read_csv(path_to_csv_file))
                for i in ['Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']:
                    df[i] = df[i].astype('float64')
                    # df[i] = df[i].astype("category")
                # self.sold_holding_history[symbol_date_range] = reduce_mem_usage(df)
                self.current_holding_history[symbol_buy_date] = reduce_mem_usage(df)

        # print(self.holding_history)
        # self.holding_history[symbol] = df
        # data = self.holdings_display_table.read_row_by_column_values()
        #
        # for symbol, hist in self.holding_history.items():
        #     print(symbol)
        #     print(hist.head(3).to_string())
        # for symbol in self.holding_history.keys():
        #     print(symbol)
        # self.holding_history
        # print(df.info())
        # exit()

    # def get_stock_history_data(self):
    #     cwd = os.getcwd()
    #
    #     data = self.holdings_display_table.read_row_by_column_values()
    #     symbol_df = pd.DataFrame(data)
    #
    #     return
    #     # col_name = list(symbol_df.columns)
    #     # list of header name to be dropped
    #     # col_drop_list = []
    #     # for hdr_name in col_name:
    #     #     if hdr_name not in CURRENT_HOLDING_LIST_DISPLAY:
    #     #         col_drop_list.append(hdr_name)
    #     #
    #     # # list of header name to be retained
    #     # col_hdr_list = []
    #     # for hdr_name in CURRENT_HOLDING_LIST_DISPLAY:
    #     #     col_hdr_list.append(CURRENT_HOLDING_DB_TO_DISPLAY[hdr_name])
    #
    #     # symbol_df.drop(CURRENT_HOLDINGS_HEADER_DROP_LIST, axis=1, inplace=True)
    #     # symbol_df.columns = CURRENT_HOLDINGS_HEADER_DISPLAY_LIST
    #
    #     # symbol = f"{symbol}.NS"
    #     path_to_csv_file = os.path.join(cwd, PATH_TO_DATABASE_CURRENT_HOLDINGS, f"{symbol}_history.csv")
    #     if os.path.isfile(path_to_csv_file):
    #         df = pd.DataFrame(pd.read_csv(path_to_csv_file))
    #         # df.reset_index(inplace=True)
    #         # print(df.head().to_string())
    #         for i in ['Open', 'Close', 'High', 'Low']:
    #             df[i] = df[i].astype('float64')

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

    def update_database_from_csv(self):
        # 1. current
        # 2. sold
        # 3. transactions

        key = 2
        if key == 1:
            # read holdings
            # path_to_holdings = os.path.join(cwd, PATH_TO_DATABASE, 'purchase.csv')
            path_to_holdings = os.path.join(PDIR, PATH_TO_DATABASE_CURRENT_HOLDINGS, 'purchase_00.xlsx')
            # holding_df = pd.read_csv(path_to_holdings, parse_dates=['trade_date'])
            holding_df = pd.read_excel(path_to_holdings)
            # print(holding_df.head().to_string())
            # print(type(holding_df))
            mask1 = holding_df['agency'] == 'Kotak'
            mask2 = holding_df['agency'] == 'Zerodha'
            holding_df = holding_df[mask1 | mask2].copy()
            # exit()
            # print(holding_df.to_string())
            # holding_df.trade_date = holding_df.trade_date.apply(lambda x: dateutil.parser.parse(x, dayfirst=True))

            # holding_df = pd.read_csv(path_to_holdings)
            col_to_remove = ['settle_date', 'unit_brockerage', 'gst_brockerage', 'stt',
                             'income_tax']
            holding_df['remarks'] = None
            holding_df.drop(col_to_remove, axis=1, inplace=True)
            # print(holding_df.head(5).to_string())
            # holding_df['trade_date'] = pd.to_datetime(holding_df['trade_date'], infer_datetime_format=True)
            # print(holding_df.head(5).to_string())
            # holding_df['trade_date'] = holding_df['trade_date'].dt.strftime(DATE_FMT_YMD)

            holding_df.sort_values(by=['trade_date'], ascending=True, inplace=True)
            # print(holding_df.to_string())
            #
            holding_df.reset_index(inplace=True)
            holding_df.columns = CURRENT_HOLDING_DB_HEADER
            print(holding_df.head(10).to_string())
            print(holding_df.info())
            holding_df.reset_index(drop=True, inplace=True)
            self.call_import_csv_to_mysql(csv_to_df=holding_df, table_name=CURRENT_HOLDINGS_DB_TABLE_NAME,
                                          csv_data=True)
        elif key == 2:
            # read sold stoks
            # path_to_sold_stock = os.path.join(cwd, PATH_TO_DATABASE, 'sale.csv')
            # sold_holding_df = pd.read_csv(path_to_sold_stock, parse_dates=['buy_date', 'trade_date'])
            # sold_holding_df['buy_date'] = sold_holding_df['buy_date'].dt.strftime(DATE_FMT_YDM)
            # # sold_holding_df['buy_date'] = pd.to_datetime(sold_holding_df['buy_date'])
            # sold_holding_df['trade_date'] = sold_holding_df['trade_date'].dt.strftime(DATE_FMT_YDM)
            # # sold_holding_df['trade_date'] = pd.to_datetime(sold_holding_df['trade_date'])

            path_to_sold_stock = os.path.join(PDIR, PATH_TO_DATABASE_SOLD_HOLDINGS, 'sale_00.xlsx')
            # holding_df = pd.read_csv(path_to_holdings, parse_dates=['trade_date'])
            sold_holding_df = pd.read_excel(path_to_sold_stock)
            mask1 = sold_holding_df['agency'] == 'Kotak'
            mask2 = sold_holding_df['agency'] == 'Zerodha'
            sold_holding_df = sold_holding_df[mask1 | mask2].copy()

            col_to_remove = ['settle_date', 'brokerage', 'gst', 'stt', 'itax']
            sold_holding_df.drop(col_to_remove, axis=1, inplace=True)
            sold_holding_df.sort_values(by=['buy_date'], ascending=True, inplace=True)
            sold_holding_df['remarks'] = None
            sold_holding_df.reset_index(inplace=True)
            sold_holding_df.columns = SOLD_HOLDING_DB_HEADER
            print(sold_holding_df.head(10).to_string())
            print(sold_holding_df.info())
            sold_holding_df.reset_index(drop=True, inplace=True)
            self.call_import_csv_to_mysql(csv_to_df=sold_holding_df, table_name=SOLD_HOLDINGS_DB_TABLE_NAME,
                                          csv_data=True)
        elif key == 3:
            # read transactions
            # path_to_sold_trans = os.path.join(cwd, PATH_TO_DATABASE, 'investment.csv')
            # transactions_df = pd.read_csv(path_to_sold_trans, parse_dates=['tr_date'])
            # transactions_df['tr_date'] = transactions_df['tr_date'].dt.strftime(DATE_FMT_YDM)
            # # transactions_df['tr_date'] = pd.to_datetime(transactions_df['tr_date'])
            path_to_sold_trans = os.path.join(PDIR, PATH_TO_DATABASE_CURRENT_HOLDINGS, 'investment_00.xlsx')
            # holding_df = pd.read_csv(path_to_holdings, parse_dates=['trade_date'])
            transactions_df = pd.read_excel(path_to_sold_trans)
            mask1 = transactions_df['agency'] == 'Kotak'
            mask2 = transactions_df['agency'] == 'Zerodha'
            transactions_df = transactions_df[mask1 | mask2].copy()

            # transactions_df.sort_values(by=['tr_date'], ascending=True, inplace=True)
            transactions_df['remarks'] = None
            transactions_df.columns = BANK_TRANSACTIONS_DB_HEADER
            print(transactions_df.to_string())
            print(transactions_df.info())
            transactions_df.reset_index(drop=True, inplace=True)
            self.call_import_csv_to_mysql(csv_to_df=transactions_df, table_name=BANK_TRANSACTIONS_DB_TABLE_NAME,
                                          csv_data=True)
        else:
            print("Unknown excel to MYSQL")
        # self.csv_to_df

    def check_sqlite_db_info(self):
        sqlite_db_path = f"sqlite3_database/{MYSQL_SQLITE_DB}"
        file_path = Path(sqlite_db_path)

        try:
            my_abs_path = file_path.resolve(strict=True)
        except FileNotFoundError:
            # # logger.critical("Failed to connect to MYSQL server")
            # msg = TimerMessageBox(10, "Database file missing !!",
            #                       f"{sqlite_db_path} missing ...\nExiting... ")
            # msg.exec_()
            # self.quit_now()

            mbox0 = QMessageBox.question(self, "MySQL database login issue!",
                                         "MYSQL login information table missing \nCreate new sql database ? ",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            message = ""
            if mbox0 == QMessageBox.Yes:
                self.mysql_hostname = "localhost"
                self.mysql_login = "kiran"
                self.mysql_passwd = "mypassword"
                self.mysql_dbname = "stock_database"
                self.mysql_port = "3306"
                # logger.warning(f"{self.mysql_dbname} MYSQL DB created ")
                # message = mysql_table_crud(**cfg_db).create_database(dbname=self.mysql_dbname)
                db = sqlite3_crud(filename=file_path, table=MYSQL_SQLITE_DB_LOGIN)
                sql = db.mysql_login(MYSQL_SQLITE_DB_LOGIN)
                db.sql_do(sql)
                message = f"{file_path} created with table {MYSQL_SQLITE_DB_LOGIN}"
                QMessageBox.information(self, "Database creation", message)
            else:
                # logger.warning(f"{self.mysql_dbname}  MYSQL DB required ")
                QMessageBox.question(self, "Exiting !", "Provide sql database with login information...  ",
                                     QMessageBox.Ok, QMessageBox.Ok)
                self.quit_now()
        else:
            pass
            # logger.info("Connected to MYSQL server")

        # self.mysql_log_data = sqlite3_crud(filename=f"{my_abs_path}", table=MYSQL_SQLITE_DB_LOGIN)
        # print(self.mysql_log_data.mysql_login())

    def extablish_db_connection(self):
        # logger.info("Connecting to MYSQL server")
        sqlite_db_path = f"sqlite3_database/{MYSQL_SQLITE_DB}"
        file_path = Path(sqlite_db_path)
        # print('extablish_db_connection')

        try:
            my_abs_path = file_path.resolve(strict=True)
        except FileNotFoundError:
            # logger.critical("Failed to connect to MYSQL server")
            msg = TimerMessageBox(10, "Database file missing !!",
                                  f"{sqlite_db_path} missing ... \n {self.print_message} \nExiting... ")
            msg.exec_()
            self.quit_now()
        else:
            pass
            # logger.info("Connected to MYSQL server")
        # print(f"{my_abs_path}")
        self.mysql_log_data = sqlite3_crud(filename=f"{my_abs_path}", table=MYSQL_SQLITE_DB_LOGIN)
        table_empty = self.mysql_log_data.check_table_empty(MYSQL_SQLITE_DB_LOGIN)

        if table_empty:
            mbox0 = QMessageBox.question(self, "MYSQL login issue !! ",
                                         "MYSQL login table empty ... \n Would you like to provide update login ? ",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if mbox0 == QMessageBox.Yes:
                self.mysql_hostname = "localhost"
                self.mysql_login = "kiran"
                self.mysql_passwd = "mypassword"
                self.mysql_dbname = "stock_database"
                self.mysql_port = "3306"
                # logger.info("Getting MYSQL server info")
                self.mysql_login_info(close_now=self.close_now)
                self.quit_now()
            else:
                # logger.warning(f"{self.mysql_dbname}  MYSQL DB required ")
                QMessageBox.question(self, "Exiting !",
                                     "MYSQL login table empty...\nCannot login to server without credentials  ",
                                     QMessageBox.Ok, QMessageBox.Ok)
                self.quit_now()

        else:
            mysql_log = self.mysql_log_data.retrieve('1')
            self.mysql_hostname = mysql_log['mysql_hostname']
            self.mysql_login = mysql_log['mysql_login']
            self.mysql_passwd = mysql_log['mysql_passwd']
            self.mysql_dbname = mysql_log['mysql_dbname']
            self.mysql_port = mysql_log['mysql_port']

            self.db_cfg = dict(user=mysql_log['mysql_login'],
                               passwd=mysql_log['mysql_passwd'],
                               port=mysql_log['mysql_port'],
                               host=mysql_log['mysql_hostname'],
                               db=mysql_log['mysql_dbname'])

            cfg_db = dict(user=mysql_log['mysql_login'],
                          passwd=mysql_log['mysql_passwd'],
                          port=mysql_log['mysql_port'],
                          host=mysql_log['mysql_hostname'])

            db_check, self.print_message = mysql_table_crud(**cfg_db).check_db_exists(self.mysql_dbname)

            if not db_check:
                # logger.warning("MYSQL DB missing..")
                mbox0 = QMessageBox.question(self, "Database Missing !", "Create new database ? ",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if mbox0 == QMessageBox.Yes:
                    # logger.warning(f"{self.mysql_dbname} MYSQL DB created ")
                    message = mysql_table_crud(**cfg_db).create_database(dbname=self.mysql_dbname)
                    QMessageBox.information(self, "Database creation", message)
                else:
                    # logger.warning(f"{self.mysql_dbname}  MYSQL DB required ")
                    QMessageBox.question(self, "Exiting !", "Provide Database connection and try again...  ",
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.quit_now()

            connection, self.print_message = mysql_table_crud(**self.db_cfg).db_connection()
            if not connection:
                # logger.critical("Access denied !!  MYSQL server connection failed")
                mbox0 = QMessageBox.question(self, "Access denied !! ",
                                             "Failed to connect to server ... \n Would you like to provide updated login ? ",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if mbox0 == QMessageBox.Yes:
                    # logger.info("Getting MYSQL server info")
                    self.mysql_login_info(close_now=self.close_now)
                    self.quit_now()
                else:
                    # logger.critical("exiting !!  MYSQL server connection failed")
                    msg = TimerMessageBox(10, "Access denied !!",
                                          f"Failed to connect to server ... \n {self.print_message} \nExiting... ")
                    msg.exec_()
                    self.quit_now()

    def get_parameter_values(self):
        parameter_conn = mysql_table_crud(db_table=PARAMETER_VALUES,
                                          db_header=PARAMETER_VALUES_HEADER,
                                          **self.db_cfg)

        para = parameter_conn.read_row_by_column_values(column_name="*")
        para_df = pd.DataFrame(para)

        if len(para_df) == 0:
            # https: // blog.softhints.com / insert - multiple - rows - at - once -with-python - and -mysql /
            initial_values = [(0, 'medical_gui', 1),
                              (0, 'hospital_gui', 0)
                              ]
            messge = parameter_conn.insert_row_by_column_values(row_val=initial_values)
            para = parameter_conn.read_row_by_column_values(column_name="*")
            para_df = pd.DataFrame(para)

        para_df.drop(['id'], axis=1, inplace=True)
        mask1 = para_df['parameter_name'] == 'medical_gui'
        mask2 = para_df['parameter_name'] == 'hospital_gui'
        self.bsheet_medical = bool(para_df.loc[mask1, ['check_condition']].values[0][0])
        self.bsheet_hospital = bool(para_df.loc[mask2, ['check_condition']].values[0][0])

    def update_window_title(self, usr):
        if self.bsheet_medical:
            self.welcome = "Durga Medicals, Daily Transaction"
            self.setWindowTitle(f"{self.welcome} ( {usr} )")
        else:
            self.setWindowTitle(f"{self.welcome} ( {usr} )")

    def widgets(self):
        self.tabs_selected = make_nested_dict()
        # self.bsheet_loaded = []
        self.tabs_displayed = make_nested_dict()

        self.print_message = "Welcome"
        # self.bsheet_title="0"
        # self.bsheet_count=0
        self.holdings_tab()
        # self.load_returns()

    def get_column_value_count(self):
        payin_table = mysql_table_crud(db_table=HOSPITAL_BILL_PAYIN_PREFIX,
                                       db_header=PAYIN_TABLE_HEADER,
                                       **self.db_cfg)
        table_list = payin_table.get_column_value_count("department")
        dpt = [list(item.values())[0] for item in table_list]
        # print(dpt)
        dept = make_nested_dict()
        for item in table_list:
            # print(list(item.values())[0],list(item.values())[1])
            dept[list(item.values())[0]] = list(item.values())[1]

        # print(dept)

    def check_db_tables_exists(self):
        list_of_tables = {
            # "xyz": create_receptionPAYIN_table_db_query("xyz"),
            CURRENT_HOLDINGS_DB_TABLE_NAME: create_current_holdings_table_db_query(CURRENT_HOLDINGS_DB_TABLE_NAME),
            SOLD_HOLDINGS_DB_TABLE_NAME: create_sold_holdings_table_db_query(SOLD_HOLDINGS_DB_TABLE_NAME),
            BANK_TRANSACTIONS_DB_TABLE_NAME: create_transaction_table_db_query(BANK_TRANSACTIONS_DB_TABLE_NAME),
            TOTAL_HOLDINGS_DB_TABLE_NAME: create_all_holdings_table_db_query(TOTAL_HOLDINGS_DB_TABLE_NAME)
        }

        for table in list_of_tables.keys():
            table_list, print_message = mysql_table_crud(db_table=table, **self.db_cfg).check_table_exists()
            # table_list = [item[0] for item in table_list]
            table_list = [list(item.values())[0] for item in table_list]

            if table not in table_list:
                mbox0 = QMessageBox.question(self, "Create Database",
                                             f"Database empty \nCreate  database  table {table}  ? ",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                if mbox0 == QMessageBox.Yes:
                    query = list_of_tables[table]
                    print_message = mysql_table_crud(**self.db_cfg).create_table(query)
                    QMessageBox.information(self, "Table creation", print_message)

    # def add_columns_name_to_table(self):
    #     payin_table = mysql_table_crud(db_table=HOSPITAL_BILL_PAYIN_PREFIX,
    #                                    db_header=PAYIN_TABLE_HEADER,
    #                                    **self.db_cfg)
    #     payout_table = mysql_table_crud(db_table=HOSPITAL_BILL_PAYOUT_PREFIX,
    #                                     db_header=PAYOUT_TABLE_HEADER,
    #                                     **self.db_cfg)
    #
    #     message = payin_table.add_column_name_to_table("mobile_no", 'BIGINT')
    #     print(message)
    #     message = payout_table.add_column_name_to_table("mobile_no", 'BIGINT')
    #     print(message)
    #     exit()

    def my_login(self):
        # logger.warning("Trying login")
        self.user_list = self.get_user_list()
        rk_db, self.print_message = mysql_table_crud(**self.db_cfg).db_connection()
        if self.bsheet_medical:
            title = "Durga Medicals"
        else:
            title = "RK Hospital"

        login = Login(rk_db, title)
        if login.exec_() == login.Accepted:
            self.usr, self.pwd, self.my_access, self.tools = login.get_inp()

            if self.bsheet_medical:
                if self.tools == LOGIN_TOOL[0] or self.tools == LOGIN_TOOL[2]:
                    self.update_window_title(self.usr)
                else:
                    QMessageBox.warning(self, 'Incorrect login (Medical) !!',
                                        'Please check User name,  password, tool access...')
                    self.quit_now()

            if self.bsheet_hospital:
                if self.tools == LOGIN_TOOL[1] or self.tools == LOGIN_TOOL[2]:
                    self.update_window_title(self.usr)
                else:
                    QMessageBox.warning(self, 'Incorrect login (Hospital) !!',
                                        'Please check User name,  password, Tool access...')
                    self.quit_now()

        else:
            # logger.warning("Quitting the program")
            # QMessageBox.critical(self, 'Login  !!', 'Login required \n Exiting....                   ')
            self.quit_now()

    def tabWidgets(self):
        self.tabs = QTabWidget()
        self.tabs.tabCloseRequested.connect(self.tab_close)
        self.tabs.setFont(FONT1)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.setCentralWidget(self.tabs)

    def tab_close(self, index):
        # https: // stackoverflow.com / questions / 63122385 / pyqt5 - tab - widget - how - can - i - get - the - index - of - active - tab - window - on - mouse - click
        # https: // stackoverflow.com / questions / 19151159 / qtabwidget - close - tab - button - not -working
        # self.tabs.tabCloseRequested.connect(lambda index: tabs.removeTab(index))
        tabname = self.tabs.tabText(index)
        self.tabs_displayed.pop(tabname)
        self.tabs.removeTab(index)

    def load_selected_tabs(self, load_tab, title):
        if len(self.tabs_selected.keys()) != 0:
            for title in self.tabs_selected.keys():
                if title not in self.tabs_displayed.keys():
                    self.tabs_displayed[title] = True
                    self.tabs.addTab(load_tab, title)
                    Curr_index = [index for index in range(self.tabs.count()) if title == self.tabs.tabText(index)]
                    self.tabs.setCurrentIndex(Curr_index[0])
                else:
                    QMessageBox.information(self, "Already displayed",
                                            f"{title} already loaded,\n please close the existing and try again ")
        else:
            print("No balance sheet selected..")
            self.quit_now()

        self.tabs_selected.clear()

    def holdings_tab(self):
        title = f"Holdings: {datetime.date.today()}"
        self.tabs_selected[title] = True
        self.load_selected_tabs(list_of_holdings_display(**self.db_cfg), title)

    def load_returns(self):
        title = f"Returns: {datetime.date.today()}"
        self.tabs_selected[title] = True
        self.load_selected_tabs(holdings_returns_display( self.plot_all_returns_history,**self.db_cfg), title)

        # self.load_selected_tabs(
        #     holdings_returns_display(self.market_value_history, self.transactions_df, self.overall_holdings,
        #                          self.plot_all_returns_history, **self.db_cfg), title)
    def update_stock_history(self):
        # import yfinance as yf
        # print("not implemented")
        title = "Unpaid Accounts"
        self.backup_folder(src_path=PATH_TO_DATABASE_CURRENT_HOLDINGS, trg_path=PATH_TO_DATABASE_CURRENT_HOLDINGS_BKP)
        # self.backup_folder(src_path=PATH_TO_DATABASE_SOLD_HOLDINGS, trg_path=PATH_TO_DATABASE_SOLD_HOLDINGS_BKP)

        # current_stock = mysql_table_crud(db_table=CURRENT_HOLDINGS_DB_TABLE_NAME,
        #                                  db_header=CURRENT_HOLDING_DB_HEADER,
        #                                  **self.db_cfg)
        # data = current_stock.read_row_by_column_values()
        # print(current_stock.table_view(data))
        # print(data['equity'])
        cwd = os.getcwd()
        # start_date = datetime(2019, 1, 1)
        # end_date = datetime(2022, 1, 4)
        # data = yf.download('DMART.NS', start=start_date, end=end_date)
        mask = self.overall_holdings["current_holding"] == True
        symbol_df = self.overall_holdings[mask]

        # print(symbol_df["equity"].to_list())
        # for symbol in symbol_df["equity"].to_list():
        symbol_list = []
        f_count = 0
        for index, row in symbol_df.iterrows():
            symbol =row['equity']
            buy_date =row['date']
            symbol_buy_date=symbol_date_string(symbol,buy_date)
            # print(row.to_dict())
            path_to_csv_file = os.path.join(cwd, PATH_TO_DATABASE_CURRENT_HOLDINGS, f"{symbol_buy_date}_history.csv")
            if os.path.isfile(path_to_csv_file):
                f_count += 1
                print(path_to_csv_file, 'exists..')
            else:
                symbol_ns = f"{symbol}.NS"
                data = yf.download(symbol_ns)
                print(symbol, path_to_csv_file)
                data.to_csv(path_to_csv_file)
                symbol_list.append(symbol)


        print(f_count, "files are available")


    def update_sold_stock_history(self):

        # print("not implemented")
        title = "Sold Stocks"
        # self.backup_folder(src_path=PATH_TO_DATABASE_CURRENT_HOLDINGS, trg_path=PATH_TO_DATABASE_CURRENT_HOLDINGS_BKP)
        # self.backup_folder(src_path=PATH_TO_DATABASE_SOLD_HOLDINGS, trg_path=PATH_TO_DATABASE_SOLD_HOLDINGS_BKP)

        # sold_stock = mysql_table_crud(db_table=SOLD_HOLDINGS_DB_TABLE_NAME, db_header=SOLD_HOLDING_DB_HEADER,
        #                               **self.db_cfg)

        data = self.sold_stocks_details_db.read_row_by_column_values()
        sold_stocks_df = pd.DataFrame(data)
        sold_stocks_df.sort_values(by="buy_date", inplace=True)
        # print(sold_stocks_df.to_string())
        # print(sold_stock.table_view(data))
        # print(data['equity'])
        # PDIR = os.getcwd()
        # start_date = datetime(2019, 1, 1)
        # end_date = datetime(2022, 1, 4)
        # data = yf.download('DMART.NS', start=start_date, end=end_date)

        symbol_list = []
        f_count = 0
        for itm in data:
            symbol = f"{itm['equity']}"
            buy_date = f"{itm['buy_date']}"
            buy_price = f"{itm['buy_price']}"
            sale_date = f"{itm['sale_date']}"
            quantity = f"{itm['sale_quantity']}"
            print(symbol, buy_date, sale_date)

            # date_range = f"_from_{buy_date}_to_{sale_date}"
            symbol_date_range = symbol_date_range_string(symbol, buy_date, sale_date)
            # csv_file_name = f"{symbol_date_range}_Xquantiy.csv"
            csv_file_name = f"{symbol_date_range}.csv"
            # symbol_date_range = f"{symbol_date_range}_Xquantiy.csv"
            path_to_csv_file = os.path.join(PDIR, PATH_TO_DATABASE_SOLD_HOLDINGS, csv_file_name)
            if os.path.isfile(path_to_csv_file):
                f_count += 1
                print(path_to_csv_file, 'exists..')
            else:
                # data = yf.download(symbol)
                symbol_ns = f"{symbol}.NS"
                sale_date_1 = datetime.date.fromisoformat(sale_date) + datetime.timedelta(days=1)
                data = yf.download(symbol_ns, start=buy_date, end=sale_date_1)
                # symbol_info = yf.Ticker(symbol_ns)
                # # print(symbol_info.actions)
                # # print(symbol_info.dividends.to_list())
                # split_q = symbol_info.splits
                # # https: // stackoverflow.com / questions / 27112865 / how - to - convert - pandas - time - series - into - a - dict -
                # # with-string - key
                # split_q = dict(zip(split_q.index.format(), split_q))
                # # print(symbol, buy_date, sale_date)
                # # print(quantity)
                # # print(split_q)
                #
                # if len(split_q) > 0:
                #     for k, v in split_q.items():
                #         # print(type(k), type(buy_date))
                #         if datetime.date.fromisoformat(k) > datetime.date.fromisoformat(buy_date):
                #             quantity = float(quantity) * float(v)
                #
                # header_list = ['Open', 'High', 'Low', 'Close', 'Adj Close']
                # for hname in header_list:
                #     data[hname] = (data[hname] - float(buy_price)) * float(quantity)

                data.head(4).to_string()

                # print(symbol, path_to_csv_file)
                data.to_csv(path_to_csv_file)
                # exit()
                # symbol_list.append(symbol)

        print(f_count, "files are available")

    def load_by_date_time(self):
        self.usr_show = ""
        self.by_user = True
        # print(self.user_list)
        # print("Displayed:",self.tabs_displayed)
        bsheet_inp = select_bsheet(self.tabs_displayed.keys(), self.usr, self.user_list)
        self.tabs_selected.clear()
        if bsheet_inp.exec_() == bsheet_inp.Accepted:
            start_time, end_time, self.usr_show, self.deptmt, self.receiptPayMethod, self.payDetail, self.search_options = bsheet_inp.get_inp()
            title = BSHEET_TITLE
            # if self.usr_show == self.usr:
            #     pass
            # else:
            if self.deptmt == "All":
                title = f" {title} ({self.usr_show})"
            else:
                title = f" {title}_{self.deptmt}({self.usr_show})"
            # print(title)
            # print("}}}}}",start_time, end_time)
            # if [start_time, end_time] not in  self.tabs_displayed.values():
            if title not in self.tabs_displayed.keys():
                # self.bsheet_count=self.bsheet_count+1
                # title=BSHEET_TITLE #+str(self.bsheet_count)

                # https: // stackoverflow.com / questions / 373370 / how - do - i - get - the - utc - time - of - midnight -for -a - given - timezone
                # start_time=datetime.datetime.strptime(start_time,"%d-%m-%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                # end_time=datetime.datetime.strptime(end_time,"%d-%m-%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                self.tabs_selected[title] = [start_time, end_time]
                # print("--->", self.tabs_selected)
                self.load_selected_tabs(check=False)

    def toolBarMenu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        # filecmp_menu = menubar.addMenu("&File")

        # menubar.setLayoutDirection(Qt.RightToLeft)
        setting_menu = menubar.addMenu("Settings")
        # if self.my_access != "Administrator":
        #     setting_menu.setEnabled(False)
        # setting_menu=menubar.addMenu(QIcon("icons/configure-2.png"),"Settings")

        user_admin_submenu = QMenu("&User Administration", self)
        add_user_menu = QAction("&New user", self)
        add_user_menu.triggered.connect(self.user_admin)
        add_user_menu.setStatusTip('Add new user')
        user_admin_submenu.addAction(add_user_menu)

        edit_user_menu = QAction("Modify user", self)
        edit_user_menu.setStatusTip('Modify user credential ')
        user_admin_submenu.addAction(edit_user_menu)

        setting_menu.addMenu(user_admin_submenu)
        # --------------------------------------
        deptmt_submenu = QMenu("&Department (Receipt)", self)
        add_deptmt_menu = QAction("&Modify Department", self)
        add_deptmt_menu.triggered.connect(self.department_modify_setting)
        add_deptmt_menu.setStatusTip('Modify list of Departments in receipt')
        deptmt_submenu.addAction(add_deptmt_menu)

        edit_deptmt_menu = QAction("Display Department", self)
        edit_deptmt_menu.setStatusTip('Select list of Departments to be displayed')
        deptmt_submenu.addAction(edit_deptmt_menu)

        setting_menu.addMenu(deptmt_submenu)
        # --------------------------------------

        detail_submenu = QMenu("&Details (Payment)", self)
        add_detail_menu = QAction("&Modify Details", self)
        add_detail_menu.setStatusTip('Modify list of Details in payment')
        detail_submenu.addAction(add_detail_menu)

        edit_detail_menu = QAction("Display Details", self)
        edit_detail_menu.setStatusTip('Select list of Details to be displayed')
        detail_submenu.addAction(edit_detail_menu)

        setting_menu.addMenu(detail_submenu)
        # --------------------------------------
        mysql_submenu = QMenu("&MYSQL", self)
        mysql_login = QAction("&Login Credential", self)
        mysql_login.triggered.connect(self.mysql_login_info0)
        mysql_login.setStatusTip('Modify MYSQL Login Info.')
        mysql_submenu.addAction(mysql_login)

        setting_menu.addMenu(mysql_submenu)
        # --------------------------------------
        plot_data_submenu = QMenu("&Plot Data", self)
        return_data_range = QAction("&Return Plot", self)
        return_data_range.triggered.connect(self.inv_returns_data_selection)
        return_data_range.setStatusTip('Selecting data range for market values.')
        plot_data_submenu.addAction(return_data_range)

        setting_menu.addMenu(plot_data_submenu)
        # --------------------------------------
        # switch_submenu = QMenu("&Medical/Hospital Switch", self)
        # gui_switch = QAction("&Medical or Hospital", self)
        # gui_switch.triggered.connect(self.gui_switching)
        # gui_switch.setStatusTip('Switch Hospital between Medical software')
        # switch_submenu.addAction(gui_switch)
        #
        # setting_menu.addMenu(switch_submenu)

    def inv_returns_data_selection(self):
        returns_data_range = return_history_range_selection(self.plot_all_returns_history)
        old_plot_all_returns_history = self.plot_all_returns_history
        if returns_data_range.exec_() == returns_data_range.Accepted:
            self.plot_all_returns_history = returns_data_range.get_inp()
            # print("Plot all data ?", self.plot_all_returns_history)
            if self.plot_all_returns_history != old_plot_all_returns_history:
                self.overall_return()

    def toolBar(self):
        tb = self.addToolBar("Tool Bar")
        tb.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        tb.addSeparator()
        holdings_tab = QAction(QIcon("icons/db_add.png"), "Holdings", self)
        holdings_tab.triggered.connect(self.holdings_tab)
        holdings_tab.setStatusTip("Today's information/data")
        holdings_tab.setToolTip("Today's information/data")
        tb.addAction(holdings_tab)
        tb.addSeparator()

        load_returns_info = QAction(QIcon("icons/dollar.png"), "Returns", self)
        load_returns_info.triggered.connect(self.load_returns)
        load_returns_info.setStatusTip("Load returns")
        load_returns_info.setToolTip("Load returns")
        tb.addAction(load_returns_info)
        tb.addSeparator()

        # delShare = QAction(QIcon("icons/db_remove.png"), "Delete \n ", self)
        # # delShare.triggered.connect(self.del_shareDB)
        # delShare.setStatusTip("Removing items from database")
        # delShare.setToolTip("Removing items from database")
        # tb.addAction(delShare)
        # tb.addSeparator()

        load_sheet = QAction(QIcon("icons/docu.png"), "Load ", self)
        load_sheet.triggered.connect(self.load_by_date_time)
        load_sheet.setStatusTip("Load Old Balance Sheet")
        load_sheet.setToolTip("Load Old Balance Sheet ")
        tb.addAction(load_sheet)
        tb.addSeparator()

        load_casesheet = QAction(QIcon("icons/download_internet.png"), "Update", self)
        load_casesheet.triggered.connect(self.update_stock_history)
        load_casesheet.setStatusTip("Update latest stock history")
        load_casesheet.setToolTip("Update latest stock history ")
        tb.addAction(load_casesheet)
        tb.addSeparator()

        # if self.my_access == "Write Only":
        #     statement_file.setEnabled(False)

        import_data = QAction(QIcon("icons/document-import.png"), "Import", self)
        import_data.triggered.connect(self.call_import_csv_to_mysql)
        import_data.setStatusTip("Import data from CSV")
        import_data.setToolTip("Import data from CSV")
        tb.addAction(import_data)
        tb.addSeparator()
        # if self.my_access != "Administrator":
        #     import_data.setEnabled(False)

        export_data = QAction(QIcon("icons/document-export.png"), "Export", self)
        export_data.triggered.connect(self.export_mysql_csv)
        export_data.setStatusTip("Export data from CSV")
        export_data.setToolTip("Export data from CSV")
        tb.addAction(export_data)
        tb.addSeparator()
        # if self.my_access != "Administrator":
        #     export_data.setEnabled(False)

        # settings_default = QAction(QIcon("icons/configure-2.png"), "Settings", self)
        # settings_default.triggered.connect(self.all_setting)
        # settings_default.setStatusTip("default parameter settings")
        # settings_default.setToolTip("default parameter settings")
        # tb.addAction(settings_default)
        # tb.addSeparator()
        # if self.my_access != "Administrator":
        #     settings_default.setEnabled(False)

        # user_admin = QAction(QIcon("icons/user-new.png"), "User\nAdmin", self)
        # user_admin.triggered.connect(self.user_admin)
        # user_admin.setStatusTip("default parameter settings")
        # user_admin.setToolTip("default parameter settings")
        # tb.addAction(user_admin)
        # tb.addSeparator()
        # if self.my_access != "Administrator":
        #     user_admin.setEnabled(False)

        # refreshShare = QAction(QIcon("icons/view-refresh-6.png"), "Refresh", self)
        # refreshShare.triggered.connect(self.refresh)
        # refreshShare.setStatusTip("loading latest  from database")
        # refreshShare.setToolTip("loading latest  from database")
        # tb.addAction(refreshShare)
        # tb.addSeparator()
        # if self.my_access != "Administrator":
        #     refreshShare.setEnabled(False)

        restartShare = QAction(QIcon("icons/quick_restart.png"), "Restart", self)
        restartShare.triggered.connect(self.restart)
        restartShare.setStatusTip("loading latest  settings")
        restartShare.setToolTip("loading latest settings")
        tb.addAction(restartShare)
        tb.addSeparator()
        # if self.my_access != "Administrator":
        #     refreshShare.setEnabled(False)

        # refreshShare = QAction(QIcon("icons/view-refresh-6.png"), "Log", self)
        # refreshShare.triggered.connect(self.refresh)
        # refreshShare.setStatusTip("loading latest  from database")
        # refreshShare.setToolTip("loading latest  from database")
        # tb.addAction(refreshShare)
        # tb.addSeparator()

        quit_app = QAction(QIcon("icons/quit.png"), "Quit", self)
        quit_app.triggered.connect(self.quit_now)
        quit_app.setStatusTip("Closing the application")
        quit_app.setToolTip("Closing the application")
        tb.addAction(quit_app)
        tb.addSeparator()

    def mysql_login_info0(self):
        self.mysql_login_info(close_now=self.close_now)
        return

    def user_admin(self):
        pass

    def mysql_login_info(self, close_now=True):
        mysql_login = update_mysql_login(self.mysql_hostname, self.mysql_dbname,
                                         self.mysql_login, self.mysql_passwd, self.mysql_port)

        # logger.info(f"updating mysql login ")
        if mysql_login.exec_() == mysql_login.Accepted:
            self.mysql_log = mysql_login.get_inp()
            print(self.mysql_log)
            if self.mysql_log_data.check_table_empty(MYSQL_SQLITE_DB_LOGIN):
                mysql_msg = self.mysql_log_data.insert(self.mysql_log)
                QMessageBox.information(self, "mysql login Registered",
                                        "Updated the login...,\nPlease re-open to continue... ")
                if close_now:
                    self.quit_now()
                else:
                    return
            else:
                if "" not in self.mysql_log.values():
                    mysql_msg = self.mysql_log_data.update(self.mysql_log)
                    print(mysql_msg)
                    # logger.info(f"MYSQL login updated/registered..")
                    QMessageBox.information(self, "mysql login Registered",
                                            "Updated the login...,\nPlease re-open to continue... ")
                    if close_now:
                        self.quit_now()
                    else:
                        return
                else:
                    QMessageBox.information(self, "Information Missing",
                                            "Inputs values missing,\nLogin information cannot be  empty ")
                    if close_now:
                        self.quit_now()

    def department_modify_setting(self):
        pass

    def restart(self):
        QCoreApplication.quit()
        status = QProcess.startDetached(sys.executable, sys.argv)
        # print(status)

    def refresh(self):
        pass

    def quit_now(self):
        # logger.info(f"Exiting the program..")
        sys.exit(0)

    def export_mysql_csv(self):
        # rk_db = mysql_table_crud.db_connection()
        rk_db, print_message = mysql_table_crud(**self.db_cfg).db_connection()
        # logger.info(f"Exporting data to CSV by {self.usr}")
        export_inp = export_mysql_dates(rk_db)
        if export_inp.exec_() == export_inp.Accepted:
            message = export_inp.get_inp()
            # logger.info(f"Exported to CSV file..")
        else:
            pass
            # #logger.info(f"Export to CSV cancelled")

    def call_import_csv_to_mysql(self, csv_to_df=None, table_name=None, csv_data=False):
        # import_csv = import_csv_to_mysql(MSQL_LOGIN,MSQL_PASSWD,)
        # logger.info(f"CSV file imported by {self.usr}")
        from sqlalchemy import create_engine
        print(self.mysql_login)
        print(self.mysql_passwd)
        print(self.mysql_hostname)
        print(self.mysql_dbname)
        # sqlEngine = create_engine('mysql+pymysql://kiran:@localhost/rk_hospital', pool_recycle=3600)
        query = f"mysql+mysqldb://{self.mysql_login}:{self.mysql_passwd}@{self.mysql_hostname}/{self.mysql_dbname}"
        # sqlEngine = create_engine("mysql+mysqldb://kiran:pass1word@localhost/rk_hospital")  # fill details
        sqlEngine = create_engine(query)
        dbConnection = sqlEngine.connect()

        if not csv_data:
            options = QFileDialog.Options()
            # options |= QFileDialog.DontUseNativeDialog
            fileName, result = QFileDialog.getOpenFileName(self, "QFileDialog.getSaveFileName()", "", "(*.csv)",
                                                           options=options)

            # print("fname",fileName,result)
            if fileName:
                # logger.info(f"Reading  CSV  file {fileName}  by {self.usr}")
                csv_data = pd.read_csv(fileName)
                # print(csv_data.to_string())
                csv_data.to_sql(name=table_name, con=dbConnection, index=False, if_exists='append',
                                index_label='id')
                return
            else:
                return
        else:
            print("Writintg to db")
            print(csv_to_df.head(10).to_string())
            csv_to_df.to_sql(name=table_name, con=dbConnection, index=False, if_exists='append',
                             index_label='id')
            return

    def report_to_excel(self):
        # user_list=[]
        # user_list.clear()
        # print("0", self.user_list)
        # logger.info(f"Excel report generation: {self.usr}")
        # rk_db = mysql_table_crud.db_connection()

        rk_db, print_message = mysql_table_crud(**self.db_cfg).db_connection()
        if self.bsheet_medical:
            export_inp = report_to_excel_by_date(rk_db, self.usr, self.user_list, pharmacy=True)
        else:
            export_inp = report_to_excel_by_date(rk_db, self.usr, self.user_list)
        if export_inp.exec_() == export_inp.Accepted:
            message = export_inp.get_inp()
            # logger.info(f"Excel report generated  by {self.usr}")
        else:
            pass

    # export_inp = export_mysql_dates(self.rk_db)
    # if export_inp.exec_() == export_inp.Accepted:
    #     message = export_inp.get_inp()
    # else:
    #     pass

    def get_user_list(self):
        login_conn = mysql_table_crud(db_table=LOGIN_TABLE,
                                      db_header=USER_LOGIN_TABLE_HEADER,
                                      **self.db_cfg)

        user_list = login_conn.read_row_by_column_values(column_name="user_name", order="order by user_name asc")
        # print(user_list)
        # login_list = [item[0] for item in user_list]
        login_list = [list(item.values())[0] for item in user_list]
        # print(login_list)

        if len(login_list) == 0:
            # logger.info(f"Login database empty..")
            mbox0 = QMessageBox.question(self, "Login Database missing..",
                                         "Login is required to continue...\n Register new users for login ?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if mbox0 == QMessageBox.Yes:
                self.user_admin()
                user_list = login_conn.read_row_by_column_values(column_name="user_name",
                                                                 order="order by user_name asc")
                login_list = [item[0] for item in user_list]
            else:
                msg = TimerMessageBox(4, "Quiting...", "Login is required to continue...\n Register users for login")
                msg.exec_()
                self.quit_now()

        user_list = []
        user_list = USER_LIST
        for name in login_list:
            user_list.append(name)
        return user_list

    # def read_mysql(self):
    #     df_all = pd.read_sql(SQL_READ_RECPT_BILL, con=self.rk_db)
    #     df_all.columns = HEADER_RECPT_DEBIT
    #     df_display=df_all.drop(columns=['User','Edit Info'])
    #     # print(len(df_display))
    #     self.bill_count=len(df_display)
    #
    #     return df_display


def main():
    app = QApplication(sys.argv)
    window = MyMainWindow()
    # import resource
    # print( resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    window.showMaximized()
    sys.exit(app.exec_())


# def exception_hook(exctype, value, traceback):
#     from Logging.my_logger import setup_log, clearlogger
#     import traceback
#
#     logger = setup_log()
#     sys._excepthook = sys.excepthook
#     # print(exctype, value, traceback)
#     logger.error("An uncaught exception occurred:")
#     logger.error("Type: %s", exctype)
#     logger.error("Value: %s", value)
#     logger.error("Value: %s", traceback)
#
#     if traceback:
#         format_exception = traceback.format_tb(traceback)
#         for line in format_exception:
#             logger.error(repr(line))
#
#     sys.exit(1)

def custom_excepthook(exc_type, exc_value, exc_traceback):
    # https: // stackoverflow.com / questions / 6234405 / logging_exception_hook - uncaught - exceptions - in -python
    from logging_exception_hook.my_logger import setup_log, clearlogger
    import traceback

    logging = setup_log()
    # Do not print exception when user cancels the program
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("An uncaught exception occurred:")
    logging.error(f"Type: {exc_type}")
    logging.error(f"Value: {exc_value}")

    if exc_traceback:
        format_exception = traceback.format_tb(exc_traceback)
        logging.error(f"\n{format_exception[0]}")
        # for line in format_exception:
        #     print(line[0])
        # logging_exception_hook.error(repr(line))

    sys.exit(1)


if __name__ == '__main__':
    import sys

    # ======================================
    # log file for the tool
    # sys.excepthook = custom_excepthook
    main()
    # ======================================
