from PyQt5.QtCore import QDate
import os
import datetime
import ast
import random
import numpy as np
import pandas as pd

from collections import defaultdict

from mysql_tools.mysql_crud import mysql_table_crud
from mysql_tools.tables_and_headers import CURRENT_HOLDINGS_DB_TABLE_NAME,\
    TOTAL_HOLDINGS_DB_TABLE_NAME,TOTAL_HOLDINGS_DB_HEADER, \
    SOLD_HOLDING_DB_HEADER, SOLD_HOLDINGS_DB_TABLE_NAME,\
    BANK_TRANSACTIONS_DB_TABLE_NAME, BANK_TRANSACTIONS_DB_HEADER

from utility.libnames import PDIR, WELCOME, MYSQL_SQLITE_DB, MYSQL_SQLITE_DB_LOGIN, PATH_TO_DATABASE_CURRENT_HOLDINGS\
    ,PATH_TO_DATABASE_SOLD_HOLDINGS

def get_statementNameByDate(name, bill_day=None):
    if bill_day:
        return str(name) + bill_day.toString('dd_MM_yyyy')
    else:
        now = QDate.currentDate()
        return str(name) + now.toString('dd_MM_yyyy')


class make_nested_dict(dict):
    """Implementation of perl's autovivification feature."""

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

def get_nested_dist_value(data, *args):
    # print(args)
    if args and data:
        element = args[0]
        if element:
            value = data.get(element)
            if len(args) == 1 :
                return value
            else :
                return get_nested_dist_value(value, * args[1:])

def weighted_average(values, weights=None):
    """
    Returns the weighted average of `values` with weights `weights`
    Returns the simple aritmhmetic average if `weights` is None.
    # >>> weighted_average([3, 9], [1, 2])
    # 7.0
    # >>> 7 == (3*1 + 9*2) / (1 + 2)
    # True
    @:param values : list of numbers to be averaged (type: list)
    @:param  weights : respective list of weights(numbers) to be used in averaging (type: list)
    @:return weighted average  value (type:float)
    """
    if weights == None:
        weights = [1 for _ in range(len(values))]
    normalization = 0.0
    val = 0.0
    for value, weight in zip(values, weights):
        val += value * weight
        normalization += weight
    return round(val / normalization, 3)


def reception_payin_bill_parse(billname):
    from DataBase.label_names import HOSPITAL_BILL_PAYIN_PREFIX, HOSPITAL_BILL_PREFIX, HOSPITAL_BILL_PAYOUT_PREFIX

    billdate = billname.split(HOSPITAL_BILL_PAYIN_PREFIX)[1]
    billname = billname.replace(HOSPITAL_BILL_PAYIN_PREFIX, HOSPITAL_BILL_PREFIX).replace('_', '-')
    bill_payout = HOSPITAL_BILL_PAYOUT_PREFIX + billdate

    return billdate, billname, bill_payout,


def date_time_range_full_day0(input_date):
    start_time = input_date + " 00:00:00"
    end_time = input_date + " 23:59:00"
    return start_time, end_time


def date_time_day_start_end(date_time):
    # date_time   is in date.date.now()
    start_time = date_time.replace(hour=0, minute=0, second=0)
    end_time = date_time.replace(hour=23, minute=59, second=50)
    return start_time, end_time


def parse_str(s):
    try:
        return ast.literal_eval(str(s))
    except:
        return str(s)


def gen_id(**db_cfg):

    transctions_details = mysql_table_crud(db_table=BANK_TRANSACTIONS_DB_TABLE_NAME,
                                                db_header=BANK_TRANSACTIONS_DB_HEADER,
                                                **db_cfg)

    total_holdings_details = mysql_table_crud(db_table=TOTAL_HOLDINGS_DB_TABLE_NAME,
                                                   db_header=TOTAL_HOLDINGS_DB_HEADER,
                                                   **db_cfg)

    id_list = []
    all_holdings_table = total_holdings_details.read_row_by_column_values(column_name='ref_number')
    cash_table = transctions_details.read_row_by_column_values(column_name='id')

    for itm in all_holdings_table:
        id_list.append(itm['ref_number'])
    for itm in cash_table:
        id_list.append(itm['id'])

    # print(id_list)
    stock_id = f'{random.randrange(1000, 10 ** 6)}'
    m = len(id_list) - 1
    # stock_id=6463
    # print("#",m,range(m))
    for i in range(m):
        # print("##"+str(i),stock_id)
        if stock_id in id_list:
            stock_id = f'{random.randrange(1000, 10 ** 6)}'
            # print("->"+str(stock_id))
        else:
            break
    # print(id_list)

    return int(stock_id)


