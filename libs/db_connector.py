import pymysql.cursors
import time
import pymysql.err

from libs.GLogger import Logger
logger = Logger("db_connector")

class mysql():
    def __init__(self,xip,xport,usr,pwd,dbname):
        self.xip = xip
        self.xport = xport
        self.usr = usr
        self.pwd = pwd
        self.dbname = dbname
        self.reconnect()

    def reconnect(self):
        self.connection = pymysql.connect(host=self.xip,
                                          port=self.xport,
                                          user=self.usr,
                                          password=self.pwd,
                                          db=self.dbname,
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()

    def QDB_FULL(self,xQuery): 
        sql = xQuery
        self.cursor.execute(sql)
        self.connection.commit()
        result = self.cursor.fetchall()
        return result

    '''
    def SAFE_QDB_FULL(self,xQuery,qparams): 
        sql = xQuery
        self.cursor.execute(sql,qparams)
        self.connection.commit()
        result = self.cursor.fetchall()
        return result
    '''

    def SAFE_QDB_FULL(self,xQuery,qparams,bypass_reconnect = False):
        if bypass_reconnect:
            return self.SAFE_QDB_FULL_PING(xQuery,qparams)
        else:
            try: 
                return self.SAFE_QDB_FULL_PING(xQuery,qparams)
            except pymysql.err.OperationalError:
                time.sleep(30)
                logger.Warn("DB Lost, reconnecting")
                self.reconnect()
                return self.SAFE_QDB_FULL(xQuery,qparams,True)


    def SAFE_QDB_FULL_PING(self,xQuery,qparams): 
        self.connection.ping(reconnect=True)
        sql = xQuery
        self.cursor.execute(sql,qparams)
        self.connection.commit()
        result = self.cursor.fetchall()
        return result

    def SAFE_QDB_FULL_ALT(self,xQuery,qparams):
        while True: #Gira finché il dato non viene salvato
            try:
                sql = xQuery
                self.cursor.execute(sql,qparams)
                result = self.cursor.fetchall()
                self.connection.commit()
                break
            except Exception as e:
                logger.Error(str(e) + "\nTRYING TO RECONNECT")
                time.sleep(60)
                try:
                    self.connection.ping(True)
                except Exception as er:
                    logger.Error(str(er) + "\nPLEASE WAIT FOR ESTABLISHED CONNECTION")
                    self.cursor = self.connection.cursor()
            else:
                raise e          
        return result

import psycopg2
import psycopg2.extras

class postgresql():
    def __init__(self,xip,xport,usr,pwd,dbname):
        self.xip = xip
        self.xport = xport
        self.usr = usr
        self.pwd = pwd
        self.dbname = dbname
        self.CONNECT()

    def CONNECT(self):
        self.connection = psycopg2.connect(host=self.xip,
                                          port=self.xport,
                                          user=self.usr,
                                          password=self.pwd,
                                          database=self.dbname,
                                          cursor_factory=psycopg2.extras.DictCursor)
        self.cursor = self.connection.cursor()

    def SAFE_QDB_FULL(self,xQuery,qparams): 
        sql = xQuery
        self.cursor.execute(sql,qparams)
        self.connection.commit()
        result = self.cursor.fetchall()
        return result
