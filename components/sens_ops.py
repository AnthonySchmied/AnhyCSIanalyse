import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
from scipy.signal import medfilt
from sklearn.model_selection import train_test_split

# def _normalize_df(df, columns):
#     max_value = df[columns].to_numpy().max()
#     min_value = df[columns].to_numpy().min()
#     scale = max(max_value, abs(min_value))
#     print(min_value)
#     print(scale)
#     if min_value < 0:
#         shift = True
#         scale *= 2 if min_value < 0 else scale
#     else:
#         shift = False
#     normalized_df = df.copy()
#     print(shift)
#     if scale != 0:
#         normalized_df[columns] = normalized_df[columns] / scale
#         if shift:
#             normalized_df[columns] = normalized_df[columns] + 0.5
#     return normalized_df


def _normalize_df(df, columns):
    max_value = df[columns].to_numpy().max()
    min_value = df[columns].to_numpy().min()
    shift_up = 0
    if min_value < 0:
        shift_up = abs(min_value)
        max_value += shift_up
    normalized_df = df.copy()
    if max_value != 0:
        normalized_df[columns] = (normalized_df[columns] + shift_up) / max_value
    return normalized_df


def _standardize_df(df, columns):
    """Standardize selected columns to mean=0, std=1."""
    standardized_df = df.copy()
    mean = df[columns].mean()
    std = df[columns].std()
    standardized_df[columns] = (df[columns] - mean) / std.replace(0, 1)
    return standardized_df


def _scale_df(df, columns):
    """Scale selected columns to [0, 1]."""
    scaled_df = df.copy()
    min_val = df[columns].min()
    max_val = df[columns].max()
    denom = (max_val - min_val).replace(0, 1)
    scaled_df[columns] = (df[columns] - min_val) / denom
    return scaled_df


def _hampel_filter(series, window_size, n_sigmas):
    # Rolling median
    rolling_median = series.rolling(window_size, center=True).median()
    # Median absolute deviation
    mad = series.rolling(window_size, center=True).apply(
        lambda x: np.median(np.abs(x - np.median(x))), raw=True
    )
    threshold = n_sigmas * 1.4826 * mad  # 1.4826 converts MAD to std
    diff = np.abs(series - rolling_median)
    filtered = series.copy()
    filtered[diff > threshold] = rolling_median[diff > threshold]
    return filtered


def _hampel_df(df, columns, window_size, n_sigmas):
    filtered_df = df.copy()
    for col in columns:
        filtered_df[col] = _hampel_filter(filtered_df[col], window_size, n_sigmas)
    return filtered_df


def _smooth_df(df, columns):
    filtered_df = df.copy()
    for col in columns:
        filtered_df[col] = medfilt(filtered_df[col], kernel_size=77)
    return filtered_df


def _center_df(df, columns):
    centered_df = df.copy()
    for col in columns:
        mean = np.mean(centered_df[col])
        centered_df[col] = centered_df[col] - mean
    return centered_df


def _compute_fft(df, columns, dt):
    fft_results = {}
    n = len(df)
    for col in columns:
        signal = df[col].to_numpy()
        fft_vals = np.fft.rfft(signal)
        freqs = np.fft.rfftfreq(n, d=dt)
        fft_results[col] = {"freqs": freqs, "magnitude": np.abs(fft_vals)}
    return fft_results


