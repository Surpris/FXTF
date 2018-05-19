# -*- coding: utf-8 -*-
from keras.models import Sequential
import numpy as np

class backtest(object):
    """
    FX backtest class.
    """
    def __init__(self, model, FXdata, FXtechIndex, tau, spread=0.01,
                 prob_threshold=0.75, initial_fund=100000,
                 nbr_of_positions=1000):
        """
        Initialization of this class.
        model           : the learned model (keras.models.Sequential).
        FXdata          : ask and bid data. (numpy.ndarray).
        FXtechIndex     : FX technical indices (numpy.ndarray).
                          This object must have a dataset with the same format
                          as that of the training dataset.
        tau             : time interval for prediction (int).
        spread          : spread (float / double).
        prob_threshold  : threshold to probability (float / double).
        initial_fund    : initial funding (int).
        nbr_of_positions: # of positions (int).
        """
        self.__model = model
        self.__data = FXdata
        self.__tech = FXtechIndex
        self.__tau = tau
        self.__spread = spread
        self.__prob_threshold = prob_threshold
        self.__initial_fund = initial_fund
        self.__final_fund = None
        self.__nbr_of_positions = nbr_of_positions
        self.__fund_history = None
        ## `answer_type` is the format of the result of prediction
        self.__answer_type = ["high", "lose", "low"]
        self.__status_type = ["long", "wait", "short"]
        self.__flag = None

        self.__fx = None
        self.__wait_count = None
        self.__status = None

    def run(self, stop=100, verbose=0):
        """
        Execute a backtest.
        """
        self.__verbose = verbose
        self.__fund_history = [self.__initial_fund]
        self.__fx = 0
        self.__flag = [1]
        self.__wait_count = 0
        self.__status = self.__status_type[1]
        self.__final_fund = self.__initial_fund + 0
        try:
            for ii in range(len(self.__tech)):
                if ii > stop-1:
                    break
                if self.__status == self.__status_type[1]:
                    ## Predict
                    ans = self.__predict(self.__tech[ii])
                    ## Ask / Wait / Bid
                    self.__order(ans, self.__data[ii])
                else:
                    self.__wait_count += 1
                    if self.__wait_count == self.__tau:
                        ## Settle the current trade
                        self.__settle(self.__data[ii])
                        self.__wait_count = 0
                self.__flag.append(self.__status_type.index(self.__status))
                self.__fund_history.append(self.__final_fund)
                if self.__verbose == 1:
                    print(ii+1, self.__fx, self.__data[ii], self.__final_fund, self.__status)

        except KeyboardInterrupt:
            print("Quit running by KeyboardInterrupt.")
        self.__compile_history()

    def __predict(self, characteristics):
        """
        Return the answer according to prediction.
        characteristics: numpy.ndarray object to predict the result with.
        """
        if characteristics.ndim == 1:
            data = characteristics[None, :]
        elif characteristics.ndim == 2:
            data = characteristics[:, :, None]
        else:
            raise ValueError

        res = self.__model.predict_proba(data, verbose=0)[0]
        if self.__verbose == 1:
            print(res)
        high_prob = res >= self.__prob_threshold
        ## TODO: improve the following context for flexibility.
        if high_prob.sum() != 0:
            return self.__answer_type[(list(res)).index(max(res))]
        else:
            return self.__answer_type[1]

    def __order(self, answer, data):
        """

        answer: the answer according to prediction
        data  : FX data (numpy.ndarray([ask, bid]))
        """
        if answer == self.__answer_type[0]: # long
            self.__fx = data[0] * self.__nbr_of_positions
            self.__status = self.__status_type[0]
        elif answer == self.__answer_type[2]: # short
            self.__fx = data[1] * self.__nbr_of_positions
            self.__status = self.__status_type[2]
        else:
            self.__fx = 0
            self.__status = self.__status_type[1]

    def __settle(self, data):
        """
        """
        if self.__status == self.__status_type[0]: # long
            sub = data[1] * self.__nbr_of_positions - self.__fx
        elif self.__status == self.__status_type[2]: # short
            sub = self.__fx - data[0] * self.__nbr_of_positions
        else:
            raise ValueError
        self.__final_fund += sub
        self.__fx = 0
        self.__status = self.__status_type[1]

    def __compile_history(self):

        self.__history = {"fund_history":self.__fund_history,
                          "initial_fund":self.__initial_fund,
                          "flag":self.__flag}
    def get_result(self):
        return self.__history
