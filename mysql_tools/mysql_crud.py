import mysql.connector
import pandas as pd
from mysql.connector import Error
from functools import wraps


class MYSQL_Database(object):

    # def __init__(self, username, password, db, host='localhost', port=3306):
    def __init__(self, **dbcfg):
        try:
            self.connection = mysql.connector.connect(**dbcfg)
        except Error as err:
            message = f"Error: '{err}'"
            raise message

        self.cursors = []

    def __enter__(self):
        curs = self.connection.cursor(dictionary=True)
        self.cursors.append(curs)
        return curs

    def __exit__(self, *args):
        for cursor in self.cursors:
            cursor.close()
        self.connection.close()


def mysql_db(dbcfg):
    def db_call(f):
        @wraps(f)
        def db_wrap(*args, **kwargs):
            with MYSQL_Database(**dbcfg) as db:
                return f(db, *args, **kwargs)

        return db_wrap

    return db_call


# def create_server_connection(host_name, user_name, user_password):
# def create_server_connection(**dbcfg):
#     connection = False
#     try:
#         connection = mysql.connector.connect(**dbcfg)
#             # host=host_name,
#             # user=user_name,
#             # passwd=user_password)
#         message = "Database connection successful"
#     except Error as err:
#         message = f"Error: '{err}'"
#
#     return connection, message


# Modify Server Connection Function, Create Database Connection Function
# def create_db_connection(**dbcfg):
#     connection = None
#     try:
#         connection = mysql.connector.connect(**dbcfg)
#             # host=host_name,
#             # user=user_name,
#             # passwd=user_password,
#             # database=db_name)
#         message = "MySQL Database read  successful"
#     except Error as err:
#         message = f"Error: '{err}'"
#         connection = False
#
#     return connection, message


# Create a New Database
# def create_database(connection, query):
#     cursor = connection.cursor()
#     try:
#         cursor.execute(query)
#         message = "Database created successfully"
#     except Error as err:
#         message = f"Error: '{err}'"
#     return message


# def check_db_exists(connection, dbname):
#     db_check = False
#     mycursor = connection.cursor()
#     # mycursor.execute("CREATE DATABASE firstdatabase")
#     mycursor.execute("SHOW DATABASES")
#     db_list = [list[0] for list in mycursor.fetchall()]
#     message = " "
#     if dbname in db_list:
#         message = f"{dbname} exists"
#         db_check = True
#
#     return db_check, message


# def execute_query(connection, query):
#     cursor = connection.cursor()
#     # print(query)
#     try:
#         cursor.execute(query)
#         connection.commit()
#         message = "Query successful"
#     except Error as err:
#         message = f"Error: '{err}'"
#     return message


# def read_query(connection, query):
#     cursor = connection.cursor()
#
#     try:
#         cursor.execute(query)
#         result = cursor.fetchall()
#         message = "Reading Data"
#         return result, message
#     except Error as err:
#         message = f"Error: '{err}'"
#         result = False
#         return result, message


# def create_db_query(dbname):
#     return f"CREATE DATABASE {dbname}"


# def check_table_exists_query(db_table):
#     return f"SHOW TABLES LIKE '{db_table}%'"


def get_all_table_by_prefix(prefix):
    return f"SHOW TABLES LIKE '{prefix}%'"


