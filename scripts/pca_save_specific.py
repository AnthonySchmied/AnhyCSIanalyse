from pathlib import Path
from datetime import datetime

from components.sens_ops import SensOps as so
from components.recording_session_collection import RecordingSessionCollection
from components.pca_set import PcaSet
from widgets.pca_plot import PcaPlot


class PcaSaveSpecific:
    def __init__(self):
        start_time = datetime.now()
        sc = RecordingSessionCollection(
            [
                Path("rec/01_recording/"),
                Path("rec/02_recording/"),
                Path("rec/03_recording/"),
                Path("rec/04_recording/"),
            ]
        )

        # p_r3_d2_a = PcaSet(
        #     sc, receivers=[3], dates=[1], names=["a"]
        # )
        # self.single_plot(
        #     pca_set=p_r3_d2_a,
        #     time=1000,
        #     frames=2000,
        # )

        for d in [1,2,3,4]:
            time1 = datetime.now()
            p_r3_d2_emt_e_i_h_a = PcaSet(
                sc, receivers=[3], dates=[d], names=["a", "e", "i", "h", "emt"]
            )
            self.single_plot(
                pca_set=p_r3_d2_emt_e_i_h_a,
                time=1000,
                frames=20000,
            )
            time2 = datetime.now()
            print(f"time total: {time2-start_time} - time loop: {time2-time1}")

    def single_plot(self, pca_set, frames, time, freq=100, offset=0):
        pca = pca_set.compute_pca(freq, time, offset, frames)
        plot = PcaPlot()
        plot_row = plot.add_row()
        plot_row.append(pca)
        plot.save(pca_set.get_save_path(0))
