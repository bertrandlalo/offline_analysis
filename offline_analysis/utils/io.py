from .analysis_config import AnalysisConfig
import pandas as pd
import os
from warnings import warn

class Loader(AnalysisConfig):
    def __init__(self, server_path):
        AnalysisConfig.__init__(self, server_path )
        self._description = {}

    def convert_bname_to_fname(self, bname, ext= ".hdf5"):
        return os.path.join(self.data_path, bname + ext)

    def select_fnames(self, query):
        self.hdf_info.columns = [c.replace('-', "_") for c in self.hdf_info.columns]
        self._bnames = self.hdf_info.query(query).index
        self._iterbnames = iter(self._bnames)

    def load_dataset(self, bname, streams):
        self._bname = bname
        try:
            self._data = {s["name"]: pd.read_hdf(self.convert_bname_to_fname(bname), s["group"], columns = s["columns"])   for s in streams}
        except KeyError as exc:
            warn(f"Could not load all data from: {bname}: {exc}")
            self._data = {}

    def load_next(self, streams):
        try:
            self.load_dataset(next(self._iterbnames), streams)
            return True
        except StopIteration:
            return False



