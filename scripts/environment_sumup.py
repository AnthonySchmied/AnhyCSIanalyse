from pathlib import Path
import pandas as pd
import numpy as np

from scripts.select_batch_minix import _SelectBatchMinix
from components.recording_session_collection import RecordingSessionCollection
from components.metadata_unpack import MetadataUnpack as MDP
from widgets.plot_holo import Plot
from components.sens_ops import SensOps as so
from components.plot_container import PointcloudPlot, _PointcloudPlotResult


class EnvironmentSumup(_SelectBatchMinix):
    def __init__(self):
        self.sc = RecordingSessionCollection(
            [
                Path("rec/01_recording/"),
                Path("rec/02_recording/"),
                Path("rec/03_recording/"),
                Path("rec/04_recording/"),
            ]
        )

        batches = self._collect_batches(
            receivers=MDP.receivers_unpack([1]),
            days=MDP.days_unpack([1,2,3,4]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i"]),
            # names=MDP.names_unpack(["emt"]),
            names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
        )

        envs = []
        for batch in batches:
            batch.load_from_storage_freq(10) # needs to be run to load all the data for the id/label
            envs.append((batch[0].get_id(), batch.get_environment()))

        results = {}

        for label, env in envs:

            day = label.get_day()[0]
            
            if day not in results.keys():
                results[day] = {
                    "temperature": {
                        "mean": env.get_mean_temperature(),
                        "min": env.get_min_temperature(),
                        "max": env.get_min_temperature(),
                        "range": 0
                    },
                    "humidity" : {
                        "mean": env.get_mean_humidity(),
                        "min": env.get_min_humidity(),
                        "max": env.get_min_humidity(),
                        "range": 0
                    },
                    "pressure" : {
                        "mean": env.get_mean_pressure(),
                        "min": env.get_min_pressure(),
                        "max": env.get_min_pressure(),
                        "range": 0
                    },
                }
            else:
                results[day]["temperature"]["mean"] = np.mean([results[day]["temperature"]["mean"], env.get_mean_temperature()])
                results[day]["temperature"]["min"] = np.min([results[day]["temperature"]["min"], env.get_min_temperature()])
                results[day]["temperature"]["max"] = np.max([results[day]["temperature"]["max"], env.get_max_temperature()])
                results[day]["temperature"]["range"] = results[day]["temperature"]["max"]-results[day]["temperature"]["min"]


                results[day]["humidity"]["mean"] = np.mean([results[day]["humidity"]["mean"], env.get_mean_humidity()])
                results[day]["humidity"]["min"] = np.min([results[day]["humidity"]["min"], env.get_min_humidity()])
                results[day]["humidity"]["max"] = np.max([results[day]["humidity"]["max"], env.get_max_humidity()])
                results[day]["humidity"]["range"] = results[day]["humidity"]["max"]-results[day]["humidity"]["min"]

                results[day]["pressure"]["mean"] = np.mean([results[day]["pressure"]["mean"], env.get_mean_pressure()])
                results[day]["pressure"]["min"] = np.min([results[day]["pressure"]["min"], env.get_min_pressure()])
                results[day]["pressure"]["max"] = np.max([results[day]["pressure"]["max"], env.get_max_pressure()])
                results[day]["pressure"]["range"] = results[day]["pressure"]["max"]-results[day]["pressure"]["min"]
            
            # print(day)

            # print(env)

        print(results)