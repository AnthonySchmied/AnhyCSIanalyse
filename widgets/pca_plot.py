import numpy as np
import holoviews as hv

hv.extension("bokeh")


class _PcaPlotRow:
    def __init__(self):
        # self._rec = rec
        self._plots = []

    def append(self, data):
        self._plots.append(data)

    def get_len(self):
        return len(self._plots)



class PcaPlot:
    def __init__(self):
        self._rows = []

    def add_row(self, rec=None):
        row = _PcaPlotRow()
        self._rows.append(row)
        return row

    def save(self, path):
        print("save")
        self._draw()

        print(path)
        layout = hv.Layout(self._pca_plots).cols(self._width())
        hv.save(layout, path, resources="inline")

        print("saved")

    def _draw(self):
        self._pca_plots = []

        for row in self._rows:
            for plot_data in row._plots:
                colors = ['red', 'blue', 'green', 'orange', 'purple']
                scatters = []
                for idx, pca_set in enumerate(plot_data):
                    X = pca_set.X_pca  # shape (N, 2)
                    # label = f"Set {idx+1}"

                    scat = hv.Scatter(
                        (X[:, 0], X[:, 1]),
                        kdims="PC1",
                        vdims="PC2",
                        label=f"{idx}-{pca_set.label}"
                    ).opts(
                        size=6,
                        color=colors[idx % len(colors)],
                        tools=['hover']
                    )

                    scatters.append(scat)

                pca_plot = hv.Overlay(scatters).opts(
                    width=700,
                    height=500,
                    title="PCA of CSI Data (Multiple Sets)"
                )


                
                # print(plot_data.X_pca)
                # pca_plot = hv.Scatter((plot_data.X_pca[:, 0], plot_data.X_pca[:, 1]), 
                #                     kdims='PC1', vdims='PC2').opts(
                #     width=700, height=500, 
                #     size=6, 
                #     color='blue', 
                #     tools=['hover'], 
                #     title='PCA of CSI Data (PC1 vs PC2)'
                # )
                # df = heatmap.matrix
                # df_long = df.reset_index().melt(
                #     id_vars=df.index.name or "index", var_name="y", value_name="value"
                # )
                # df_long = df_long.rename(columns={df_long.columns[0]: "x"})
                # hv_map = hv.HeatMap(df_long, kdims=["x", "y"], vdims=["value"]).opts(
                #     cmap="viridis", colorbar=True, width=300, height=300
                # )

                # heatmap = hv.HeatMap(df_long, kdims=["x", "y"], vdims=["value"]).opts(
                #     cmap="viridis", colorbar=True, linewidths=0.5
                # )

                self._pca_plots.append(pca_plot)

    def _width(self):
        return self._max_subplots()

    def _height(self):
        return len(self._rows)

    def _max_subplots(self):
        return max([rec.get_len() for rec in self._rows])
