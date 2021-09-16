#!/usr/bin/env python3

import mysql.connector
import datetime
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    connSqlite = None
    try:
        connSqlite = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return connSqlite

def select(connSqlite,sql):
    """
    Query all rows in the tasks table
    :param connSqlite: the Connection object
    :return:
    """
    curSqlite = connSqlite.cursor()
    curSqlite.execute(sql)

    rows = curSqlite.fetchall()

    for row in rows:
        print(row)

def lastDateMySQL():
    try:
        connMySQL = mysql.connector.connect(
        user="root",
        password="teslalogger",
        db="Haus",
        host="localhost")
    except MySQLdb.Error as e:
        print("Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
        
    cursorMySQL = connMySQL.cursor()
    cursorMySQL.execute('SELECT Datum FROM PVLG ORDER BY Datum DESC LIMIT 1')
    myresult = cursorMySQL.fetchall()
    if len(myresult) == 1:
        dtv = myresult[0][0]
        print('lastDateMySQL gefunden',dtv)
        dt = dtv.strftime('%Y%m%d%H%M%S')
    else:
        dt="20001010000000"
    
    print('lastDateMySQL Ergebnis',dt)
    return dt
    
def selectdb():
    try:
        connMySQL = mysql.connector.connect(
        user="user",
        password="user",
        #db="Haus",
        host="localhost")
    except MySQLdb.Error as e:
        print("Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    cursorMySQL = connMySQL.cursor()
    cursorMySQL.execute("CREATE DATABASE IF NOT EXISTS Haus")

    try:
        connMySQL = mysql.connector.connect(
        user="user",
        password="user",
        db="Haus",
        host="localhost")
    except MySQLdb.Error as e:
        print("Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    cursorMySQL = connMySQL.cursor()
    cursorMySQL.execute("CREATE TABLE IF NOT EXISTS `PVLG` (`Datum` datetime NOT NULL,`pv_power` float NOT NULL,`batt_charge` float NOT NULL,`batt_soc` float NOT NULL,`load_consumption_sum` float NOT NULL,`grid_feed_in` float NOT NULL,`pv_generation_sum` float NOT NULL,`load_power` float NOT NULL,`batt_discharge` float NOT NULL,`pv_direct_consumption` float NOT NULL,`grid_power_purchase` float NOT NULL,PRIMARY KEY (`Datum`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT")
    return connMySQL

def insertintodb(connSqlite,sql,connMySQL):
    """
    Query all rows in the tasks table
    :param connSqlite: the Connection object
    :return:
    """
    curSqlite = connSqlite.cursor()
    curSqlite.execute(sql)

    rows = curSqlite.fetchall()
    print('selectdb rows\n',rows)

    cursorMySQL = connMySQL.cursor()

    for row in rows:
        print(row[1],str(row[1]))

        sql = "INSERT INTO PVLG (Datum,pv_power,batt_charge,batt_soc,load_consumption_sum,grid_feed_in, pv_generation_sum ,load_power,batt_discharge,pv_direct_consumption,grid_power_purchase) "
        sql += "VALUES ('"+str(row[1])+"',"
        sql += str(row[3]/4)+","
        sql += str(row[7]/4)+","
        sql += str(int(row[11]))+","
        sql += str(row[22])+","
        sql += str(row[14]/4)+","
        sql += str(row[21])+","
        sql += str(row[18]/4)+","
        sql += str(row[9]/4)+","
        sql += str(row[5]/4)+","
        sql += str(row[12]/4)+")"
        print('selectdb insert:\n',sql)
        cursorMySQL.execute(sql)
        connMySQL.commit()

def main():
    database = r"/media/RAM/ems_DEU.db"

    # create a database connection
    connMySQL = selectdb()
    connSqlite = create_connection(database)
    with connSqlite:
        insertintodb(connSqlite,"SELECT * FROM tbl_record_quarter WHERE time_local > "+lastDateMySQL(),connMySQL)

if __name__ == '__main__':
    main()


