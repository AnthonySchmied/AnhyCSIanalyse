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
        # self.just_print()
        # exit()

        self.sc = RecordingSessionCollection(
            [
                Path("rec/01_recording/"),
                Path("rec/02_recording/"),
                Path("rec/03_recording/"),
                Path("rec/04_recording/"),
            ]
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

        recs = self.sc.get_recordings_set()
        # sub_recs = []
        print(len(recs))

        for rec in recs:
            print("read")
            rec.split_by_frequency()
            sub_recs = rec.get_subrecordings()
            for sub in sub_recs:

                date_packed = sub.get_date_packed()[0]
                recv_packed = sub.get_recv_packed()[0]
                if len(sub.get_frequencies()) > 1:
                    exit(sub.get_frequencies())
                frequency = int(sub.get_frequencies()[0])

                print("--------------------------------------------------------------------------------------------")
                # print(recv_packed)
                # print(stats[date_packed][recv_packed][frequency])
                # print(sub)

                print(f"d {date_packed}, r {recv_packed}, f {frequency}")
                stats[date_packed][recv_packed][frequency][
                    "tx_count"
                ] += sub.get_tx_packets_count()

                stats[date_packed][recv_packed][frequency][
                    "rx_count"
                ] += sub.get_rx_packets_count()

                if stats[date_packed][recv_packed][frequency]["mean_interval"] is None:
                    stats[date_packed][recv_packed][frequency]["mean_interval"] = sub.get_mean_rx_interval()
                else:
                    stats[date_packed][recv_packed][frequency]["mean_interval"] = np.mean([sub.get_mean_rx_interval(), stats[date_packed][recv_packed][frequency]["mean_interval"]])

                stats[date_packed][recv_packed][frequency][
                    "tx_lost"
                ] += sub.get_tx_packets_lost()

                stats[date_packed][recv_packed][frequency][
                    "rx_lost"
                ] += sub.get_rx_packets_lost()

                # stats[date_packed][recv_packed][frequency]["all_intervals"].extend(sub.get_all_rx_intervals())
                # print(stats[date_packed][recv_packed][frequency]["all_intervals"])

                max = np.max(sub.get_max_tx_interval())
                # print(max)
                # print(stats[date_packed][recv_packed][frequency]["max_interval"])
                stats[date_packed][recv_packed][frequency]["max_interval"] = np.max([stats[date_packed][recv_packed][frequency]["max_interval"], max])

                min = np.min(sub.get_min_rx_interval())
                # print(min)
                # print(stats[date_packed][recv_packed][frequency]["min_interval"])
                stats[date_packed][recv_packed][frequency]["min_interval"] = np.min([stats[date_packed][recv_packed][frequency]["min_interval"], min])

                # print(stats[date_packed][recv_packed][frequency])
                # print(stats)
                # exit()

        for d in stats.keys():
            for r in stats[d].keys():
                for f in stats[d][r].keys():
                    stats[d][r][f]["tx_ratio"] = 1 - (stats[d][r][f]["tx_lost"] / (stats[d][r][f]["tx_lost"]+stats[d][r][f]["tx_count"]))

                    # if len(stats[d][r][f]["all_intervals"]) > 0:
                        # stats[d][r][f]["median_interval"] = np.median(stats[d][r][f]["all_intervals"])
                    # stats[d][r][f]["all_intervals"] = []

        print(stats)

        exit()

        print(type(sub_recs))
        for rec in sub_recs:
            print(rec)
            date_packed = rec.get_date_packed()[0]
            recv_packed = rec.get_recv_packed()[0]
            frequency = int(rec.get_frequencies()[0])
            print(f"d {date_packed}, r {recv_packed}, f {frequency}")
            stats[date_packed][recv_packed][frequency][
                "tx_count"
            ] = rec.get_tx_packets_count()

            stats[date_packed][recv_packed][frequency][
                "rx_count"
            ] = rec.get_rx_packets_count()

            stats[date_packed][recv_packed][frequency][
                "tx_lost"
            ] = rec.get_tx_packets_lost()

            stats[date_packed][recv_packed][frequency][
                "rx_lost"
            ] = rec.get_rx_packets_lost()

            stats[date_packed][recv_packed][frequency]["max_interval"] = np.max(
                rec.get_max_tx_interval()
            )
            stats[date_packed][recv_packed][frequency]["min_interval"] = np.min(
                rec.get_min_tx_interval()
            )

            print(stats[date_packed][recv_packed][frequency])

        print(stats)

    def just_print(self):
        stats = {1: {3: {10: {'tx_count': 5988, 'rx_count': 5893, 'tx_lost': 95, 'rx_lost': 0, 'max_interval': np.float64(300.0), 'min_interval': np.float64(47.431)}, 25: {'tx_count': 14988, 'rx_count': 14784, 'tx_lost': 204, 'rx_lost': 0, 'max_interval': np.float64(160.0), 'min_interval': np.float64(0.173)}, 50: {'tx_count': 29990, 'rx_count': 29416, 'tx_lost': 574, 'rx_lost': 0, 'max_interval': np.float64(80.0), 'min_interval': np.float64(0.173)}, 100: {'tx_count': 59990, 'rx_count': 59024, 'tx_lost': 966, 'rx_lost': 0, 'max_interval': np.float64(40.0), 'min_interval': np.float64(0.147)}}, 2: {10: {'tx_count': 5988, 'rx_count': 5935, 'tx_lost': 53, 'rx_lost': 0, 'max_interval': np.float64(300.0), 'min_interval': np.float64(47.432)}, 25: {'tx_count': 14990, 'rx_count': 14856, 'tx_lost': 134, 'rx_lost': 0, 'max_interval': np.float64(120.0), 'min_interval': np.float64(0.174)}, 50: {'tx_count': 29989, 'rx_count': 29566, 'tx_lost': 423, 'rx_lost': 0, 'max_interval': np.float64(100.0), 'min_interval': np.float64(0.152)}, 100: {'tx_count': 59989, 'rx_count': 59273, 'tx_lost': 716, 'rx_lost': 0, 'max_interval': np.float64(30.0), 'min_interval': np.float64(0.142)}}, 1: {10: {'tx_count': 5989, 'rx_count': 5949, 'tx_lost': 40, 'rx_lost': 0, 'max_interval': np.float64(300.0), 'min_interval': np.float64(47.429)}, 25: {'tx_count': 14990, 'rx_count': 14873, 'tx_lost': 117, 'rx_lost': 0, 'max_interval': np.float64(120.0), 'min_interval': np.float64(0.173)}, 50: {'tx_count': 29990, 'rx_count': 29675, 'tx_lost': 315, 'rx_lost': 0, 'max_interval': np.float64(80.0), 'min_interval': np.float64(0.164)}, 100: {'tx_count': 59990, 'rx_count': 59463, 'tx_lost': 527, 'rx_lost': 0, 'max_interval': np.float64(30.0), 'min_interval': np.float64(0.139)}}}, 2: {3: {10: {'tx_count': 7188, 'rx_count': 7083, 'tx_lost': 105, 'rx_lost': 0, 'max_interval': np.float64(300.0), 'min_interval': np.float64(28.884)}, 25: {'tx_count': 14990, 'rx_count': 14800, 'tx_lost': 190, 'rx_lost': 0, 'max_interval': np.float64(160.0), 'min_interval': np.float64(0.222)}, 50: {'tx_count': 35987, 'rx_count': 35595, 'tx_lost': 392, 'rx_lost': 0, 'max_interval': np.float64(60.0), 'min_interval': np.float64(0.153)}, 100: {'tx_count': 59987, 'rx_count': 59351, 'tx_lost': 636, 'rx_lost': 0, 'max_interval': np.float64(50.0), 'min_interval': np.float64(0.138)}}, 2: {10: {'tx_count': 7187, 'rx_count': 7128, 'tx_lost': 59, 'rx_lost': 0, 'max_interval': np.float64(200.0), 'min_interval': np.float64(28.885)}, 25: {'tx_count': 14990, 'rx_count': 14830, 'tx_lost': 160, 'rx_lost': 0, 'max_interval': np.float64(80.0), 'min_interval': np.float64(0.22)}, 50: {'tx_count': 35986, 'rx_count': 35736, 'tx_lost': 250, 'rx_lost': 0, 'max_interval': np.float64(80.0), 'min_interval': np.float64(0.164)}, 100: {'tx_count': 59990, 'rx_count': 59462, 'tx_lost': 528, 'rx_lost': 0, 'max_interval': np.float64(30.0), 'min_interval': np.float64(0.147)}}, 1: {10: {'tx_count': 7188, 'rx_count': 7148, 'tx_lost': 40, 'rx_lost': 0, 'max_interval': np.float64(200.0), 'min_interval': np.float64(28.877)}, 25: {'tx_count': 14990, 'rx_count': 14896, 'tx_lost': 94, 'rx_lost': 0, 'max_interval': np.float64(120.0), 'min_interval': np.float64(0.22)}, 50: {'tx_count': 35988, 'rx_count': 35812, 'tx_lost': 176, 'rx_lost': 0, 'max_interval': np.float64(60.0), 'min_interval': np.float64(0.164)}, 100: {'tx_count': 59990, 'rx_count': 59682, 'tx_lost': 308, 'rx_lost': 0, 'max_interval': np.float64(30.0), 'min_interval': np.float64(0.139)}}}, 3: {3: {10: {'tx_count': 5990, 'rx_count': 5942, 'tx_lost': 48, 'rx_lost': 0, 'max_interval': np.float64(200.0), 'min_interval': np.float64(49.677)}, 25: {'tx_count': 14990, 'rx_count': 14887, 'tx_lost': 103, 'rx_lost': 0, 'max_interval': np.float64(120.0), 'min_interval': np.float64(0.203)}, 50: {'tx_count': 29989, 'rx_count': 29822, 'tx_lost': 167, 'rx_lost': 0, 'max_interval': np.float64(60.0), 'min_interval': np.float64(0.157)}, 100: {'tx_count': 59990, 'rx_count': 59634, 'tx_lost': 356, 'rx_lost': 0, 'max_interval': np.float64(30.0), 'min_interval': np.float64(0.144)}}, 2: {10: {'tx_count': 5990, 'rx_count': 5910, 'tx_lost': 80, 'rx_lost': 0, 'max_interval': np.float64(200.0), 'min_interval': np.float64(49.677)}, 25: {'tx_count': 14989, 'rx_count': 14816, 'tx_lost': 173, 'rx_lost': 0, 'max_interval': np.float64(160.0), 'min_interval': np.float64(0.21)}, 50: {'tx_count': 29990, 'rx_count': 29685, 'tx_lost': 305, 'rx_lost': 0, 'max_interval': np.float64(60.0), 'min_interval': np.float64(0.166)}, 100: {'tx_count': 59990, 'rx_count': 59343, 'tx_lost': 647, 'rx_lost': 0, 'max_interval': np.float64(30.208), 'min_interval': np.float64(0.154)}}, 1: {10: {'tx_count': 5990, 'rx_count': 5918, 'tx_lost': 72, 'rx_lost': 0, 'max_interval': np.float64(300.0), 'min_interval': np.float64(49.681)}, 25: {'tx_count': 14990, 'rx_count': 14827, 'tx_lost': 163, 'rx_lost': 0, 'max_interval': np.float64(120.0), 'min_interval': np.float64(0.211)}, 50: {'tx_count': 29990, 'rx_count': 29663, 'tx_lost': 327, 'rx_lost': 0, 'max_interval': np.float64(60.0), 'min_interval': np.float64(0.168)}, 100: {'tx_count': 59990, 'rx_count': 59410, 'tx_lost': 580, 'rx_lost': 0, 'max_interval': np.float64(40.0), 'min_interval': np.float64(0.145)}}}, 4: {3: {10: {'tx_count': 5990, 'rx_count': 5965, 'tx_lost': 25, 'rx_lost': 0, 'max_interval': np.float64(200.0), 'min_interval': np.float64(51.965)}, 25: {'tx_count': 14989, 'rx_count': 14904, 'tx_lost': 85, 'rx_lost': 0, 'max_interval': np.float64(80.0), 'min_interval': np.float64(0.183)}, 50: {'tx_count': 32989, 'rx_count': 32703, 'tx_lost': 286, 'rx_lost': 0, 'max_interval': np.float64(60.126), 'min_interval': np.float64(0.148)}, 100: {'tx_count': 59990, 'rx_count': 59676, 'tx_lost': 314, 'rx_lost': 0, 'max_interval': np.float64(20.126), 'min_interval': np.float64(0.146)}}, 2: {10: {'tx_count': 5990, 'rx_count': 5909, 'tx_lost': 81, 'rx_lost': 0, 'max_interval': np.float64(300.0), 'min_interval': np.float64(51.966)}, 25: {'tx_count': 14990, 'rx_count': 14800, 'tx_lost': 190, 'rx_lost': 0, 'max_interval': np.float64(120.0), 'min_interval': np.float64(0.183)}, 50: {'tx_count': 32988, 'rx_count': 32384, 'tx_lost': 604, 'rx_lost': 0, 'max_interval': np.float64(80.126), 'min_interval': np.float64(0.147)}, 100: {'tx_count': 59990, 'rx_count': 59170, 'tx_lost': 820, 'rx_lost': 0, 'max_interval': np.float64(40.0), 'min_interval': np.float64(0.136)}}, 1: {10: {'tx_count': 5990, 'rx_count': 5915, 'tx_lost': 75, 'rx_lost': 0, 'max_interval': np.float64(300.0), 'min_interval': np.float64(51.963)}, 25: {'tx_count': 14989, 'rx_count': 14842, 'tx_lost': 147, 'rx_lost': 0, 'max_interval': np.float64(120.0), 'min_interval': np.float64(0.184)}, 50: {'tx_count': 32987, 'rx_count': 32440, 'tx_lost': 547, 'rx_lost': 0, 'max_interval': np.float64(60.0), 'min_interval': np.float64(0.148)}, 100: {'tx_count': 59990, 'rx_count': 59253, 'tx_lost': 737, 'rx_lost': 0, 'max_interval': np.float64(40.0), 'min_interval': np.float64(0.147)}}}}

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
