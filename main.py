import datetime
import os.path
import shutil
from pathlib import Path

import pandas as pd
import yfinance as yf
from PyQt5.QtCore import Qt, QTimer, QCoreApplication, QProcess
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction, QTableView, QMessageBox, \
    QAbstractItemView, \
    QHeaderView, QFileDialog
from PyQt5.QtWidgets import QTabWidget \
    , QMainWindow, QApplication

from display_tabs.current_holding_display import list_of_holdings_display
from display_tabs.indexes_trend_display import indexes_display
from display_tabs.overall_holding_returns_display import \
    holdings_returns_display
from display_tabs.super_trend_display import stock_super_trend_display
from display_tabs.watchlist_display import watchlist_display_tab
from gui_widgets.gui_widgets_add_mysql_login import update_mysql_login
from gui_widgets.gui_widgets_return_history_data_selection import \
    return_history_range_selection
from gui_widgets.gui_widgets_transactions import \
    show_transactions as bank_transactions_details
from mysql_tools.mysql_crud import mysql_table_crud
from mysql_tools.tables_and_headers import CURRENT_HOLDINGS_DB_TABLE_NAME, \
    create_current_holdings_table_db_query,WATCHLIST_DB_TABLE_NAME, \
    create_transaction_table_db_query, create_sold_holdings_table_db_query, \
    create_all_holdings_table_db_query, create_watchlist_table_db_query, \
    BANK_TRANSACTIONS_DB_HEADER, SOLD_HOLDINGS_DB_TABLE_NAME, \
    BANK_TRANSACTIONS_DB_TABLE_NAME,WATCHLIST_DB_HEADER, WATCHLIST_DISPLAY, \
    SOLD_HOLDINGS_LIST_DISPLAY, SOLD_HOLDING_DB_TO_DISPLAY, \
    TOTAL_HOLDINGS_DB_HEADER, TOTAL_HOLDINGS_DB_TABLE_NAME, \
    CURRENT_HOLDING_LIST_DISPLAY, CURRENT_HOLDING_DB_TO_DISPLAY, \
    BANK_TRANSACTIONS_LIST_DISPLAY, \
    BANK_TRANSACTIONS_DB_TO_DISPLAY, INDEX_DB_TABLE_NAME, \
    create_indexes_table_db_query, INDEXES_DB_HEADER,INDEX_NAME_DICT, \
    INDEX_LIST_DISPLAY
from sqlite3_database.sqlite3_crud import sqlite3_crud
from utility.fonts_style import FONT1, TABLE_HEADER_FONT, TABLE_FONT
from share.libnames import PDIR, WELCOME, MYSQL_SQLITE_DB, \
    MYSQL_SQLITE_DB_LOGIN, PATH_TO_DATABASE_CURRENT_HOLDINGS, \
    PATH_TO_DATABASE, PATH_TO_DATABASE_BACKUP, PATH_TO_DATABASE_SOLD_HOLDINGS, \
    PATH_TO_DATABASE_SOLD_HOLDINGS_BKP, \
    PATH_TO_DATABASE_CURRENT_HOLDINGS_BKP,PATH_TO_DATABASE_CURRENT_INDEX, \
    PATH_TO_DATABASE_INDEX_BKP,PATH_TO_DATABASE_WATCHLIST_BKP, \
    PATH_TO_DATABASE_WATCHLIST
