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
    def __init__(self, X_pca, eigenvectors, eigenvalues, label):
        self._X_pca = X_pca
        self._eigenvectors = eigenvectors
        self._eigenvalues = eigenvalues
        self._label = label
        self._mean = None
        self._std = None
        self._two_std_range = None

    def get_pc_X(self, X):
        return self._X_pca[:, X-1]

    def get_label(self):
        return self._label

    def set_label(self, label):
        self._label = label

    def get_mean(self):
        if self._mean is None:
            self._mean = np.mean(self._X_pca, axis=0)
        return self._mean

    def get_std(self):
        if self._std is None:
            self._std = np.std(self._X_pca, axis=0)
        return self._std
    
    def get_two_std_range(self):
        if self._two_std_range is None:
            self._two_std_range = (self.get_mean() - 2 * self.get_std(), self.get_mean() + 2 * self.get_std())
        return self._two_std_range

    def in_ref_range(self, ref, X):
        if self.get_mean()[X-1] > ref.get_two_std_range()[0][X-1] and self.get_mean()[X-1] < ref.get_two_std_range()[1][X-1]:
            print(f"{ref.get_two_std_range()[0][X-1]} < {self.get_mean()[X-1]} < {ref.get_two_std_range()[1][X-1]}")
            return True
        return False



class PointcloudPlot:
    def __init__(self, plots: list, pc1 = 1, pc2 = 2):
        self._results = plots
        self._pc1 = pc1
        self._pc2 = pc2

    def __iter__(self):
        return iter(self._results)

    def get_pc(self):
        return (self._pc1, self._pc2)

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
