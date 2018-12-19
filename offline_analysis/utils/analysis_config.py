from datascience_utils.data_io import load_pickle, save_pickle
from os import path

class AnalysisConfig():
    def __init__(self, server_path):

        self.server_path = server_path

        self.data_path = path.join(self.server_path, "DATA", "DATA_OMI", "raw_hdf5")
        self.diagnostic_path = path.join(self.server_path, "DATA_diagnostic")
        self.typeform_path = path.join(self.server_path, "DATA_typeform")

        self.xdf_info = load_pickle(self.diagnostic_path + '/xdf_info.pickle')
        self.hdf_info = load_pickle(self.diagnostic_path + '/hdf_info.pickle')

    def save_hdf_info(self):
         save_pickle(self.hdf_info, self.diagnostic_path + '/hdf_info.pickle')