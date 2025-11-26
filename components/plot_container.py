import numpy as np

class _HeatmapPlotResult:
    def __init__(self, matrix):
        corr = matrix
        for col in corr.columns:
            corr = corr.rename(columns={col: col.split('_')[2]})
            corr = corr.rename(index={col: col.split('_')[2]})
        self.matrix = corr
        self.index = np.mean(self.matrix)
        self.max = self.matrix.max()
        self.min = self.matrix.min()
        print(self.index)

class HeatmapPlot:
    def __init__(self, result:_HeatmapPlotResult):
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
    def __init__(self, plots:list):
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