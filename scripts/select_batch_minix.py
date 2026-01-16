from components.batch import Batch
from components.recording_session_collection import RecordingSessionCollection

class _SelectBatchMinix:
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