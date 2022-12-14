# mysql db info
MYSQL_DB_NAME = "stock_database_new"
TOTAL_HOLDINGS_DB_TABLE_NAME = "total_holdings_new"
CURRENT_HOLDINGS_DB_TABLE_NAME = "current_holdings"
SOLD_HOLDINGS_DB_TABLE_NAME = "sold_out_holdings"
BANK_TRANSACTIONS_DB_TABLE_NAME = "bank_transations"
DEFAULTS = "defaults_values"
# TRANSACTION_FROM_DEMAT_ACCOUNT_TABLE="transation_from_demat"

TRADE_TYPE = ["Buy", "Sell"]

# # mysql table header names
# TOTAL_HOLDINGS_DB_HEADER = ['id', 'ref_number', 'date', 'type', 'agency', 'exchange', 'equity', 'quantity', 'price',
#                             'fees', 'avg_price', 'remarks']
# TOTAL_HOLDINGS_EXTRA_HEADER = ['transact_val', 'cashflow', 'prev_units', 'cml_units', 'prev_cost',
#                                'cml_cost', 'gain_loss', 'yield']
# # cml- cummulative
# TOTAL_HOLDINGS_CALC_HEADER = TOTAL_HOLDINGS_DB_HEADER + TOTAL_HOLDINGS_EXTRA_HEADER

# mysql table header names
TOTAL_HOLDINGS_DB_HEADER = ['id', 'ref_number', 'date', 'type','agency','equity', 'quantity', 'price',
                            'fees', 'avg_price', 'current_holding','remarks']
TOTAL_HOLDINGS_EXTRA_HEADER = ['transact_val', 'cashflow', 'prev_units', 'cml_units', 'prev_cost',
                               'cml_cost', 'gain_loss', 'yield']
# cml- cummulative
TOTAL_HOLDINGS_CALC_HEADER = TOTAL_HOLDINGS_DB_HEADER + TOTAL_HOLDINGS_EXTRA_HEADER




CURRENT_HOLDING_DB_HEADER = ['id', 'ref_number', 'agency', 'exchange', 'equity', 'buy_date', 'avg_price', 'quantity',
                             'remarks']
SOLD_HOLDING_DB_HEADER = ['id', 'ref_number', 'agency', 'exchange', 'equity', 'buy_date', 'buy_price',
                          'sale_date', 'sale_price', 'sale_quantity', 'remarks']
BANK_TRANSACTIONS_DB_HEADER = ['id', 'agency', 'transaction_date', 'transaction_id', 'amount', 'from_bank',
                               'to_bank', 'remarks']
# BANK_TRANSACTIONS_DB_HEADER=['id','to_agency','transaction_date','transaction_id','amount','from_bank','to_bank','remarks']
DEFAULTS_DB_HEADER = ['brokerage', 'gst', 'stt', 'itax']

HOLDINGS_HEADER = ["ID", "Reference", "Buy Date", 'Type', "Agency", "Exchange", "Equity", "Quantity", "Avg. Price",
                   "Remarks"]
# Current holding headers
CURRENT_HOLDINGS_HEADER = ["ID", "Reference", "Agency", "Exchange", "Equity", "Buy Date", "Avg. Price", "Quantity",
                           "Remarks"]
# Columns to be displayed in the gui
CURRENT_HOLDING_LIST_DISPLAY = ['ref_number', 'equity', 'buy_date', 'avg_price', 'quantity']
CURRENT_HOLDING_DB_TO_DISPLAY = dict(zip(CURRENT_HOLDING_DB_HEADER, CURRENT_HOLDINGS_HEADER))

# list of header name to be dropped
CURRENT_HOLDINGS_HEADER_DROP_LIST = []
for hdr_name in CURRENT_HOLDING_DB_HEADER:
    if hdr_name not in CURRENT_HOLDING_LIST_DISPLAY:
        CURRENT_HOLDINGS_HEADER_DROP_LIST.append(hdr_name)

# list of header name to be retained
CURRENT_HOLDINGS_HEADER_DISPLAY_LIST = []
for hdr_name in CURRENT_HOLDING_LIST_DISPLAY:
    CURRENT_HOLDINGS_HEADER_DISPLAY_LIST.append(CURRENT_HOLDING_DB_TO_DISPLAY[hdr_name])

# print(CURRENT_HOLDINGS_HEADER_DROP_LIST)
# print(CURRENT_HOLDINGS_HEADER_DISPLAY_LIST)
# sold holdings header
SOLD_HOLDINGS_HEADER = ["ID", "Reference", "Agency", "Exchange", "Equity", "Buy Date", "Buy Price", 'Sale Date',
                        'Sale Price', 'Sale Quantity', "Remarks"]
