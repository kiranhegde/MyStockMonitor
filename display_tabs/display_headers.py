from mysql_tools.tables_and_headers import STOCK_LIST


#display names
STOCK_HEADER=["ID","Ref. Number",'Exchange','Equity','Avg. Price','Quantity','Buy Date','Sale Date','Remarks']


STOCK_DB_TO_DISAPLY={}
for k,v in zip(STOCK_LIST,STOCK_HEADER):
    STOCK_DB_TO_DISAPLY[k]=v

print(STOCK_DB_TO_DISAPLY)