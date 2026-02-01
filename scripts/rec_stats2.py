from pathlib import Path
import pandas as pd
import numpy as np
import copy

from scripts.select_batch_minix import _SelectBatchMinix
from components.recording_session_collection import RecordingSessionCollection
from components.metadata_unpack import MetadataUnpack as MDP
from widgets.plot_holo import Plot
from components.sens_ops import SensOps as so
from components.plot_container import PointcloudPlot, _PointcloudPlotResult


class RecStats(_SelectBatchMinix):
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
            receivers=MDP.receivers_unpack([3,2,1]),
            days=MDP.days_unpack([1,2,3,4]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i"]),
            # names=MDP.names_unpack(["a", "e", "h", "i"]),
            # names=MDP.names_unpack(["emt"]),
            # names=MDP.names_unpack(["emt"]),
            # names=MDP.names_unpack(NAMES),
            names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
        )


        m = {
            "tx_count": 0,
            "rx_count": 0,
            "tx_lost": 0,
            "rx_lost": 0,
            "tx_ratio": 0,
            "mean_interval": None,
            "max_interval": 0.0,
            "min_interval": 99999999.0,
            # "median_interval" : 0,
            # "all_intervals": []
        }

        f = {
            10: copy.deepcopy(m),
            25:  copy.deepcopy(m),
            50:  copy.deepcopy(m),
            100: copy.deepcopy(m),
        }

        day = {
            3: copy.deepcopy(f),
            2: copy.deepcopy(f),
            1: copy.deepcopy(f),
        }

        stats = {
            1: copy.deepcopy(day),
            2: copy.deepcopy(day),
            3: copy.deepcopy(day),
            4: copy.deepcopy(day),
        }

        for idx, batch in enumerate(batches3):
            for f in [10,25,50,100]:
                print("read")
                batch.load_from_storage_freq(f)
                # print(batch)
                # print(batch.get_masked_amplitude(0,0,6000))

                for amp in batch.get_masked_amplitude(0,0,6000):
                    date_packed = amp.recording.get_date_packed()[0]
                    recv_packed = amp.recording.get_recv_packed()[0]
                    frequency = int(amp.recording.get_frequencies()[0])

                    stats[date_packed][recv_packed][frequency][
                        "tx_count"
                    ] += amp.recording.get_tx_packets_count()

                    stats[date_packed][recv_packed][frequency][
                        "rx_count"
                    ] += amp.recording.get_rx_packets_count()

                    if stats[date_packed][recv_packed][frequency]["mean_interval"] is None:
                        stats[date_packed][recv_packed][frequency]["mean_interval"] = amp.recording.get_mean_rx_interval()
                    else:
                        stats[date_packed][recv_packed][frequency]["mean_interval"] = np.mean([amp.recording.get_mean_rx_interval(), stats[date_packed][recv_packed][frequency]["mean_interval"]])
                        
                    stats[date_packed][recv_packed][frequency][
                        "tx_lost"
                    ] += amp.recording.get_tx_packets_lost()

                    stats[date_packed][recv_packed][frequency][
                        "rx_lost"
                    ] += amp.recording.get_rx_packets_lost()

                    max = np.max(amp.recording.get_max_tx_interval())
                    stats[date_packed][recv_packed][frequency]["max_interval"] = np.max([stats[date_packed][recv_packed][frequency]["max_interval"], max])

                    min = np.min(amp.recording.get_min_rx_interval())
                    stats[date_packed][recv_packed][frequency]["min_interval"] = np.min([stats[date_packed][recv_packed][frequency]["min_interval"], min])

        for d in stats.keys():
            for r in stats[d].keys():
                for f in stats[d][r].keys():
                    if stats[d][r][f]["tx_count"] > 0:
                        stats[d][r][f]["tx_ratio"] = 1 - (stats[d][r][f]["tx_lost"] / (stats[d][r][f]["tx_lost"]+stats[d][r][f]["tx_count"]))


        freqs = [10, 25, 50, 100]

        for f in freqs:
            print(
                f"{f} Hz \n \
                                    | Tag 1 Tag 1 Tag 1 | Tag 2 Tag 2 Tag 2 | Tag 3 Tag 3 Tag 3 | Tag 4 Tag 4 Tag 4 | \n \
                                    | R3    R2    R1    |  R3    R2    R1   |  R3    R2    R1   |  R3    R2    R1   | \n \
                    tx_count        | {stats[1][3][f]["tx_count"]} {stats[1][2][f]["tx_count"]} {stats[1][1][f]["tx_count"]} | {stats[2][3][f]["tx_count"]} {stats[2][2][f]["tx_count"]} {stats[2][1][f]["tx_count"]} | {stats[3][3][f]["tx_count"]} {stats[3][2][f]["tx_count"]} {stats[3][1][f]["tx_count"]} | {stats[4][3][f]["tx_count"]} {stats[4][2][f]["tx_count"]} {stats[4][1][f]["tx_count"]} | \n \
                    tx_lost          | {stats[1][3][f]["tx_lost"]} {stats[1][2][f]["tx_lost"]} {stats[1][1][f]["tx_lost"]} | {stats[2][3][f]["tx_lost"]} {stats[2][2][f]["tx_lost"]} {stats[2][1][f]["tx_lost"]} | {stats[3][3][f]["tx_lost"]} {stats[3][2][f]["tx_lost"]} {stats[3][1][f]["tx_lost"]} | {stats[4][3][f]["tx_lost"]} {stats[4][2][f]["tx_lost"]} {stats[4][1][f]["tx_lost"]} | \n \
                    rx_lost \        | {stats[1][3][f]["rx_lost"]} {stats[1][2][f]["rx_lost"]} {stats[1][1][f]["rx_lost"]} | {stats[2][3][f]["rx_lost"]} {stats[2][2][f]["rx_lost"]} {stats[2][1][f]["rx_lost"]} | {stats[3][3][f]["rx_lost"]} {stats[3][2][f]["rx_lost"]} {stats[3][1][f]["rx_lost"]} | {stats[4][3][f]["rx_lost"]} {stats[4][2][f]["rx_lost"]} {stats[4][1][f]["rx_lost"]} | \n \
                    min_interval \   | {stats[1][3][f]["min_interval"]} {stats[1][2][f]["min_interval"]} {stats[1][1][f]["min_interval"]} | {stats[2][3][f]["min_interval"]} {stats[2][2][f]["min_interval"]} {stats[2][1][f]["min_interval"]} | {stats[3][3][f]["min_interval"]} {stats[3][2][f]["min_interval"]} {stats[3][1][f]["min_interval"]} | {stats[4][3][f]["min_interval"]} {stats[4][2][f]["min_interval"]} {stats[4][1][f]["min_interval"]} | \n \
                    max_interval    | {stats[1][3][f]["max_interval"]} {stats[1][2][f]["max_interval"]} {stats[1][1][f]["max_interval"]} | {stats[2][3][f]["max_interval"]} {stats[2][2][f]["max_interval"]} {stats[2][1][f]["max_interval"]} | {stats[3][3][f]["max_interval"]} {stats[3][2][f]["max_interval"]} {stats[3][1][f]["max_interval"]} | {stats[4][3][f]["max_interval"]} {stats[4][2][f]["max_interval"]} {stats[4][1][f]["max_interval"]} | \n "
            )

        print(stats)