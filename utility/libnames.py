# log file
LOG_FILE = r'logging/log_file.log'

# mysql db info
mysql_db_name="stock_database"
current_stock_table="stocks_in_account"
sold_stock_table="stocks_sold_out"
transaction_to_demat_account="transation_to_demat"
transaction_from_demat_account="transation_from_demat"


#mysql table header names
STOCK_LIST=['id','ref_number','exchange','equity','avg_price','quantity','buy_date','sale_date','remarks']
#display names
STOCK_HEADER=["ID","Ref. Number",'Exchange','Equity','Avg. Price','Quantity','Buy Date','Sale Date','Remarks']

STOCK_DB_TO_DISAPLY={}
for k,v in zip(STOCK_LIST,STOCK_HEADER):
    STOCK_DB_TO_DISAPLY[k]=v

print(STOCK_DB_TO_DISAPLY)