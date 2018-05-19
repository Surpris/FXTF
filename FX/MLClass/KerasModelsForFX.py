#-*- coding: utf-8 -*-
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers import LSTM
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import *
from keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
import numpy as np
import time
from ..core import analyzefuncs as af
import copy

layers = {"Dense":Dense, "LSTM":LSTM}
activations = ["tanh", "relu", "softmax", "sigmoid", "softmax"]
activations_advanced = {"LeakyReLU":LeakyReLU,
                                     "PReLU":PReLU,
                                     "ELU":ELU}

class KerasModelsForFX(object):
    def __init__(self, input_shape, output_shape, layers_info, compile_info):
        """
        layer_info = {layer_type:str,
                            layer_size:int,
                            activation_type:str,
                            dropout:float,
                            batchnormalization:boolean,
                            kwargs:dict}
        layers_info = list of layer_info
        """
        self._input_shape = input_shape
        self._output_shape = output_shape
        self._layers_info = layers_info
        self._compile_info = compile_info

    def _create_model(self):
        """
        Create a model which has layers described in `layers_info`.
        """
        # Initialize a model.
        model = Sequential()

        # The first layer = the input layer.
        model = self._add_layer(model, self._layers_info[0], True)

        # Intermediate layers.
        if len(self._layers_info) > 2:
            for layer_info in self._layers_info[1:-1]:
                model = self._add_layer(model, layer_info)

        # The last layer = the output layer.
        model = self._add_layer(model, self._layers_info[-1], False, True)

        # Compile.
        model.compile(loss=self._compile_info["loss"],
            optimizer=self._compile_info["optimizer"],
            metrics=self._compile_info["metrics"])

        return model

    def _add_layer(self, model, layer_info, is_input=False, is_output=False):
        """
        Add a layer to `model`.

        < Input >
        model: Sequential
        layer_info = {layer_type:str,
                            layer_size:int,
                            activation_type:str,
                            dropout:float,
                            batchnormalization:boolean,
                            kwargs:dict}
        is_input: boolean
        is_output: boolean

        < Output >
        model: Sequential
        """
        layer = layers[layer_info["layer_type"]]
        size = layer_info["layer_size"]
        batchnormalization = layer_info["batchnormalization"]
        activation = layer_info["activation_type"]
        dropout = layer_info["dropout"]
        if is_input:
            model.add(layer(size, input_shape=self._input_shape))
        elif is_output:
            model.add(layer(size, output_shape=self._output_shape))
        else:
            model.add(layer(size))
        if batchnormalization is True:
            model.add(BatchNormalization())
        if activation is not None and isinstance(activation, str):
            if activation in activations:
                model.add(Activation(activation))
            else:
                model.add(activations_advanced[activation]())
        if is_output:
            return model
        else:
            if dropout is not None and type(dropout) in [int, float, np.int32, np.float32]:
                model.add(Dropout(dropout))
            return model

    def train(self, X, close, s=0.01, ks=1, iter_epochs=1, **kwargs):
        """
        Create len(ks)*len(iter_epochs) models and train them with a dataset (X, y).
        The dataset is split into the trainining dataset (X_train, y_train) and the test dataset (X_test, y_test).
        The label data `y` are generated in this method according to `close`, `s` and `ks`.

        < Input >
        X: Characteristics. (input_shape[:-1] numpy.ndarray)
        close: FX close rate. (input_shape[-1] numpy.ndarray)
        s: split of FX rate. (float)
        ks: timespans when high/low is predicted. (list or numpy.ndarray)
        iter_epochs: iteration number of epochs. The actual # of epochs is iter_epochs * epochs_base (in kwargs).
        """
        # Validation of parameters
        self._ks = ks
        if type(ks) in [int, np.int32]:
            nbr_of_ks = 1
        else:
            nbr_of_ks = len(ks)
        self._iter_epochs = iter_epochs
        if type(iter_epochs) in [int, np.int32]:
            nbr_of_iter = 1
        else:
            nbr_of_iter = len(iter_epochs)
        self._train_kwargs = kwargs
        if kwargs.get("batch_size") is None:
            batch_size = 100; self._train_kwargs["batch_size"] = batch_size
        else:
            batch_size = kwargs.get("batch_size")
        if kwargs.get("epochs") is None:
            epochs_base = 100; self._train_kwargs["epochs"] = epochs_base
        else:
            epochs_base = kwargs.get("epochs")
        if kwargs.get("test_size") is None:
            test_size = 100; self._train_kwargs["test_size"] = test_size
        else:
            test_size = kwargs.get("test_size")
        if kwargs.get("test_seed") is None:
            test_seed = 100; self._train_kwargs["test_seed"] = test_seed
        else:
            test_seed = kwargs.get("test_seed")

        # Train.
        st = time.time()
        print("Training starts...")
        self.models = []
        self.histories = []
        self.scores = []
        for kk in range(nbr_of_ks):
            hists = [None] * nbr_of_iter
            scores = [None] * nbr_of_iter
            models = [None] * nbr_of_iter
            y = af.labeling(close, s, ks[kk], mode=2)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=test_seed)
            for ii in range(nbr_of_iter):
                model, hist, score = self._fit(X_train, y_train, X_test, y_test, batch_size, epochs_base*iter_epochs[ii])
                models[ii] = copy.deepcopy(model)
                hists[ii] = copy.deepcopy(hist)
                scores[ii] = copy.deepcopy(score)
                print("k=", ks[kk], "epochs=", epochs_base*iter_epochs[ii],
                        'loss=', score[0], 'accuracy=', score[1])
            self.histories.append(hists)
            self.models.append(models)
            self.scores.append(scores)
        print("Training finished. Elapsed time: {0:.2f} sec.".format(time.time()-st))

    def _fit(self, X_train, y_train, X_test, y_test, batch_size, epochs):
        model = self._create_model()
        hist = model.fit(X_train, y_train,
                                batch_size=batch_size,
                                epochs=epochs,
                                shuffle=True,
                                callbacks=[EarlyStopping(monitor='val_loss', patience=2)],
                                verbose=0)
        score = model.evaluate(X_test, y_test, verbose=0)
        return model, hist, score
