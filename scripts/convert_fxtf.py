#-*- coding: utf-8 -*-

import argparse
import numpy as np
import pandas as pd
import datetime
import time

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

def makeDataset(data, s, k=1, mode=2, ratio_s=2.0):
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
        
        # SMA
        close = ohlc[-1]
        sma_size = [7, 13, 25]
        sma_dict = get_sma(close, sma_size)
        sma = np.vstack((sma_dict["sma07"], sma_dict["sma13"], sma_dict["sma25"]))

        # Labeling
        labels = labeling(close, s*ratio_s, k, mode)[0]
        
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
    df[["open", "high", "low", "close", "sma07", "sma13", "sma25", "volume","label1", "label2", "label3"]] = \
    df[["open", "high", "low", "close", "sma07", "sma13", "sma25", "volume","label1", "label2", "label3"]].astype(float)
    
    return df

def main(fpath, split, ks):
    """main script"""
    try:
        data = pd.read_csv(fpath, index_col=None)
        for k in ks:
            print("k:", k)
            res = makeDataset(data, split, k)
            res.to_csv(fpath.replace(".csv", "_k{0:03d}.csv".format(k)), index=False)
    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert an OHLC dataset to characteristics.")
    parser.add_argument('-i', action='store', dest='i', required=True, type=str)
    parser.add_argument('-split', action='store', dest='split', type=float)
    parser.add_argument('-k', action='store', dest='k', type=int, nargs="+")
    argmnt = parser.parse_args()

    print("start.")
    st = time.time()
    if argmnt.split is None:
        split = 0.003
    else:
        split = argmnt.split
    if argmnt.k is None:
        ks = [1, 2, 3, 4, 5, 10, 15, 30, 60, 120]
    else:
        ks = [k for k in argmnt.k]
    main(argmnt.i, split, ks)
    print("finished. Elapsed time: {0:.2f} sec.".format(time.time() - st))