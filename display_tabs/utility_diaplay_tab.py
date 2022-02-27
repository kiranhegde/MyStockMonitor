import os
import pandas as pd
import datetime
import yfinance as yf

from utility.utility_functions import reduce_mem_usage, make_nested_dict,symbol_date_range_string, date_symbol_split, gen_id,\
    symbol_date_string,create_current_holdings_csv_file_names,create_sold_holdings_csv_file_names,symbol_date_split


def get_current_holdings_history(current_holding_data_df):
    current_holding_history = make_nested_dict()
    current_holdings_csv_file_names = create_current_holdings_csv_file_names(current_holding_data_df)

    # for index, row in  .current_holding_data_df.iterrows():
    for symbol_buy_date,path_to_csv_file in  current_holdings_csv_file_names.items():

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
            data = yf.download(symbol_ns)
            # print(symbol, path_to_csv_file)
            data.to_csv(path_to_csv_file)
            df = pd.DataFrame(pd.read_csv(path_to_csv_file))
            for i in ['Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']:
                df[i] = df[i].astype('float64')
                # df[i] = df[i].astype("category")
            #  .sold_holding_history[symbol_date_range] = reduce_mem_usage(df)
            current_holding_history[symbol_buy_date] = reduce_mem_usage(df)
    return current_holding_history


def get_sold_holdings_history(overall_holdings):
    sold_holding_history = make_nested_dict()
    sold_holdings_csv_file_names = create_sold_holdings_csv_file_names(overall_holdings)
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
            symbol, start_date, end_date=date_symbol_split(symbol_date_range)
            symbol_ns = f"{symbol}.NS"
            sale_date_1 = datetime.date.fromisoformat(str(end_date)) + datetime.timedelta(days=1)
            data = yf.download(symbol_ns, start=start_date, end=sale_date_1)
            data.to_csv(path_to_csv_file)
            df = pd.DataFrame(pd.read_csv(path_to_csv_file))
            for i in ['Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']:
                df[i] = df[i].astype('float64')
                # df[i] = df[i].astype("category")
                #   sold_holding_history[symbol_date_range] = reduce_mem_usage(df)
            sold_holding_history[symbol_date_range] = df

    return sold_holding_history