from utility.tableViewModel import pandasModel
from utility.utility_functions import make_nested_dict
from utility.utility_functions import reduce_mem_usage, \
    symbol_date_range_string, symbol_date_string, \
    create_current_holdings_csv_file_names, create_sold_holdings_csv_file_names, \
    symbol_date_split,create_current_index_csv_file_names


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
        self.setWindowIcon(QIcon('icons/stock_mngmt.ico'))
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
        # self.get_indices_data()
        self.check_folders()
        self.check_sqlite_db_info()
        self.extablish_db_connection()
        self.check_db_tables_exists()
        self.connect_to_db_tables()

        # print(os.cpu_count())

        # self.update_stock_history_multithread()
        # self.update_stock_history_multi_process()
        # symbol_df = self.get_indexes_details()
        # self.index_trend_data_df = symbol_df.loc[:, INDEX_LIST_DISPLAY]
        # file_names = self.create_index_filename(self.index_trend_data_df)
        # # print(file_names)
        #
        # # self.current_index_history = self.extract_current_holdings_history()
        # self.current_index_history = self.extract_current_index_history(
        #     file_names)

        # exit()

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

    def get_indices_data(self):
        symbol='NSE'
        # symbol='CNXIT'
        symbol_ns=f"{symbol}.NS"
        # start_date="2015-1-1"
        # end_date = datetime.date.today()
        # data = yf.download(symbol_ns, start=start_date, end=end_date, threads=True)
        # # data = yf.download(symbol_ns)
        # path_to_csv_file = os.path.join(PATH_TO_DATABASE_CURRENT_HOLDINGS, f"{symbol}_history.csv")
        # data.to_csv(path_to_csv_file)
        # df = pd.DataFrame(pd.read_csv(path_to_csv_file))
        # print(df.head(10).to_string())
        # print(df.tail(10).to_string())

        # from pandas_datareader import data as pdr
        #
        # import yfinance as yf
        # yf.pdr_override()  # <== that's all it takes :-)

        import pandas_datareader as web

        start = datetime.datetime(2017, 9, 1)
        end = datetime.datetime(2022, 3, 15)
        df = web.DataReader("nifty50", 'yahoo', start, end)

        # download dataframe
        # data = pdr.get_data_yahoo(symbol_ns, start="2017-01-01", end="2017-04-30")
        # df = pd.DataFrame(data)
        print(df.head(10).to_string())
        print(df.tail(10).to_string())
        exit()

    def connect_to_db_tables(self):

        self.transctions_details = mysql_table_crud(db_table=BANK_TRANSACTIONS_DB_TABLE_NAME,
                                                    db_header=BANK_TRANSACTIONS_DB_HEADER,
                                                    **self.db_cfg)

        self.total_holdings_details = mysql_table_crud(db_table=TOTAL_HOLDINGS_DB_TABLE_NAME,
                                                       db_header=TOTAL_HOLDINGS_DB_HEADER,
                                                       **self.db_cfg)

        self.total_index_details = mysql_table_crud(db_table=INDEX_DB_TABLE_NAME,
                                                    db_header=INDEXES_DB_HEADER,
                                                    **self.db_cfg)
        self.total_watchlist_details = mysql_table_crud(
            db_table=WATCHLIST_DB_TABLE_NAME, db_header=WATCHLIST_DB_HEADER,
            **self.db_cfg)

    def get_indexes_details(self):
        data = make_nested_dict()
        for col in INDEXES_DB_HEADER:
            data[col] = None
        data = self.total_index_details.read_row_by_column_values()
        df = pd.DataFrame(data)

        return df

    def get_watchlist_details(self):
        data = make_nested_dict()
        for col in WATCHLIST_DB_HEADER:
            data[col] = None
        data = self.total_watchlist_details.read_row_by_column_values()
        symbol_df = pd.DataFrame(data)
        symbol_df = symbol_df.loc[:, WATCHLIST_DISPLAY]

        return symbol_df


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
                        data = yf.download(symbol_ns, start=start_date,
                                           end=sale_date_1,threads=True)
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
            print(df)
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
            WATCHLIST_DB_TABLE_NAME: create_watchlist_table_db_query(WATCHLIST_DB_TABLE_NAME),
            SOLD_HOLDINGS_DB_TABLE_NAME: create_sold_holdings_table_db_query(SOLD_HOLDINGS_DB_TABLE_NAME),
            BANK_TRANSACTIONS_DB_TABLE_NAME: create_transaction_table_db_query(BANK_TRANSACTIONS_DB_TABLE_NAME),
            TOTAL_HOLDINGS_DB_TABLE_NAME: create_all_holdings_table_db_query(TOTAL_HOLDINGS_DB_TABLE_NAME),
            INDEX_DB_TABLE_NAME: create_indexes_table_db_query(INDEX_DB_TABLE_NAME)
        }

        for table in list_of_tables.keys():
            table_list, print_message = mysql_table_crud(db_table=table, **self.db_cfg).check_table_exists()
            # table_list = [item[0] for item in table_list]
            table_list = [list(item.values())[0] for item in table_list]

            if table not in table_list:
                mbox0 = QMessageBox.question(self, "Create Database",
                                             f"Database empty \nCreate  "
                                             f"database  table  named {table}  "
                                             f"? ",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                if mbox0 == QMessageBox.Yes:
                    query = list_of_tables[table]
                    print_message = mysql_table_crud(**self.db_cfg).create_table(query)
                    print(print_message)
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

    def watchlist_tab(self):
        title = f"Watchlist: {datetime.date.today()}"
        self.tabs_selected[title] = True
        self.load_selected_tabs(watchlist_display_tab(**self.db_cfg), title)


    def load_returns(self):
        title = f"Returns: {datetime.date.today()}"
        self.tabs_selected[title] = True
        self.load_selected_tabs(holdings_returns_display( self.plot_all_returns_history,**self.db_cfg), title)

        # self.load_selected_tabs(
        #     holdings_returns_display(self.market_value_history, self.transactions_df, self.overall_holdings,
        #                          self.plot_all_returns_history, **self.db_cfg), title)

    def update_stock_and_index_history(self):
        self.update_stock_history()

        # index data update
        symbol_df = self.get_indexes_details()
        self.index_trend_data_df = symbol_df.loc[:, INDEX_LIST_DISPLAY]
        file_names = self.create_index_filename(self.index_trend_data_df)
        self.current_index_history = self.extract_current_index_history(
            file_names)
        # watchlist update



    def update_stock_history(self):
        self.backup_folder(src_path=PATH_TO_DATABASE_CURRENT_HOLDINGS, trg_path=PATH_TO_DATABASE_CURRENT_HOLDINGS_BKP)
        data = self.total_holdings_details.read_row_by_column_values()
        df = pd.DataFrame(data)
        mask = df["current_holding"] == True
        symbol_df = df.loc[mask].copy()
        # symbol_df =df[mask]

        symbol_list = []
        f_count = 0
        for index, row in symbol_df.iterrows():
            symbol =row['equity']
            buy_date =row['date']
            symbol_buy_date=symbol_date_string(symbol,buy_date)
            # print(row.to_dict())
            path_to_csv_file = os.path.join(PATH_TO_DATABASE_CURRENT_HOLDINGS, f"{symbol_buy_date}_history.csv")
            if os.path.isfile(path_to_csv_file):
                f_count += 1
                print(path_to_csv_file, 'exists..')
            else:
                symbol_ns = f"{symbol}.NS"
                data = yf.download(symbol_ns,threads=True)
                print(symbol, path_to_csv_file)
                data.to_csv(path_to_csv_file)
                symbol_list.append(symbol)
            f_count += 1


        print(f_count, "files are available")


    def update_watchlist_history(self):
        self.backup_folder(src_path=PATH_TO_DATABASE_WATCHLIST, trg_path=PATH_TO_DATABASE_WATCHLIST_BKP)
        data = self.total_holdings_details.read_row_by_column_values()
        df = pd.DataFrame(data)
        mask = df["current_holding"] == True
        symbol_df = df.loc[mask].copy()
        # symbol_df =df[mask]

        symbol_list = []
        f_count = 0
        for index, row in symbol_df.iterrows():
            symbol =row['equity']
            buy_date =row['date']
            symbol_buy_date=symbol_date_string(symbol,buy_date)
            # print(row.to_dict())
            path_to_csv_file = os.path.join(PATH_TO_DATABASE_CURRENT_HOLDINGS, f"{symbol_buy_date}_history.csv")
            if os.path.isfile(path_to_csv_file):
                f_count += 1
                print(path_to_csv_file, 'exists..')
            else:
                symbol_ns = f"{symbol}.NS"
                data = yf.download(symbol_ns,threads=True)
                print(symbol, path_to_csv_file)
                data.to_csv(path_to_csv_file)
                symbol_list.append(symbol)
            f_count += 1


        print(f_count, "files are available")

    def update_stock_history_multithread(self):
        from threading import Thread

        def y_hist(symbol_ns,start_date,end_date,path_to_csv_file):
            try:
                data = yf.download(symbol_ns, start=start_date, end=end_date,
                                   group_by="ticker")
                data.to_csv(path_to_csv_file)
            except Exception as e:
                data = yf.download(symbol_ns, start=start_date, end=end_date,
                                   group_by="ticker")
                data.to_csv(path_to_csv_file)
                print(type(e))
                print(repr(e))

        self.backup_folder(src_path=PATH_TO_DATABASE_CURRENT_HOLDINGS,
                           trg_path=PATH_TO_DATABASE_CURRENT_HOLDINGS_BKP)
        data_stock = self.total_holdings_details.read_row_by_column_values()
        df = pd.DataFrame(data_stock)
        mask = df["current_holding"] == True
        symbol_df = df.loc[mask].copy()
        ticker_list=symbol_df['equity'].tolist()[0:4]
        ticker_buy_date=symbol_df['date'].tolist()[0:4]

        print(ticker_list)
        print(ticker_buy_date)
        end_date=datetime.date.today()
        start_date = end_date - datetime.timedelta(1 * 365)

        threads = []
        # for i in range(os.cpu_count()):
        # for i in range(len(ticker_list)):
        i=0
        for symbol,buy_date in zip(ticker_list,ticker_buy_date):
            print('registering thread %d' % i)
            symbol_buy_date = symbol_date_string(symbol, buy_date)
            # print(row.to_dict())
            path_to_csv_file = os.path.join(PATH_TO_DATABASE_CURRENT_HOLDINGS,
                                            f"{symbol_buy_date}_history.csv")
            symbol_ns = f"{symbol}.NS"
            threads.append(Thread(target=y_hist, args=(symbol_ns,start_date,
                                                       end_date,path_to_csv_file,)))
            i=i+1

        for thread in threads:
            thread.start()

        return_val=[]
        for thread in threads:
            val= thread.join()
            return_val.append(val)
        print(return_val)

    def update_stock_history_multi_process(self):
        import multiprocessing as mp

        def y_hist(symbol_ns, start_date, end_date, path_to_csv_file):
            try:
                data = yf.download(symbol_ns, start=start_date, end=end_date,
                                   group_by="ticker")
                                   # threads=True)
                data.to_csv(path_to_csv_file)
            except Exception as e:
                data = yf.download(symbol_ns, start=start_date, end=end_date,
                                   threads=True)
                data.to_csv(path_to_csv_file)
                print(type(e))
                print(repr(e))

        self.backup_folder(src_path=PATH_TO_DATABASE_CURRENT_HOLDINGS,
                           trg_path=PATH_TO_DATABASE_CURRENT_HOLDINGS_BKP)
        data_stock = self.total_holdings_details.read_row_by_column_values()
        df = pd.DataFrame(data_stock)
        mask = df["current_holding"] == True
        symbol_df = df.loc[mask].copy()
        ticker_list = symbol_df['equity'].tolist()[0:4]
        ticker_buy_date = symbol_df['date'].tolist()[0:4]

        print(ticker_list)
        print(ticker_buy_date)
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(1 * 365)

        threads = []
        # for i in range(os.cpu_count()):
        # for i in range(len(ticker_list)):
        mp.set_start_method('spawn')
        q = mp.Queue()
        i = 0
        for symbol, buy_date in zip(ticker_list, ticker_buy_date):
            print('registering thread %d' % i)
            symbol_buy_date = symbol_date_string(symbol, buy_date)
            # print(row.to_dict())
            path_to_csv_file = os.path.join(PATH_TO_DATABASE_CURRENT_HOLDINGS,
                                            f"{symbol_buy_date}_history.csv")
            symbol_ns = f"{symbol}.NS"
            threads.append(mp.Process(target=y_hist, args=(symbol_ns, start_date,
                                                       end_date,
                                                       path_to_csv_file,)))
            i = i + 1

        for thread in threads:
            thread.start()

        return_val = []
        for thread in threads:
            val = thread.join()
            return_val.append(val)
        print(return_val)

    def create_index_filename(self, index_trend_data_df):
        # return get_current_holdings_history(self.current_holding_data_df)
        self.backup_folder(src_path=PATH_TO_DATABASE_CURRENT_INDEX,
                           trg_path=PATH_TO_DATABASE_INDEX_BKP)
        current_holdings_csv_file_names = create_current_index_csv_file_names(
            index_trend_data_df)
        return current_holdings_csv_file_names
        # return get_current_holdings_history_mp(current_holdings_csv_file_names)

    def extract_current_index_history(self, holdings_csv_file_names):
        # https://stackoverflow.com/questions/62130801/parallel-processing-in-python-to-fill-a-dictionary-with-the-value-as-a-dictionar
        # from multiprocessing import Process, Manager
        current_holding_history = make_nested_dict()

        # current_holdings_csv_file_names = create_current_holdings_csv_file_names(current_holding_data_df)

        def csv_file_read(filename):
            f = pd.read_csv(filename)
            return f

        def download_and_read_csv(symbol, filename):
            # data = yf.download(symbol_ns, threads=True)
            # print(symbol)
            # print(filename)
            data = yf.download(symbol)
            data.to_csv(filename)
            f = csv_file_read(filename)
            return f

        def compile_stock_data(result):
            df = pd.DataFrame(result)
            mask = df['Date'] > str(deltatime)
            for i in ['Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']:
                df[i] = df[i].astype('float64')
            df = df.loc[mask].copy()
            current_holding_history[symbol_buy_date] = reduce_mem_usage(df)

        # pool = Pool(processes=6)
        jobs = []
        deltatime = datetime.date.today() - datetime.timedelta(5 * 365)
        for symbol_buy_date, path_to_csv_file in holdings_csv_file_names.items():

            if os.path.isfile(path_to_csv_file):
                csv_data = csv_file_read(path_to_csv_file)
                compile_stock_data(csv_data)
                # process=multiprocessing.Process(target=compile_stock_data,args=(csv_data))
                # jobs.append(process)
                # pool.apply_async(csv_file_read, args=(path_to_csv_file,), callback=compile_stock_data)
            else:
                print(path_to_csv_file, 'path missing')
                symbol, buy_date = symbol_date_split(symbol_buy_date)
                symbol_ns = f"{INDEX_NAME_DICT[symbol]}"
                csv_data = download_and_read_csv(symbol_ns, path_to_csv_file)
                compile_stock_data(csv_data)
                # process = multiprocessing.Process(target=compile_stock_data, args=(csv_data))
                # jobs.append(process)

                # pool.apply_async(download_and_read_csv, args=(symbol_ns,path_to_csv_file,), callback=compile_stock_data)

        # # Start the processes (i.e. calculate the random number lists)
        # for j in jobs:
        #     j.start()
        #
        # # Ensure all of the processes have finished
        # for j in jobs:
        #     j.join()

        # pool.close()
        # pool.join()
        return current_holding_history


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

                # data.head(4).to_string()

                # print(symbol, path_to_csv_file)
                data.to_csv(path_to_csv_file)
                # exit()
                # symbol_list.append(symbol)

        print(f_count, "files are available")


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

        trend_sheet = QAction(QIcon("icons/docu.png"), "Index", self)
        trend_sheet.triggered.connect(self.indexes_trend)
        trend_sheet.setStatusTip("Plot trend of a stock")
        trend_sheet.setToolTip("Plot trend of a stock")
        tb.addAction(trend_sheet)
        tb.addSeparator()

        tb.addSeparator()
        holdings_tab = QAction(QIcon("icons/db_add.png"), "Holdings", self)
        holdings_tab.triggered.connect(self.holdings_tab)
        holdings_tab.setStatusTip("Today's information/data")
        holdings_tab.setToolTip("Today's information/data")
        tb.addAction(holdings_tab)
        tb.addSeparator()

        tb.addSeparator()
        holdings_tab = QAction(QIcon("icons/folder_saved_search.png"), "Watchlist",
                               self)
        holdings_tab.triggered.connect(self.watchlist_tab)
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

        # load_sheet = QAction(QIcon("icons/docu.png"), "Load ", self)
        # load_sheet.triggered.connect(self.load_by_date_time)
        # load_sheet.setStatusTip("Load Old Balance Sheet")
        # load_sheet.setToolTip("Load Old Balance Sheet ")
        # tb.addAction(load_sheet)
        # tb.addSeparator()

        load_casesheet = QAction(QIcon("icons/download_internet.png"), "Update", self)
        load_casesheet.triggered.connect(self.update_stock_and_index_history)
        load_casesheet.setStatusTip("Update latest stock history")
        load_casesheet.setToolTip("Update latest stock history ")
        tb.addAction(load_casesheet)
        tb.addSeparator()
        # load_casesheet.setEnabled(False)

        # if self.my_access == "Write Only":
        #     statement_file.setEnabled(False)
        trend_sheet = QAction(QIcon("icons/docu.png"), "Trend", self)
        trend_sheet.triggered.connect(self.stock_trend)
        trend_sheet.setStatusTip("Plot trend of a stock")
        trend_sheet.setToolTip("Plot trend of a stock")
        tb.addAction(trend_sheet)
        tb.addSeparator()



        delShare = QAction(QIcon("icons/emblem-money.png"), "Bank \nTransaction", self)
        delShare.triggered.connect(self.bank_transaction)
        delShare.setStatusTip("Removing stock from list")
        delShare.setToolTip("Removing stock from list")
        tb.addAction(delShare)
        tb.addSeparator()


        import_data = QAction(QIcon("icons/document-import.png"), "Import", self)
        import_data.triggered.connect(self.call_import_csv_to_mysql)
        import_data.setStatusTip("Import data from CSV")
        import_data.setToolTip("Import data from CSV")
        tb.addAction(import_data)
        tb.addSeparator()
        # if self.my_access != "Administrator":
        import_data.setEnabled(False)

        # export_data = QAction(QIcon("icons/document-export.png"), "Export", self)
        # export_data.triggered.connect(self.export_mysql_csv)
        # export_data.setStatusTip("Export data from CSV")
        # export_data.setToolTip("Export data from CSV")
        # tb.addAction(export_data)
        # tb.addSeparator()
        # export_data.setEnabled(False)
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



    def indexes_trend(self):
        title = f"Index Trend: {datetime.date.today()}"
        self.tabs_selected[title] = True
        # print(self.db_cfg)
        self.load_selected_tabs(indexes_display(**self.db_cfg), title)

    def stock_trend(self):
        title = f"Super Trend: {datetime.date.today()}"
        self.tabs_selected[title] = True
        self.load_selected_tabs(stock_super_trend_display(**self.db_cfg), title)

    def bank_transaction(self):
        trans=bank_transactions_details(**self.db_cfg)
        trans.exec_()

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

    def quit_now(self):
        # logger.info(f"Exiting the program..")
        sys.exit(0)

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
    from logging_exception_hook.my_logger import setup_log
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
