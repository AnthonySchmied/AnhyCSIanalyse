from pathlib import Path

from widgets.plot_holo import Plot
from components.sens_ops import SensOps as so
from components.plot_container import HeatmapPlot, PointcloudPlot, AmplitudePlot, HeatmapPlotArrays

class Rising():
    def __init__(self, batch, cic, base_path, freq, image_shift=5, cols=10):
        # cic.register(batch)
        self.prepare_outpath(batch, base_path, freq)
        for image_shift_i in range(image_shift):
            plot = Plot(3*len(batch))
            for i in range(cols):
                for idx, data in enumerate(batch.get_masked_amplitude((image_shift_i*10000)+1000,0,100+i*(50))):
                    data = so.smooth(data)
                    pca = so.pca(data)
                    plot.append_row_idx((idx*3)+2, PointcloudPlot([pca]))
                    # last_pca = pca
                    data = so.normalized(data)
                    # if i == cols-1:
                    #     plot.append_row_idx((idx*3), AmplitudePlot(data))
                    data = so.centered(data)
                    corr = so.pearson_correlation(data)
                    # cic.append(batch, idx, corr.index)
                    plot.append_row_idx((idx*3)+1, HeatmapPlot(corr))
                    
                    # TODO return results or callback to collector
                
            plot.save(self.get_outpath(image_shift_i))

    def prepare_outpath(self, batch, base_path, freq):
        self._batch_id = batch.get_id()
        self._outpath = Path("plots", f"{base_path}_f{freq}_10s_1s-6s")
        self._outpath.mkdir(parents=True, exist_ok=True)

    def get_outpath(self, i):
        return Path(self._outpath, f"{self._batch_id}-{i}.png")
    
class Shifting():
    def __init__(self, batch, cic, base_path, freq, image_shift=10, cols=10):
        # cic.register(batch)
        self.prepare_outpath(batch, base_path, freq)
        for image_shift_i in range(image_shift):
            plot = Plot(3*len(batch))
            for i in range(cols):
                for idx, data in enumerate(batch.get_masked_amplitude(0,(i*100)+(image_shift_i*image_shift*100),200)):
                    data = so.smooth(data)
                    pca = so.pca(data)
                    plot.append_row_idx((idx*3)+2, PointcloudPlot([pca]))
                    # last_pca = pca
                    data = so.normalized(data)
                    # if i == cols-1:
                    #     plot.append_row_idx((idx*3), AmplitudePlot(data))
                    data = so.centered(data)
                    corr = so.pearson_correlation(data)
                    # cic.append(batch, idx, corr.index)
                    plot.append_row_idx((idx*3)+1, HeatmapPlot(corr))
                    
                    # TODO return results or callback to collector
                
            plot.save(self.get_outpath(image_shift_i))

    def prepare_outpath(self, batch, base_path, freq):
        self._batch_id = batch.get_id()
        self._outpath = Path("plots", f"{base_path}_f{freq}_10s_1s")
        self._outpath.mkdir(parents=True, exist_ok=True)

    def get_outpath(self, i):
        return Path(self._outpath, f"{self._batch_id}-{i}.png")
    
class MultTrans():
    def __init__(self, batch, cic, base_path, freq, image_shift=3, cols=10):
        # cic.register(batch)
        # cic.register()

        for s in batch:
            cic.register_label(s.get_id())    

        self.prepare_outpath(batch, base_path, freq)
        cic.set_path(self._outpath)

        for image_shift_i in range(image_shift):
            # plot = Plot(9)
            for i in range(cols):
                for idx, data in enumerate(batch.get_masked_amplitude(0,(image_shift_i*image_shift*50)+i*50,100)):
                    # data = so.smooth(data)
                    data = so.norm_by_time(data)
                    pc = so.pca_X(data, 4)
                    pc.set_label(batch[idx].get_id())
                    cic.push_data(pc, batch[idx].get_id())

                    # plot.append_row_idx(idx*2, AmplitudePlot(data))
                    # data = so.normalized(data)
                    # autocorr = HeatmapPlotArrays(so.multiply(data, False, True), "x@xT")
                    # cic.push_data(batch[idx].get_id(), autocorr.get_matrix_mean(), autocorr.get_matrix_variance())
                    # plot.append_row_idx(idx*2+1, autocorr)

                    # plot.append_row_idx(idx*2+1, HeatmapPlotArrays(so.to_heatmap_arrays(data, False), "x"))

                    # plot.append_row_idx((idx*2)+2, HeatmapPlotArrays(so.to_heatmap_arrays(data, True), "xT"))
                    # plot.append_row_idx((idx*2)+2, HeatmapPlotArrays(so.multiply(data, True, False), "xT@x"))
                    
            # plot.save(self.get_outpath(image_shift_i))
            # exit()

    def prepare_outpath(self, batch, base_path, freq):
        self._batch_id = batch.get_id()
        self._outpath = Path("plots", f"{base_path}_f{freq}_10s_500ms_overlap")
        self._outpath.mkdir(parents=True, exist_ok=True)

    def get_outpath(self, i):
        return Path(self._outpath, f"{self._batch_id}-{i}.png")