#-*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import json
import datetime
# import importlib

# spam_spec = importlib.util.find_spec("pandas_datareader")
# found = spam_spec is not None
# if found is True:
#     import pandas_datareader as pdr

def getFXRateWithYQL(pair="USDJPY"):
    """
    Get FX rate from via YQL.
    See: http://www.yoheim.net/blog.php?q=20160807 (in Japanese)

    <Input>
        pair: currency pair code
    <Output>
        result: (json object)
    """
    # URL of API for YQL
    url = "https://query.yahooapis.com/v1/public/yql"
    params = {
        "q": 'select * from yahoo.finance.xchange where pair in ("{}")'.format(pair),
        "format": "json",
        "env": "store://datatables.org/alltableswithkeys"
    }
    # Convert the contents of a dict object to URL.
    url += "?" + urllib.parse.urlencode(params) 
    
    # Send a quary and receive the result.
    res = urllib.request.urlopen(url)

    # Convert the result to a json object.
    result = json.loads(res.read().decode('utf-8'))

    return result

def get_FX_from_gaitame(currencyPairCode="USDJPY"):
    """
    Get ask/bid from "Gaitame Online".
    See: http://qiita.com/chromabox/items/a1323225bae146c80bec (in Japanese)
    
    <Caution>
        Gaitame Online updates the rates every 1 sec, 
        but we should take them every more than 5 sec as those who live on the Internet.
    
    <Input>
        currencyPairCode: currency pair code
    
    <Output>
        nowtime: The datetime of request
        ask: ask rate
        bid: bid rate
        is_gotten: True = success in getting the rates
    """

    url = "http://www.gaitameonline.com/rateaj/getrate"
    nowtime = datetime.datetime.now()
    try:
        res = urllib.request.urlopen(url)
        quotes = json.loads(res.read().decode('utf-8'))["quotes"]
        for quo in quotes:
            if quo["currencyPairCode"] == currencyPairCode: 
                try:
                    ask = float(quo["ask"])
                    bid = float(quo["bid"])
                    is_gotten = True
                except:
                    ask = -1.0; bid = -1.0; is_gotten = False
                break
    except Exception as e:
        print(nowtime, e)
    return nowtime, ask, bid, is_gotten

if __name__ == "__main__":
    print(getFXRateWithYQL.__doc__)
    print(getFXRateWithYQL())

    print(get_FX_from_gaitame.__doc__)
    print(get_FX_from_gaitame())
