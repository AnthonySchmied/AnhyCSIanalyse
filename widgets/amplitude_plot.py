from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from components.recording import Recording

class AmplitudePlot(QWidget):
    def __init__(self, rec):
        super().__init__()

        # Get amplitude data from the Recording
        # Expecting a dict where each key is a line
        self.data = rec.get_amplitudes()
        self.title = f"{rec.get_senders_name_mac()} - {rec.get_receivers_name_mac()} - {rec.get_frequencies()}"
        self.setFixedHeight(300)


        # Create Matplotlib Figure and Canvas
        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)

        # Layout to hold the canvas
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Draw the plot
        self.plot_amplitudes(title=self.title)

    def plot_amplitudes(self, title):
        ax = self.figure.add_subplot(111)
        ax.clear()

        for key, values in self.data.items():
            ax.plot(values, marker='o', label=f"Line {key}")

        ax.set_xlabel("Index")
        ax.set_ylabel("Amplitude")
        ax.set_title(title)
        ax.grid(True)
        print(f"plot: {title}")
        # ax.legend()

        # Refresh the canvas
        self.canvas.draw()