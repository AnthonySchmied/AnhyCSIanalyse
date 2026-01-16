from pathlib import Path
import pandas as pd

from scripts.select_batch_minix import _SelectBatchMinix
from components.recording_session_collection import RecordingSessionCollection
from components.metadata_unpack import MetadataUnpack as MDP
from widgets.plot_holo import Plot
from components.sens_ops import SensOps as so
from components.plot_container import PointcloudPlot, _PointcloudPlotResult


class PcaAll(_SelectBatchMinix):
    def __init__(self):
        self.sc = RecordingSessionCollection(
            [
                Path("rec/01_recording/"),
                Path("rec/02_recording/"),
                Path("rec/03_recording/"),
                Path("rec/04_recording/"),
            ]
        )

        batches3 = self._collect_batches(
            receivers=MDP.receivers_unpack([3]),
            days=MDP.days_unpack([1,2,3,4]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i"]),
            names=MDP.names_unpack(["emt"]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
        )

        data = None
        labels_i = 0
        result_lengths_labels = []

        freqs = [100]

        for f in freqs:
            for idx, batch in enumerate(batches3):
                batch.load_from_storage_freq(f)
                amp = batch.get_masked_amplitude(0,0,6000)[0]
                result_lengths_labels.append((len(so.mask(amp.df)),batch[0].get_id()))
                if data is None:
                    data = amp
                else:
                    data.df = pd.concat([data.df, so.mask(amp.df)], ignore_index=True)

                print(data.df.shape)
                labels_i += 1
            print(f"{f}: {len(result_lengths_labels)}")




        plot = Plot(6)
        pc = so.pca_X(data, 4)

        print(len(pc._X_pca))
        print(len(pc._eigenvalues))
        print(len(pc._eigenvalues))


        print(result_lengths_labels)
        print(len(result_lengths_labels))

        # pc.set_label(batch[0].get_id())


        label_pc = []
        i = 0

        print(pc._X_pca.shape)
        for idx, (l, label) in enumerate(result_lengths_labels):
            # print(i, l+i)
            res = _PointcloudPlotResult(X_pca=pc._X_pca[i:l+i], eigenvectors=pc._eigenvectors, eigenvalues=pc._eigenvalues, label=label)
            i += l

            print(res._X_pca.shape)

            label_pc.append(res)

        plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 2))
        plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 3))
        plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 4))
        plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 5))
        plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 6))
        plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 1))
        plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 3))
        plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 4))
        plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 5))
        plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 6))
        plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 1))
        plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 2))
        plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 4))
        plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 5))
        plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 6))
        plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 1))
        plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 2))
        plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 3))
        plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 5))
        plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 6))
        plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 1))
        plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 2))
        plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 3))
        plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 4))
        plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 6))
        plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 1))
        plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 2))
        plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 3))
        plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 4))
        plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 5))
        plot.save(Path("plots", "all_empty_by_day_100hz_r3.png"))
        exit()


 