#-*- coding: utf-8 -*-

import json
import h5py
import os
from keras.models import Sequential
from keras.models import model_from_json

class KerasModelAdapter(object):
    def __init__(self, model=None):
        self.model = model

    def save(self, fldrpath):
        """
        Save the whole information on the model
        """
        if self.model is None:
            raise ValueError("There is no model set in this adapter.")
        if not os.path.exists(fldrpath):
            os.makedirs(fldrpath)

        # Save the model architecture
        model = self.model
        model_json_str = model.to_json()
        with open(fldrpath + "model.json", 'w') as ff:
            ff.write(model_json_str)

        # Save the learned weights
        model.save_weights(fldrpath + "weights.h5")

        # Save the information on compilation
        loss_name = model.loss
        opt_name = model.optimizer.__class__.__name__.split(".")[-1].lower()
        metrics_list = model.metrics
        compile_info = {"loss":loss_name, "optimizer":opt_name, "metrics":metrics_list}
        with open(fldrpath + 'compile_info.json','w') as ff:
            json.dump(compile_info, ff)

    def load(self, fldrpath):
        """
        Load and generate the model from the files in `fldrpath`.
        """
        # Load the model architecture
        model = model_from_json(open(fldrpath + "model.json", "r").read())

        # Load the learned weights
        model.load_weights(fldrpath + "weights.h5")

        # Load the information on compilation
        with open(fldrpath + 'compile_info.json','r') as ff:
            compile_info = json.load(ff)
        model.compile(loss=compile_info["loss"],
            optimizer=compile_info["optimizer"],
            metrics=compile_info["metrics"])
        self.model = model
