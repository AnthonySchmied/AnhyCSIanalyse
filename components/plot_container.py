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
    def __init__(self, X_pca, explained_variance, model, label):
        self.X_pca = X_pca
        self.explained_variance = explained_variance
        self.model = model
        self.label = label


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
    def __init__(self):
        pass


class CorrelationIndexPlot:
    def __init__(self):
        pass


# class MultTransPlot:
#     def __init__(self, raw, cr0, cr1):
#         self._raw = raw
#         self._cr0 = cr0
#         self._cr1 = cr1


class _HeatmapArraysPlotResult:
    def __init__(self, data):
        self._data = data


class HeatmapPlotArrays:
    def __init__(self, result: _HeatmapArraysPlotResult, title=None):
        self._result = result
        self._title = title
        if title is None:
            self._title = ""

    def get_matrix(self):
        return self._result._data

    def get_matrix_mean(self):
        return np.mean(self._result._data)

    def get_matrix_median(self):
        return np.median(self._result._data)

    def get_matrix_min(self):
        return np.min(self._result._data)

    def get_matrix_max(self):
        return np.max(self._result._data)
    
    def get_matrix_variance(self):
        return np.var(self._result._data)

    def get_width(self):
        return len(self._result._data[0])

    def get_height(self):
        return len(self._result._data)

    def get_title(self):
        return f"{self._title} - mean: {self.get_matrix_mean():.2f} - var: {self.get_matrix_variance():.2f}"
