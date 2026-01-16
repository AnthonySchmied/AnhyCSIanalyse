from pathlib import Path
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from collections import Counter

from scripts.select_batch_minix import _SelectBatchMinix
from components.recording_session_collection import RecordingSessionCollection
from components.metadata_unpack import MetadataUnpack as MDP
from widgets.plot_holo import Plot
from components.sens_ops import SensOps as so
from components.plot_container import PointcloudPlot, _PointcloudPlotResult


class DecisionTree():
    def __init__(self):
        self._reset()

    def _reset(self):
        self._scaler = StandardScaler()
        self._pca = PCA(n_components=4, svd_solver='full')
        self._pc_boarders = None

    def fit_using_empty(self, amp, label):
        df = so.mask(amp.df)
        data = df[amp.columns].to_numpy()
        Xs = self._scaler.fit_transform(data)
        X_pca = self._pca.fit_transform(Xs)
        eigenvectors = self._pca.components_
        eigenvalues = self._pca.explained_variance_
        self._pc_boarders = None # reset empty area values when updating empty
        self._empty_pca_result = _PointcloudPlotResult(X_pca, eigenvectors, eigenvalues, label)
        return self._empty_pca_result

    def transform(self, amp, label):
        df = so.mask(amp.df)
        data = df[amp.columns].to_numpy()
        Xs = self._scaler.transform(data)
        X_pca = self._pca.transform(Xs)
        eigenvectors = self._pca.components_
        eigenvalues = self._pca.explained_variance_
        return _PointcloudPlotResult(X_pca, eigenvectors, eigenvalues, label)

    def get_pc_min_max(self, pc_X, pointcloudplotresult):
        minimum = min([x[pc_X-1] for x in pointcloudplotresult._X_pca])
        maximum = max([x[pc_X-1] for x in pointcloudplotresult._X_pca])
        center = ((maximum-minimum)/2) + minimum
        return (minimum, center, maximum)

    def is_in_empty_area_pc_x(self, borders, pc_X):
        if borders[1] < self._pc_boarders[pc_X-1][2]:
            # print(f"{borders[1]} < {self._pc_boarders[pc_X-1][2]}")
            if borders[1] > self._pc_boarders[pc_X-1][0]:
                # print(f"{borders[1]} > {self._pc_boarders[pc_X-1][0]}:")
                return True
            
        # print(f"{borders[1]} > {self._empty_pca_result._X_pca[pc_X-1][2]}")
        # print(f"{borders[1]} < {self._empty_pca_result._X_pca[pc_X-1][0]}:")
        return False
    
    def test_pc_X_is_in_empty(self, pca, pc_X):
        border = self.get_pc_min_max(pc_X, pca)
        # print(f"pc{pc_X}: {border}")
        if self.is_in_empty_area_pc_x(border, pc_X):
            # print(f"pc{pc_X} inside")
            return True
        else:
            # print(f"pc{pc_X} outside")
            return False

    def classify(self, pointcloudplotresult):
        if self._pc_boarders is None: # calculate boarders
            self._pc_boarders = []
            for i in range(len(pointcloudplotresult._X_pca[0])):
                self._pc_boarders.append(self.get_pc_min_max(i+1, self._empty_pca_result))
            print(self._pc_boarders)
        
        print(str(pointcloudplotresult.get_label()))
        result = []
        # result.append(self.test_pc_X_is_in_empty(pointcloudplotresult, 1))
        result.append(self.test_pc_X_is_in_empty(pointcloudplotresult, 2))
        # result.append(self.test_pc_X_is_in_empty(pointcloudplotresult, 3))
        # result.append(self.test_pc_X_is_in_empty(pointcloudplotresult, 4))
        # result.append(self.test_pc_X_is_in_empty(pointcloudplotresult, 5))

        print("-------------")
        print(str(pointcloudplotresult.get_label()))
        print(result)
        # Count the occurrences of each element
        counts = Counter(result)
        # Find the most common element
        print(counts.most_common(1)[0][0])
        print("-------------")
        return counts.most_common(1)[0][0]




class DecisionTreeEvaluation(_SelectBatchMinix):
    def __init__(self):
        self.sc = RecordingSessionCollection(
            [
                Path("rec/01_recording/"),
                Path("rec/02_recording/"),
                Path("rec/03_recording/"),
                Path("rec/04_recording/"),
            ]
        )
        self.dt = DecisionTree()

        RECVS = [3]

        training_batches = self._collect_batches(
            receivers=MDP.receivers_unpack(RECVS),
            days=MDP.days_unpack([3,4]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i"]),
            names=MDP.names_unpack(["emt"]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
        )
        
        training_amp = None
        for idx, batch in enumerate(training_batches):
            batch.load_from_storage_freq(100)
            amp = batch.get_masked_amplitude(0,0,6000)[0]
            if training_amp == None:
                training_amp = amp
            else:
                training_amp.df = pd.concat([training_amp.df, so.mask(amp.df)])
            # print(training_amp.df.shape)

        training_pca_result = self.dt.fit_using_empty(training_amp, batch[0].get_id())
        

        plot = Plot(2)
        scatters = [training_pca_result]

        wrong_empty_counter = 0
        wrong_presence_counter = 0
        right_counter = 0

        evaluation_batches = self._collect_batches(
            receivers=MDP.receivers_unpack(RECVS),
            days=MDP.days_unpack([1,2,3,4]),
            names=MDP.names_unpack(["a", "e", "emt", "h", "i"]),
            # names=MDP.names_unpack(["a","e","h"]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
        )

        for idx, batch in enumerate(evaluation_batches):
            batch.load_from_storage_freq(100)
            amp = batch.get_masked_amplitude(0,0,6000)[0]
            # if evaluation_amp == None:
            #     evaluation_amp = amp
            # else:
            #     evaluation_amp.df = pd.concat([evaluation_amp.df, so.mask(amp.df)])
            # print(evaluation_amp.df.shape)

            evaluation_pca_result = self.dt.transform(amp, batch[0].get_id())
            classification = self.dt.classify(evaluation_pca_result)
            truth_name = batch[0].get_id().get_names()[0]
            if classification:
                if truth_name == "emt":
                    print("true")
                    right_counter += 1
                else:
                    wrong_empty_counter += 1
            else:
                if truth_name == "emt":
                    wrong_presence_counter += 1
                else:
                    print("true")
                    right_counter += 1

            scatters.append(evaluation_pca_result)


        print(f"result wrong_empty: {wrong_empty_counter} - wrong presence: {wrong_presence_counter} - right ratio: {(right_counter)/(wrong_presence_counter+wrong_empty_counter+right_counter)}")


        plot.append_row_idx(0, PointcloudPlot(scatters, 1, 2))
        plot.append_row_idx(0, PointcloudPlot(scatters, 1, 3))
        plot.append_row_idx(0, PointcloudPlot(scatters, 1, 4))
        plot.append_row_idx(1, PointcloudPlot(scatters, 2, 1))
        plot.append_row_idx(1, PointcloudPlot(scatters, 2, 3))
        plot.append_row_idx(1, PointcloudPlot(scatters, 2, 4))

        plot.save(Path("plots", "eval.png"))