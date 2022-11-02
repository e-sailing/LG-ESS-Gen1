#!/usr/bin/env python3

import mysql.connector
import datetime
import sqlite3
import sys
from sqlite3 import Error

MariaDBuser="user"
MariaDBpassword="user"

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
        user=MariaDBuser,
        password=MariaDBpassword,
        db="Haus",
        host="localhost")
    except mysql.connector.Error as e:
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

def lastDateMySQLmonth():
    try:
        connMySQL = mysql.connector.connect(
        user=MariaDBuser,
        password=MariaDBpassword,
        db="Haus",
        host="localhost")
    except mysql.connector.Error as e:
        print("Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
        
    cursorMySQL = connMySQL.cursor()
    cursorMySQL.execute('SELECT Datum FROM PVLGmonth ORDER BY Datum DESC LIMIT 1')
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
        user=MariaDBuser,
        password=MariaDBpassword,
        #db="Haus",
        host="localhost")
    except mysql.connector.Error as e:
        print("Error connecting to MariaDB Platform: {"+str(e.errno)+"}")
        sys.exit(1)

    cursorMySQL = connMySQL.cursor()
    cursorMySQL.execute("CREATE DATABASE IF NOT EXISTS Haus")

    try:
        connMySQL = mysql.connector.connect(
        user=MariaDBuser,
        password=MariaDBpassword,
        db="Haus",
        host="localhost")
    except mysql.connector.Error as e:
        print("Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    cursorMySQL = connMySQL.cursor()
    cursorMySQL.execute("CREATE TABLE IF NOT EXISTS `PVLG` (`Datum` datetime NOT NULL,`pv_power` float NOT NULL,`batt_charge` float NOT NULL,`batt_soc` float NOT NULL,`load_consumption_sum` float NOT NULL,`grid_feed_in` float NOT NULL,`pv_generation_sum` float NOT NULL,`load_power` float NOT NULL,`batt_discharge` float NOT NULL,`pv_direct_consumption` float NOT NULL,`grid_power_purchase` float NOT NULL,PRIMARY KEY (`Datum`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT")
   
    cursorMySQL.execute("CREATE TABLE IF NOT EXISTS `PVLGmonth` (`Datum` datetime NOT NULL,`pv_power` float NOT NULL,`pv_direct_consumption` float NOT NULL,`batt_charge` float NOT NULL,`batt_discharge` float NOT NULL,`grid_power_purchase` float NOT NULL,`grid_feed_in` float NOT NULL,PRIMARY KEY (`Datum`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT")

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

def insertintodbmonth(connSqlite,sql,connMySQL):
    """
    Query all rows in the tasks table
    :param connSqlite: the Connection object
    :return:
    """
    curSqlite = connSqlite.cursor()
    curSqlite.execute(sql)

    rows = curSqlite.fetchall()
    print('selectdb PVLGmonth rows\n',rows)

    cursorMySQL = connMySQL.cursor()
    print('insert rows\n')

    for row in rows:
        print(row[1],str(row[1]))

        sql = "INSERT INTO PVLGmonth (Datum,pv_power,pv_direct_consumption,batt_charge,batt_discharge,grid_power_purchase,grid_feed_in) "
        sql += "VALUES ('"+str(row[0])+"',"
        sql += str(row[1])+","
        sql += str(row[2])+","
        sql += str(row[3])+","
        sql += str(row[4])+","
        sql += str(row[5])+","
        sql += str(row[6])+")"
        print('selectdb insert:\n',sql)
        cursorMySQL.execute(sql)
        connMySQL.commit()
		
		

def main():
    #Usage: python3 copyDB_LG.py /media/RAM
    try:
        database = sys.argv[1]+"/ems_DEU.db"
    except IndexError:
        database = r"/media/RAM/ems_DEU.db"
        #raise SystemExit(f"Usage: {sys.argv[0]} <path to database>")
    
    print(database)

    # create a database connection
    connMySQL = selectdb()
    connSqlite = create_connection(database)
    with connSqlite:
        insertintodb(connSqlite,"SELECT * FROM tbl_record_quarter WHERE time_local > "+lastDateMySQL(),connMySQL)

    sql2="\
       SELECT \
       time_local,\
       sum(pv_power_energy) as pv_power_energy,\
       sum(pv_direct_consumption_energy) as pv_direct_consumption_energy,\
       sum(batt_charge_energy) as batt_charge_energy,\
       sum(batt_discharge_energy) as batt_discharge_energy,\
       sum(grid_power_purchase_energy) as grid_power_purchase_energy,\
       sum(grid_feed_in_energy) as grid_feed_in_energy\
       FROM tbl_record_month"
    sql2b = " Group By time_local"
    with connSqlite:
        insertintodbmonth(connSqlite,sql2+" WHERE time_local > "+lastDateMySQLmonth()+sql2b,connMySQL)

if __name__ == '__main__':
    main()


