from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import numpy as np

# from components.recording import Recording
# from components.amplitudes import Amplitudes
# from components.phases import Phases
class CorrelationPlot(QWidget):
    def __init__(self, rec):
        super().__init__()

        # self.data = data
        # rec = rec
        # self.amps = amps
        # self.max_y = max_y
        # self.min_y = min_y
        self.title = rec.get_id()
        self._heatmaps = []

        # datetime, name = rec.get_datetime_name()
        # self.title = f"{datetime} - {rec.get_senders_name_mac()} - {rec.get_receivers_name_mac()} - {rec.get_frequencies()} - {name}"
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

    def plot_correlation(self, in_data):
        # Initialize storage if missing
        if not hasattr(self, "_heatmaps"):
            self._heatmaps = []

        # Add the new heatmap to the list
        self._heatmaps.append(in_data)

        # Number of plots to draw
        n_plots = len(self._heatmaps)

        self.figure.clear()
        # Clear figure

        # Adjust figure width dynamically
        self.figure.set_size_inches(4 * n_plots, 3)

        # Create subplots horizontally
        axes = self.figure.subplots(1, n_plots)

        # Calculate mean and mean absolute value of all .index attributes
        indices = [h.index for h in self._heatmaps]
        abs_indices = [abs(h.index) for h in self._heatmaps]
        mean_index = np.mean(indices)
        mean_abs_index = np.mean(abs_indices)
        
        self.figure.suptitle(f"{self.title} {mean_index:.4f} {mean_abs_index:.4f}", fontsize=12)

        # Handle the single-subplot case
        if n_plots == 1:
            axes = [axes]

        # Draw each stored heatmap
        for i, ax in enumerate(axes):
            sns.heatmap(
                self._heatmaps[i].matrix,
                annot=False,
                cmap="coolwarm",
                vmin=0,
                vmax=1,
                ax=ax
            )
            ax.set_title(f"#{i+1} - {self._heatmaps[i].index:.4f}")

        # Improve spacing and render
        self.figure.tight_layout()
        self.canvas.draw()

    # def plot_correlation(self, in_data):
    #     sns.heatmap(in_data, annot=False, cmap="coolwarm", vmin=0, vmax=1, ax=self.ax)

    #     # for key, values in in_data.items():
    #     #     self.ax.plot(values, label=f"Line {key}")
    #     # self.ax.set_xlabel("Index")
    #     # if isinstance(self.amps, Amplitudes):
    #     #     self.ax.set_ylabel("Amplitude")
    #     # elif isinstance(self.amps, Phases):
    #     #     self.ax.set_ylabel("Phase")
    #     # self.ax.set_ylim(self.min_y, self.max_y)
    #     self.ax.set_title(self.title)
    #     # self.ax.grid(True)
    #     self.canvas.draw()
