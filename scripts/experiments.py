from pathlib import Path
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from components.recording_session_collection import RecordingSessionCollection
from components.batch import Batch
from components.metadata_unpack import MetadataUnpack as MDP
from widgets.plot_holo import Plot
from components.sens_ops import SensOps as so
from components.plot_container import PointcloudPlot, _PointcloudPlotResult


class _OneMinix:
    def ExperimentOne(self):

        # 4 Durchläufe mit je dem ersten Recording des Tages als Referenz.
        # Referenz wird über Standardabweichung und Mittelwert von PC1 und PC2 eingegrenzt. Dann werden je die anderen CSI als veränderung dazu genommen und entschieden ob neuer Datensatz im Empty Cluster liegt.

        # Das ganze bei 10 Hz und 25 Hz und 50 Hz und 100 Hz

        freq = 10

        ref_batch = self._collect_batches(
            receivers=MDP.receivers_unpack([3]),
            days=MDP.days_unpack([2]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i"]),
            # names=MDP.names_unpack(["emt"]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
            names=MDP.names_unpack(["emt"]),
        )

        scaler = StandardScaler()
        pca = PCA(n_components=4, svd_solver="full")

        for batch in ref_batch:

            batch.load_from_storage_freq(freq)
            reference_amp = batch.get_masked_amplitude(0, 0, 6000)[0]
            data = so.mask(reference_amp.df)

            data = data[reference_amp.columns].to_numpy()
            Xs = scaler.fit_transform(data)
            X_pca = pca.fit_transform(Xs)
            reference_pca = _PointcloudPlotResult(
                X_pca, eigenvectors=pca.components_, eigenvalues=pca.explained_variance_, label=reference_amp.recording.get_label()
            )

        print(len(reference_amp.df))
        print(f"mean: {reference_pca.get_mean()}")
        print(f"std: {reference_pca.get_std()}")
        print(f"range: {reference_pca.get_two_std_range()}")




        batches = self._collect_batches(
            receivers=MDP.receivers_unpack([3]),
            days=MDP.days_unpack([1,2,3,4]),
            names=MDP.names_unpack(["a", "e", "emt", "h", "i"]),
            # names=MDP.names_unpack(["emt"]),
            # names=MDP.names_unpack(["a", "e", "emt", "h", "i", "ei", "ie", "ha", "ah"]),
            # names=MDP.names_unpack(["emt"]),
        )

        pcs = []

        all_batches_counter = 0
        wrong_empty_batches_counter = 0
        wrong_presence_bateches_counter = 0

        for idx, batch in enumerate(batches):
            # batch = batches[0]
            batch.load_from_storage_freq(freq)
            amp = batch.get_masked_amplitude(0, 0, 6000)[0]

            # df = pd.concat([reference_amp.df, so.mask(amp.df)], ignore_index=True)
            df = so.mask(amp.df)

            data = df[amp.columns].to_numpy()
            Xs = scaler.transform(data)
            X_pca = pca.transform(Xs)
            # print(f"scaler: mean {scaler.mean_} - var {scaler.var_} - scale {scaler.scale_}")

            pca_result = _PointcloudPlotResult(
                X_pca, eigenvectors=pca.components_, eigenvalues=pca.explained_variance_, label=batch[0].get_id()
            )
            pcs.append(pca_result)
            all_batches_counter += 1

            print(pca_result.get_two_std_range())
            if pca_result.in_ref_range(reference_pca, 3):
                print(f"{batch[0].get_names()} is empty - mean: {pca_result.get_mean()}")
                if batch[0].get_names()[0] != "emt":
                    print(f"WRONG")
                    wrong_empty_batches_counter += 1
            else:
                # print(f"{batch.get_id()} is presence")
                print(f"{batch[0].get_names()} is presence - mean: {pca_result.get_mean()}")
                if batch[0].get_names()[0] == "emt":
                    print(f"WRONG - mean: {pca_result.get_mean()}")
                    wrong_presence_bateches_counter += 1

            print("-------------")


        print(f"wrong_rate: {wrong_empty_batches_counter+wrong_presence_bateches_counter/all_batches_counter}- wrong_empty:{wrong_empty_batches_counter} - wrong_presence:{wrong_presence_bateches_counter}")


        plot = Plot(6)

        plot.append_row_idx(0, PointcloudPlot(pcs, 1, 2))
        plot.append_row_idx(0, PointcloudPlot(pcs, 1, 3))
        plot.append_row_idx(0, PointcloudPlot(pcs, 1, 4))
        plot.save(Path("plots", "debug.png"))


            # print(f"mean: {reference_pca.get_mean()}")
            # print(f"std: {reference_pca.get_std()}")
            # print(f"range: {reference_pca.get_two_std_range()}")


class Experiments(_OneMinix):
    def __init__(self):
        self.sc = RecordingSessionCollection(
            [
                Path("rec/01_recording/"),
                Path("rec/02_recording/"),
                Path("rec/03_recording/"),
                Path("rec/04_recording/"),
            ]
        )

        one = self.ExperimentOne()

        exit()

        data = None
        labels_i = 0
        result_lengths_labels = []

        freqs = [10]

        for f in freqs:
            for idx, batch in enumerate(batches3):
                batch.load_from_storage_freq(f)
                amp = batch.get_masked_amplitude(0, 0, 6000)[0]
                result_lengths_labels.append((len(so.mask(amp.df)), batch[0].get_id()))
                if data is None:
                    data = amp
                else:
                    data.df = pd.concat([data.df, so.mask(amp.df)], ignore_index=True)

                print(data.df.shape)
                labels_i += 1
            print(f"{f}: {len(result_lengths_labels)}")

        plot = Plot(6)
        pc = so.pca_X(data, 4)

        print(len(pc._X_pca))
        print(len(pc._eigenvalues))
        print(len(pc._eigenvalues))

        print(result_lengths_labels)
        print(len(result_lengths_labels))

        # pc.set_label(batch[0].get_id())

        label_pc = []
        i = 0

        print(pc._X_pca.shape)
        for idx, (l, label) in enumerate(result_lengths_labels):
            # print(i, l+i)
            res = _PointcloudPlotResult(
                X_pca=pc._X_pca[i : l + i],
                eigenvectors=pc._eigenvectors,
                eigenvalues=pc._eigenvalues,
                label=label,
            )
            i += l

            print(res._X_pca.shape)

            label_pc.append(res)

        plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 2))
        plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 3))
        plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 4))
        plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 5))
        plot.append_row_idx(0, PointcloudPlot(label_pc, 1, 6))
        # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 1))
        # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 3))
        # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 4))
        # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 5))
        # plot.append_row_idx(1, PointcloudPlot(label_pc, 2, 6))
        # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 1))
        # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 2))
        # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 4))
        # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 5))
        # plot.append_row_idx(2, PointcloudPlot(label_pc, 3, 6))
        # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 1))
        # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 2))
        # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 3))
        # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 5))
        # plot.append_row_idx(3, PointcloudPlot(label_pc, 4, 6))
        # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 1))
        # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 2))
        # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 3))
        # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 4))
        # plot.append_row_idx(4, PointcloudPlot(label_pc, 5, 6))
        # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 1))
        # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 2))
        # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 3))
        # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 4))
        # plot.append_row_idx(5, PointcloudPlot(label_pc, 6, 5))
        plot.save(Path("plots", "pca_second_person_alldays.png"))
        exit()

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
