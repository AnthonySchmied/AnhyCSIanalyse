from datetime import datetime
import holoviews as hv
# import panel as pn
# pn.extension('bokeh')
# from holoviews import GridSpec

hv.extension("bokeh")

from components.plot_container import HeatmapPlot, PointcloudPlot, AmplitudePlot

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
        # gs = pn.GridSpec(width=self.width()*350,height=self.height()*300)
        # gs = pn.GridSpec()

        # for i, row in enumerate(self._rows):
        #     if len(row) == 1:
        #         for entry in row:
        #         # entry = row[0]
        #             if isinstance(entry, AmplitudePlot):
        #                 print("Amplitude", i)
        #                 elt = self._draw_amplitude(entry)
        #             gs[i, 0:self.width()] = elt
        #         continue

        #     for col_idx, entry in enumerate(row):
        #         if isinstance(entry, AmplitudePlot):
        #             # elt = self._draw_amplitude(entry)
        #             pass
        #         elif isinstance(entry, HeatmapPlot):
        #             print("heatmap", i)
        #             elt = self._draw_heatmap(entry)
        #         elif isinstance(entry, PointcloudPlot):
        #             print("pointcloud", i)
        #             elt = self._draw_pointcloud(entry)

        #         gs[i, col_idx] = elt

        # self._layout = gs
        # return


        # self._layout = []
        # plot_rows = []

        # grid = {}

        plots = []

        for i, row in enumerate(self._rows):
            # col_idx = 0
            for entry in row:
                if isinstance(entry, AmplitudePlot):
                    plots.append(self._draw_amplitude(entry))
                    for _ in range(self.width()-1):
                        plots.append(self._draw_blank())
                elif isinstance(entry, HeatmapPlot):
                    plots.append(self._draw_heatmap(entry))
                elif isinstance(entry, PointcloudPlot):
                    plots.append(self._draw_pointcloud(entry))
                # grid[f"{i}_{col_idx}"] = elt
                # col_idx += 1

        self._layout = hv.Layout(plots).cols(self.width())
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
            width=self.width() * 400,
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

    def _draw_pointcloud(self, entry):
        colors = ["red", "blue", "green", "orange", "purple"]
        scatters = []
        for idx, dataset in enumerate(entry):
            X = dataset.X_pca  # shape (N, 2)
            # label = f"Set {idx+1}"

            scat = hv.Scatter(
                (X[:, 0], X[:, 1]),
                kdims="PC1",
                vdims="PC2",
                label=f"{idx}-{dataset.label}",
            ).opts(size=6, color=colors[idx % len(colors)], tools=["hover"])

            scatters.append(scat)

        pca_plot = hv.Overlay(scatters).opts(
            width=350, height=300, title=f"PCA {entry._results[0].explained_variance}"
        )
        return pca_plot

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
