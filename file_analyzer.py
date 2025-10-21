from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QScrollArea, QScrollBar, QSizePolicy
import pyqtgraph as pg
import csv
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np
from PyQt5.QtCore import Qt
import ast



# White theme globally
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class ScrollablePlot(pg.PlotWidget):
    """Single scrollable plot with fixed Y-axis."""

    def __init__(self, x_data, y_data_list, window_size=100, colors=None):
        super().__init__()

        self.x_data = np.array(x_data)
        self.y_data_list = [np.array(y) for y in y_data_list]
        self.window_size = window_size
        self.start_index = 0

        # Compute fixed Y-axis limits
        all_y = np.concatenate(self.y_data_list)
        self.y_min, self.y_max = np.min(all_y), np.max(all_y)
        self.setYRange(self.y_min, self.y_max)

        # Lines
        self.colors = colors or pg.intColor
        self.curves = []
        for i, y in enumerate(self.y_data_list):
            curve = self.plot([], [], pen=pg.mkPen(color=self.colors(i), width=2))
            self.curves.append(curve)

        # Vertical line and text for hover
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen='k')
        self.addItem(self.vLine)
        self.text_item = pg.TextItem("", anchor=(0, 1))
        self.addItem(self.text_item)
        self.scene().sigMouseMoved.connect(self.on_hover)

        self.update_plot(0)

    def update_plot(self, start_index):
        self.start_index = start_index
        end_index = start_index + self.window_size
        x_win = self.x_data[start_index:end_index]
        for i, curve in enumerate(self.curves):
            y_win = self.y_data_list[i][start_index:end_index]
            curve.setData(x_win, y_win)
        self.setXRange(x_win[0], x_win[-1], padding=0)

    def on_hover(self, pos):
        vb = self.plotItem.vb
        mouse_point = vb.mapSceneToView(pos)
        x_val = mouse_point.x()
        idx = np.searchsorted(self.x_data, x_val)
        if 0 <= idx < len(self.x_data):
            self.vLine.setPos(self.x_data[idx])
            texts = [f"L{i}: {y[idx]:.3f}" for i, y in enumerate(self.y_data_list)]
            self.text_item.setText(f"x={self.x_data[idx]:.3f}\n" + "\n".join(texts))
            self.text_item.setPos(self.x_data[idx], self.y_max)


class MultiPlotWidget(QWidget):
    """Container for multiple synchronized ScrollablePlots."""

    def __init__(self, x_data, data_list, window_size=100):
        """
        x_data: shared x-axis values
        y_data_list_of_lists: list of y_data_lists for each subplot
        """
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.plots = []
        self.scrollbar = QScrollBar(Qt.Horizontal)
        self.scrollbar.setMinimum(0)
        self.scrollbar.setMaximum(max(0, len(x_data) - window_size))
        self.scrollbar.valueChanged.connect(self.on_scrollbar_scroll)
        layout.addWidget(self.scrollbar)

        # # Create subplots
        # for y_data_list in y_data_list_of_lists:
        #     plot = ScrollablePlot(x_data, y_data_list, window_size=window_size)
        #     self.plots.append(plot)
        #     layout.addWidget(plot)

        amps_np = np.array(data_list[1])
        amps_data = amps_np.T
        mean_diff = []

        for i in range(1, len(data_list[0])):
            mean_diff.append((data_list[0][i] - data_list[0][i-1]))

        amplitudes_plot = ScrollablePlot(data_list[0], amps_data, colors=None, window_size=window_size)

        frequency_plot = ScrollablePlot(data_list[0], [data_list[2]], colors=None, window_size=window_size)
        mean_diff_plot = ScrollablePlot(data_list[0], [mean_diff], colors=None, window_size=window_size)

        # plot1 = AmplitudePlot(data_list[1], window_size=self.window_size)
        # plot2 = SinglePlot(data_list[1], window_size=self.window_size)
        layout.addWidget(amplitudes_plot)
        layout.addWidget(frequency_plot)
        layout.addWidget(mean_diff_plot)
        self.plots.append(amplitudes_plot)
        self.plots.append(frequency_plot)
        self.plots.append(mean_diff_plot)


    def on_scrollbar_scroll(self, value):
        for plot in self.plots:
            plot.update_plot(value)

# # Set white theme globally
# pg.setConfigOption('background', 'w')
# pg.setConfigOption('foreground', 'k')


