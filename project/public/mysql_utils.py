import mysql.connector
import os

HOST = os.getenv("EBOOK_HOST")
USER = os.getenv("EBOOK_USER")
PWD = os.getenv("EBOOK_PASSWD")
PORT = os.getenv("EBOOK_PORT")
DB = os.getenv("EBOOK_DB")


class MySqlUtils:

    @staticmethod
    def get_db_connection():
        try:
            con = mysql.connector.connect(
                    host = HOST,
                    port = PORT,
                    user = USER,
                    passwd = PWD,
                    database = DB
                )

            return con, con.cursor()
        
        except Exception as e:
            print(e)
    
        return None, None

    @staticmethod
    def execute_query(query):
        con = None
        result = None

        try:
            con, cur = MySqlUtils.get_db_connection()
        
            cur.execute(query)
            result = cur.fetchall()
        
        except Exception as e:
            print(e)
        
        if con == None:
            con.close()
        
        return result

    @staticmethod
    def execute_non_query(query):
        con = None
        try:
            con, cur = MySqlUtils.get_db_connection()
            cur.execute(query)
            con.commit()
        
        except Exception as e:
            print(e)

        if con == None:
            con.close()