#-*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import sqlite3
import os
import time
import datetime
from ..core.datetimefuncs  import datetime2timeInteger
from .SQLBase import SQLBase

class SQLBaseforFX(SQLBase):
    """
    The base class of SQLDB for FX.
    This class mainly has methods processing the "main" table,
    which has the structure (datetime, dateval, ask, bid).
    """
    def __init__(self, year_month=None, currencyPair="usdjpy", recreate=False):
        """
        Initialization
        If a database named `sef._dbname` doesn't exist, then it will be created first.
        If `recreate` is true, then the database will be dropped and recreated.
        """
        self._currencyPair = currencyPair

        if year_month is None:
            now = datetime.datetime.now()
            self._dbname = "../../data/{2}_{0}{1:02d}.db".format(now.year, now.month, self._currencyPair)
        else:
            self._dbname = "../../data/{1}_{0}.db".format(year_month, self._currencyPair)
        super().__init__(self._dbname, recreate)

        # Make the main table.
        self._tblmain = "main"
        self._mainstruct = "(datetime varchar(255), dateval int, ask real, bid real)"
        self.maketable(self._tblmain, self._mainstruct)

        self._dtformat = "%Y-%m-%d %H:%M:%S"
        self._DataFrameIndexStr = "datetime"
        
    ############## FX data insertion processing ##############
    def addFXRecordsFromFolder(self, fldrpath):
        """
        Add (, or insert) the records in the all file `fpath` which has the following datasets:
            datetime (string), ask (float), bid (float).
        The structure of the main table is:
            (datetime varchar(255), dateval int, ask real, bid real)
        This method is used in case of making a test table after recording, etc., for real-time recording.
        """
        filelist = os.listdir(fldrpath)
        print("Start insertion of the data in folder: {}".format(fldrpath))
        st = time.time()
        for fname in filelist:
            _ = self.addFXRecordsFromFile(os.path.join(fldrpath, fname))
        print("Finished. Elapsed time: {0:.2f} sec.".format(time.time()-st))

    def addFXRecordsFromFile(self, fpath):
        """
        Add (, or insert) the records in the file `fpath` which has the following datasets:
            datetime (string), ask (float), bid (float).
        The structure of the main table is:
            (datetime varchar(255), dateval int, ask real, bid real)
        This method is used in case of making a test table after recording, etc., for real-time recording.
        """
        _ = pd.read_csv(fpath, index_col=0)
        data = _.as_matrix()
        timestamps = list(_.index)
        dates = [datetime2timeInteger(datetime.datetime.strptime(s, self._dtformat))
                 for s in timestamps]
        dataset = [(timestamps[ii], dates[ii], data[ii, 0], data[ii,1]) for ii in range(len(dates))]

        insert_sql = '''insert into {} (datetime, dateval, ask, bid) values (?,?,?,?)'''.format(self._tblmain)
        return self.executemany(insert_sql, dataset)

    def addFXRecord(self, dt, ask, bid):
        """
        Add (, or insert) a record (dt, dt->dateval, ask, bid).
        The structure of the main table is:
            (datetime varchar(255), dateval int, ask real, bid real)
        This method is used mainly for real-time recording.
        """
        datetimestr = dt.strftime(self._dtformat)
        date = datetime2timeInteger(dt)
        dataset = (datetimestr, date, ask, bid)
        insert_sql = '''insert into {} (datetime, dateval, ask, bid) values (?,?,?,?)'''.format(self._tblmain)
        res = self.execute(insert_sql, dataset)
