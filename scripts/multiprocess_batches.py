from datetime import datetime 
from pathlib import Path

from components.recording_session_collection import RecordingSessionCollection
from components.batch import Batch
from components.metadata_unpack import MetadataUnpack as MDP
from scripts.processings import Rising, Shifting, MultTrans
from components.plot_container import CorrelationIndexPlot

# class CorrelationResult():
#     def __init__(self):
#         pass

class CorrelationIndexCollector():
    def __init__(self):
        self._data = {}

    def register(self, batch):
        self._batch = batch
        if batch.get_id() not in self._data.keys():
            self._data[batch.get_id()] = {}

    def append(self, batch, idx, mean_corr):
        if idx not in self._data[batch.get_id()].keys():
            self._data[batch.get_id()][idx] = []
        self._data[batch.get_id()][idx].append(mean_corr)

    def get_by_day(self):
        pass


class MultiprocessBatches():
    def __init__(self):
        self._start_time = datetime.now()

        self.sc = RecordingSessionCollection(
            [
                Path("rec/01_recording/"),
                Path("rec/02_recording/"),
                Path("rec/03_recording/"),
                Path("rec/04_recording/"),
            ]
        )

        batches = self._collect_batches(
            receivers=MDP.receivers_unpack([3,2,1]),
            days=MDP.days_unpack([1,2,3,4]),
            names=MDP.names_unpack(["emt"]),
        )
        self._plot_batches(batches)

    def _plot_batches(self, batches):
        self.corr_index_collector = CorrelationIndexCollector()
        for idx, batch in enumerate(batches):
            time = datetime.now()
            self._plot_batch(batch)
            print(f"saved: {idx+1}/{len(batches)} in: {datetime.now()-time} total: {datetime.now()-self._start_time} each: {(datetime.now()-self._start_time)/(idx+1)}")

    def _plot_batch(self, batch, freq=100):
        # print(batch)
        batch.load_from_storage_freq(freq)

        # Rising(batch, self.corr_index_collector, "rising", freq)
        # Shifting(batch, self.corr_index_collector, "shifting", freq)

        MultTrans(batch, self.corr_index_collector, "multtrans", freq);

        # global result = Rising(batch)
        # correlation shift

        # returns correlation mean, median, max, min
        

        # correlation raise
        # returns correlation mean, median, max, min

        # pcr shift

        # pcr raise

    def _collect_batches(
        self,
        receivers,
        days,
        names,
        senders=[("Sender-1", "75eb44")],
        modes=["empty", "1 person", "2 person"]
        ):
        batches = []
        for day in days:
            for name in names:
                batches.extend(
                    self._get_batch(senders, receivers, [day], modes, [name])
                )
        return batches        
            
    def _get_batch(self, senders, receivers, dates, modes, names):
        batches = []
        for ses in filter(
            lambda ses: RecordingSessionCollection.applyFilter(
                ses,
                senders=senders,
                receivers=receivers,
                dates=dates,
                names=names,
                modes=modes,
            ),
            self.sc.get_recordings_set(),
        ):
            batches.append(ses)
        
        if len(batches) > len(receivers):
            times = {}
            for rec in batches:
                key = rec.get_datetime()
                if key not in times:
                    times[key] = []
                times[key].append(rec)
            return [Batch(times[time]) for time in times.keys()]
        else:
            return [Batch(batches)]