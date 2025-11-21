from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import numpy as np

matplotlib.use('Agg')

# from components.recording import Recording
# from components.amplitudes import Amplitudes
# from components.phases import Phases

class _CorrelationPlotRecording:
    def __init__(self, rec):
        self._rec = rec
        self._heatmaps = []
    
    def append(self, data):
        self._heatmaps.append(data)

    def get_len(self):
        return len(self._heatmaps)

class CorrelationPlot():
    def __init__(self, rec=None, width=12, height=3):

        self._recordings = []

    def add_recording(self, rec):
        sub_rec = _CorrelationPlotRecording(rec)
        self._recordings.append(sub_rec)
        return sub_rec

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
        # self.figure.tight_layout()

    def _draw(self):
        width = self._max_subplots() * 4
        height = len(self._recordings) * 3

        self.figure = Figure(figsize=(width, height))
        self.canvas = FigureCanvas(self.figure)

        self.ax = self.figure.add_subplot(111)
        self.ax.clear()

        n_plots = len(self._recordings)
        self.figure.clear()

        # Create subplots horizontally
        axes = self.figure.subplots(len(self._recordings), self._max_subplots())

        # Calculate mean and mean absolute value of all .index attributes
        # indices = [h.index for h in self._heatmaps]
        # abs_indices = [abs(h.index) for h in self._heatmaps]
        # mean_index = np.mean(indices)
        # mean_abs_index = np.mean(abs_indices)
        
        # self.figure.suptitle(f"{self.title} {mean_index:.4f} {mean_abs_index:.4f}", fontsize=12)

        # Handle the single-subplot case
        if n_plots == 1:
            axes = [axes]

        # print(self._recordings[0]._heatmaps[0].matrix)
        # exit()

        # Draw each stored heatmap
        
        for i, ax in enumerate(axes):
            for j in range(len(ax)):
                sns.heatmap(
                    self._recordings[i]._heatmaps[j].matrix,
                    annot=False,
                    cmap="coolwarm",
                    vmin=0,
                    vmax=1,
                    ax=axes[i][j]
                )
                axes[i][j].set_title(f"{self._recordings[i]._rec.get_receivers_name_mac()[0]} - #{j+1} - {self._recordings[i]._heatmaps[j].index:.4f} - {self._recordings[i]._rec.get_time()}")

            # ax.set_title(f"#{i+1} - {self._heatmaps[i].index:.4f}")

        # Improve spacing and render
        # self.figure.tight_layout()

    def _max_subplots(self):
        return max([rec.get_len() for rec in self._recordings])

    def show(self):
        self.canvas.draw()

    def save(self, path):
        print("save")
        self._draw()

        self.figure.savefig(path, dpi=100)
        # self.figure.close()
        print(path)
        print("saved")
        


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

class CorrelationPlotWidget(QWidget, CorrelationPlot):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(300)

        # Layout to hold the canvas
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)