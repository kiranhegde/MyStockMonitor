import os

# working/project directory
PDIR = os.getcwd()

# log file
LOG_FILE = r'logging_exception_hook/log_file.log'

# welcome text
WELCOME = "Stock Monitor"
# sqlite db table name
MYSQL_SQLITE_DB = 'mysql_input_data.db'
MYSQL_SQLITE_DB_LOGIN = 'mysql_login'

# mysql db info
mysql_db_name = "stock_database"
# database folders
PATH_TO_DATABASE = 'database'
PATH_TO_DATABASE_BACKUP = 'database_backup'
PATH_TO_DATABASE_CURRENT_HOLDINGS = os.path.join(PDIR, PATH_TO_DATABASE, 'current_holdings')
PATH_TO_DATABASE_SOLD_HOLDINGS = os.path.join(PDIR, PATH_TO_DATABASE, 'sold_holdings')
PATH_TO_DATABASE_CURRENT_HOLDINGS_BKP = os.path.join(PDIR, PATH_TO_DATABASE_BACKUP, 'current_holdings')
PATH_TO_DATABASE_SOLD_HOLDINGS_BKP = os.path.join(PDIR, PATH_TO_DATABASE_BACKUP, 'sold_holdings')

# current_stock_table="stocks_in_account"
# sold_stock_table="stocks_sold_out"
# transaction_to_demat_account="transation_to_demat"
# transaction_from_demat_account="transation_from_demat"

AGENCY_LIST = ["Zerodha", "Kotak"]
EXCHANGE_LIST = ['NSE', 'BSE']
