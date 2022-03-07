import os
import pandas as pd
from multiprocessing import Pool

# wrap your csv importer in a function that can be mapped
def read_csv(filename):
    'converts a filename to a pandas dataframe'
    return pd.read_csv(filename)


def main():
    source_folder=os.path.join('E:\SharesAndStocks\MyStockMonitor\database\current_holdings',"")
    # get a list of file names
    files = os.listdir(source_folder)
    file_list0 = [filename for filename in files if filename.split('.')[1]=='csv']
    file_list = []
    for fname in file_list0:
        file_path=os.path.join(source_folder,fname)
        file_list.append(file_path)
        # print(file_path)
    # print(file_list)

    # set up your pool
    with Pool(processes=8) as pool: # or whatever your hardware can support
        # have your pool map the file names to dataframes
        df_list = pool.map(read_csv, file_list)
        # reduce the list of dataframes to a single dataframe
        combined_df = pd.concat(df_list, ignore_index=True)

        # df.sort_values(by=['Date'], ascending=True, inplace=True)
        # market_value_history = pd.concat([market_value_history, df]).groupby(['Date']).sum().reset_index()

    print(combined_df.head().to_string())

if __name__ == '__main__':
    main()