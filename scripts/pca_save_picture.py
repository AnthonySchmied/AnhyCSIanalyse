from pathlib import Path
import datetime


from components.sens_ops import SensOps as so
from components.recording_session_collection import RecordingSessionCollection
from widgets.pca_plot import PcaPlot


class PcaSavePicture:
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
                ("Recv-1", "46ef78"),
                ("Recv-2", "73d1b8"),
                ("Recv-3", "46e648"),
            ],
            dates=[
                datetime.date(2025, 11, 4),
                datetime.date(2025, 11, 5),
                datetime.date(2025, 11, 11),
                datetime.date(2025, 11, 12),
            ],
            names=[
                "hussein",
                "hussein-anthony",
                "anthony-hussein",
                "ian",
                "ian-estelle",
                "estelle",
                "empty",
                "estelle-ian",
                "anthony",
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
                batch = self._get_batch(senders, receivers, [date], modes, [name])
                if len(batch) > 0:
                    batch.sort(
                        key=lambda item: item.get_receivers_name_mac()[0], reverse=True
                    )
                    recs = []
                    for ses in batch:
                        rec = ses.get_recording(freqs=freqs)[0]
                        recs.append(rec)
                    
                    plot = PcaPlot()
                    plot_time = datetime.datetime.now()
                    for image_shift_i in range(20):
                        for ses_i in range(len(batch)):
                            sub_plot = plot.add_row(recs[ses_i])
                            for i in range(10):
                                recs[ses_i].set_mask_frames_at_time(
                                    1000, (30 * 9 * image_shift_i) + (30 * i), 200
                                )
                                data = recs[ses_i].get_amplitudes()
                                pca = so.pca(data)
                                sub_plot.append(pca)
                                
                            #     data = so.normalized(data)
                            #     data = so.centered(data)
                            #     # data = so.smooth(data)
                            #     corr = so.pearson_correlation(data)
                            #     sub_plot.append(corr)
                        plot.save(
                            self._get_filepath_for_batch(batch, freqs, image_shift_i)
                        )
                    break
                break

    def _get_batch(self, senders, receivers, dates, modes, names):
        batch = []
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
            batch.append(ses)

        return batch

    def _get_filepath_for_batch(self, batch, freqs, i):
        file = f"{batch[0].get_name()}_{freqs}_{batch[0].get_datetime()}_{i}.png"
        return Path("plots", "pca", file)
