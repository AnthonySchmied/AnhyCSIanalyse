from pathlib import Path
import pandas as pd

from scripts.select_batch_minix import _SelectBatchMinix
from components.recording_session_collection import RecordingSessionCollection
from components.batch import Batch
from components.metadata_unpack import MetadataUnpack as MDP
from components.amplitudes import Amplitudes
from widgets.plot_holo import Plot
from components.sens_ops import SensOps as so
from components.plot_container import PointcloudPlot, _PointcloudPlotResult
from components.plot_container import EnvironmentPlotContainer

class EnvironmentPlot(_SelectBatchMinix):
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
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
            names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
        )

        env_plot = EnvironmentPlotContainer()
        plot = Plot(1)

        for idx, batch in enumerate(batches):
            batch.load_from_storage_freq(10) # needs to be run to load all the data for the id/label
            env = batch.get_environment()
            df = env.get_df()
            env_plot.append(range(len(df["timestamp_pc"])), df["pressure"], batch[0].get_id())


        plot.append_row_idx(0, env_plot)
        plot.save(Path("plots", "environment_pressure_all_days.png"))