# class ScrollablePlot(QWidget):
#     """
#     Horizontally scrollable plot with fixed Y-axis.
#     """

#     def __init__(self, x_data: np.ndarray, y_data_list: list[np.ndarray],
#                  window_size: int = 100, title: str = "Scrollable Plot",
#                  x_label: str = "X", y_label: str = "Y", colors=None):
#         super().__init__()

#         self.x_data = np.array(x_data)
#         # Convert to list of 1D arrays if 2D
#         self.y_data_list = []
#         for y in y_data_list:
#             y = np.array(y)
#             if y.ndim == 2 and y.shape[0] == len(x_data):
#                 for i in range(y.shape[1]):
#                     self.y_data_list.append(y[:, i])
#             else:
#                 self.y_data_list.append(y)

#         self.window_size = window_size
#         self.start_index = 0

#         # Compute global Y min/max
#         all_y = np.concatenate(self.y_data_list)
#         self.y_min = np.min(all_y)
#         self.y_max = np.max(all_y)

#         # Layout
#         layout = QVBoxLayout()
#         self.setLayout(layout)

#         # Plot widget
#         self.plot_widget = pg.PlotWidget(title=title)
#         self.plot_widget.setLabel('bottom', x_label)
#         self.plot_widget.setLabel('left', y_label)
#         self.plot_widget.showGrid(x=True, y=True)
#         self.plot_widget.setYRange(self.y_min, self.y_max)  # FIXED Y-axis
#         layout.addWidget(self.plot_widget)

#         # Lines
#         self.colors = colors or pg.intColor
#         self.curves = []
#         for i, y in enumerate(self.y_data_list):
#             curve = self.plot_widget.plot([], [], pen=pg.mkPen(color=self.colors(i), width=2), name=f"Line {i}")
#             self.curves.append(curve)

#         # Horizontal scrollbar
#         self.scrollbar = QScrollBar(Qt.Horizontal)
#         self.scrollbar.setMinimum(0)
#         self.scrollbar.setMaximum(max(0, len(self.x_data) - window_size))
#         self.scrollbar.valueChanged.connect(self.on_scroll)
#         layout.addWidget(self.scrollbar)

#         # Hover info
#         self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('k', width=1))
#         self.plot_widget.addItem(self.vLine, ignoreBounds=True)
#         self.text_item = pg.TextItem("", anchor=(0, 1))
#         self.plot_widget.addItem(self.text_item)
#         self.plot_widget.scene().sigMouseMoved.connect(self.on_hover)

#         # Initial plot
#         self.update_plot(0)

#     def update_plot(self, start_index):
#         self.start_index = start_index
#         end_index = start_index + self.window_size
#         x_win = self.x_data[start_index:end_index]
#         for i, curve in enumerate(self.curves):
#             y = self.y_data_list[i][start_index:end_index]
#             curve.setData(x_win, y)
#         self.plot_widget.setXRange(x_win[0], x_win[-1], padding=0)
#         # Y-axis remains fixed

#     def on_scroll(self, value):
#         self.update_plot(value)

#     def on_hover(self, pos):
#         vb = self.plot_widget.plotItem.vb
#         mouse_point = vb.mapSceneToView(pos)
#         x_val = mouse_point.x()
#         idx = np.searchsorted(self.x_data, x_val)
#         if 0 <= idx < len(self.x_data):
#             self.vLine.setPos(self.x_data[idx])
#             texts = [f"L{i}: {y[idx]:.3f}" for i, y in enumerate(self.y_data_list)]
#             self.text_item.setText(f"x={self.x_data[idx]:.3f}\n" + "\n".join(texts))
#             # Place text at top of plot for visibility
#             self.text_item.setPos(self.x_data[idx], self.y_max)

# # class ScrollablePlot(QWidget):
#     """
#     A universal, reusable horizontally scrollable plot widget for PyQt.
#     Supports multiple lines and absolute X-axis values.
#     """

#     def __init__(self, x_data: np.ndarray, y_data_list: list[np.ndarray],
#                  window_size: int = 100, title: str = "Scrollable Plot",
#                  x_label: str = "X", y_label: str = "Y", colors=None):
#         """
#         Args:
#             x_data: 1D array of x values (e.g. timestamps or indices)
#             y_data_list: list of 1D arrays for multiple lines
#             window_size: number of points to show in one window
#             title: plot title
#             x_label: label for x-axis
#             y_label: label for y-axis
#             colors: optional list of colors for the lines
#         """
#         super().__init__()