SOLD_HOLDINGS_LIST_DISPLAY = ['equity', 'buy_date', 'buy_price', 'sale_date', 'sale_price', 'sale_quantity']
SOLD_HOLDING_DB_TO_DISPLAY = dict(zip(SOLD_HOLDING_DB_HEADER, SOLD_HOLDINGS_HEADER))

# bank transactions
BANK_TRANSACTIONS_HEADER = ['ID', "Agency", "Date", "Reference_no", "Amount", "From_Bank", "To_Bank", "Remarks"]
BANK_TRANSACTIONS_LIST_DISPLAY = ["agency", 'transaction_date', 'amount']
BANK_TRANSACTIONS_DB_TO_DISPLAY = dict(zip(BANK_TRANSACTIONS_DB_HEADER, BANK_TRANSACTIONS_HEADER))


def create_transaction_table_db_query(tablename):
    create_transaction_table = """
              CREATE TABLE  IF NOT EXISTS %s (     
              id INT AUTO_INCREMENT  PRIMARY KEY,    
              agency TEXT NOT NULL, 
              transaction_date DATE NOT NULL,  
              transaction_id TEXT NOT NULL, 
              amount FLOAT(10.2) ,
              from_bank TEXT NOT NULL,
              to_bank TEXT NOT NULL,                                 
              remarks TEXT
              ) ;
              """ % tablename
    return create_transaction_table


def create_sold_holdings_table_db_query(tablename):
    create_sold_holdings_table = """
              CREATE TABLE  IF NOT EXISTS %s (     
              id INT AUTO_INCREMENT  PRIMARY KEY,       
              ref_number INT NOT NULL,
              agency TEXT NOT NULL,
              exchange TEXT NOT NULL,
              equity TEXT NOT NULL,  
              buy_date DATE NOT NULL,
              buy_price FLOAT(10.2) ,   
              sale_date DATE NOT NULL,
              sale_price FLOAT(10.2) ,
              sale_quantity INT NOT NULL,
              remarks TEXT
              ) ;
              """ % tablename
    return create_sold_holdings_table


def create_current_holdings_table_db_query(tablename):
    create_current_holdings_table = """
              CREATE TABLE  IF NOT EXISTS %s (     
              id INT AUTO_INCREMENT  PRIMARY KEY,       
              ref_number INT NOT NULL,
              agency TEXT NOT NULL,
              exchange TEXT NOT NULL,
              equity TEXT NOT NULL,  
              buy_date DATE NOT NULL,
              avg_price FLOAT(10.2) ,
              quantity INT NOT NULL,                                 
              remarks TEXT
              ) ;
              """ % tablename
    return create_current_holdings_table


# ['id', 'ref_number', 'date', 'type', 'agency', 'exchange', 'equity', 'quantity', 'price',
#                      'fees', 'avg_price']
def create_all_holdings_table_db_query_old(tablename):
    create_current_holdings_table = """
              CREATE TABLE  IF NOT EXISTS %s (     
              id INT AUTO_INCREMENT  PRIMARY KEY,       
              ref_number INT NOT NULL,
              date DATE NOT NULL,
              type TEXT NOT NULL,
              agency TEXT NOT NULL,
              exchange TEXT NOT NULL,
              equity TEXT NOT NULL,  
              quantity INT NOT NULL, 
              price FLOAT(10.2) ,                                              
              fees FLOAT(10.2) ,                                              
              avg_price FLOAT(10.2) ,                                              
              remarks TEXT
              ) ;
              """ % tablename
    return create_current_holdings_table

# id', 'ref_number', 'date', 'type','agency','equity', 'quantity', 'price',
#                             'fees', 'avg_price', 'current_holding','remarks'
def create_all_holdings_table_db_query(tablename):
    create_current_holdings_table = """
              CREATE TABLE  IF NOT EXISTS %s (     
              id INT AUTO_INCREMENT  PRIMARY KEY,       
              ref_number INT NOT NULL,
              date DATE NOT NULL,
              type TEXT NOT NULL,
              agency TEXT NOT NULL,
              equity TEXT NOT NULL,  
              quantity INT NOT NULL, 
              price FLOAT(10.2) ,                                              
              fees FLOAT(10.2) ,                                              
              avg_price FLOAT(10.2) ,                                              
              current_holding BOOLEAN ,                                              
              remarks TEXT
              ) ;
              """ % tablename
    return create_current_holdings_table
