import cx_Oracle
import os

class OracleUtils:

    USER = os.getenv("MYUSER")
    PWD = os.getenv("MYPASSWD")
    IP = os.getenv("MYHOST")
    PORT = os.getenv("MYPORT")
    DB = os.getenv("MYDB")
        
    DB_ENCONDING = 'UTF-8'

    def __init__(self, autocommit=False):
        super().__init__()
        self.con = None
        self.cur = None
        self.autocommit = False

    def __enter__(self):
        self.initiate_connection()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self.terminate_connection()

    def initiate_connection(self):
        self.con, self.cur = self.get_db_connection()

    def terminate_connection(self):
        if self.con is not None:
            self.con.close()

    def commit_changes(self):
        if self.con is not None:
            self.con.commit()

    def rollback_changes(self):
        if self.con is not None:
            self.con.rollback()

    def get_db_connection(self):
        try:
            self.con = cx_Oracle.connect(OracleUtils.USER, OracleUtils.PWD, 
                cx_Oracle.makedsn(OracleUtils.IP, OracleUtils.PORT, None, OracleUtils.DB), 
                encoding=OracleUtils.DB_ENCONDING, nencoding=OracleUtils.DB_ENCONDING)
        
        except Exception as e:
            print(e)
            raise e
    
        return self.con, None if self.con == None else self.con.cursor()

    def execute_query(self, query, as_dict=False):
        self.cur.execute(query)
        
        if as_dict:
            self.cur.rowfactory = lambda *args: dict(zip([d[0] for d in self.cur.description], args))   

    def execute_non_query(self, query):
        self.cur.execute(query)
        
        if self.autocommit:
            self.commit_changes()

    def fetchone(self):
        if self.cur is not None:
            return self.cur.fetchone()

    def fetchall(self):
        if self.cur is not None:
            return self.cur.fetchall()

    def fetchmany(self, amount):
        if self.cur is not None:
            return self.cur.fetchmany(amount)