#-*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import datetime
from .SQLBaseforFX import SQLBaseforFX

class SQLAnaforFX(SQLBaseforFX):
    """
    The class of SQLDB for FX.
    This class mainly has methods processing the table related to results of analysis (called "analysis tables"),
    which has the structure (datetime, open, high, low, close, etc.).
    """
    def __init__(self, *args, **kwargs):
        """
        Initialization
        In this process the analysis tables are not recreated.
        """
        super().__init__(*args, **kwargs)
        self.initialize_ana_tables()

    def initialize_ana_tables(self, recreate=False):
        """
        Initialize the analysis tables.
        If `recreate` is True, then the tables will be dropped and recreated.
        """
        self._mins = [1, 5, 10, 15, 30, 60]

        self._asktblnames = ["ask{0:02d}min".format(n) for n in self._mins]
        for tblname in self._asktblnames:
            self.maketable(tblname, "(datetime varchar(255), open real, high real, low real, close real)", recreate)

        self._bidtblnames = ["bid{0:02d}min".format(n) for n in self._mins]
        for tblname in self._bidtblnames:
            self.maketable(tblname, "(datetime varchar(255), open real, high real, low real, close real)", recreate)

    ############## OHLC data getting processing ##############
    def open(self, minute=1, ask_or_bid="ask"):
        """
        Return an array with open values.
        """
        return self.toDataFrame("{0}{1:02d}min".format(ask_or_bid, minute), colselect=["open"]).as_matrix()[:,0]

    def close(self, minute=1, ask_or_bid="ask"):
        """
        Return an array with close values.
        """
        return self.toDataFrame("{0}{1:02d}min".format(ask_or_bid, minute), colselect=["close"]).as_matrix()[:,0]

    def high(self, minute=1, ask_or_bid="ask"):
        """
        Return an array with high values.
        """
        return self.toDataFrame("{0}{1:02d}min".format(ask_or_bid, minute), colselect=["high"]).as_matrix()[:,0]

    def low(self, minute=1, ask_or_bid="ask"):
        """
        Return an array with close values.
        """
        return self.toDataFrame("{0}{1:02d}min".format(ask_or_bid, minute), colselect=["low"]).as_matrix()[:,0]

    ############## OHLC data insertion processing ##############
    def addOHLCRecordFromDataFrame(self, df, minute, bid_or_ask):
        """
        Add (, or insert) OHLC data from a DataFrame object `df` to the analysis table
        named "bidXXmin" or "askXXmin".
        `df` has the following structure:
            datetimes = df.index
            open = df["open"]
            high = df["high"]
            low = df["low"]
            close = df["close"]
        `minute` and `bid_or_ask` are used to select the table to insert data to.
            minute: the value in `self._mins`.
            bid_or_ask: "bid" or "ask".
        This method is used in case of making a test table after recording, etc., for real-time recording.
        """
        datetimes = list(df.index)
        opens = df["open"].as_matrix()
        highs = df["high"].as_matrix()
        lows = df["low"].as_matrix()
        closes = df["close"].as_matrix()
        dataset = [(datetimes[ii], opens[ii], highs[ii], lows[ii], closes[ii]) for ii in range(len(datetimes))]

        tblname = self._select_ana_table(minute, bid_or_ask)
        insert_sql = '''insert into {} (datetime, open, high, low, close) values (?,?,?,?,?)'''.format(tblname)
        res = self.executemany(insert_sql, dataset)

    def addOHLCRecord(self, dataset, minute, bid_or_ask):
        """
        Add (, or insert) a OHLC set (dt, open, high, low, close).
        dataset = (datetime, open, high, low, close).
        `minute` and `bid_or_ask` are used to select the table to insert data to.
            minute: the value in `self._mins`.
            bid_or_ask: "bid" or "ask".
        This method is used mainly for real-time recording.
        """
        tblname = self._select_ana_table(minute, bid_or_ask)
        insert_sql = '''insert into {} (datetime, open, high, low, close) values (?,?,?,?,?)'''.format(tblname)
        res = self.execute(insert_sql, dataset)

    def addSMARecordFromDataFrame(self, df, minute, bid_or_ask):
        """
        Add records realted to SMA.
        """
        datetimes = df.index
        colnames = df.columns
        tblname = self._select_ana_table(minute, bid_or_ask)

        res = self.execute("PRAGMA table_info({})".format(tblname))
        current_colnames = [row[1] for row in res]

        # Check the existence of columns named `colname` in `colnames`.
        for colname in colnames:
            if colname not in current_colnames:
                _ = self.addcolumn(tblname, colname, "real")

        # Update the table.
        data = df.as_matrix()
        setcols = ",".join(["{0} = ?".format(colname) for colname in colnames])
        update_sql = "update {0} set {1} where datetime = ?".format(tblname, setcols)
        dataset = [None]*len(datetimes)
        for ii in range(len(datetimes)):
            _ = list(data[ii])
            _.append(datetimes[ii])
            dataset[ii] = tuple(_)
        self.executemany(update_sql, dataset)

    def __addSMARecord(self, dataset, minute, bid_or_ask):
        """
        Add (, or insert) a OHLC set (dt, open, high, low, close).
        dataset = (datetime, open, high, low, close).
        `minute` and `bid_or_ask` are used to select the table to insert data to.
            minute: the value in `self._mins`.
            bid_or_ask: "bid" or "ask".
        This method is used mainly for real-time recording.

        (Under construction.)
        """
        tblname = self._select_ana_table(minute, bid_or_ask)
        insert_sql = '''update {0} set sma open, high, low, close) values (?,?,?,?,?)'''.format(tblname)
        res = self.execute(insert_sql, dataset)

    def AnaToDataFrame(self, minute, bid_or_ask, colselect=None):
        tblname = self._select_ana_table(minute, bid_or_ask)
        return self.toDataFrame(tblname, colselect)

    def _select_ana_table(self, minute, bid_or_ask):
        """
        Select the table named "{0}{1:02d}min".format(bid_or_ask, minute) .
        """
        if bid_or_ask == "ask":
            return self._asktblnames[self._mins.index(minute)]
        else:
            return self._bidtblnames[self._mins.index(minute)]
