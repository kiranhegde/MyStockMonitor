import sqlite3

class sqlite3_crud:
    def __init__(self, **kwargs):
        self.filename = kwargs.get('filename')
        self.table = kwargs.get('table', 'test')
        # self.my_abs_path=self.get_path()

    def sql_do(self, sql, *params):
        self._db.execute(sql, params)
        self._db.commit()

    def insert(self, row):
        self._db.execute('insert into {} (id,mysql_login,mysql_passwd,mysql_dbname,mysql_hostname,mysql_port) values (?,?,?,?,?,?)'
                         .format(self._table), (row['id'],row['mysql_login'], row['mysql_passwd'],row['mysql_dbname'], row['mysql_hostname'],row['mysql_port']))
        self._db.commit()

    def retrieve(self, key):
        cursor = self._db.execute('select * from {} where id = ?'.format(self._table), (key,))
        return dict(cursor.fetchone())

    def update(self, row):
        self._db.execute(
            'update {} set mysql_login = ?,mysql_passwd=?,mysql_dbname=?,mysql_hostname=?,mysql_port=? where id = ?'.format(self._table),
            (row['mysql_login'], row['mysql_passwd'],row['mysql_dbname'], row['mysql_hostname'],row['mysql_port'], row['id']))
        self._db.commit()

    def check_table_empty(self,tname):
        # cursor = self._db.execute('select count(*) from {}'.format(tname))
        cursor = self._db.execute('SELECT count(*) FROM(select 1 from {} limit 1)'.format(tname))
        val=list(dict(cursor.fetchone()).values())
        return val[0]