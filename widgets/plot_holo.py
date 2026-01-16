from datetime import datetime
import holoviews as hv
import pandas as pd
import numpy as np

# import panel as pn
# pn.extension('bokeh')
# from holoviews import GridSpec

hv.extension("bokeh")

from components.plot_container import (
    HeatmapPlot,
    PointcloudPlot,
    AmplitudePlot,
    HeatmapPlotArrays,
    CorrelationIndexPlot,
    EnvironmentPlotContainer,
)

# from components.sens_ops import SensOps as so


class _PlotRow:
    def __init__(self):
        self._entries = []

    def append(self, sub_plot):
        self._entries.append(sub_plot)

    def __len__(self):
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)


class Plot:
    def __init__(self, rows):
        self._rows = [_PlotRow() for _ in range(rows)]

    def append_row_idx(self, idx, sub_plot):
        self._rows[idx].append(sub_plot)

    def _draw(self):
        plots = []

        for i, row in enumerate(self._rows):
            # print(row)
            # col_idx = 0
            for entry in row:
                if isinstance(entry, AmplitudePlot):
                    plots.append(self._draw_amplitude(entry))
                    # for _ in range(self.width()-1):
                    #     plots.append(self._draw_blank())
                elif isinstance(entry, HeatmapPlot):
                    plots.append(self._draw_heatmap(entry))
                elif isinstance(entry, PointcloudPlot):
                    plots.append(self._draw_pointcloud(entry))
                elif isinstance(entry, HeatmapPlotArrays):
                    plots.append(self._draw_heatmap_array(entry))
                elif isinstance(entry, CorrelationIndexPlot):
                    plots.append(self._draw_correlation_index_plot(entry))
                elif isinstance(entry, EnvironmentPlotContainer):
                    plots.append(self._draw_environment_plot(entry))
                # grid[f"{i}_{col_idx}"] = elt
                # col_idx += 1

        # self._layout = hv.Layout(plots)
        self._layout = hv.Layout(plots).cols(self.width()).opts(shared_axes=False)

        # exit()
        #     plot_rows.append(hv.Layout(row_plts).cols(len(row)))
        # self._layout = hv.Layout(plot_rows).cols(1)

    def _draw_amplitude(self, entry):
        data = entry.get_amplitudes().get_by_subcarriers()
        curves = []

        for key, values in data.items():
            # for v in values:
            #     if isinstance(v, str):
            #         print("STRING VALUE FOUND in", key, ":", v)
            #         raise ValueError("String value in amplitude data!")

            # exit()
            # x = range(len(values))
            # x = [i for i in range(len(values))]
            # print(values)
            # print(len(values))
            # curves.append(hv.Curve(values))
            # x = range(len(values))
            x = [i for i in range(len(values))]
            # curves.append(hv.Curve((x, values)))
            curves.append(hv.Curve((x, values), kdims=["x"], vdims=["y"]).relabel(key))

        return hv.Overlay(curves).opts(
            width=400,
            height=300,
            xlabel="Time",
            ylabel="Amplitude",
        )

    def _draw_environment_plot(self, entry):
        curves = []

        colors = {
            1: "red",
            2: "blue",
            3: "orange",
            4: "purple",
        }

        for curve in entry:
            print(curve.get_label().get_day())

            curves.append(
                hv.Curve(
                    (curve.get_x_data(), curve.get_y_data()),
                    kdims=["x"],
                    vdims=["y"],
                    label=f"d{curve.get_label().get_day()[0]}",
                ).opts(color=colors[curve.get_label().get_day()[0]])
            )

        return hv.Overlay(curves).opts(
            width=2000, height=500, xlabel="Zeit", ylabel=curve.get_y_data().name
        )

    def _draw_heatmap(self, entry):
        df = entry.get_matrix()
        df_long = df.reset_index().melt(
            id_vars=df.index.name or "index", var_name="y", value_name="value"
        )
        df_long = df_long.rename(columns={df_long.columns[0]: "x"})
        hv_map = hv.HeatMap(df_long, kdims=["x", "y"], vdims=["value"]).opts(
            cmap="viridis",
            colorbar=True,
            width=350,
            height=300,
            title=f"Corr mean: {entry.get_index():.6f}",  # clim=(-1, 1)
        )
        return hv_map

    def _draw_heatmap_array(self, entry):
        d = entry.get_matrix()

        rows, cols = d.shape
        xs, ys = np.meshgrid(range(cols), range(rows))

        df = pd.DataFrame({"x": xs.flatten(), "y": ys.flatten(), "value": d.flatten()})

        hv_map = hv.HeatMap(df, kdims=["x", "y"], vdims=["value"]).opts(
            cmap="viridis",
            shared_axes=False,
            colorbar=True,
            # width=30*entry.get_width()+100,
            # height=30*entry.get_height()+60,
            width=3 * entry.get_width() + 100,
            height=3 * entry.get_height() + 60,
            title=entry.get_title(),
            # title=f"Corr mean: {entry.get_index():.6f}",  # clim=(-1, 1)
        )

        # hv_map = hv.HeatMap(df, kdims=["x", "y"]).opts(
        #     cmap="viridis",
        #     colorbar=True,
        #     width=350,
        #     height=300,
        #     #title=f"Corr mean: {entry.get_index():.6f}",  # clim=(-1, 1)
        # )
        return hv_map

    def _draw_pointcloud(self, entry):
        # colors = {
        #     "i-r":"red",
        #     "a-r":"blue",
        #     "e-r":"orange",
        #     "h-r":"purple",
        #     "emt":"green"
        # }
        # colors = {
        #     "i-r":"blue",
        #     "a-r":"blue",
        #     "e-r":"blue",
        #     "h-r":"blue",
        #     "emt":"green"
        # }

        # colors = {
        #     10: "red",
        #     25: "blue",
        #     50: "green",
        #     100: "purple"
        # }

        # colors = {
        #     "i": "#D73027",  # rot
        #     "a": "#4575B4",  # blau
        #     "e": "#F46D43",  # orange
        #     "h": "#7B3294",  # lila
        #     "emt": "#1A9850",  # grün
        #     "ei": "#2C7BB6",  # cyan-blau (druckstabil)
        #     "ie": "#C51B7D",  # magenta
        #     "ha": "#66A61E",  # olivgrün statt lime
        #     "ah": "#8C510A",  # braun
        # }

        # colors = {
        #     1: "#D73027",  # rot
        #     2: "#4575B4",  # blau
        #     3: "#F46D43",  # orange
        #     4: "#7B3294",  # lila
        # }

        # colors = {
        #     # Rot
        #     1:  "#D73027",  # rot (primär)
        #     11: "#A50026",  # rot (dunkler Partner) Leerraum

        #     # Blau
        #     2:  "#4575B4",  # blau (primär)
        #     22: "#313695",  # blau (dunkler Partner) Leerraum

        #     # Orange
        #     3:  "#F46D43",  # orange (primär)
        #     33: "#D94801",  # orange (dunkler Partner) Leerraum

        #     # Lila
        #     4:  "#7B3294",  # lila (primär)
        #     44: "#542788",  # lila (dunkler Partner) Leerraum
        # }

        colors = {
            # Rot
            "i":  "#D73027",  # rot (primär)
            "ie": "#A50026",  # rot (dunkler Partner) Leerraum

            # Blau
            "a":  "#4575B4",  # blau (primär)
            "ah": "#313695",  # blau (dunkler Partner) Leerraum

            # Orange
            "e":  "#F46D43",  # orange (primär)
            "ei": "#D94801",  # orange (dunkler Partner) Leerraum

            # Lila
            "h":  "#7B3294",  # lila (primär)
            "ha": "#542788",  # lila (dunkler Partner) Leerraum
        }

        # colors = {
        #     0:"red",
        #     1:"blue",
        #     2:"orange",
        #     3:"purple",
        #     4:"green",
        #     5:"cyan",
        #     6:"magenta",
        #     7:"lime",
        # }

        def customize_plot(plot, element):
            plot.handles["xaxis"].axis_label_text_font_style = "bold"
            plot.handles["yaxis"].axis_label_text_font_style = "bold"
            plot.handles["xaxis"].major_label_text_font_size = "20pt"
            plot.handles["yaxis"].major_label_text_font_size = "20pt"
            plot.handles["plot"].outline_line_color = "black"
            plot.handles["plot"].outline_line_alpha = 1
            # plot.handles['plot'].above[0].outline_line_color = 'black'
            # plot.handles['plot'].above[0].outline_line_alpha = 1
            # plot.handles['plot'].right[0].outline_line_color = 'black'
            # plot.handles['plot'].right[0].outline_line_alpha = 1
            plot.handles["xaxis"].major_label_text_font_style = "bold"
            plot.handles["yaxis"].major_label_text_font_style = "bold"

        scatters = []
        dim1, dim2 = entry.get_pc()
        for idx, dataset in enumerate(entry):
            # print(dataset.get_label())
            print(str(dataset.get_label()))
            # print(colors[dataset.get_label().get_frequency()])

            # scat = hv.Scatter(
            #     (dataset.get_pc_X(dim1), dataset.get_pc_X(dim2)),
            #     kdims="pc"+str(dim1),
            #     vdims="pc"+str(dim2),
            #     label=f"{str(dataset.get_label())}",
            # ).opts(size=5, color=colors[idx], tools=["hover"]) # , xlim=(-7,7), ylim=(-5,5)

            # colorcode = dataset.get_label().get_day()[0]
            colorcode = dataset.get_label().get_names()[0]
            # if dataset.get_label().get_names()[0] == "emt":
            #     colorcode += colorcode * 10
            #     print(colorcode)

            scat = hv.Scatter(
                (dataset.get_pc_X(dim1), dataset.get_pc_X(dim2)),
                kdims="PC " + str(dim1),
                vdims="PC " + str(dim2),
                # label=f"{str(dataset.get_label())}",
            ).opts(
                size=1,
                # color=colors[dataset.get_label().get_names()[0]],
                color=colors[colorcode],
                tools=["hover"],
                fontsize={"labels": 20},
                xlim=(-15, 15),
                ylim=(-15, 15),
                hooks=[customize_plot],
            )

            scatters.append(scat)

        pca_plot = hv.Overlay(scatters).opts(
            width=500,
            height=500,
            # title=f"PCA",
            show_legend=False,
        )
        return pca_plot

    def _draw_correlation_index_plot(self, entry):
        # colors = ["red", "blue", "green", "orange", "purple"]

        colors = {
            "i-r": "red",
            "a-r": "blue",
            "e-r": "orange",
            "h-r": "purple",
            "emt": "green",
        }

        scatters = []
        for idx, dataset in enumerate(entry):
            # X = dataset.X_pca  # shape (N, 2)
            # label = f"Set {idx+1}"
            # print(dataset)

            # print(dataset.get_label()[3:6])

            scat = hv.Scatter(
                (dataset.get_mean(), dataset.get_variance()),
                kdims="mean",
                vdims="variance",
                label=f"{dataset.get_label()[3:6]}",
            ).opts(size=1, color=colors[dataset.get_label()[3:6]], tools=["hover"])

            scatters.append(scat)

        corr_index_plot = hv.Overlay(scatters).opts(
            width=1900, height=1000, title="Scatter"
        )
        return corr_index_plot

    def _draw_blank(self):
        dummy = hv.Scatter(([], []), kdims="PC1", vdims="PC2").opts(
            width=350,
            height=300,
            size=1,
            color="white",
            alpha=0,  # fully transparent
            tools=[],
            title="",
            show_legend=False,
        )
        return dummy

    def width(self):
        return max([len(r) for r in self._rows])

    def height(self):
        return len(self._rows)

    def save(self, path):
        time = datetime.now()
        self._draw()
        hv.save(self._layout, path, resources="inline", dpi=300)
        print(f"saved {path} in {datetime.now()-time}")
