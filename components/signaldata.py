from components.sens_ops import _normalize_df, _standardize_df, _scale_df, _hampel_df


class SignalData:
    def __init__(self, df, rec=None):
        if df is None:
            raise Exception("df can not be None")
        if df.empty:
            raise Exception("df can not be empty")
        self.df = df.copy()
        self.recording = rec

    def __add__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            new_df = self.df[self.columns] + other
            return self.__class__(new_df, self.recording, self.columns)
        elif isinstance(other, SignalData):
            common_cols = list(set(self.columns) & set(other.columns))
            new_df = self.df[common_cols].add(other.df[common_cols])
            return self.__class__(new_df.dropna(), other.recording, other.columns)
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            new_df = self.df[self.columns] - other
            return self.__class__(new_df, self.recording, self.columns)
        elif isinstance(other, SignalData):
            common_cols = list(set(self.columns) & set(other.columns))
            new_df = self.df[common_cols].sub(other.df[common_cols])
            return self.__class__(new_df.dropna(), other.recording, other.columns)
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            new_df = self.df[self.columns] * other
            return self.__class__(new_df, self.recording, self.columns)
        elif isinstance(other, SignalData):
            common_cols = list(set(self.columns) & set(other.columns))
            new_df = self.df[common_cols].mul(other.df[common_cols], fill_value=0)
            new_df = new_df.dropna()
            return self.__class__(new_df, self.recording, common_cols)
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (float, int)):
            if other == 0:
                raise ZeroDivisionError("division by zero")
            new_df = self.df[self.columns] / other
            return self.__class__(new_df, self.recording, self.columns)
        elif isinstance(other, SignalData):
            common_cols = list(set(self.columns) & set(other.columns))
            new_df = self.df[common_cols].div(other.df[common_cols], fill_value=np.nan)
            new_df = new_df.dropna()
            return self.__class__(new_df, self.recording, common_cols)
        else:
            return NotImplemented

    def get_by_subcarriers(self):
        to_return = {col: self.df[col].tolist() for col in self.columns}
        return to_return

    def normalize(self):
        self.df = _normalize_df(self.df, self.columns)
        return self

    def standardize(self):
        self.df = _standardize_df(self.df, self.columns)
        return self

    def scale(self):
        self.df = _scale_df(self.df, self.columns)
        return self

    def hampel(self, window_size, n_sigmas):
        self.df = _hampel_df(self.df, self.columns, window_size, n_sigmas)
