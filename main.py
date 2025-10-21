import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea
from pathlib import Path

from components.recording_session import RecordingSession
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
        
        session_anthony = RecordingSession(
            Path("rec/20251021_084451_Anthony-1 person_static")
        )
        session_empty = RecordingSession(Path("rec/20251021_084851_empty_static"))
        session_anthony_2 = RecordingSession(
            Path("rec/20251021_150423_Anthony-1 person_static")
        )
        session_empty_2 = RecordingSession(Path("rec/20251021_150834_empty_static"))

        session_anthony.remove_subcarrier(
            [1, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]
        )
        session_empty.remove_subcarrier([1, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38])
        session_anthony_2.remove_subcarrier(
            [1, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]
        )
        session_empty_2.remove_subcarrier([1, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38])

        cut_first_ms = 5000
        total_length_ms = 3000

        session_anthony.split_and_cut_subrecordings(cut_first_ms, total_length_ms)
        session_empty.split_and_cut_subrecordings(cut_first_ms, total_length_ms)
        session_anthony_2.split_and_cut_subrecordings(cut_first_ms, total_length_ms)
        session_empty_2.split_and_cut_subrecordings(cut_first_ms, total_length_ms)

        # print(
        #     session_anthony.get_recording(None, None, [100])[
        #         0
        #     ].get_mean_amplitude_per_id()
        # )

        # print([0].get_mean_amplitude_per_id())

        print(session_anthony.get_senders_name_mac())
        print(session_anthony.get_receivers_name_mac())
        print(session_anthony.get_frequencies())

        freqs = [100, 50, 25, 20, 10]

        for f in freqs:
            self.plot_amplitudes(
                session_anthony, cut_first_ms, total_length_ms, "75eb44", "46ef78", [f]
            )
            self.plot_amplitudes(
                session_anthony_2, cut_first_ms, total_length_ms, "75eb44", "46ef78", [f]
            )
            # self.plot_amplitudes(
            #     session_anthony, cut_first_ms, total_length_ms, "75eb44", "73d1b8", [f]
            # )
            self.plot_amplitudes(
                session_empty, cut_first_ms, total_length_ms, "75eb44", "46ef78", [f]
            )
            self.plot_amplitudes(
                session_empty_2, cut_first_ms, total_length_ms, "75eb44", "46ef78", [f]
            )
            # self.plot_amplitudes(
            #     session_empty, cut_first_ms, total_length_ms, "75eb44", "73d1b8", [f]
            # )

    def plot_amplitudes(
        self,
        rec_sess,
        cut_first_ms,
        total_length_ms,
        sender_mac,
        receiver_mac,
        freqs,
    ):
        rec_sess.split_and_cut_subrecordings(cut_first_ms, total_length_ms)
        recs = rec_sess.get_recording(sender_mac, receiver_mac, freqs)
        f = []
        for rec in recs:
            rec_freq = rec.get_frequencies()[0]  # check if unique -> take first
            if not rec_freq in f:
                f.append(rec_freq)
                # print(rec)
                plot = AmplitudePlot(rec)
                self.plots.append(plot)
                self.scroll_layout.addWidget(plot)


def main():
    app = QApplication(sys.argv)

    # Get folder path from command-line argument
    folder_path = sys.argv[1] if len(sys.argv) > 1 else None

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
