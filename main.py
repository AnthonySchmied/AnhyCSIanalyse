import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea
from pathlib import Path

from components.recording_session_collection import RecordingSessionCollection
from components.recording_session import RecordingSession
from components.amplitudes import Amplitudes
from components.sens_ops import SensOps as so
from widgets.amplitude_plot import AmplitudePlot


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSI Analyzer")
        self.resize(1920, 1000)

        # # Main layout for the scroll area container
        layout = QVBoxLayout(self)

        # Create the scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)  # Important: widget resizes with scroll area

        # Inner widget that holds the actual content
        content = QWidget()
        self.scroll_layout = QVBoxLayout(content)

        content.setLayout(self.scroll_layout)

        # Set the inner widget as the scroll area's widget
        scroll.setWidget(content)

        # Add scroll area to the main layout
        layout.addWidget(scroll)
        self.setLayout(layout)

        self.plots = []

        cut_first_ms = 5000
        total_length_ms = 15000

        def get_prepared_session(path):
            session = RecordingSession(Path(path))
            session.split_by_frequency()
            session.split_and_cut_subrecordings(cut_first_ms, total_length_ms)
            return session

        # ses_anthony_morning = get_prepared_session(
        #     "rec/20251021_084451_Anthony-1 person_static"
        # )
        # ses_empty_morning = get_prepared_session("rec/20251021_084851_empty_static")
        # ses_anthony_afternoon = get_prepared_session(
        #     "rec/20251021_150423_Anthony-1 person_static"
        # )
        # ses_empty_afternoon = get_prepared_session("rec/20251021_150834_empty_static")

        # [('Recv-2', '73d1b8'), ('Recv-1', '46ef78'), ('Recv-3', '46e648')]

        recordings = []
        def session_all():
            session_coll = RecordingSessionCollection([Path("rec/01_recording/"),Path("rec/02_recording/")], ["anthony", "estelle", "ian", "hussein"], ["empty", "1 person"])
            session_coll.sort_by_name_asc()
            
            sessions = session_coll.get_sessions()
        
            for ses in sessions:
                print(ses.get_name())

                ses.split_by_frequency()
                ses.split_and_cut_subrecordings(cut_first_ms, total_length_ms)

                # r3 = ses.get_recording("75eb44", "46e648", [100])[0].get_amplitudes()
                r2 = ses.get_recording("75eb44", "73d1b8", [100])[0].get_amplitudes()
                # r1 = ses.get_recording("75eb44", "46ef78", [100])[0].get_amplitudes()
                # recordings.extend([r3,r2,r1])
                recordings.append(r2)

            for data in recordings:
                # plot = self.plot_amplitudes(data, min_y=5, max_y=20)
                # plot.plot_amplitudes(data.get_by_subcarriers())

                data = so.normalized(data)
                plot = self.plot_amplitudes(data, max_y=5)
                plot.plot_ftt(so.calculate_ftt(data))

        session_all()

        def session_specific():
            ses_empty_1 = get_prepared_session(
                "rec/01_recording/20251104_124422_empty_static"
            )
            ses_anthony = get_prepared_session(
                "rec/01_recording/20251104_133450_anthony-1 person_static"
            )
            ses_empty_2 = get_prepared_session(
                "rec/01_recording/20251104_134029_empty_static"
            )

            anthony_1_100_r2 = ses_anthony.get_recording("75eb44", "73d1b8", [100])[
                0
            ].get_amplitudes()
            recordings.append(anthony_1_100_r2)

            for data in recordings:

                plot = self.plot_amplitudes(data, min_y=5, max_y=20)
                plot.plot_amplitudes(data.get_by_subcarriers())


                # data = so.bandpassed(so.normalized(data), 5, 25, 4)
                data = so.bandpassed(data, 5, 40, 4)
                # data = so.hampeled(data, 100, 2)
                plot = self.plot_amplitudes(data, min_y=-10, max_y=10)
                plot.plot_amplitudes(data.get_by_subcarriers())

                # # data = so.abs(data)

                # plot = self.plot_amplitudes(data, max_y=100)
                # plot.plot_ftt(so.calculate_ftt(data))

                # data = so.normalized(data)
                # plot = self.plot_amplitudes(data, min_y=-5, max_y=20)
                # plot.plot_amplitudes(data.get_by_subcarriers())

                plot = self.plot_amplitudes(data, max_y=5)
                plot.plot_ftt(so.calculate_ftt(data))

        # session_specific()

        def session_complex():
            ses_empty_1 = get_prepared_session(
                "rec/01_recording/20251104_124422_empty_static"
            )
            ses_anthony = get_prepared_session(
                "rec/01_recording/20251104_133450_anthony-1 person_static"
            )

            anthony_1_100_r2 = ses_anthony.get_recording("75eb44", "73d1b8", [100])[
                0
            ].get_complex_values()

            empty_1_100_r2 = ses_empty_1.get_recording("75eb44", "73d1b8", [100])[
                0
            ].get_complex_values()
            anthony_1_100_r2.subcarrier_enable([i for i in range(1,64) if not (i % 8)])
            empty_1_100_r2.subcarrier_enable([i for i in range(1,64) if not (i % 8)])
            recordings.append(anthony_1_100_r2)
            recordings.append(empty_1_100_r2)

            for data in recordings:
                plot_real, plot_imanginary = self.plot_complex(data, min_y=-30, max_y=30)               
                plot_real.plot_amplitudes(data.get_real_by_subcarriers())
                plot_imanginary.plot_amplitudes(data.get_imag_by_subcarriers())


                # plot = self.plot_amplitudes(data, max_y=5)
                # plot.plot_ftt(so.calculate_ftt(data))


        # session_complex()

            # empty_1_100_r3 = ses_empty_1.get_recording("75eb44", "46e648", [100])[
            #     0
            # ].get_amplitudes()
            # recordings.append(empty_1_100_r3)
            # empty_1_100_r2 = ses_empty_1.get_recording("75eb44", "73d1b8", [100])[
            #     0
            # ].get_amplitudes()
            # recordings.append(empty_1_100_r2)
            # empty_1_100_r1 = ses_empty_1.get_recording("75eb44", "46ef78", [100])[
            #     0
            # ].get_amplitudes()
            # recordings.append(empty_1_100_r1)
            # anthony_1_100_r3 = ses_anthony.get_recording("75eb44", "46e648", [100])[
            #     0
            # ].get_amplitudes()
            # # recordings.append(anthony_1_100_r3)
            # anthony_1_100_r2 = ses_anthony.get_recording("75eb44", "73d1b8", [100])[
            #     0
            # ].get_amplitudes()
            # recordings.append(anthony_1_100_r2)
            # anthony_1_100_r1 = ses_anthony.get_recording("75eb44", "46ef78", [100])[
            #     0
            # ].get_amplitudes()
            # recordings.append(anthony_1_100_r1)
            # anthony_100_los = ses_anthony.get_recording("75eb44", "46ef78", [100])[
            #     0
            # ].get_amplitudes()
            # recordings.append(anthony_100_los)
            # empty_2_100_los = ses_empty_2.get_recording("75eb44", "46ef78", [100])[
            #     0
            # ].get_amplitudes()
            # recordings.append(empty_2_100_los)
            # empty_1_100_non_los = ses_empty_1.get_recording("75eb44", "73d1b8", [100])[
            #     0
            # ].get_amplitudes()
            # recordings.append(empty_1_100_non_los)
            # anthony_100_non_los = ses_anthony.get_recording("75eb44", "73d1b8", [100])[
            #     0
            # ].get_amplitudes()
            # recordings.append(anthony_100_non_los)
            # empty_2_100_non_los = ses_empty_2.get_recording("75eb44", "73d1b8", [100])[
            #     0
            # ].get_amplitudes()
            # recordings.append(empty_2_100_non_los)

        # bg_100_los = empty_1_100_los - anthony_100_los
        # recordings.append(bg_100_los)
        # empty_100_los = empty_1_100_los - empty_2_100_los
        # recordings.append(empty_100_los)

        # bg_100_non_los = empty_1_100_non_los - anthony_100_non_los
        # recordings.append(bg_100_non_los)
        # empty_100_non_los = empty_1_100_non_los - empty_2_100_non_los
        # recordings.append(empty_100_non_los)

        # morning_100_background_amp =  empty_afternoon_100_amp - anthony_morning_100_amp
        # afternoon_100_background_amp = empty_afternoon_100_amp - anthony_afternoon_100_amp

        # anthony_sub_amp = (anthony_morning_100_amp.normalize() - anthony_afternoon_100_amp.normalize())
        # emtpty_sub_amp = (empty_morning_100_amp.normalize() - empty_afternoon_100_amp.normalize())
        # anthony_morning_100_amp = anthony_morning_100_amp * 0.5
        # empty_morning_100_amp = empty_morning_100_amp * 0.5
        # anthony_morning_100_amp.normalize()
        # recordings = [
        #     anthony_morning_100_amp,
        #     so.bandpassed(anthony_morning_100_amp, 5, 45) + 0.5
        # ]

        # for data in recordings:
        #     # data.subcarrier_enable([25])
        #     # amps = so.hampeled(so.normalized(amps), 20, 5)
        #     # data = so.hampeled(data, 20, 5)

        #     plot = self.plot_amplitudes(data, min_y=5, max_y=20)
        #     plot.plot_amplitudes(data.get_by_subcarriers())

        #     # data = so.bandpassed(data, 5, 25, 4)
        #     # data = so.hampeled(data, 100, 2)
        #     # plot = self.plot_amplitudes(data, max_y=25)
        #     # plot.plot_amplitudes(data.get_by_subcarriers())

        #     # # data = so.abs(data)

        #     # plot = self.plot_amplitudes(data, max_y=100)
        #     # plot.plot_ftt(so.calculate_ftt(data))

        #     data = so.normalized(data)
        #     # plot = self.plot_amplitudes(data, min_y=-5, max_y=20)
        #     # plot.plot_amplitudes(data.get_by_subcarriers())

        #     plot = self.plot_amplitudes(data, max_y=5)
        #     plot.plot_ftt(so.calculate_ftt(data))

            # plot = self.plot_amplitudes(amps, max_y=80)
            # plot.plot_ftt(so.calculate_ftt(amps), x_limit=5)
            # print(so.calculate_ftt(amps))
            # self.plot_amplitudes(amps, so.calculate_ftt(amps))

        # session_anthony_2 = RecordingSession(
        #     Path("rec/20251021_150423_Anthony-1 person_static")
        # )
        # session_empty_2 = RecordingSession(Path("rec/20251021_150834_empty_static"))

        # session_anthony.remove_subcarrier(
        #     [1, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]
        # )
        # session_empty.remove_subcarrier([1, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38])
        # session_anthony_2.remove_subcarrier(
        #     [1, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]
        # )
        # session_empty_2.remove_subcarrier([1, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38])

        # cut_first_ms = 5000
        # total_length_ms = 3000

        # session_anthony.split_and_cut_subrecordings(cut_first_ms, total_length_ms)
        # session_empty.split_and_cut_subrecordings(cut_first_ms, total_length_ms)
        # session_anthony_2.split_and_cut_subrecordings(cut_first_ms, total_length_ms)
        # session_empty_2.split_and_cut_subrecordings(cut_first_ms, total_length_ms)

        # # print(
        # #     session_anthony.get_recording(None, None, [100])[
        # #         0
        # #     ].get_mean_amplitude_per_id()
        # # )

        # # print([0].get_mean_amplitude_per_id())

        # print(session_anthony.get_senders_name_mac())
        # print(session_anthony.get_receivers_name_mac())
        # print(session_anthony.get_frequencies())

        # cut_first_ms = 5000
        # total_length_ms = 10000

        # session_anthony = RecordingSession(
        #     "rec/20251027_150314_anthony-emily_2 person_static"
        # )
        # session_anthony.remove_subcarrier(
        #     [1, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]
        # )
        # session_anthony.split_by_frequency()
        # session_anthony.split_and_cut_subrecordings(cut_first_ms, total_length_ms)
        # print(session_anthony.get_receivers_name_mac())
        # amps50 = session_anthony.get_recording("75eb44", "46ef78", [50])[
        #     0
        # ].get_amplitudes()
        # amps50normalized = so.normalized(so.subcarrier_enabled(amps50, [2,25,40,50]))
        # self.plot_amplitudes(amps50normalized)
        # self.plot_amplitudes(so.hampeled(amps50.normalize(), 5, 2))

        # plot = AmplitudePlot(amps50normalized, max_value=1)
        # self.plots.append(plot)
        # self.scroll_layout.addWidget(plot)

        # amps100 = session_anthony.get_recording("75eb44", "46ef78", [100])[
        #     0
        # ].get_amplitudes()
        # print(amps100.normalized())
        # plot = AmplitudePlot(amps100, max_value=1)
        # self.plots.append(plot)
        # self.scroll_layout.addWidget(plot)

        # print(session_anthony)

        # freqs = [100, 50]

        # for f in freqs:
        #     self.plot_amplitudes(
        #         session_anthony, cut_first_ms, total_length_ms, "75eb44", "46ef78", [f]
        #     )
        #     # self.plot_amplitudes(
        #     #     session_anthony_2, cut_first_ms, total_length_ms, "75eb44", "46ef78", [f]
        #     # )
        #     # # self.plot_amplitudes(
        #     # #     session_anthony, cut_first_ms, total_length_ms, "75eb44", "73d1b8", [f]
        #     # # )
        #     # self.plot_amplitudes(
        #     #     session_empty, cut_first_ms, total_length_ms, "75eb44", "46ef78", [f]
        #     # )
        #     # self.plot_amplitudes(
        #     #     session_empty_2, cut_first_ms, total_length_ms, "75eb44", "46ef78", [f]
        #     # )
        #     # self.plot_amplitudes(
        #     #     session_empty, cut_first_ms, total_length_ms, "75eb44", "73d1b8", [f]
        #     # )

    # def plot_amplitudes(
    #     self,
    #     rec_sess,
    #     cut_first_ms,
    #     total_length_ms,
    #     sender_mac,
    #     receiver_mac,
    #     freqs,
    # ):
    #     rec_sess.split_and_cut_subrecordings(cut_first_ms, total_length_ms)
    #     recs = rec_sess.get_recording(sender_mac, receiver_mac, freqs)
    #     f = []
    #     for rec in recs:
    #         rec_freq = rec.get_frequencies()[0]  # check if unique -> take first
    #         if not rec_freq in f:
    #             f.append(rec_freq)
    #             # print(rec)
    #             plot = AmplitudePlot(rec)
    #             self.plots.append(plot)
    #             self.scroll_layout.addWidget(plot)

    def plot_amplitudes(self, amps_in, min_y=0, max_y=1):
        plot = AmplitudePlot(amps_in, min_y=min_y, max_y=max_y)
        self.plots.append(plot)
        self.scroll_layout.addWidget(plot)
        return plot

    def plot_complex(self, amps_in, min_y=0, max_y=1):
        plot_real = AmplitudePlot(amps_in, min_y=min_y, max_y=max_y)
        self.plots.append(plot_real)
        self.scroll_layout.addWidget(plot_real)

        plot_complex = AmplitudePlot(amps_in, min_y=min_y, max_y=max_y)
        self.plots.append(plot_complex)
        self.scroll_layout.addWidget(plot_complex)
        return plot_real, plot_complex

def main():
    app = QApplication(sys.argv)

    # Get folder path from command-line argument
    folder_path = sys.argv[1] if len(sys.argv) > 1 else None

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
