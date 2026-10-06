from pathlib import Path
import pandas as pd
# import duckdb

from scripts.select_batch_minix import _SelectBatchMinix
from components.recording_session_collection import RecordingSessionCollection
from components.metadata_unpack import MetadataUnpack as MDP
from widgets.plot_holo import Plot
from components.sens_ops import SensOps as so
from components.plot_container import PointcloudPlot, _PointcloudPlotResult


class ParquetExport(_SelectBatchMinix):
    def __init__(self):
        self.sc = RecordingSessionCollection(
            [
                Path("rec/01_recording/"),
                # Path("rec/02_recording/"),
                # Path("rec/03_recording/"),
                # Path("rec/04_recording/"),
            ]
        )

        self.recordings_matadata = pd.DataFrame({
            "idx": pd.Series(dtype="int64"),
            "key": pd.Series(dtype="string"),
            "receiver_mac": pd.Series(dtype="str"),
            "sender_mac": pd.Series(dtype="str"),
            "recording_key": pd.Series(dtype="int64"),
            "label": pd.Series(dtype="str"),
            "sample_frequency": pd.Series(dtype="int64"),
            "datetime": pd.Series(dtype="datetime64[ns]"),
        })

        def append_recording(key, receiver_mac, sender_mac, recording_key, label, sample_frequency, date, time):
            self.recordings_matadata.loc[len(self.recordings_matadata)] = (len(self.recordings_matadata)+1, key, receiver_mac, sender_mac, recording_key, label, sample_frequency, pd.to_datetime(f"{date} {time}"))
            return len(self.recordings_matadata)

        for ses in self.sc.get_sessions():
            ses.save_split_by_frequency_to_parquet_file(append_recording)
           
        print(self.recordings_matadata)

    # def init_parquet(self):
    #     self.con = duckdb.connect()


        # # NAMES = ["i", "ie"]
        # RECVS = [3]
        # # FREQS = [10,25,50,100]
        # DAYS = [1,2,3,4]

        # for RECV in RECVS:
        #     for DAY in DAYS:

        #         batches3 = self._collect_batches(
        #             receivers=MDP.receivers_unpack([RECV]),
        #             days=MDP.days_unpack([DAY]),
        #             # days=MDP.days_unpack(DAYS),
        #             names=MDP.names_unpack(["a", "e", "emt", "h", "i"]),
        #             # names=MDP.names_unpack(["a", "e", "h", "i"]),
        #             # names=MDP.names_unpack(["e"]),
        #             # names=MDP.names_unpack(NAMES),
        #             # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
        #             # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
        #         )
        #         # FILENAME = f"empty_oneperson_by_entity_100hz_r{RECV}.png"
        #         FILENAME = f"empty_oneperson_d{DAY}_100hz_r{RECV}.png"
        #         # FILENAME = f"empty_double_d{DAY}_100hz_r{RECV}.png"

        #         data = None
        #         labels_i = 0
        #         result_lengths_labels = []

        #         plot = Plot(6)

        #         # for f in FREQS:
        #         for idx, batch in enumerate(batches3):

        #             batch.load_from_storage_freq(100)
        #             amp = batch.get_masked_amplitude(0,0,6000)[0]
        #             result_lengths_labels.append((len(so.mask(amp.df)),batch[0].get_id()))
        #             if data is None:
        #                 data = amp
        #             else:
        #                 data.df = pd.concat([data.df, so.mask(amp.df)], ignore_index=True)

        #             print(data.df.shape)
        #             labels_i += 1
        #         # print(f"{f}: {len(result_lengths_labels)}")




        #         pc = so.pca_X(data, 4)

        #         # print(len(pc._X_pca))
        #         # print(len(pc._eigenvalues))
        #         # print(len(pc._eigenvalues))


        #         # print(result_lengths_labels)
        #         # print(len(result_lengths_labels))

        #         # pc.set_label(batch[0].get_id())


        #         label_pc = []
        #         i = 0

        #         print(pc._X_pca.shape)
        #         for idx, (l, label) in enumerate(result_lengths_labels):
        #             # print(i, l+i)
        #             res = _PointcloudPlotResult(X_pca=pc._X_pca[i:l+i], eigenvectors=pc._eigenvectors, eigenvalues=pc._eigenvalues, label=label)
        #             i += l

        #             print(res._X_pca.shape)

        #             label_pc.append(res)

        #         plot.append_row_idx(0, PointcloudPlot(label_pc, 2, 1))
        #         plot.append_row_idx(0, PointcloudPlot(label_pc, 3, 1))
        #         plot.append_row_idx(0, PointcloudPlot(label_pc, 4, 1))
        # # plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 5))
        #     # plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 6))
        #     # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 1))
        #     # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 3))
        #     # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 4))
        #     # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 5))
        #     # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 6))
        #     # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 1))
        #     # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 2))
        #     # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 4))
        #     # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 5))
        #     # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 6))
        #     # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 1))
        #     # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 2))
        #     # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 3))
        #     # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 5))
        #     # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 6))
        #     # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 1))
        #     # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 2))
        #     # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 3))
        #     # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 4))
        #     # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 6))
        #     # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 1))
        #     # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 2))
        #     # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 3))
        #     # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 4))
        #     # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 5))
        #         plot.save(Path("plots", "latex", FILENAME))
            


 