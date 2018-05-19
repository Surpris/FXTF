# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import urllib.request
import json
import time
import datetime
from .datetimefuncs import is_weekend
from .rategetter import *

def downloadFXdata(update_time = 60, update_count = 20, savefldrpath=None):
    if savefldrpath is None:
        savefldrpath = "../data/"
    savenow = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    savepath = savefldrpath + "fxdata_{0}.csv".format(savenow)

    st = time.time()
    nowtimes = []
    fx = []
    count = 0
    nowtime = datetime.datetime.now()
    isholiday = is_weekend(nowtime)
    if isholiday:
        print(nowtime.strftime("%Y%m%d_%H%M%S"), "holiday.")
        print("Wait until holiday ends...")
    while True:
        try:
            if not isholiday:
                nowtime, ask, bid, is_gotten = get_FX_from_gaitame()
                if is_weekend(nowtime):
                    print("holiday.")
                    print("Wait until holiday ends...")
                    isholiday = True
                    if len(nowtimes) != 0:
                        df = ToDataFrame(nowtimes, fx)
                        df.to_csv(savepath)
                    nowtimes = []
                    fx = []
                    count = 0
                    savenow = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    savepath = savefldrpath + "fxdata_{0}.csv".format(savenow)
                    time.sleep(60)
                    continue
            else:
                if not is_weekend(datetime.datetime.now()):
                    print("holiday ends.")
                    savenow = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    savepath = "../data/fxdata_{0}.csv".format(savenow)
                    isholiday = False
                    continue
                else:
                    time.sleep(60)
                    continue
            if is_gotten == False:
                print(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), "Failure in getting FX data.")
                time.sleep(5.0)
                continue
            nowtimes.append(nowtime.strftime("%Y-%m-%d %H:%M:%S"))
            fx.append([ask, bid])
            time.sleep(5.0)
            if time.time() - st > update_time:
                st = time.time()
                df = ToDataFrame(nowtimes, fx)
                df.to_csv(savepath)
                count += 1
                if count >= update_count:
                    nowtimes = []
                    fx = []
                    savenow = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    savepath = savefldrpath + "fxdata_{0}.csv".format(savenow)
                    count = 0
        except Exception as e:
            print(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
            print(e)
            df = ToDataFrame(nowtimes, fx)
            df.to_csv(savepath)
            print("Wait for 1 minute...")
            time.sleep(30) # Wait for 30 seconds if failure.
            nowtimes = []
            fx = []
            savenow = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            savepath = savefldrpath + "fxdata_{0}.csv".format(savenow)

if __name__ == "__main__":
    print("{}: Downloading...".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
    downloadFXdata()
