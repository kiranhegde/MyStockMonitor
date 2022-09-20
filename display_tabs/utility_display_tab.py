import os
import pandas as pd
import datetime
import yfinance as yf

from utility.utility_functions import reduce_mem_usage, make_nested_dict, symbol_date_range_string, date_symbol_split, \
    gen_id, \
    symbol_date_string, create_current_holdings_csv_file_names, create_sold_holdings_csv_file_names, symbol_date_split

from share.libnames import HISTORY_YEARS
from multiprocessing import Pool
import multiprocessing
from threading import Thread

def get_current_holdings_history_mp(holdings_csv_file_names):
    # https://stackoverflow.com/questions/62130801/parallel-processing-in-python-to-fill-a-dictionary-with-the-value-as-a-dictionar
    # from multiprocessing import Process, Manager
    current_holding_history = make_nested_dict()
    # current_holdings_csv_file_names = create_current_holdings_csv_file_names(current_holding_data_df)

    def csv_file_read(filename):
        f = pd.read_csv(filename)
        return f

    def download_and_read_csv(symbol,filename):
        # data = yf.download(symbol_ns, threads=True)
        data = yf.download(symbol,threads=True,start=deltatime)
        data.to_csv(filename)
        f=csv_file_read(filename)
        return f

    def compile_stock_data(result):
        df = pd.DataFrame(result)
        mask = df['Date'] > str(deltatime)
        for i in ['Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']:
            df[i] = df[i].astype('float64')
        df = df.loc[mask].copy()
        current_holding_history[symbol_buy_date] = reduce_mem_usage(df)

    # pool = Pool(processes=6)
    jobs=[]
    deltatime = datetime.date.today() - datetime.timedelta(HISTORY_YEARS * 365)
    for symbol_buy_date, path_to_csv_file in holdings_csv_file_names.items():

        if os.path.isfile(path_to_csv_file):
            csv_data=csv_file_read(path_to_csv_file)
            compile_stock_data(csv_data)
            # process=multiprocessing.Process(target=compile_stock_data,args=(csv_data))
            # jobs.append(process)
            # pool.apply_async(csv_file_read, args=(path_to_csv_file,), callback=compile_stock_data)
        else:
            print(path_to_csv_file, 'path missing')
            symbol, buy_date = symbol_date_split(symbol_buy_date)
            symbol_ns = f"{symbol}.NS"
            csv_data=download_and_read_csv(symbol_ns,path_to_csv_file)
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


def get_current_holdings_history(current_holding_data_df):
    current_holding_history = make_nested_dict()
    current_holdings_csv_file_names = create_current_holdings_csv_file_names(current_holding_data_df)

    # for index, row in  .current_holding_data_df.iterrows():
    for symbol_buy_date, path_to_csv_file in current_holdings_csv_file_names.items():

        if os.path.isfile(path_to_csv_file):
            df = pd.DataFrame(pd.read_csv(path_to_csv_file))
            deltatime = datetime.date.today() - datetime.timedelta(5 * 365)
            mask = df['Date'] > str(deltatime)
            for i in ['Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']:
                df[i] = df[i].astype('float64')
                # df[i] = df[i].astype("category")
            # print('----------------after')
            # df = reduce_mem_usage(df)
            # print(df.memory_usage(deep=True))
            df = df.loc[mask].copy()
            current_holding_history[symbol_buy_date] = reduce_mem_usage(df)
            # print(df.head(4).to_string())
        else:
            print(path_to_csv_file, 'path missing')
            symbol, buy_date = symbol_date_split(symbol_buy_date)
            symbol_ns = f"{symbol}.NS"
            data = yf.download(symbol_ns, threads=True)
            # print(symbol, path_to_csv_file)
            data.to_csv(path_to_csv_file)
            df = pd.DataFrame(pd.read_csv(path_to_csv_file))
            for i in ['Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']:
                df[i] = df[i].astype('float64')
                # df[i] = df[i].astype("category")
            #  .sold_holding_history[symbol_date_range] = reduce_mem_usage(df)
            current_holding_history[symbol_buy_date] = reduce_mem_usage(df)
    return current_holding_history


def get_sold_holdings_history(sold_holdings_csv_file_names):
    sold_holding_history = make_nested_dict()
    # sold_holdings_csv_file_names = create_sold_holdings_csv_file_names(overall_holdings)
    # print(sold_holdings_csv_file_names)
    # exit()

    for symbol_date_range, path_to_csv_file in sold_holdings_csv_file_names.items():

        if os.path.isfile(path_to_csv_file):
            df = pd.DataFrame(pd.read_csv(path_to_csv_file))
            for i in ['Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']:
                df[i] = df[i].astype('float64')
                # df[i] = df[i].astype("category")
                #   sold_holding_history[symbol_date_range] = reduce_mem_usage(df)
            sold_holding_history[symbol_date_range] = df
        else:
            print(path_to_csv_file, 'path missing, downloading the data..')
            symbol, start_date, end_date = date_symbol_split(symbol_date_range)
            symbol_ns = f"{symbol}.NS"
            sale_date_1 = datetime.date.fromisoformat(str(end_date)) + datetime.timedelta(days=1)
            data = yf.download(symbol_ns, start=start_date, end=sale_date_1, threads=True)
            data.to_csv(path_to_csv_file)
            df = pd.DataFrame(pd.read_csv(path_to_csv_file))
            for i in ['Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']:
                df[i] = df[i].astype('float64')
                # df[i] = df[i].astype("category")
                #   sold_holding_history[symbol_date_range] = reduce_mem_usage(df)
            sold_holding_history[symbol_date_range] = df

    return sold_holding_history

# def download_stock_history(list_fo_files,start_date,end_date):
#
#     for path_to_csv_file in list_fo_files:
#         if not os.path.isfile(path_to_csv_file):
#             data = yf.download(symbol_ns, start=start_date, end=sale_date_1, threads=True)
#             data.to_csv(path_to_csv_file)
