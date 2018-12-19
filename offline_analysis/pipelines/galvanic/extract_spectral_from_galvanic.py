from offline_analysis.utils.pipeline import Pipeline
from datascience_utils import spectral, filters, signal_quality, general, unity, data_io
import numpy as np
from warnings import warn
import pandas as pd
import os

## for test purposes
# fname = '/Users/raph/OMIND_SERVER/DATA/DATA_OMI/raw_hdf5/data_2018-03-26.13.12.42_507dd660ac2c6ec9364b44644c9bdb2f775c5ac0f6529ee74f9205c7309bde3a.hdf5'
# unity_events = pd.read_hdf(fname, "unity/events/unity_events")
# nexus_signal_raw = pd.read_hdf(fname, "nexus/signal/nexus_signal_raw")

class ExtractSpectralFeature(Pipeline):
    def __init__(self, sequence_names = ['session_sequence']):
        self._modality = "galvanic"
        self._type = "physio"
        self._sequence_names = sequence_names

        self._feature_names = ["spectral_vLF", "spectral_LF", "spectral_HF"]

        self._feature_desc= [ "relative power extracted using welch method between 0. and 0.03",
                              "relative power extracted using welch method between 0.04 and 0.15",
                              "relative power extracted using welch method between 0.15 and 0.4"]

        self._description = {n:d for (n,d) in zip(self._feature_names, self._feature_desc )}


    def set_params(self, column_name, fs, band_params, welch_params):
        self._column_name = column_name
        self._fs = fs
        self._band_params = band_params
        self._welch_params = welch_params

    def set_data(self, unity_events, nexus_signal_raw):
        self._unity_events = unity_events.copy()
        self._dataframe = nexus_signal_raw.copy()

    def preprocess(self, dataframe, column_name):
        dataframe = dataframe[[column_name]]
        # get rid of 0.0 values
        dataframe = dataframe.replace(0.0, np.NaN).interpolate("pchip")
        # resample
        dataframe = filters.resample(dataframe, self._fs)
        # take inverse to have the SKIN CONDUCTANCE G = 1/R = I/U
        dataframe = 1 / dataframe
        # scale signal on the all session
        dataframe = filters.scipy_scale_signal(dataframe, method="minmax")
        return dataframe

    def set_sequence_times(self):
        sequence_names = self._sequence_names
        unity_events = self._unity_events
        subsequences_list = data_io.print_subsequences_report(unity_events)
        self.sequence_names = general.intersect(sequence_names, subsequences_list)
        if len(self.sequence_names)<len(sequence_names):
            missing_sequences = [a for a in sequence_names if a not in self.sequence_names]
            warn("could not extract all sequences from unity_events, missing {missing_sequences}".format(missing_sequences=str(missing_sequences)))
        self.sequence_times = {}
        for sequence_name in self.sequence_names:
            times = unity.extract_unity_subsequence_times(unity_events, sequence_name)
            for k, (begin, end) in enumerate(times):
                self.sequence_times[sequence_name + "_" + str(k)] = {"begin":begin, "end":end}

    def run(self):

        dataframe = self._dataframe

        dataframe = self.preprocess(dataframe, self._column_name)

        feature_dataframe = spectral.rolling_welch_bandpower(dataframe, column_name=self._column_name,
                                                                      band_names=["vLF-relative", "LF-relative",
                                                                                  "HF-relative"],
                                                                      apply_log=False, outpower="relative",
                                                                      **self._welch_params, **self._band_params)
        flat_stats_list = []
        for sequence_name, times in self.sequence_times.items():
            begin = times["begin"]
            end = times["end"]

            stats = general.extract_summary(unity.troncate_dataframe(feature_dataframe, begin, end), feature_dataframe.columns)

            flat_stats = pd.DataFrame(pd.concat([stats.iloc[k, :].T for k in range(len(stats))], 0)).T
            stats.index = self._feature_names
            flat_stats.columns = [
                "{type}_{sequence}_{modality}_{feature}_{stat}".format(type=self._type, sequence=sequence_name, modality=self._modality,
                                                                       feature=feature, stat=stat) for (feature) in stats.index for stat in stats.columns]
            flat_stats_list.append(flat_stats)

        return pd.concat(flat_stats_list, 1)
