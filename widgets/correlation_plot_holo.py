import numpy as np

import holoviews as hv

hv.extension("bokeh")


class _CorrelationPlotRecording:
    def __init__(self, rec):
        self._rec = rec
        self._heatmaps = []

    def append(self, data):
        self._heatmaps.append(data)

    def get_len(self):
        return len(self._heatmaps)


class CorrelationPlot:
    def __init__(self):
        self._recordings = []

    def add_recording(self, rec):
        sub_rec = _CorrelationPlotRecording(rec)
        self._recordings.append(sub_rec)
        return sub_rec

    def save(self, path):
        print("save")
        self._draw()

        layout = hv.Layout(self.heatmaps).cols(self._width())
        hv.save(layout, path, resources='inline')

        print(path)
        print("saved")

    def _draw(self):
        self.heatmaps = []

        for rec in self._recordings:
            for heatmap in rec._heatmaps:
                df = heatmap.matrix
                df_long = df.reset_index().melt(
                    id_vars=df.index.name or "index", var_name="y", value_name="value"
                )
                df_long = df_long.rename(columns={df_long.columns[0]: "x"})
                hv_map = hv.HeatMap(df_long, kdims=["x", "y"], vdims=["value"]).opts(
                    cmap="viridis", colorbar=True, width=300, height=300, #clim=(-1, 1)
                )

                # heatmap = hv.HeatMap(df_long, kdims=["x", "y"], vdims=["value"]).opts(
                #     cmap="viridis", colorbar=True, linewidths=0.5
                # )

                self.heatmaps.append(hv_map)

    def _width(self):
        return self._max_subplots()

    def _height(self):
        return len(self._recordings)

    def _max_subplots(self):
        return max([rec.get_len() for rec in self._recordings])
