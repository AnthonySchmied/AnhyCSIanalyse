from pathlib import Path
import pandas as pd

from scripts.select_batch_minix import _SelectBatchMinix
from components.recording_session_collection import RecordingSessionCollection
from components.metadata_unpack import MetadataUnpack as MDP
from widgets.plot_holo import Plot
from components.sens_ops import SensOps as so
from components.plot_container import PointcloudPlot, _PointcloudPlotResult, EnvironmentPlotContainer, _EnvironmentPlotLine


class PcaLine(_SelectBatchMinix):
    def __init__(self):
        self.sc = RecordingSessionCollection(
            [
                Path("rec/01_recording/"),
                Path("rec/02_recording/"),
                Path("rec/03_recording/"),
                Path("rec/04_recording/"),
            ]
        )

        # NAMES = ["i", "ie"]
        RECVS = [2]
        FREQS = [10,25,50,100]
        DAYS = [1]

        for RECV in RECVS:
            for DAY in DAYS:

                batches3 = self._collect_batches(
                    receivers=MDP.receivers_unpack([RECV]),
                    days=MDP.days_unpack([DAY]),
                    # names=MDP.names_unpack(["a", "e", "emt", "h", "i"]),
                    # names=MDP.names_unpack(["a", "e", "h", "i"]),
                    names=MDP.names_unpack(["e"]),
                    # names=MDP.names_unpack(NAMES),
                    # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
                    # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
                )
                # FILENAME = f"empty_oneperson_by_entity_100hz_r{RECV}.png"
                FILENAME = f"line_samecount_pc1_d{DAY}_10_25_50_100hz_r{RECV}.png"

                data = None
                labels_i = 0
                result_lengths_labels = []

                plot = Plot(6)

                for f in FREQS:
                    for idx, batch in enumerate(batches3):

                        batch.load_from_storage_freq(f)
                        amp = batch.get_masked_amplitude(0,0,100)[0]
                        result_lengths_labels.append((len(so.mask(amp.df)),batch[0].get_id()))
                        if data is None:
                            data = amp
                        else:
                            data.df = pd.concat([data.df, so.mask(amp.df)], ignore_index=True)

                        print(data.df.shape)
                        labels_i += 1
                    # print(f"{f}: {len(result_lengths_labels)}")




                pc = so.pca_X(data, 4)

                # print(len(pc._X_pca))
                # print(len(pc._eigenvalues))
                # print(len(pc._eigenvalues))


                # print(result_lengths_labels)
                # print(len(result_lengths_labels))

                # pc.set_label(batch[0].get_id())


                label_pc = []
                i = 0

                print(pc._X_pca.shape)
                for idx, (l, label) in enumerate(result_lengths_labels):
                    # print(i, l+i)
                    # print(label.get_frequency())
                    f = label.get_frequency()
                    pc_X = 0
                    labels_data = pc._X_pca[i:l+i]
                    label_pc_X = [j[pc_X] for j in labels_data]
                    res = _EnvironmentPlotLine(x_data=[k for k in range(l)], y_data=label_pc_X, label=label)
                    # res = _PointcloudPlotResult(X_pca=pc._X_pca[i:l+i], eigenvectors=pc._eigenvectors, eigenvalues=pc._eigenvalues, label=label)
                    i += l

                    # print(res._X_pca.shape)

                    label_pc.append(res)

                plot.append_row_idx(0, EnvironmentPlotContainer("Zeit", "PC1", label_pc, y_lim=(-12,12)))
                # plot.append_row_idx(0, PointcloudPlot(label_pc, 2, 1))
                # plot.append_row_idx(0, PointcloudPlot(label_pc, 3, 1))
                # plot.append_row_idx(0, PointcloudPlot(label_pc, 4, 1))
        # plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 5))
            # plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 6))
            # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 1))
            # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 3))
            # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 4))
            # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 5))
            # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 6))
            # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 1))
            # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 2))
            # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 4))
            # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 5))
            # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 6))
            # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 1))
            # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 2))
            # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 3))
            # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 5))
            # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 6))
            # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 1))
            # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 2))
            # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 3))
            # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 4))
            # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 6))
            # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 1))
            # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 2))
            # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 3))
            # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 4))
            # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 5))
                plot.save(Path("plots", "latex", FILENAME))
            


 