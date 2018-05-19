#-*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import sqlite3
import os

class SQLBase(object):
    """
    The base class of SQLDB to provide the methods make SQL queries easy.
    """
    def __init__(self, dbname, recreate=False):
        """
        Initialization
        If a database named `sef._dbname` doesn't exist, then it will be created first.
        If `recreate` is true, then the database will be dropped and recreated.
        """
        self._dbname=dbname
        if os.path.exists(self._dbname) and recreate is True:
            os.remove(self._dbname)
        if not os.path.exists(self._dbname):
            try:
                conn = sqlite3.connect(self._dbname)
                conn.close()
            except Exception as e:
                print(e)

        self._tblmain = ""
        self._DataFrameIndexStr = ""

    ############## Database processing ##############
    def maketable(self, tblname, structure, recreate=False):
        """
        Make a table named `tblname` with the structure `structure`.
        If `recreate` is true, then the table will be dropped and recreated.
        """
        conn = sqlite3.connect(self._dbname)
        c = conn.cursor()
        try:
            c.execute("select name from sqlite_master where type='table'")
            table_names = [row[0] for row in c.fetchall()]
            if tblname not in table_names:
                create_table = '''create table {0} {1}'''.format(tblname, structure)
                c.execute(create_table)
                conn.commit()
            elif recreate is True:
                drop_sql = '''drop table {}'''.format(tblname)
                c.execute(drop_sql)
                conn.commit()
                create_table = '''create table {0} {1}'''.format(tblname, structure)
                c.execute(create_table)
                conn.commit()
        except Exception as e:
            print("Error:", e)
        conn.close()

    def showtablenames(self):
        res = self.execute("select name from sqlite_master where type='table'")
        return [name[0] for name in res]

    def execute(self, sql_txt, value=None):
        """
        Execute a SQL query `sql_txt`.
        """
        res = None
        conn = sqlite3.connect(self._dbname)
        c = conn.cursor()
        try:
            if value is None:
                c.execute(sql_txt)
            else:
                c.execute(sql_txt, value)
            res = c.fetchall()
            conn.commit()
        except Exception as e:
            print("Error:", e)
        conn.close()
        return res

    def executemany(self, sql_txt, value):
        """
        Execute a SQL query `sql_txt` with many datasets `value`.
        """
        res = None
        conn = sqlite3.connect(self._dbname)
        c = conn.cursor()
        try:
            c.executemany(sql_txt, value)
            res = c.fetchall()
            conn.commit()
        except Exception as e:
            print("Error:", e)
        conn.close()
        return res

    def addcolumn(self, tblname, colname, coltype):
        """
        Add a column with the name `colname` and the type `coltype` to the table `tblname`.
        All the input parameters have the "str" type.
        """
        res = self.execute("PRAGMA table_info({})".format(tblname))
        colnames = [row[1] for row in res]
        if colname in colnames:
            print("{} has been already added.".format(colname))
            return
        alter_sql = "alter table {0} add column {1} {2}".format(tblname, colname, coltype)
        res = self.execute(alter_sql)

    def deletecolumn(self, tblname, colname):
        """
        Delete at column with the name `colname`.
        In fact SQLite3 doesn't have the straightforward way to delete any columns.
        Here the column will be deleted through the following steps:
            1. Make a new table.
            2. Copy the records except `colname` data from the
               table `tblname` to the new one.
            3. Drop the table `tblname`.
            4. Rename the new table after `tblname`.
        """

        # Check the existence of `colname` and extract the structure of `tblname`.
        res = self.execute("PRAGMA table_info({})".format(tblname))
        colnames = []
        coltypes = []
        ind_exist = False
        for row in res:
            if row[1] != colname:
                colnames.append(row[1])
                coltypes.append(row[2])
            else:
                ind_exist = True
                break
        if ind_exist == False:
            print("No existence: {}".format(colname))
            return

        # 1. Make.
        cols = [colnames[ii] + " " + coltypes[ii] for ii in range(len(colnames))]
        structure = "(" + ",".join(cols) + ")"
        self.maketable("newtable", structure)

        # 2. Copy.
        coltargets = ",".join(colnames)
        colins = ",".join(["?"]*len(colnames))
        select_sql = '''select {1} from {0}'''.format(tblname, coltargets)
        res = self.execute(select_sql)
        insert_sql = '''insert into newtable ({1}) values ({2})'''.format(tblname, coltargets, colins)
        res = self.executemany(insert_sql, res)

        # 3. Drop.
        drop_sql = '''drop table {}'''.format(tblname)
        res = self.execute(drop_sql)

        # 4. Rename.
        rename_sql = '''alter table newtable rename to {0}'''.format(tblname)
        res = self.execute(rename_sql)

    ############## Data conversion ##############
    def toDataFrame(self, tblname=None, colselect=None):
        """
        Convert the table `tblname` to a DataFrame object.
        The default table to convert is `self._tblmain`.
        """
        if tblname is None:
            tblname = self._tblmain

        # Get column names except "DataFrameIndexStr".
        res = self.execute("PRAGMA table_info({})".format(tblname))
        colnames = []
        is_indexstr = False
        for row in res:
            if row[1] != self._DataFrameIndexStr :
                colnames.append(row[1])
            else:
                is_indexstr = True
        if len(colnames) == 0:
            raise ValueError("No columns as data.")
        if colselect is not None:
            colnames = colselect[:]
        coltargets = ",".join(colnames)

        # Select all the records except "DataFrameIndexStr" and make a DataFrame object.
        select_sql = '''select {1} from {0}'''.format(tblname, coltargets)
        _ = self.execute(select_sql)
        data = np.array(_)
        df = pd.DataFrame(data, columns=colnames)

        # If "DataFrameIndexStr" data are in the target table, then they are used as the index of  the DataFrame.
        if is_indexstr == True:
            select_sql = '''select {1} from {0}'''.format(tblname, self._DataFrameIndexStr)
            _ = self.execute(select_sql)
            nowtimes = [n[0] for n in _]
            df.index = nowtimes

        return df

    def toCSV(self, savepath, tblname=None, colselect=None):
        """
        Save the table `tblname` to the file `savepath`.
        """
        df = self.toDataFrame(tblname, colselect)
        df.to_csv(savepath)
