from abc import ABC, abstractmethod
import inspect

class Pipeline(ABC):
    def __init(self):
        pass

    def set_params(self, column_name, fs, band_params, welch_params):
        pass

    def set_data(self, unity_events, nexus_signal_raw):
        pass

    def set_data_from_loader(self, loader):
        self.set_data(**{k: loader._data[k] for k in self.get_data_keys()})

    def get_data_keys(self):
        return [p for p in inspect.signature(self.set_data).parameters]

    def get_params_keys(self):
        return [p for p in inspect.signature(self.set_params).parameters]

    @abstractmethod
    def run(self, dataframe):
        pass



