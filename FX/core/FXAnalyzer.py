#-*- coding: utf-8 -*-
import time
import numpy as np
import pandas as pd
import datetime
from . import analyzefuncs as af
from . import datetimefuncs as dtf

class OHLCanalyzer(object):
    """
    User-defined analyzer of FX rates.
    In the beginning of analysis of FX data, we should calculate OHLC.
        O: open, H: high, L: low, C: colse.
    This class is used to insert OHLC to the initlal tables created by `SQLAnaforFX`.
    For real-time operation another class is to be used (not implemented yet).
    """
    def __init__(self, df):
        """
        Initialization
        A DataFrame object `df` which has (datetime=index, dateval, ask, bid) is given as a initialization parameter.
        """
        self._dtformat = "%Y-%m-%d %H:%M:%S"
        self._mins = [1, 5, 10, 15, 30, 60]
        self.DataFrame = df
        # print("Process timestamps...")
        self._process_timestamp()
        # print("Make bins...")
        self._make_bins()

    def _process_timestamp(self):
        """
        Process the timestamp for plotting
        """
        timestamps = list(self.DataFrame.index)
        timestamps_dt = [datetime.datetime.strptime(timestamps[ii], self._dtformat) for ii in range(len(timestamps))]
        self._timestamp_start = timestamps_dt[0]
        self._timestamps_ary = np.array([(timestamps_dt[ii]-timestamps_dt[0]).total_seconds() for ii in range(len(timestamps_dt))])

    def _make_bins(self):
        """
        Make bins for OHLC.
        """
        timestamp_ary = self._timestamps_ary.copy()
        self._time_edges = [np.arange(timestamp_ary[0], timestamp_ary[-1], n*60) for n in self._mins]
        self._datetimes = []
        self._is_weekdays = []
        for mm in range(len(self._mins)):
            time_edges = self._time_edges[mm] + self._mins[mm]*60
            days = time_edges  // 86400
            seconds = time_edges % 86400
            datetimes = np.array([self._timestamp_start + datetime.timedelta(days[ii], seconds[ii]) for ii in range(len(time_edges))])
            is_weekday = np.array([dtf.is_weekend(date) == False for date in datetimes])
            self._time_edges[mm] = self._time_edges[mm][is_weekday]
            self._datetimes.append(np.array([val.strftime(self._dtformat) for val in datetimes[is_weekday]]))
            self._is_weekdays.append(is_weekday)

    def __make_bins_slow(self):
        """
        Make bins for OHLC.
        This method takes much time.
        """
        timestamps = np.array(self.DataFrame.index)

        self._time_edges = [np.arange(self._timestamp_ary[0], self._timestamp_ary[-1], n*60) for n in self._mins]

        self._datetimes_start = []
        self._datetimes_end = []
        for mm in range(len(self._mins)):
            time_edges = self._time_edges[mm]
            starts = [""]  * len(time_edges)
            ends = [""]  * len(time_edges)
            for ii in range(len(time_edges)):
                if ii < len(time_edges)-1:
                    ind = (self._timestamps_ary>=time_edges[ii])&(self._timestamps_ary<=time_edges[ii+1])
                else:
                    ind = (self._timestamps_ary>=time_edges[ii])
                if sum(ind) != 0:
                    _ = timestamps[ind]
                    starts[ii] = _[0]
                    ends[ii] = _[-1]
            self._datetimes_start.append(starts)
            self._datetimes_end.append(ends)

    def calc_ohlc(self, minute=1):
        asks, bids = self.DataFrame["ask"].as_matrix(), self.DataFrame["bid"].as_matrix()
        index = self._mins.index(minute)
        self.asks_edge = af.get_ohlc(asks, self._timestamps_ary, self._time_edges[index])
        self.bids_edge = af.get_ohlc(bids, self._timestamps_ary, self._time_edges[index])
        self._datetime_edge = self._datetimes[index]

    def toDataFrame(self):
        ind_exist = (self.asks_edge.sum(axis=1) != 0)&(self.bids_edge.sum(axis=1) != 0)

        df_ask = pd.DataFrame(self.asks_edge[ind_exist], columns=["open", "high", "low", "close"])
        df_ask.index = self._datetime_edge[ind_exist]
        df_bid = pd.DataFrame(self.bids_edge[ind_exist], columns=["open", "high", "low", "close"])
        df_bid.index = self._datetime_edge[ind_exist]
        return df_ask, df_bid

class SMAanalyzer(object):
    def __init__(self):
        self._sma_size = [7, 13, 25]

    def calc_sma(self, df):
        """
        Calculate SMA trends.
        datetimes = df.index
        close = df["close"]
        """
        self.datetimes = df.index
        close_data = df["close"].as_matrix()
        self.sma_dict = af.get_sma(close_data, self._sma_size)

    def toDataFrame(self):
        colnames = ["sma{0:02d}".format(n) for n in self._sma_size]
        _ = [self.sma_dict[key] for key in colnames]
        data = np.zeros((len(colnames), len(_[0])))
        for ii in range(len(_)):
            data[ii] = _[ii]
        df = pd.DataFrame(data.transpose(), columns=colnames)
        df.index = self.datetimes
        return df
