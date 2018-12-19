import os
import sys

import importlib
import logging

import yaml
import pickle

import time
import tqdm
from tqdm import *

import pandas as pd
import numpy as np

from datetime import datetime

from offline_analysis.utils.analysis_config import AnalysisConfig
from offline_analysis.utils.io import Loader


def get_basename(fname):
    return os.path.splitext(os.path.basename(fname))[0]


class FeaturesGenerator():
    def __init__(self, server_path, author = "omind"):
        self._server_path = server_path
        self._now = str(datetime.now().today())
        self._summary_description = {}
        self._summary_description["meta"] = {"author": author, "date": self._now}


    def set_loader(self, query, streams):
        self._loader = Loader(self._server_path)
        self._loader.select_fnames(query)

        for c in streams:
            if "columns" not in c: c["columns"] = None

        self._streams_params = streams
        self._summary_description["loader"] = {"config_inputs": {"query":query, "streams": streams},
                                                "report": {"nb_selected_files": len(self._loader._bnames),
                                                      "nb_computed_files": None}}


    def set_pipelines(self, config_pipelines):
        self._summary_description["pipelines"] = {}
        self._pipelines = []
        for pipeline_config in config_pipelines:
            pipeline_id = pipeline_config["id"]
            logging.info("Run pipeline {pipeline_id}".format(pipeline_id=pipeline_id))
            m = importlib.import_module(pipeline_config['module'])
            c = getattr(m, pipeline_config['class'])
            if not 'sequence_names' in pipeline_config:
                sequence_names = ['session_sequence']
            else:
                sequence_names = pipeline_config['sequence_names']
            pipeline = c(sequence_names)
            pipeline._id = pipeline_id
            if not 'params' in pipeline_config:
                pipeline_params = {}
            else:
                if not (("path" in pipeline_config["params"]) & ("key" in pipeline_config["params"])):
                    sys.exit("invalid config in pipeline {pipeline_id}".format(pipeline_id=pipeline._id))
                with open(pipeline_config["params"]["path"]) as config_file:
                    try:
                        pipeline_config_params = yaml.load(config_file)
                    except yaml.YAMLError as exc:
                        sys.exit(f"Could not parse: {config_file}: {exc}")
                if not pipeline_config["params"]["key"] in pipeline_config_params:
                    sys.exit(f"Could not find config key in : {config_file}")
                else:
                    pipeline_params = pipeline_config_params[pipeline_config["params"]["key"]]

            # check config params
            if not (set(pipeline.get_params_keys()) == set(pipeline_params.keys())):
                sys.exit(f"Invalid pipeline params for {pipeline_id}".format(pipeline_id=pipeline._id))
            else:
                pipeline.set_params(**pipeline_params)

            if not (set(pipeline.get_data_keys()) == set([s["name"] for s in self._streams_params])):
                sys.exit(f"Invalid streams params for {pipeline_id}".format(pipeline_id=pipeline.id))

            self._pipelines.append(pipeline)
            # add description
            self._summary_description["pipelines"][pipeline._id] = {"description": pipeline._description, "params": pipeline_params}


    def run(self):
        logging.info("Loading and running pipelines.....")
        global_tic = time.perf_counter()
        timit_dict = {}
        datasets_flat_stats_list = []
        # while self._loader.load_next(self._streams_params):
        for bname in tqdm(self._loader._bnames):
            # print(bname)
            self._loader.load_dataset(bname, self._streams_params)
            if self._loader._data:
                dataset_flat_stats_list = []
                index = self._loader._bname
                for pipeline in self._pipelines:
                    if pipeline._id not in timit_dict:
                        timit_dict[pipeline._id]=[]
                    pipeline.set_data_from_loader(self._loader)
                    pipeline.set_sequence_times()
                    # TODO: fix timit
                    local_tic = time.perf_counter()
                    flat_stats = pipeline.run()
                    local_toc = time.process_time()
                    timit_dict[pipeline._id].append(local_toc-local_tic)
                    flat_stats.index = [index]
                    dataset_flat_stats_list.append(flat_stats)
                dataset_flat_stats_df = pd.concat(dataset_flat_stats_list, axis=1, sort=True)
                datasets_flat_stats_list.append(dataset_flat_stats_df)
        global_toc = time.process_time()
        self._summary_description["meta"]["timit"] = {**{"all": (global_toc-global_tic)/60}, **{k:np.mean(v)/60 for (k,v) in timit_dict.items()}}

        self.output_features = pd.concat(datasets_flat_stats_list, axis=0)
        self._summary_description["loader"]["report"]["nb_computed_files"] = len(self.output_features)

        return self.output_features

    def save(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # save description in a yaml
        with open(os.path.join(output_dir, self._now + "_readme.yml"), 'w') as outfile:
            yaml.dump(self._summary_description, outfile, default_flow_style=False)

        # save matrice of features in csv
        self.output_features.to_csv(os.path.join(output_dir, self._now + "_features.csv"))

        # save matrice of features in pickle
        with open(os.path.join(output_dir, self._now + "_features.pickle"), 'wb') as outfile:
            pickle.dump(self.output_features, outfile, protocol=pickle.HIGHEST_PROTOCOL)
        logging.info("Saving Description and Features in {output_dir} .....".format(output_dir=output_dir))