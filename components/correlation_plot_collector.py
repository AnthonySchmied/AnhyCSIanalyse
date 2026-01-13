from pathlib import Path

from components.plot_container import PointcloudPlot
from widgets.plot_holo import Plot


class CorrelationIndexCollector():
    def __init__(self):
        self._data = {}

    def register_label(self, label):
        self._data[label] = []
        return label

    def push_data(self, data, label):
        self._data[label].append(data)

    def save(self, name):
        plot = Plot(1)
        datas = []
        [datas.extend(p) for _, p in self._data.items()]
        plot.append_row_idx(0, PointcloudPlot(datas))
        plot.save(Path(self._path, name))

    def set_path(self, path):
        self._path = path

    def _reset(self):
        self._data = {}