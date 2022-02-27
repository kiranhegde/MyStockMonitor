from pathlib import Path
import sqlite3
from sqlite3 import Error
from utility.libnames import MYSQL_SQLITE_DB_LOGIN

class sqlite3_crud:
    def __init__(self, **kwargs):
        self.filename = kwargs.get('filename')
        self.table = kwargs.get('table','test')
        # self.my_abs_path=self.get_path()

    def sql_do(self, sql, *params):
        self._db.execute(sql, params)
        self._db.commit()

    def insert(self, row):
        self._db.execute('insert into {} (id,mysql_login,mysql_passwd,mysql_dbname,mysql_hostname,mysql_port) values (?,?,?,?,?,?)'
                         .format(self._table), (row['id'],row['mysql_login'], row['mysql_passwd'],row['mysql_dbname'], row['mysql_hostname'],row['mysql_port']))
        self._db.commit()

    def retrieve(self, key):
        if not self.check_row_empty():
            cursor = self._db.execute('select * from {} where id = ?'.format(self._table), (key,))
            return dict(cursor.fetchone())
        else:
            return None

    def check_row_empty(self):
        sql = f'SELECT * FROM   {self._table}   WHERE id IS NULL  OR  id = "";'
        cursor = self._db.execute(sql)
        val=False
        row_data=cursor.fetchone()
        if row_data != None:
            data=list(dict(cursor.fetchone()).values())
            if "" in data:
                val= True
        return val

    def update(self, row):
        self._db.execute(
            'update {} set mysql_login = ?,mysql_passwd=?,mysql_dbname=?,mysql_hostname=?,mysql_port=? where id = ?'.format(self._table),
            (row['mysql_login'], row['mysql_passwd'],row['mysql_dbname'], row['mysql_hostname'],row['mysql_port'], row['id']))
        self._db.commit()

    def check_table_empty(self,tname):
        # cursor = self._db.execute('select count(*) from {}'.format(tname))
        cursor = self._db.execute('SELECT count(*) FROM(select 1 from {} limit 1)'.format(tname))
        val=list(dict(cursor.fetchone()).values())
        if val[0] == 0:
            return True
        else:
            return False

    def mysql_login(self,tname):
        sql = f'''CREATE TABLE IF NOT EXISTS {tname}(
             id   int  NOT NULL,
             mysql_login CHAR(60) NOT NULL,
             mysql_passwd CHAR(60),
             mysql_dbname CHAR(60),
             mysql_hostname CHAR(60),
             mysql_port INT NOT NULL
          )'''
        return sql

    def create_table(self,conn):
        try:
            c = conn.cursor()
            sql = self.mysql_login(MYSQL_SQLITE_DB_LOGIN)

            c.execute(sql)
        except Error as e:
            print(e)

    def check_db_exists_create_empty_db(self,file_path,db):
        conn = None
        try:
            conn = sqlite3.connect(file_path)
            self.create_table(conn)
            log_info = {'id': 1, 'mysql_login': 'myname', 'mysql_passwd': 'mypasswd', 'mysql_dbname': 'stock_database',
                        'mysql_hostname': 'localhost', 'mysql_port': '3306'}
            mysql_msg = db.insert(log_info)
            # print(sqlite3.version)
        except IOError as e:
            print(e)
        finally:
            if conn:
                conn.close()

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, fn):
        self._filename = fn
        self._db = sqlite3.connect(fn)
        self._db.row_factory = sqlite3.Row

    @filename.deleter
    def filename(self):
        self.close()

    @property
    def table(self):
        return self._table

    @table.setter
    def table(self, t):
        self._table = t

    @table.deleter
    def table(self):
        self._table = 'test'

    def close(self):
        self._db.close()
        del self._filename


def main():
    import os
    dbname='mysql_input9.db'
    tname='mysql_login'
    cwd = os.getcwd()
    sqlite_db_path = os.path.join(cwd,dbname)
    print(sqlite_db_path)
    file_path = Path(sqlite_db_path)
    print(file_path)

    db = sqlite3_crud(filename =dbname , table =tname )
    db.check_db_exists_create_empty_db(file_path,db)
    table_empty=db.check_table_empty(tname)
    print(table_empty)
    row_empty=db.check_row_empty()
    check_val=False
    if not table_empty and not row_empty:
        mysql_log = db.retrieve('1')
        print(mysql_log)
    else:
        print("Table empty")
        if db.check_row_empty():
            log_info={'id': 1, 'mysql_login': 'kiran', 'mysql_passwd': 'pass1word', 'mysql_dbname': 'stock_database', 'mysql_hostname': 'localhost', 'mysql_port': '3306'}
            mysql_msg = db.insert(log_info)
        else:
            log_info = {'id': 1, 'mysql_login': 'kiran', 'mysql_passwd': 'pass9word', 'mysql_dbname': 'rk_hospital_new',
                        'mysql_hostname': 'localhost', 'mysql_port': '3306'}
            mysql_msg = db.update(log_info)

if __name__ == "__main__":
    main()