#         self.x_data = np.array(x_data)
#         self.y_data_list = [np.array(y) for y in y_data_list]
#         self.window_size = window_size
#         self.start_index = 0

#         # Setup Matplotlib Figure
#         self.fig, self.ax = plt.subplots()
#         self.canvas = FigureCanvas(self.fig)
#         self.canvas.mpl_connect("scroll_event", self.on_mouse_scroll)
#         self.canvas.mpl_connect("motion_notify_event", self.on_hover)

#         # Y-axis scaling once globally
#         ymin = np.min([np.min(y) for y in self.y_data_list]) * 0.9
#         ymax = np.max([np.max(y) for y in self.y_data_list]) * 1.1
#         self.ax.set_ylim(ymin, ymax)

#         # Create Layout
#         layout = QVBoxLayout()
#         layout.addWidget(self.canvas)

#         # Add horizontal scrollbar
#         self.scrollbar = QScrollBar(Qt.Horizontal)
#         self.scrollbar.setMinimum(0)
#         self.scrollbar.setMaximum(max(0, len(self.x_data) - window_size))
#         # self.scrollbar.valueChanged.connect(self.on_scrollbar_scroll)
#         layout.addWidget(self.scrollbar)
#         self.setLayout(layout)

#         # Plot setup
#         self.colors = colors or plt.cm.tab10.colors
#         self.lines = []
#         for i, y in enumerate(self.y_data_list):
#             (line,) = self.ax.plot([], [], color=self.colors[i % len(self.colors)], label=f"Line {i}")
#             self.lines.append(line)

#         # Annotation for hover display
#         self.annotation = self.ax.annotate(
#             "",
#             xy=(0, 0),
#             xytext=(15, 15),
#             textcoords="offset points",
#             bbox=dict(boxstyle="round", fc="w"),
#             arrowprops=dict(arrowstyle="->"),
#         )
#         self.annotation.set_visible(False)

#         # Plot style
#         self.ax.set_title(title)
#         self.ax.set_xlabel(x_label)
#         self.ax.set_ylabel(y_label)
#         self.ax.grid(True)
#         self.ax.legend()

#         self.update_plot(0, force=True)

#     # ---------- Plot Updating ----------
#     def update_plot(self, start_index: int, force=False):
#         """Update visible data window based on the start index."""
#         self.start_index = start_index
#         end_index = start_index + self.window_size

#         x_window = self.x_data[start_index:end_index]
#         for i, line in enumerate(self.lines):
#             y_window = self.y_data_list[i][start_index:end_index]
#             line.set_xdata(x_window)
#             line.set_ydata(y_window)

#         self.ax.set_xlim(self.x_data[start_index], self.x_data[min(end_index, len(self.x_data) - 1)])

#         if force:
#             self.ax.relim()
#             self.ax.autoscale_view()

#         self.canvas.draw_idle()

#     # ---------- Scroll Handlers ----------
#     def on_scrollbar_scroll(self, value: int):
#         """Triggered when scrollbar moves."""
#         self.update_plot(value)

#     def on_mouse_scroll(self, event):
#         """Triggered when mouse wheel scrolls over the plot."""
#         if event.button == 'up':
#             new_value = max(self.scrollbar.minimum(), self.scrollbar.value() - 10)
#         elif event.button == 'down':
#             new_value = min(self.scrollbar.maximum(), self.scrollbar.value() + 10)
#         else:
#             return
#         self.parent().shared_scrollbar.setValue(new_value)

#     # ---------- Hover Event ----------
#     def on_hover(self, event):
#         """Show data values near the mouse pointer."""
#         if not event.inaxes:
#             self.annotation.set_visible(False)
#             self.canvas.draw_idle()
#             return

#         vis = self.annotation.get_visible()
#         x_val = event.xdata
#         y_val = event.ydata

#         # Find nearest point in x_data
#         idx = np.searchsorted(self.x_data, x_val)
#         if idx < 0 or idx >= len(self.x_data):
#             self.annotation.set_visible(False)
#             self.canvas.draw_idle()
#             return

#         # Get closest data value from first line (or show multiple if desired)
#         texts = []
#         for i, y in enumerate(self.y_data_list):
#             if idx < len(y):
#                 texts.append(f"L{i}: {y[idx]:.3f}")
#         text = f"x={self.x_data[idx]:.3f}\n" + "\n".join(texts)

