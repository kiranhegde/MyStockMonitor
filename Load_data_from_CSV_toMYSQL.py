import datetime
import os.path
from pathlib import Path
import pandas as pd
import random
import numpy as np
from pandas_datareader import data as web


from utility.libnames import PDIR, MYSQL_SQLITE_DB, MYSQL_SQLITE_DB_LOGIN, PATH_TO_DATABASE_CURRENT_HOLDINGS, \
    PATH_TO_DATABASE, PATH_TO_DATABASE_BACKUP, PATH_TO_DATABASE_SOLD_HOLDINGS, PATH_TO_DATABASE_SOLD_HOLDINGS_BKP, \
    PATH_TO_DATABASE_CURRENT_HOLDINGS_BKP

from utility.utility_functions import make_nested_dict
from mysql_tools.mysql_crud import mysql_table_crud
from mysql_tools.tables_and_headers import CURRENT_HOLDINGS_DB_TABLE_NAME, create_current_holdings_table_db_query, \
    create_transaction_table_db_query, create_sold_holdings_table_db_query, create_all_holdings_table_db_query, \
    SOLD_HOLDING_DB_HEADER, BANK_TRANSACTIONS_DB_HEADER, TRADE_TYPE, \
    BANK_TRANSACTIONS_DB_TABLE_NAME, TOTAL_HOLDINGS_DB_HEADER
# CURRENT_HOLDING_DB_HEADER, SOLD_HOLDINGS_DB_TABLE_NAME, \

from mysql_tools.tables_and_headers import  TOTAL_HOLDINGS_DB_TABLE_NAME_test as  TOTAL_HOLDINGS_DB_TABLE_NAME
from mysql_tools.tables_and_headers import  BANK_TRANSACTIONS_DB_TABLE_NAME_test as  BANK_TRANSACTIONS_DB_TABLE_NAME

from sqlite3_database.sqlite3_crud import sqlite3_crud

CURRENT_HOLDING_DB_HEADER = ['id', 'ref_number', 'agency', 'exchange', 'equity', 'buy_date', 'avg_price', 'quantity',
                             'remarks']


def gen_id(**db_cfg):

    total_holdings_details = mysql_table_crud(db_table=TOTAL_HOLDINGS_DB_TABLE_NAME,
                                                   db_header=TOTAL_HOLDINGS_DB_HEADER,
                                                   **db_cfg)

    transctions_details = mysql_table_crud(db_table=BANK_TRANSACTIONS_DB_TABLE_NAME,
                                           db_header=BANK_TRANSACTIONS_DB_HEADER,
                                           **db_cfg)
    id_list = []

    total_holdings_table = total_holdings_details.read_row_by_column_values(column_name='id')
    cash_table = transctions_details.read_row_by_column_values(column_name='id')

    for itm in cash_table:
        id_list.append(itm['id'])
    for itm in total_holdings_table:
        id_list.append(itm['id'])

    stock_id = f'{random.randrange(1000, 10 ** 6)}'
    m = len(id_list) - 1

    for i in range(m):
        if stock_id in id_list:
            stock_id = f'{random.randrange(1000, 10 ** 6)}'
        else:
            break

    return int(stock_id)



# PEP8 Reformat Code press Ctrl+Alt+L.
# File>Setting>Save Actions -> disable/enable Reformat code
# https://stackoverflow.com/questions/40623605/how-to-stop-pycharm-auto-format-code-after-pasted/56991669