class mysql_table_crud(object):

    # def __init__(self, user, passwd, db, host, port, db_table=None, db_header=None):
    def __init__(self, db_table=None, db_header=None, **mysql_cfg):

        self.db_table = db_table
        self.db_header = db_header
        self.db_name = mysql_cfg.get('db')
        self.conn = False
        self.__refresh()

        try:
            self.conn = mysql.connector.connect(**mysql_cfg)
            # self.cursor = self.conn.cursor()
            self.cursor = self.conn.cursor(dictionary=True)
            self.message = "Database connection successful"
        except Error as err:
            self.message = f"Error: '{err}'"
            print(self.message)

    def __exit__(self, *args):
        for cursor in self.cursor:
            cursor.close()
        self.conn.close()

    def __refresh(self):
        self.message = ""
        self.criteria = None
        self.column_name = "*"
        self.order = None
        self.set_argument = None

    def db_connection(self):
        return self.conn, self.message

    def check_db_exists(self, dbname):
        db_check = False
        # mycursor = connection.cursor()
        # mycursor.execute("CREATE DATABASE firstdatabase")
        self.cursor.execute("SHOW DATABASES")
        # db_list =[list[0] for list in self.cursor.fetchall()]
        db_list = [list(dictn.values())[0] for dictn in self.cursor.fetchall()]
        # db_list = self.cursor.fetchall()
        # print(db_list)
        message = f"{dbname} not available"
        if dbname in db_list:
            message = f"{dbname} exists"
            db_check = True

        return db_check, message

    def check_table_exists(self):
        query = f"SHOW TABLES LIKE '{self.db_table}%'"
        # print(query)
        return self.__read_query(query)

    def create_table(self, query):
        return self.__execute_query(query)

    def create_database(self, dbname=None):
        if dbname != None:
            query = f"CREATE DATABASE {dbname}"
            try:
                self.cursor.execute(query)
                # self.__execute_query(query)
                message = "Database created successfully"
            except Error as err:
                message = f"Error: '{err}'"
        else:
            message = f"database name not provided"
        return message

    def table_view(self, data):
        if isinstance(data[0], dict):
            df = pd.DataFrame(data)
            print(df.to_string())
        elif isinstance(data, list):
            for val in data:
                print('  '.join(str(item) for item in val))
        else:
            print(data)

        print(f"")

    def get_departments_in_db(self, order=None):
        sql = f"SELECT distinct department FROM {self.db_table}"
        try:
            if order != None:
                sql = f"{sql} {order} "
            sql = f"{sql} ;"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Error as err:
            return f"Error: '{err}'"

    def insert_row_by_column_values(self, row_val, criteria=None):
        self.criteria = criteria
        sql = self.__column_value_search(task='insert')
        sql = f"{sql} ;"
        # print(sql)
        # print(row_val)
        try:
            self.cursor.executemany(sql, row_val)
            self.conn.commit()
            return f"Row inerted successfuly "
        except Error as err:
            return f"Error: '{err}'"

    def read_row_by_column_values(self, column_name="*", order=None, criteria=None):
        self.column_name = column_name
        self.order = order
        self.criteria = criteria
        sql = self.__column_value_search(task='read')
        try:
            if order != None:
                sql = f"{sql} {order} "
            sql = f"{sql} ;"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Error as err:
            return f"Error: '{err}'"

    def delete_row_by_column_values(self, criteria):
        self.criteria = criteria
        sql = self.__column_value_search(task='delete')
        sql = f"{sql} ;"
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            return f"Deleted successfuly"
        except Error as err:
            return f"Error: '{err}'"

    def update_rows_by_column_values(self, set_argument, criteria):
        self.criteria = criteria
        self.set_argument = set_argument
        sql = self.__column_value_search(task='update')
        sql = f"{sql} ;"
        # print(sql)
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            return f"Updated successfuly"
        except Error as err:
            return f"Error: '{err}'"

    def get_column_value_count(self, col_name):
        query = f"select {col_name}, count({col_name}) from {self.db_table} group by {col_name} order by  count({col_name}) DESC;"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as err:
            return f"Error: '{err}'"

    def add_column_name_to_table(self, col_name, dtype):
        query = f"ALTER TABLE {self.db_table} ADD {col_name} {dtype}"
        # print(query)
        try:
            self.cursor.execute(query)
            self.conn.commit()
            return f"columns:{col_name},datatype:{dtype} added successfuly"
        except Error as err:
            return f"Failed to add columns:{col_name},datatype:{dtype} \nError: '{err}'"

    # def __column_value_search(self, criteria,set_argument=None,column_name="*",  task=None):
    def __column_value_search(self, task=None):

        if task == 'read':
            sql = f"SELECT {self.column_name} FROM {self.db_table}"
            if self.criteria:
                sql = f"{sql} WHERE {self.criteria}"
        elif task == 'insert':
            column_names = ', '.join(self.db_header)
            placeholders = ', '.join(['%s'] * len(self.db_header))
            sql = f"INSERT INTO {self.db_table} ({column_names}) VALUES ({placeholders})"
            # if criteria:
            #     sql = f"{sql} WHERE {criteria};"
        elif task == 'delete':
            sql = f"DELETE from {self.db_table} where {self.criteria}"
        elif task == 'update':
            sql = f"UPDATE {self.db_table} SET {self.set_argument} where {self.criteria}"
        else:
            sql = "None"
        # print(sql)
        self.__refresh()
        return sql

    def __read_query(self, query):
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            message = "Reading Data"
            return result, message
        except Error as err:
            message = f"Error: '{err}'"
            result = False
            return result, message

    def __execute_query(self, query):
        try:
            self.cursor.execute(query)
            self.conn.commit()
            message = "Executed successful"
        except Error as err:
            message = f"Error: '{err}'"
        return message

    def con_close(self):
        if self.conn:
            self.conn.close()


if __name__ == '__main__':

    RECEPTION_BILL_PAYIN_PREFIX = "pharmacy_statement_payin"
    PAYIN_TABLE_HEADER = ['id', 'bill_no', 'user', 'date_time', 'patient_name', 'department', 'pay_cash',
                          'pay_credit_card',
                          'pay_debit_card', 'pay_eft', 'pay_unpaid', 'edit_info', 'remarks', 'mobile_no']

    db_cfg = dict(user='kiran',
                  passwd='pass1word',
                  port=3306,
                  host='localhost',
                  db='rk_hospital_new')

    payin_table = mysql_table_crud(db_table=RECEPTION_BILL_PAYIN_PREFIX,
                                   db_header=PAYIN_TABLE_HEADER,
                                   **db_cfg)

    table_list = [
        {'id': 0, 'bill_no': 404, 'user': 'kiran', 'date_time': '2021-05-12 14:15:52', 'patient_name': 'qwerty',
         'department': 'OPD', 'pay_cash': 1.0, 'pay_credit_card': 1.0, 'pay_debit_card': 0.0,
         'pay_eft': 0.0, 'pay_unpaid': 0.0, 'edit_info': 'kiran', 'remarks': 'na', 'mobile_no': ""}
    ]

    tab = payin_table.read_row_by_column_values(criteria=f"pay_cash='434'")
    # print(tab)
    payin_table.table_view(tab)

    row_data = tab[0]
    pnameold = "sdf"
    pnameNew = '21RK000101'

    mobile_number = 123456789
    row_data['mobile_no'] = mobile_number
    row_data['patient_name'] = pnameNew
    id = 531
    set_list = ""
    for k, v in row_data.items():
        if k != 'id':
            set_list = f"{set_list},{k}='{v}'"
    set_list = set_list[1:]
    # print(set_list)

    set_list = f" patient_name='{pnameNew}' , mobile_no={mobile_number} "
    messge = payin_table.update_rows_by_column_values(set_argument=set_list, criteria=f"patient_name='{pnameold}'")
    print(messge)
    # tab = payin_table.read_row_by_column_values()
    # print(tab)