#         # Update annotation
#         self.annotation.xy = (self.x_data[idx], self.y_data_list[0][idx])
#         self.annotation.set_text(text)
#         self.annotation.set_visible(True)
#         self.canvas.draw_idle()



# class AmplitudePlot(QWidget):
#     def __init__(self, amplitudes: list, window_size=100):
#         super().__init__()
#         self.amplitudes = np.array(amplitudes)
#         self.window_size = window_size
#         self.start_index = 0

#         # Create figure and canvas
#         self.fig, self.ax = plt.subplots()
#         self.canvas = FigureCanvas(self.fig)

#         self.canvas.mpl_connect("scroll_event", self.on_scroll)

#         # Layout
#         layout = QVBoxLayout()
#         layout.addWidget(self.canvas)

#         # Add horizontal scroll bar
#         self.scrollbar = QScrollBar()
#         self.scrollbar.setOrientation(1)  # Horizontal
#         self.scrollbar.setMinimum(0)
#         self.scrollbar.setMaximum(max(0, len(self.amplitudes) - self.window_size))
#         self.scrollbar.valueChanged.connect(self.update_plot)
#         layout.addWidget(self.scrollbar)

#         self.setLayout(layout)

#         # Plot initial window
#         self.lines = []
#         self.plot_initial()

#     def plot_initial(self):
#         """Plot first window of data."""
#         self.ax.clear()
#         num_timestamps, num_indices = self.amplitudes.shape
#         x = np.arange(self.window_size)
#         self.lines = []
#         for i in range(num_indices):
#             (line,) = self.ax.plot(
#                 x, self.amplitudes[: self.window_size, i], label=f"Index {i}"
#             )
#             self.lines.append(line)

#         self.ax.set_xlabel("Timestamp")
#         self.ax.set_ylabel("Amplitude")
#         self.ax.set_title("Amplitude per Index")
#         self.ax.set_xlim(0, self.window_size)
#         # self.ax.legend()
#         self.ax.grid(True)
#         self.canvas.draw()

#     def update_plot(self, value):
#         """Update visible window and keep absolute X-axis values"""
#         start = value
#         end = start + self.window_size
#         x = np.arange(start, end)  # absolute packet indices
#         for i, line in enumerate(self.lines):
#             line.set_ydata(self.amplitudes[start:end, i])
#             line.set_xdata(x)  # use absolute indices
#         self.ax.set_xlim(start, end)  # show correct range on X-axis
#         self.canvas.draw_idle()

#     def on_scroll(self, event):
#         direction = -1 if event.button == 'up' else 1
#         new_value = self.start_index + direction * 10
#         new_value = max(0, min(len(self.values) - self.window_size, new_value))
#         self.parent().shared_scrollbar.setValue(new_value)


# class SinglePlot(QWidget):
#     """A single horizontally scrollable amplitude plot."""
#     def __init__(self, values: np.ndarray, window_size=100):
#         super().__init__()
#         self.values = np.array(values)
#         self.window_size = window_size
#         self.start_index = 0

#         # Create Matplotlib figure
#         self.fig, self.ax = plt.subplots()
#         self.canvas = FigureCanvas(self.fig)
#         self.canvas.mpl_connect("scroll_event", self.on_scroll)

#         layout = QVBoxLayout()
#         layout.addWidget(self.canvas)
#         self.setLayout(layout)

#         # Draw initial plot
#         self.line, = self.ax.plot([], [])
#         self.update_plot(0, redraw=True)

#     def update_plot(self, value, redraw=False):
#         """Update the visible window based on scrollbar value."""
#         self.start_index = value
#         end = value + self.window_size
#         x = np.arange(value, min(end, len(self.values)))
#         y = self.values[value:end]

#         self.line.set_xdata(x)
#         self.line.set_ydata(y)

#         self.ax.set_xlim(value, value + self.window_size)
#         self.ax.set_ylim(np.min(self.values), np.max(self.values))
#         self.ax.set_xlabel("Index")
#         self.ax.set_ylabel("Amplitude")
#         self.ax.set_title("Amplitude over Time")
#         self.ax.grid(True)

#         if redraw:
#             self.ax.relim()
#             self.ax.autoscale_view()

#         self.canvas.draw_idle()

#     def on_scroll(self, event):
#         """Handle mouse wheel scroll events."""
#         direction = -1 if event.button == 'up' else 1
#         new_value = self.start_index + direction * 10
#         new_value = max(0, min(len(self.values) - self.window_size, new_value))
#         self.parent().shared_scrollbar.setValue(new_value)


