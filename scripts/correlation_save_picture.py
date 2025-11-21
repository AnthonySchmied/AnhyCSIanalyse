from pathlib import Path
import datetime

from components.sens_ops import SensOps as so
from components.recording_session_collection import RecordingSessionCollection
from widgets.correlation_plot_holo import CorrelationPlot


class CorrelationSavePicture:
    def __init__(self):
        self.session_coll = RecordingSessionCollection(
            [
                Path("rec/01_recording/"),
                Path("rec/02_recording/"),
                Path("rec/03_recording/"),
                Path("rec/04_recording/"),
            ]
        )

        self._plot_grouped_by_entity(
            receivers=[
                # ("Recv-1", "46ef78"),
                # ("Recv-2", "73d1b8"),
                ("Recv-3", "46e648"),
            ],
            dates=[
                datetime.date(2025, 11, 4),
                # datetime.date(2025, 11, 5),
                # datetime.date(2025, 11, 11),
                # datetime.date(2025, 11, 12),
            ],
            names=[
                "hussein",
                # "hussein-anthony",
                # "anthony-hussein",
                # "ian",
                # "ian-estelle",
                # "estelle",
                "empty",
                # "estelle-ian",
                # "anthony",
            ],
            modes=["empty", "1 person"],
        )

    def _plot_grouped_by_entity(
        self,
        senders=[("Sender-1", "75eb44")],
        receivers=[],
        dates=[],
        names=[],
        modes=[],
        freqs=[100],
    ):
        start_time = datetime.datetime.now()
        for name in names:
            for date in dates:
                print(name)
                batches = self._get_batch(senders, receivers, [date], modes, [name])
                if len(batches) > 0:
                    for batch in batches:
                        batch.sort(
                            key=lambda item: item.get_receivers_name_mac()[0], reverse=True
                        )
                        recs = []
                        for ses in batch:
                            rec = ses.get_recording(freqs=freqs)[0]
                            recs.append(rec)
                        plot_time = datetime.datetime.now()
                        plot = CorrelationPlot()
                        for image_shift_i in range(3):
                            sub_plot = plot.add_recording(recs[0])
                            # for ses_i in range(len(batch)):
                            for i in range(10):
                                recs[0].set_mask_frames_at_time(
                                    1000, image_shift_i*1000, (i*100)+100
                                )
                                data = recs[0].get_amplitudes()
                                data = so.normalized(data)
                                data = so.centered(data)
                                # data = so.smooth(data)
                                corr = so.correlation(data)
                                # print(corr)
                                # corr = so.pearson_correlation(data)
                                sub_plot.append(corr)
                        plot.save(
                            self._get_filepath_for_batch(batch, freqs, 0)
                        )
                        now = datetime.datetime.now()
                        print(f"this plot: {now-plot_time}")
                        print(f"total: {now-start_time}")
                    #     break
                    # break

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
            self.session_coll.get_recordings_set(),
        ):
            batches.append(ses)

        if len(batches) > len(receivers):
            times = {}
            for rec in batches:
                key = rec.get_datetime()
                if key not in times:
                    times[key] = []
                times[key].append(rec)
            batches = [times[time] for time in times.keys()]
            return batches
        else:
            return [batches]


    def _get_filepath_for_batch(self, batch, freqs, i):
        file = f"{batch[0].get_name()}_{freqs}_{batch[0].get_datetime()}_{i}.html"
        return Path("plots", file)
