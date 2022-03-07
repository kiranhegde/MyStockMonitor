from glob import glob
import pandas as pd
from multiprocessing import Pool
import os

# source_folder = os.path.join('E:\SharesAndStocks\MyStockMonitor\database\current_holdings', "")
# # get a list of file names
# files = os.listdir(source_folder)
# folder = "./task_1/" # note the "/" at the end
# file_list = glob(folder+'*.xlsx')

# DF_LIST = [] # A) end
DF = pd.DataFrame()  # B) during

source_folder=os.path.join('E:\SharesAndStocks\MyStockMonitor\database\current_holdings',"")
# get a list of file names
files = os.listdir(source_folder)
file_list0 = [filename for filename in files if filename.split('.')[1]=='csv']
file_list = []
for fname in file_list0:
    file_path=os.path.join(source_folder,fname)
    file_list.append(file_path)


def my_read(filename):
    f = pd.read_csv(filename)
    return f #(f.VALUE.as_matrix()).reshape(75,90)


def DF_LIST_append(result):
    #DF_LIST.append(result) # A) end
    global DF # B) during
    result['Volume'] = 1
    # DF.sort_values(by=['Date'], ascending=True, inplace=True)
    DF = pd.concat([DF, result]).groupby(['Date']).sum().reset_index()
    # DF = pd.concat([DF,result], ignore_index=True) # B) during
    # print(DF.head().to_string())

def main():
    global DF
    pool = Pool(processes=6)
    for file in file_list:
        pool.apply_async(my_read, args = (file,), callback = DF_LIST_append)

    pool.close()
    pool.join()
    print(DF.to_string())
    print(len(DF.to_string()))

#DF = pd.concat(DF_LIST, ignore_index=True) # A) end

# print(DF.shape)
#

if __name__ == '__main__':
    main()