# class MultiPlotWidget(QWidget):
#     """Widget that contains multiple synchronized plots and a shared scrollbar."""
#     def __init__(self, data_list, window_size=100):
#         super().__init__()
#         self.window_size = window_size

#         layout = QVBoxLayout()
#         self.plots = []



#         # Create all plots
#         # for data in data_list:

#         amps_np = np.array(data_list[1])
#         amps_data = amps_np.T
#         mean_diff = []

#         for i in range(1, len(data_list[0])):
#             mean_diff.append((data_list[0][i] - data_list[0][i-1])/1000)

#         amplitudes_plot = ScrollablePlot(data_list[0], amps_data, title="Amplitude over rx time", x_label="None", y_label="None", colors=None)

#         frequency_plot = ScrollablePlot(data_list[0], [data_list[2]], title="Frequency over rx time", x_label="None", y_label="None", colors=None)
#         mean_diff_plot = ScrollablePlot(data_list[0], [mean_diff], title="", x_label="", y_label="None", colors=None)

#         # plot1 = AmplitudePlot(data_list[1], window_size=self.window_size)
#         # plot2 = SinglePlot(data_list[1], window_size=self.window_size)
#         layout.addWidget(amplitudes_plot)
#         layout.addWidget(frequency_plot)
#         layout.addWidget(mean_diff_plot)
#         self.plots.append(amplitudes_plot)
#         self.plots.append(frequency_plot)
#         self.plots.append(mean_diff_plot)

#         # Shared scrollbar
#         self.shared_scrollbar = QScrollBar(Qt.Horizontal)
#         max_len = max(len(d) for d in data_list)
#         self.shared_scrollbar.setMinimum(0)
#         self.shared_scrollbar.setMaximum(max(0, max_len - window_size))
#         self.shared_scrollbar.valueChanged.connect(self.on_scroll)

#         layout.addWidget(self.shared_scrollbar)
#         self.setLayout(layout)

#         # Make scrollbar accessible to children for mouse scrolling
#         for plot in self.plots:
#             plot.parent = lambda p=self: p  # bind parent lookup

#     def on_scroll(self, value):
#         """Update all plots when the scrollbar moves."""
#         for plot in self.plots:
#             plot.update_plot(value)


class FileAnalyzer(QWidget):
    def __init__(self, filepath):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        try:
            with open(filepath, newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                self.data = list(reader)

                # Print first 10 rows (or all if less than 10)
                # for row in self.data[:10]:
                #     print(row[10])

        except Exception as e:
            print(f"Failed to load CSV: {e}")

        datalist = []

        amplitudes = []
        freqs = []
        rx_times = []

        for row in self.data[1:1000]:  # skip header row
            # amps = ast.literal_eval(row[11])
            # amplitudes.append(amps)
            # freqs.append(int(row[7]))
            # rx_times.append(int(row[6])/1e3)
            
            # Parse amplitudes (assume row[11] is a list string)
            try:
                amps = ast.literal_eval(row[11])
            except Exception:
                amps = [range(64)]  # fallback if parsing fails
            amplitudes.append(amps)

            # Parse frequency, fallback to 0
            try:
                freqs.append(int(float(row[7])))
            except Exception:
                freqs.append(1)

            # Parse rx_times, fallback to 0
            try:
                rx_times.append(int(float(row[6])) / 1e3)
            except Exception:
                rx_times.append(rx_times[-1])


        datalist.extend([rx_times, amplitudes, freqs])


        print(len(rx_times))
        print(len(amplitudes))
        print(len(freqs))

        plots = MultiPlotWidget(rx_times, datalist, window_size=10000)
        layout.addWidget(plots)

        # amplitude_plot = AmplitudePlot(amplitudes)
        # freq_plot = SinglePlot(freqs)

        # layout.addWidget(amplitude_plot)
        # layout.addWidget(freq_plot)

        # self._num_subcarrier = None
        # self._amplitude_buffer = None
        # self._lines = None
        # self.ampitude_plot = pg.PlotWidget(title="CSI Amplitudes per Subcarrier")
        # self.ampitude_plot.setLabel("left", "Amplitude")
        # self.ampitude_plot.setLabel("bottom", "Packet Index")
        # self.ampitude_plot.setYRange(0, 30)
        # # layout.addWidget(self.ampitude_plot)