def _bandpass_filter(series, lowcut, highcut, fs, order):
    """
    Band-pass filter for CSI data.

    Parameters:
        data : np.ndarray
            Input data, shape (time, subcarriers)
        lowcut : float
            Low frequency cutoff (Hz)
        highcut : float
            High frequency cutoff (Hz)
        fs : float
            Sampling frequency (Hz)
        order : int
            Filter order

    Returns:
        filtered_data : np.ndarray
            Band-pass filtered data, same shape as input
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    print(f"{fs} - {nyq} - {low} - {high}")
    b, a = butter(order, [low, high], btype="band")
    filtered_data = filtfilt(b, a, series, axis=0)
    return filtered_data


def _bandpass_df(df, columns, lowcut, highcut, fs, order):
    filtered_df = df.copy()
    for col in columns:
        filtered_df[col] = _bandpass_filter(
            filtered_df[col], lowcut, highcut, fs, order
        )
    return filtered_df


def _compute_abs(df, columns):
    abs_df = df.copy()
    abs_df = abs(abs_df[columns])
    return abs_df

class corr_result:
        def __init__(self, matrix):
            corr = matrix
            for col in corr.columns:
                corr = corr.rename(columns={col: col.split('_')[2]})
                corr = corr.rename(index={col: col.split('_')[2]})
            self.matrix = corr
            self.index = np.mean(self.matrix)
            self.max = self.matrix.max()
            self.min = self.matrix.min()
            print(self.index)

def _compute_pearson_correlation_matrix(df1, columns, df2):
    if not df2 is None:
        df1_sel = df1[columns]
        df2_sel = df2[columns]

        min_len = min(len(df1_sel), len(df2_sel))
        df1_sel = df1_sel.iloc[:min_len]
        df2_sel = df2_sel.iloc[:min_len]

        # Concatenate for np.corrcoef
        # combined = np.concatenate([df1_sel.values.T, df2_sel.values.T], axis=0)
        # corr_matrix = np.corrcoef(combined)

        corr = pd.DataFrame(
            [[df1_sel[c1].corr(df2_sel[c2]) for c2 in df2_sel.columns] for c1 in df1_sel.columns],
            index=df1.columns,
            columns=df2.columns,
        )
        print(corr)

        # n1 = df1_sel.shape[1]
        # n2 = df2_sel.shape[1]
        # print(corr)
        # print("coor")

        # return corr_result(corr_matrix[:n1, n1 : n1 + n2])
        
        return corr_result(corr)
    
        # pairwise_corr_abs = np.abs(pairwise_corr)
        # result.index = np.mean(result.matrix)
        # return result
    else:
        corr = df1[columns].corr()
        return corr_result(corr)
        # result.index = np.mean(result.matrix)
        # return result

def _compute_correlation(df1, columns):
    # m = [df1[columns].iloc[i].tolist() for i in range(len(df1))]
    with np.errstate(invalid='raise'):
        m = df1[columns].to_numpy()
        corr = m.T @ m
        corr_pd = pd.DataFrame(corr, columns=columns, index=columns)
        print(corr_pd)
        return corr_result(corr_pd)

class pca_result:
    def __init__(self, X_pca, explained_variance, model, label):
        self.X_pca = X_pca
        self.explained_variance = explained_variance
        self.model = model
        self.label = label

def _compute_pca(df, columns, label, n_components=2):

    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
        
    X = df[columns].values

    X_scaled = StandardScaler().fit_transform(X)
    
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X_scaled)

    explained_variance = pca.explained_variance_ratio_
    print("Explained variance ratio:", explained_variance)

    return pca_result(X_pca, explained_variance, pca, label)

class SensOps:
    @staticmethod
    def mask(df):
        return df[df["mask"]].copy()

    @staticmethod
    def normalized(data_in):
        normalized_df = _normalize_df(data_in.df, data_in.columns)
        return data_in.__class__(normalized_df, data_in.recording, data_in.columns)

    @staticmethod
    def standardized(data_in):
        standardized_df = _standardize_df(data_in.df, data_in.columns)
        return data_in.__class__(standardized_df, data_in.recording, data_in.columns)

    @staticmethod
    def scaled(data_in):
        scaled_df = _scale_df(data_in.df, data_in.columns)
        return data_in.__class__(scaled_df, data_in.recording, data_in.columns)

    @staticmethod
    def hampeled(data_in, window_size, n_sigmas):
        filtered_df = _hampel_df(data_in.df, data_in.columns, window_size, n_sigmas)
        return data_in.__class__(filtered_df, data_in.recording, data_in.columns)

    @staticmethod
    def subcarrier_enabled(data_in, subcarrier: list):
        data_in.subcarrier_enable(subcarrier)
        new_amps = data_in.__class__(data_in.df, data_in.recording, data_in.columns)
        new_amps.subcarrier_enable(subcarrier)
        return new_amps

    @staticmethod
    def calculate_ftt(data_in):
        return _compute_fft(
            data_in.df, data_in.columns, 1 / data_in.recording.get_frequencies()[0]
        )

    @staticmethod
    def smooth(data_in):
        filtered_df = _smooth_df(data_in.df, data_in.columns)
        return data_in.__class__(filtered_df, data_in.recording, data_in.columns)

    @staticmethod
    def centered(data_in):
        centered_df = _center_df(data_in.df, data_in.columns)
        return data_in.__class__(centered_df, data_in.recording, data_in.columns)

    @staticmethod
    def bandpassed(data_in, lowcut, highcut, order=4):
        filtered_df = _bandpass_df(
            data_in.df,
            data_in.columns,
            lowcut,
            highcut,
            data_in.recording.get_frequencies()[0],
            order,
        )
        return data_in.__class__(filtered_df, data_in.recording, data_in.columns)

    @staticmethod
    def get_mean_by_subcarrier_sorted(data_in):
        mean = {}
        for sub in data_in.columns:
            mean[sub] = np.mean(data_in.df[sub])
        mean = dict(sorted(mean.items(), key=lambda item: item[1]))
        return mean

    @staticmethod
    def abs(data_in):
        return data_in.__class__(
            _compute_abs(data_in.df, data_in.columns),
            data_in.recording,
            data_in.columns,
        )

    @staticmethod
    def pearson_correlation(data1_in, data2_in=None):
        if data2_in is not None:
            return _compute_pearson_correlation_matrix(
                SensOps.mask(data1_in.df), data1_in.columns, SensOps.mask(data2_in.df)
            )
        else:
            return _compute_pearson_correlation_matrix(
                SensOps.mask(data1_in.df), data1_in.columns, None
            )

    @staticmethod
    def correlation(data1_in, data2_in=None):
        return _compute_correlation(SensOps.mask(data1_in.df), data1_in.columns)
    
    @staticmethod
    def pca(data_in):
        return _compute_pca(SensOps.mask(data_in.df), data_in.columns, data_in.recording.get_label())