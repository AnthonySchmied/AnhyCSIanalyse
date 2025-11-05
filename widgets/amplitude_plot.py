from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from components.recording import Recording
from components.amplitudes import Amplitudes
from components.phases import Phases
class AmplitudePlot(QWidget):
    def __init__(self, amps, min_y, max_y):
        super().__init__()

        # self.data = data
        rec = amps.recording
        self.amps = amps
        self.max_y = max_y
        self.min_y = min_y

        datetime, name = rec.get_datetime_name()
        self.title = f"{datetime} - {rec.get_senders_name_mac()} - {rec.get_receivers_name_mac()} - {rec.get_frequencies()} - {name}"
        self.setFixedHeight(300)

        # Create Matplotlib Figure and Canvas
        self.figure = Figure(figsize=(12, 3))
        self.canvas = FigureCanvas(self.figure)

        # Layout to hold the canvas
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.ax = self.figure.add_subplot(111)
        self.ax.clear()

    def plot_amplitudes(self, in_data):
        for key, values in in_data.items():
            self.ax.plot(values, label=f"Line {key}")
        self.ax.set_xlabel("Index")
        if isinstance(self.amps, Amplitudes):
            self.ax.set_ylabel("Amplitude")
        elif isinstance(self.amps, Phases):
            self.ax.set_ylabel("Phase")    
        self.ax.set_ylim(self.min_y, self.max_y)
        self.ax.set_title(self.title)
        self.ax.grid(True)
        self.canvas.draw()

    def plot_ftt(self, in_data, x_limit=None):
        if x_limit is None:
            for sub in self.amps.columns:
                freqs = in_data[sub]['freqs']
                magnitude = in_data[sub]['magnitude']
                self.ax.plot(freqs, magnitude)
        else:
            for sub in self.amps.columns:
                freqs = [f for f in in_data[sub]['freqs'] if f < x_limit]
                magnitude = in_data[sub]['magnitude'][:len(freqs)]
                self.ax.plot(freqs, magnitude)

        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Magnitude")
        self.ax.set_ylim(self.min_y, self.max_y)
        self.ax.set_title(self.title)
        self.ax.grid(True)
        self.canvas.draw()
