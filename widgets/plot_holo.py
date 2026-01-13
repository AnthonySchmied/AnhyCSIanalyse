from datetime import datetime
import holoviews as hv
import pandas as pd
import numpy as np

# import panel as pn
# pn.extension('bokeh')
# from holoviews import GridSpec

hv.extension("bokeh")

from components.plot_container import HeatmapPlot, PointcloudPlot, AmplitudePlot, HeatmapPlotArrays, CorrelationIndexPlot

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
            x = [ i for i in range(len(values))]
            # curves.append(hv.Curve((x, values)))
            curves.append(hv.Curve((x, values), kdims=["x"], vdims=["y"]).relabel(key))

        return hv.Overlay(curves).opts(
            width=400,
            height=300,
            xlabel="Time",
            ylabel="Amplitude",
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

        df = pd.DataFrame({
            "x": xs.flatten(),
            "y": ys.flatten(),
            "value": d.flatten()
        })

        hv_map = hv.HeatMap(df, kdims=["x", "y"], vdims=["value"]).opts(
            cmap="viridis",
            shared_axes=False,
            colorbar=True,
            # width=30*entry.get_width()+100,
            # height=30*entry.get_height()+60,
            width=3*entry.get_width()+100,
            height=3*entry.get_height()+60,
            title=entry.get_title()
            #title=f"Corr mean: {entry.get_index():.6f}",  # clim=(-1, 1)
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

        colors = {
            "i":"red",
            "a":"blue",
            "e":"orange",
            "h":"purple",
            "emt":"green",
            "ei": "cyan",
            "ie": "magenta",
            "ha": "lime",
            "ah": "brown",
        }

        scatters = []
        dim1, dim2 = entry.get_pc()
        for idx, dataset in enumerate(entry):
            # print(dataset.get_label())
            print(str(dataset.get_label()))
            # print(colors[dataset.get_label().get_frequency()])

            scat = hv.Scatter(
                (dataset.get_pc_X(dim1), dataset.get_pc_X(dim2)),
                kdims="pc"+str(dim1),
                vdims="pc"+str(dim2),
                label=f"{str(dataset.get_label())}",
            ).opts(size=5, color=colors[dataset.get_label().get_names()[0]], tools=["hover"]) # , xlim=(-7,7), ylim=(-5,5)

            scatters.append(scat)

        pca_plot = hv.Overlay(scatters).opts(
            width=1900, height=1000, title=f"PCA", show_legend=True
        )
        return pca_plot

    def _draw_correlation_index_plot(self, entry):
        # colors = ["red", "blue", "green", "orange", "purple"]

        colors = {
            "i-r":"red",
            "a-r":"blue",
            "e-r":"orange",
            "h-r":"purple",
            "emt":"green"
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
            alpha=0,          # fully transparent
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
        hv.save(self._layout, path, resources="inline")
        print(f"saved {path} in {datetime.now()-time}")