class export_data_sql_mysql():

    def __init__(self):
        self.UI()


    def UI(self):
        self.check_folders()
        self.check_sqlite_db_info()
        self.extablish_db_connection()
        self.check_db_tables_exists()
        self.connect_to_db_tables()


        # ------------------------------------------------
        # read excel file of all data
        # key
        # 1. current
        # 2. sold
        # 3. transactions
        key = 1
        self.current_holding_df=self.update_database_from_csv(key=key)
        # print(self.current_holding_df.head(10).to_string())

        key = 2
        self.sold_holding_df = self.update_database_from_csv(key=key)
        # print(self.sold_holding_df.head(10).to_string())

        key = 3
        self.transactions_df = self.update_database_from_csv(key=key)
        # print(self.transactions_df.head(10).to_string())

        # get stock split/dividend details
        # self.update_sold_stock_history()
        # exit()
        # print(holding_df.info())
        #
        # # convert all holdings to new format
        self.total_holdings_df=self.export_all_holdings_to_db()

        # write to mysql table
        # combined total holdings
        self.call_import_csv_to_mysql(csv_to_df=self.total_holdings_df, table_name=TOTAL_HOLDINGS_DB_TABLE_NAME,
                                      csv_data=True)

        exit()
        # Cash transactions from bank
        self.call_import_csv_to_mysql(csv_to_df=self.transactions_df, table_name=BANK_TRANSACTIONS_DB_TABLE_NAME,
                                      csv_data=True)

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
            else:
                print(f"{folder} exists..")
        for folder in list_of_backup_folders:
            # print(folder, os.path.exists(folder))
            if not os.path.exists(folder):
                Path(folder).mkdir(parents=True, exist_ok=True)
            else:
                print(f"{folder} exists..")

    def check_sqlite_db_info(self):
        sqlite_db_path = f"sqlite3_database/{MYSQL_SQLITE_DB}"
        file_path = Path(sqlite_db_path)

        try:
            my_abs_path = file_path.resolve(strict=True)
            print(f"MYSQL login information table {file_path} exists")
        except FileNotFoundError:
            print("MYSQL login information table missing, Create new sql database ? ",)


    def extablish_db_connection(self):
        print("Connecting to MYSQL server")
        sqlite_db_path = f"sqlite3_database/{MYSQL_SQLITE_DB}"
        file_path = Path(sqlite_db_path)
        # print('extablish_db_connection')

        try:
            my_abs_path = file_path.resolve(strict=True)
        except FileNotFoundError:
            print("Failed to connect to MYSQL server")
            exit()
        else:
            pass
            # logger.info("Connected to MYSQL server")
        # print(f"{my_abs_path}")
        self.mysql_log_data = sqlite3_crud(filename=f"{my_abs_path}", table=MYSQL_SQLITE_DB_LOGIN)
        table_empty = self.mysql_log_data.check_table_empty(MYSQL_SQLITE_DB_LOGIN)

        if table_empty:
            print('MYSQL login table empty ')
            exit()
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
               print("Database Missing !", "Create new database ? ")
               exit()

            connection, self.print_message = mysql_table_crud(**self.db_cfg).db_connection()
            if not connection:
                print("DB Access denied !! ")
                exit()



    def check_db_tables_exists(self):
        list_of_tables = {
            # "xyz": create_receptionPAYIN_table_db_query("xyz"),
            # CURRENT_HOLDINGS_DB_TABLE_NAME: create_current_holdings_table_db_query(CURRENT_HOLDINGS_DB_TABLE_NAME),
            # SOLD_HOLDINGS_DB_TABLE_NAME: create_sold_holdings_table_db_query(SOLD_HOLDINGS_DB_TABLE_NAME),
            # BANK_TRANSACTIONS_DB_TABLE_NAME: create_transaction_table_db_query(BANK_TRANSACTIONS_DB_TABLE_NAME),
            TOTAL_HOLDINGS_DB_TABLE_NAME: create_all_holdings_table_db_query(TOTAL_HOLDINGS_DB_TABLE_NAME),
            BANK_TRANSACTIONS_DB_TABLE_NAME: create_transaction_table_db_query(BANK_TRANSACTIONS_DB_TABLE_NAME)
        }

        for table in list_of_tables.keys():
            table_list, print_message = mysql_table_crud(db_table=table, **self.db_cfg).check_table_exists()
            # table_list = [item[0] for item in table_list]
            table_list = [list(item.values())[0] for item in table_list]

            if table not in table_list:
                query = list_of_tables[table]
                print_message = mysql_table_crud(**self.db_cfg).create_table(query)
                print(print_message)
                print(f"Database empty \n database  table {table}  created.. ")


    def connect_to_db_tables(self):

        self.transctions_details = mysql_table_crud(db_table=BANK_TRANSACTIONS_DB_TABLE_NAME,
                                                    db_header=BANK_TRANSACTIONS_DB_HEADER,
                                                    **self.db_cfg)

        self.total_holdings_details = mysql_table_crud(db_table=TOTAL_HOLDINGS_DB_TABLE_NAME,
                                                       db_header=TOTAL_HOLDINGS_DB_HEADER,
                                                       **self.db_cfg)


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
        for index, row in self.sold_holding_df.iterrows():
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
        for index, row in self.current_holding_df.iterrows():
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
        # print(total_holdings_df.to_string())

        # writing to database
        # for indx, row in total_holdings_df.iterrows():
        #     row = row.to_dict()
        #     listt = list(row.values())
        #     vals_tuple = [tuple(listt)]
        #     messge = self.total_holdings_details.insert_row_by_column_values(row_val=vals_tuple)
        #     print(messge)
        return total_holdings_df


    def update_database_from_csv(self,key):
        PATH_TO_DATABASE= os.path.join(PDIR, 'data_from_sql')
        if key == 1:
            print()
            print()
            print("Current holding")
            print()
            # read holdings
            # path_to_holdings = os.path.join(cwd, PATH_TO_DATABASE, 'purchase.csv')
            path_to_holdings = os.path.join(PATH_TO_DATABASE, 'purchase.xlsx')
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

            holding_df.sort_values(by=['equity'], ascending=True, inplace=True)
            holding_df.reset_index(inplace=True)
            holding_df.columns = CURRENT_HOLDING_DB_HEADER
            holding_df.reset_index(drop=True, inplace=True)
            return holding_df
            # self.call_import_csv_to_mysql(csv_to_df=holding_df, table_name=CURRENT_HOLDINGS_DB_TABLE_NAME,
            #                               csv_data=True)
        elif key == 2:
            print()
            print()
            print("Sold holding")
            print()
            # read sold stoks
            # path_to_sold_stock = os.path.join(cwd, PATH_TO_DATABASE, 'sale.csv')
            # sold_holding_df = pd.read_csv(path_to_sold_stock, parse_dates=['buy_date', 'trade_date'])
            # sold_holding_df['buy_date'] = sold_holding_df['buy_date'].dt.strftime(DATE_FMT_YDM)
            # # sold_holding_df['buy_date'] = pd.to_datetime(sold_holding_df['buy_date'])
            # sold_holding_df['trade_date'] = sold_holding_df['trade_date'].dt.strftime(DATE_FMT_YDM)
            # # sold_holding_df['trade_date'] = pd.to_datetime(sold_holding_df['trade_date'])

            path_to_sold_stock = os.path.join(PATH_TO_DATABASE, 'sale.xlsx')
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
            # sold_holding_df.sort_values(by=['equity'], ascending=True, inplace=True)
            # print(sold_holding_df.to_string())
            # print(sold_holding_df.info())
            sold_holding_df.reset_index(drop=True, inplace=True)
            return sold_holding_df

            # self.call_import_csv_to_mysql(csv_to_df=sold_holding_df, table_name=SOLD_HOLDINGS_DB_TABLE_NAME,
            #                               csv_data=True)
        elif key == 3:
            print()
            print()
            print("Transactions")
            print()
            # read transactions
            # path_to_sold_trans = os.path.join(cwd, PATH_TO_DATABASE, 'investment.csv')
            # transactions_df = pd.read_csv(path_to_sold_trans, parse_dates=['tr_date'])
            # transactions_df['tr_date'] = transactions_df['tr_date'].dt.strftime(DATE_FMT_YDM)
            # # transactions_df['tr_date'] = pd.to_datetime(transactions_df['tr_date'])
            path_to_sold_trans = os.path.join(PATH_TO_DATABASE, 'investment.xlsx')
            # holding_df = pd.read_csv(path_to_holdings, parse_dates=['trade_date'])
            transactions_df = pd.read_excel(path_to_sold_trans)
            mask1 = transactions_df['agency'] == 'Kotak'
            mask2 = transactions_df['agency'] == 'Zerodha'
            transactions_df = transactions_df[mask1 | mask2].copy()
            # transactions_df.sort_values(by=['tr_date'], ascending=True, inplace=True)
            transactions_df['remarks'] = None
            transactions_df.columns = BANK_TRANSACTIONS_DB_HEADER
            # print(transactions_df.to_string())
            # print(transactions_df.info())
            transactions_df.reset_index(drop=True, inplace=True)
            return transactions_df
        else:
            print("Unknown excel to MYSQL")

    def call_import_csv_to_mysql(self, csv_to_df=None, table_name=None, csv_data=False):

        # print("call_import_csv_to_mysql not ready")
        # return

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


        print(f"Writintg to db: {table_name}",)
        print(csv_to_df.head(10).to_string())
        csv_to_df.to_sql(name=table_name, con=dbConnection, index=False, if_exists='append',
                         index_label='id')
        return

    def update_sold_stock_history(self):
        import yfinance as yf
        # print("not implemented")
        title = "Sold Stocks"
        # self.backup_folder(src_path=PATH_TO_DATABASE_CURRENT_HOLDINGS, trg_path=PATH_TO_DATABASE_CURRENT_HOLDINGS_BKP)
        # self.backup_folder(src_path=PATH_TO_DATABASE_SOLD_HOLDINGS, trg_path=PATH_TO_DATABASE_SOLD_HOLDINGS_BKP)

        # sold_stock = mysql_table_crud(db_table=SOLD_HOLDINGS_DB_TABLE_NAME, db_header=SOLD_HOLDING_DB_HEADER,
        #                               **self.db_cfg)

        # data = self.sold_stocks_details_db.read_row_by_column_values()
        # sold_stocks_df = pd.DataFrame(data)
        sold_stocks_df=self.sold_holding_df
        sold_stocks_df.sort_values(by="buy_date", inplace=True)
        # print(sold_stocks_df.to_string())
        # print(sold_stock.table_view(data))
        # print(data['equity'])
        # PDIR = os.getcwd()
        # start_date = datetime(2019, 1, 1)
        # end_date = datetime(2022, 1, 4)
        # data = yf.download('DMART.NS', start=start_date, end=end_date)

        symbol_list = sold_stocks_df['equity'].to_list()
        symbol_list=list(set(symbol_list))
        f_count = 0
        for symbol in symbol_list:
        # for index, row in self.current_holding_df.iterrows():
        #     symbol=row['equity']
            # symbol = f"{itm['equity']}"
            # buy_date = f"{itm['buy_date']}"
            # buy_price = f"{itm['buy_price']}"
            # sale_date = f"{itm['sale_date']}"
            # quantity = f"{itm['sale_quantity']}"
            # print(symbol, buy_date, sale_date)
            # print(symbol)

            # # date_range = f"_from_{buy_date}_to_{sale_date}"
            # symbol_date_range = symbol_date_range_string(symbol, buy_date, sale_date)
            # # csv_file_name = f"{symbol_date_range}_Xquantiy.csv"
            # csv_file_name = f"{symbol_date_range}.csv"
            # # symbol_date_range = f"{symbol_date_range}_Xquantiy.csv"
            # path_to_csv_file = os.path.join(PDIR, PATH_TO_DATABASE_SOLD_HOLDINGS, csv_file_name)
            # if os.path.isfile(path_to_csv_file):
            #     f_count += 1
            #     print(path_to_csv_file, 'exists..')
            # else:
            # data = yf.download(symbol)
            symbol_ns = f"{symbol}.NS"
            # sale_date_1 = datetime.date.fromisoformat(sale_date) + datetime.timedelta(days=1)
            # data = yf.download(symbol_ns, start=buy_date, end=sale_date_1)
            # symbol_info = yf.Ticker(symbol_ns,start='2020-06-01')

            df = web.DataReader(symbol_ns, data_source='yahoo-actions', start='2020-06-01')
            mask=df['action'].str.contains("SPLIT")
            df=df[mask]
            if not df.empty:
                print(symbol)
                print(df.to_string())
                symbol_info = yf.Ticker(symbol_ns)
                split_q = symbol_info.splits
                print(split_q)
            # print(symbol_info.actions)
            # print(symbol_info.dividends.to_list())
            # split_q = symbol_info.splits
            # # https: // stackoverflow.com / questions / 27112865 / how - to - convert - pandas - time - series - into - a - dict -
            # # with-string - key
            # split_q = dict(zip(split_q.index.format(), split_q))
            # # print(symbol, buy_date, sale_date)
            # # print(quantity)
            # print(split_q)
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
            # data.to_csv(path_to_csv_file)
            # exit()
            # symbol_list.append(symbol)

        print(f_count, "files are available")




if __name__ == '__main__':

    export_data_sql_mysql()
    # ======================================
