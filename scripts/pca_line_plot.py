from pathlib import Path
import pandas as pd
import numpy as np

from scripts.select_batch_minix import _SelectBatchMinix
from components.recording_session_collection import RecordingSessionCollection
from components.metadata_unpack import MetadataUnpack as MDP
from widgets.plot_holo import Plot
from components.sens_ops import SensOps as so
from components.plot_container import PointcloudPlot, _PointcloudPlotResult
from components.plot_container import EnvironmentPlotContainer, _EnvironmentPlotLine

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

        RECVS = [3,2,1]
        NAMES = ["a", "e", "emt", "h", "i"]
        # NAMES = ["emt"]

        for NAME in NAMES:
            for RECV in RECVS:

                batches3 = self._collect_batches(
                    receivers=MDP.receivers_unpack([RECV]),
                    days=MDP.days_unpack([1]),
                    names=MDP.names_unpack([NAME]),
                    # names=MDP.names_unpack(["a", "e", "h", "i"]),
                    # names=MDP.names_unpack(["emt", "e"]),
                    # names=MDP.names_unpack(NAMES),
                    # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
                    # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
                )

                FREQS = [100]

                for FREQ in FREQS:

                    data = None
                    labels_i = 0
                    result_lengths_labels = []

                    for idx, batch in enumerate(batches3):
                        batch.load_from_storage_freq(FREQ)
                        amp = batch.get_masked_amplitude(0,0,1000)[0]
                        result_lengths_labels.append((len(so.mask(amp.df)),batch[0].get_id()))
                        if data is None:
                            data = amp
                        else:
                            data.df = pd.concat([data.df, so.mask(amp.df)], ignore_index=True)
                        labels_i += 1

                    pc = so.pca_X(data, 8)



                    print(pc._X_pca.shape)

                    for pc_X in [0,1,2,3,4,5,6,7]:
                        i = 0
                        label_pc = []
                        label_pc_fft = []
                        plot = Plot(2)
                        print(pc_X)
                        for idx, (l, label) in enumerate(result_lengths_labels):
                            # print(i, l+i)
                            labels_data = pc._X_pca[i:l+i]
                            label_pc_X = [j[pc_X] for j in labels_data]
                            # print(label_pc_X)
                            res = _EnvironmentPlotLine([k for k in range(l)], label_pc_X, label=label)
                            i += l
                            label_pc.append(res)

                            # Fourier Transform
                            fft_vals = np.fft.rfft(label_pc_X)
                            fft_freqs = np.fft.rfftfreq(len(label_pc_X), 1/FREQ)
                            # print(fft_vals)
                            # print(fft_freqs)
                            # exit()
                            fft_res = _EnvironmentPlotLine(fft_freqs, np.abs(fft_vals), label)
                            label_pc_fft.append(fft_res)

                        plot.append_row_idx(0, EnvironmentPlotContainer(plot_data=label_pc, axes_Y_label=f"PC {pc_X+1}", axes_X_label="CSI Sequenz", y_lim=(-15,15)))
                        y_max = 50
                        if pc_X == 0:
                            y_max = 400
                        if pc_X == 1:
                            y_max = 300
                        if pc_X == 2:
                            y_max = 200
                        if pc_X == 3:
                            y_max = 100
                        plot.append_row_idx(1, EnvironmentPlotContainer(plot_data=label_pc_fft, axes_Y_label=f"PC {pc_X+1}", axes_X_label="Frequenz", y_lim=(0, y_max)))
                        plot.save(Path("plots", "latex", f"{NAME}_r{RECV}_d{1}_pc{pc_X+1}_f{FREQ}hz.png"))


