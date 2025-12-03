import numpy as np

class _HeatmapPlotResult:
    def __init__(self, matrix):
        corr = matrix
        # if isinstance(str())
        # for col in corr.columns:
        #     corr = corr.rename(columns={col: col.split('_')[2]})
        #     corr = corr.rename(index={col: col.split('_')[2]})
        self.matrix = corr
        self.index = np.mean(self.matrix)
        self.max = self.matrix.max()
        self.min = self.matrix.min()
        print(self.index)


class HeatmapPlot:
    def __init__(self, result: _HeatmapPlotResult):
        self._result = result

    def get_matrix(self):
        return self._result.matrix

    def get_index(self):
        return self._result.index


class _PointcloudPlotResult:
    def __init__(self, X_pca, label):
        self._X_pca = X_pca
        # self.explained_variance = explained_variance
        # self.model = model
        self._label = label

    def get_pc_X(self, X):
        return [r[X-1] for r in self._X_pca]

    def get_label(self):
        return self._label

    def set_label(self, label):
        self._label = label

class PointcloudPlot:
    def __init__(self, plots: list):
        self._results = plots

    def __iter__(self):
        return iter(self._results)


class AmplitudePlot:
    def __init__(self, amplitudes):
        self._amplitudes = amplitudes

    def get_amplitudes(self):
        return self._amplitudes


class _CorrelationIndexPlotResult:
    def __init__(self, label, mean, variance):
        self._label = label
        self._mean = mean
        self._variance = variance

    def get_mean(self):
        return self._mean
        
    def get_variance(self):
        return self._variance

    def get_label(self):
        return self._label

class CorrelationIndexPlot:
    def __init__(self, data):
        self._data = data

    def __iter__(self):
        return iter(self._data)

    @staticmethod
    def to_result(label, mean, var):
        return _CorrelationIndexPlotResult(label, mean, var)

class _HeatmapArraysPlotResult:
    def __init__(self, data):
        self._data = data


class HeatmapPlotArrays:
    def __init__(self, result: _HeatmapArraysPlotResult, title=None):
        self._result = result
        self._title = title
        if title is None:
            self._title = ""
        self._mean = None
        self._median = None
        self._variance = None
        self._min = None
        self._max = None

    def get_matrix(self):
        return self._result._data

    def get_matrix_mean(self):
        if self._mean is None:
            # print(self.get_matrix())
            
            # for row in self._result._data:
            #     print(row)
            #     print(np.mean(row))
            
            # exit()
            self._mean = np.mean(self._result._data)

            # print(self._mean)
            # exit()
        return self._mean

    def get_matrix_median(self):
        if self._median is None:
            self._median = np.median(self._result._data)
        return self._median

    def get_matrix_min(self):
        if self._min is None:
            self._min = np.min(self._result._data)
        return self._min

    def get_matrix_max(self):
        if self._max is None:
            self._max = np.max(self._result._data)
        return self._max

    def get_matrix_variance(self):
        if self._variance is None:
            self._variance = np.var(self._result._data)
        return self._variance

    def get_width(self):
        return len(self._result._data[0])

    def get_height(self):
        return len(self._result._data)

    def get_title(self):
        return f"{self._title} - m: {self.get_matrix_mean():.6f} - v: {self.get_matrix_variance():.6f}"
