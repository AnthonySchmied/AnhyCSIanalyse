import pandas as pd
from components.signaldata import SignalData

class ComplexValues(SignalData):
    def __init__(self, df, rec=None, subcarrier_columns=None):
        super().__init__(df, rec)
        self.columns = subcarrier_columns
        if subcarrier_columns is None:
            self.subcarrier_enable(
                [i + 1 for i in range(len(self.df["complex"].iloc[0]))]
            )
            if len(self.columns) < 1:
                raise Exception("wrong data format")
            df_expanded = pd.DataFrame(
                self.df["complex"].tolist(), columns=self.columns
            )
            self.df = self.df.drop(columns=["complex"]).join(df_expanded)
        self.subcarrier_disable([1, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38])

    def subcarrier_enable(self, subcarrier: list):
        self.columns = [f"complex_sub_{i}" for i in subcarrier]

    def subcarrier_disable(self, subcarrier: list):
        for i in subcarrier:
            id = f"complex_sub_{i}"
            if id in self.columns:
                self.columns.remove(id)

    def get_real_by_subcarriers(self):
        to_return = {col: [val.real for val in self.df[col]] for col in self.columns}
        return to_return
            
    def get_imag_by_subcarriers(self):
        to_return = {col: [val.imag for val in self.df[col]] for col in self.columns}
        return to_return
        

    # def get_real(self):
    #     pass


    # def get_imaginary(self):
    #     pass