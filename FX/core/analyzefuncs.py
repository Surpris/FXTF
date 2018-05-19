#-*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import datetime

def get_ohlc(fxdata, timestamp, time_edge=None):
    """
    Calculate OHLC.
    O=open, H=high, L=low, c=close

    <Input>
        fxdata: FX data
        timestamp: timestamp
        time_edge: bin edge

    <Output>
        ohlc: OHLC data (len(time_edge), 4) array
    """
    ### Check validation of time_edge
    if time_edge is None:
        edges = np.arange(timestamp[0], timestamp[-1], 60)
    else:
        edges = time_edge.copy()

    ### Calculate
    ohlc = np.zeros((len(edges), 4), dtype=float)
    for ii in range(len(edges)):
        if ii < len(edges)-1:
            ind = (timestamp>=edges[ii])&(timestamp<=edges[ii+1])
        else:
            ind = (timestamp>=edges[ii])
        if ind.sum() != 0:
            _ = fxdata[ind]
            ohlc[ii] = np.array([_[0], _.max(), _.min(), _[-1]])
    return ohlc

def get_sma(close_data, sma_size=[7, 13, 25]):
    """
    Calculate Simple Moving Average (SMA).
    < Input >
        close_data: close-data array
        sma_size: the size of SMA
    < Output >
        sma_dict: SMA dictionary object
    """
    if type(close_data) not in [list, np.ndarray]:
        raise TypeError
    elif type(close_data) == list:
        data = np.array(close_data)
    else:
        data = close_data.copy()

    sma_dict = dict()
    for size in sma_size:
        key = "sma{0:02d}".format(size)
        sma = [data[max(0, ii-size+1):ii+1].mean() for ii in range(len(data))]
        sma_dict[key] = sma
    return sma_dict

def labeling(M, s, k=1, mode=1):
    """
    Label each value of `M`.
    Labeling follows the below rule:
        * Label 0 (higher):  $M(n+k) - M(n) > s$
        * Label 1 (lose)  : $|M(n+k) - M(n)| < s$
        * Label 2 (lower) :  $M(n+k) - M(n) < -s$
    If a value cannot be labeled for some reasons (e.g. the earlier data are missing),
    they should be set to 1 (lose).

    < Input >
        M: value array to label
        k: step
        s: criterion
        mode: 1=return a 1D array, 2=return a 2D array
    """
    if mode == 1:
        diff = M[k:] - M[:-k]
        output_diff = np.zeros_like(M)
        output_diff[:-k] = diff[:]

        label = np.ones_like(diff)
        label[diff>s] = 0
        label[diff<-s] = 2

        output = np.ones_like(M)
        output[:-k] = label[:]
        return output.copy(), output_diff.copy()
    else:
        diff = M[k:] - M[:-k]
        output_diff = np.zeros_like(M)
        output_diff[:-k] = diff[:]

        label1 = np.zeros((k, 3))
        label1[:, 1] = 1
        label2 = np.zeros((len(diff), 3))
        label2[diff>s, 0] = 1
        label2[np.abs(diff)<=s, 1] = 1
        label2[diff<-s, 2] = 1
        return np.vstack((label2, label1)), output_diff.copy()

def timeseries(M, k=1, size_limit=1e7):
    """
    Make an array with k-sequential time series.
    < Input >
        M: value array
        k: the size of time series
    """
    if k< 1:
        raise ValueError("k must be >=1.")
    elif k == 1:
        return M
    elif (len(M)-k)*k > size_limit:
        raise ValueError("(len(M)-k)*k > {}.".format(size_limit))
    else:
        output = np.zeros((len(M), k))
        # First k-1 rows
        for ii in range(k-1):
            _ = M[0] * np.ones(k)
            if ii > 0:
                _[-ii:] = M[1:ii+1]
            output[ii] = _.copy()
        # Other rows
        for ii in range(k-1, len(M)):
            output[ii] = M[ii-k+1:ii+1]
    return output.copy()

def makeDataset(data, s, k=1, mode=2):
    """
    Extract and return the following dataset as DataFrame: 
        * OHLC
        * SMA (7, 13 25)
        * Volume
        * Label by labeling (vector type)
    
    Some data from the beginning and from the end of week are removed
    since they are not appropreate to use as the characteristics.
    
    Each row of the input data has the following dataset:
    [date, time, open, high, low, close, volume]
    """
    
    ### Separate the dataset by each week.
    # Make a list of weekdays' No.
    date_weekdays = []
    datetime_fmt = "%Y.%m.%d %H:%M"
    for date_t, time_t in zip(data["date"], data["time"]):
        datetime_str = date_t + " " + time_t
        datetime_t = datetime.datetime.strptime(datetime_str, datetime_fmt)
        date_weekdays.append(datetime_t.weekday())
    date_weekdays = np.array(date_weekdays)

    # Differentiate `date_weekdays`.
    date_wds_diff = np.diff(date_weekdays)
    ind_weekdayends = np.where(date_wds_diff == -4)[0]

    # Separation.
    inds = np.concatenate(([-1], ind_weekdayends, [len(data)-1]))
    weeks = []
    data_array = data.as_matrix()
    for ii in range(len(inds)-1):
        weeks.append(data_array[inds[ii]+1:inds[ii+1]+1].copy())
    
    ### Process and remove.
    buff = None
    for week in weeks:
        date_time = week.transpose()[:2]
        ohlc = week.transpose()[2:6]
        volume = week.transpose()[-1]
        close = ohlc[-1]
        
        # SMA
        sma_size = [7, 13, 25]
        sma_dict = get_sma(close, sma_size)
        sma = np.vstack((sma_dict["sma07"], sma_dict["sma13"], sma_dict["sma25"]))
        
        # Labeling
        labels = labeling(close, s, k, mode)[0]
        
        # Stacking
        buffs = np.vstack((date_time, ohlc, sma, volume, labels.transpose())).transpose().copy()
        
        # Remove
        sma_size.append(k)
        nbr_remove = max(sma_size)
        buffs = buffs[nbr_remove:]
        buffs = buffs[:-nbr_remove]
        
        if buff is None:
            buff = buffs
        else:
            buff = np.vstack((buff, buffs))
    
    # Convert into DataFrame
    idx = ["date", "time", 
           "open", "high", "low", "close", 
           "sma07", "sma13", "sma25", "volume",
           "label1", "label2", "label3"]
    df = pd.DataFrame(buff, columns=idx)
    
    return df
