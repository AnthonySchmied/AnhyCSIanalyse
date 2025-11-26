from pathlib import Path
from datetime import datetime

from components.sens_ops import SensOps as so
from components.recording_session_collection import RecordingSessionCollection
from components.metadata_unpack import MetadataUnpack as MDP
from widgets.correlation_plot_holo import CorrelationPlot

class CorrelationRisingPicture:
    _subpath = "corr_rising_1s_5s-3s"
    def __init__(self):
        self._make_out_dir()
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
            receivers=MDP.receivers_unpack([1, 2, 3]),
            days=MDP.days_unpack([1,2,3,4]),
            names=MDP.names_unpack(["a", "h", "e", "i", "emt"]),
        )
        
        self._plot_batches(batches, 6, 5)
        
    def _plot_batches(self, batches, image_shifts, cols, freq=100):
        for idx, batch in enumerate(batches):
            time = datetime.now()
            self._plot_batch(batch, image_shifts, cols, freq)
            print(f"saved: {idx+1}/{len(batches)} in: {datetime.now()-time} total: {datetime.now()-self._start_time} {batch[0].get_id()}")

    def _plot_batch(self, batch, image_shifts, cols, freq):
        recs = [ses.get_recording_freq(freq) for ses in batch]
        for image_shift in range(image_shifts):    
            plot = CorrelationPlot()
            for rec in recs:
                sub_plot = plot.add_recording(rec)
                for i in range(cols):
                    start_time = (image_shift*10000)+1000
                    offset = 0
                    length = 1000+i*(10*freq)
                    print(f"time: {start_time} - offset: {offset} - length: {length}")
                    rec.set_mask_frames_at_time(start_time, offset, length)
                    data = rec.get_amplitudes()
                    data = so.smooth(data)
                    data = so.normalized(data)
                    data = so.centered(data)
                    corr = so.pearson_correlation(data)
                    sub_plot.append(corr)
            plot.save(self._get_filepath_for_batch(batch, freq, image_shift))

    def _collect_batches(
        self,
        receivers,
        days,
        names,
        senders=[("Sender-1", "75eb44")],
        modes=["empty", "1 person", "2 person"],
    ):
        batches = []
        for day in days:
            for name in names:
                batches.extend(
                    self._get_batch(senders, receivers, [day], modes, [name])
                )
        return [self._sort_batch_desc(batch) for batch in batches]

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
            return [times[time] for time in times.keys()]
        else:
            return [batches]

    def _sort_batch_desc(self, batch):
        batch.sort(
            key=lambda item: item.get_receivers_name_mac()[0],
            reverse=True,
        )
        return batch

    def _make_out_dir(self):
        p = Path("plots", self._subpath)
        p.mkdir(parents=True, exist_ok=True)

    def _get_filepath_for_batch(self, batch, freqs, i):
        file = f"{batch[0].get_name()}_{freqs}_{batch[0].get_datetime()}_{i}.png"
        return Path("plots", self._subpath, file)