# This function is used to reduce memory of a pandas dataframe
# The idea is cast the numeric type to another more memory-effective type
# For ex: Features "age" should only need type='np.int8'
# Source: https://www.kaggle.com/gemartin/load-data-reduce-memory-usage
def reduce_mem_usage(df):
    """ iterate through all the columns of a dataframe and modify the data type
        to reduce memory usage.
    """
    start_mem = df.memory_usage().sum() / 1024 ** 2
    # print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))

    for col in df.columns:
        col_type = df[col].dtype

        if col_type != object and col_type.name != 'category' and 'datetime' not in col_type.name:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        elif 'datetime' not in col_type.name:
            df[col] = df[col].astype('category')

    end_mem = df.memory_usage().sum() / 1024 ** 2
    # print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
    # print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))

    return df

def symbol_date_string(symbol, buy_date):
    buy_date = f"_buy_date_{buy_date}"
    return f"{symbol}{buy_date}"

def symbol_date_split(symbol_buy_date):
    symbol = symbol_buy_date.split('_buy_date_')[0]
    buy_date = symbol_buy_date.split('_buy_date_')[1]
    return symbol, buy_date


def symbol_date_range_string(symbol, start_date, end_date):
    date_range = f"_from_{start_date}_to_{end_date}"
    return f"{symbol}{date_range}"


def date_symbol_split(symbol_start_date_end_date):
    # date_range = f"_from_{start_date}_to_{end_date}"
    symbol = symbol_start_date_end_date.split('_from_')[0]
    second_string = symbol_start_date_end_date.split('_from_')[1]
    start_date = second_string.split('_to_')[0]
    end_date = second_string.split('_to_')[1]
    # print(symbol, start_date, end_date)
    return symbol, start_date, end_date

# date_symbol_split('ADANIGREEN_from_2020-10-14_to_2020-12-11')

def create_current_holdings_csv_file_names(symbol_df):
    # mask = df["current_holding"] == True
    # symbol_df = df[mask]
    # print(symbol_df.head(3).to_string())
    # exit()
    symbol_csv_path_list = make_nested_dict()
    for index, row in symbol_df.iterrows():
        symbol = row['equity']
        buy_date = row['date']
        symbol_buy_date = symbol_date_string(symbol, buy_date)
        path_to_csv_file = os.path.join(PATH_TO_DATABASE_CURRENT_HOLDINGS, f"{symbol_buy_date}_history.csv")
        symbol_csv_path_list[symbol_buy_date]=path_to_csv_file
    return  symbol_csv_path_list


def create_sold_holdings_csv_file_names(df):
    symbol_csv_path_list = make_nested_dict()
    mask1 = df["current_holding"] == False
    symbol_df = df[mask1].copy()
    symbol_list = sorted(list(set(symbol_df['equity'].to_list())))
    for symbol in symbol_list:
        mask = symbol_df["equity"] == symbol
        col_list = ['date', 'type', 'quantity', 'prev_units', 'cml_units','price','avg_price']
        df = symbol_df.loc[mask, col_list].copy()
        df.sort_values(by=['date'], ascending=True, inplace=True)

        # print(symbol)
        # if symbol == "ADANIGREEN":
        #     print(df.to_string())

        c = 0
        cml_units_old = 0
        start_date = datetime.date.today()
        end_date = datetime.date.today()
        for index, row in df.iterrows():
            # print('c=',c)
            if row['prev_units'] == 0:
                start_date = row['date']
                cml_units_old = row['cml_units']

            if row['cml_units'] < cml_units_old:
                end_date = row['date']

            if c == 0 and row['type'] != 'Buy':  # and start_date != end_date :
                print('start_date', start_date)
                print('end_date', end_date)
                print(f"Something wrong, before selling a stock must bought {symbol}")
                print(df.to_string())
                exit()

            c += 1
            if row['type'] == 'Sell':
                # print(symbol, start_date, end_date, row['type'])
                # print(df.to_string())
                symbol_date_range = symbol_date_range_string(symbol, start_date, end_date)
                # csv_file_name = f"{symbol_date_range}_Xquantiy.csv"
                csv_file_name = f"{symbol_date_range}.csv"
                path_to_csv_file = os.path.join(PATH_TO_DATABASE_SOLD_HOLDINGS, csv_file_name)
                symbol_csv_path_list[symbol_date_range]=path_to_csv_file
            cml_units_old = row['cml_units']
        # if symbol == "ADANIGREEN":
        #     exit()
    return  symbol_csv_path_list
