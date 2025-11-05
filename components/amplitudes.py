import pandas as pd
from components.signaldata import SignalData

class Amplitudes(SignalData):
    def __init__(self, df, rec=None, subcarrier_columns=None):
        super().__init__(df, rec)
        self.columns = subcarrier_columns
        if subcarrier_columns is None:
            self.subcarrier_enable(
                [i + 1 for i in range(len(self.df["amplitude"].iloc[0]))]
            )
            if len(self.columns) < 1:
                raise Exception("wrong data format")
            df_expanded = pd.DataFrame(
                self.df["amplitude"].tolist(), columns=self.columns
            )
            self.df = self.df.drop(columns=["amplitude"]).join(df_expanded)
        self.subcarrier_disable([1, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38])

    def subcarrier_enable(self, subcarrier: list):
        self.columns = [f"amp_sub_{i}" for i in subcarrier]

    def subcarrier_disable(self, subcarrier: list):
        for i in subcarrier:
            id = f"amp_sub_{i}"
            if id in self.columns:
                self.columns.remove(id)
