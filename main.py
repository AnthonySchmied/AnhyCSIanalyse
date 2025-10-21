import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QScrollArea
)
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


        print(session_anthony.get_senders_name_mac())
        print(session_anthony.get_receivers_name_mac())
        print(session_anthony.get_frequencies())

        cut_first_ms = 5000
        total_length_ms = 1000

        self.plot_amplitudes(
            session_anthony, cut_first_ms, total_length_ms, "75eb44", "46ef78", [100]
        )
        self.plot_amplitudes(
            session_anthony, cut_first_ms, total_length_ms, "75eb44", "73d1b8", [100]
        )
        self.plot_amplitudes(
            session_empty, cut_first_ms, total_length_ms, "75eb44", "46ef78", [100]
        )
        self.plot_amplitudes(
            session_empty, cut_first_ms, total_length_ms, "75eb44", "73d1b8", [100]
        )

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

    window = MainWindow(folder_path=folder_path)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
