from pathlib import Path
import pandas as pd
import numpy as np
import datetime
import re


FORCE_READ_CSV = False
DEBUG = True


def ensure_data_loaded(func):
    def wrapper(self, *args, **kwargs):
        if getattr(self, "df", None) is None or getattr(self, "df", None).empty:
            self.read_from_storage()
        return func(self, *args, **kwargs)

    return wrapper


class _InitRecordingMinix:
    def reset(self):
        self._duration_ms = None
        self._mean_temperature = None
        self._min_temperature = None
        self._max_temperature = None
        self._mean_humidity = None
        self._min_humidity = None
        self._max_humidity = None
        self._mean_pressure = None
        self._min_pressure = None
        self._max_pressure = None


class _ReadEnvironmentMinix:
    def parse_receiver(self):
        m = re.match(
            r"^env_([0-9a-fA-F]{6})_([^_]+)\.csv$",
            self._path.name,
        )
        if m:
            (
                self._mac_receiver,
                self._name_receiver,
            ) = (m.group(1), m.group(2))
        else:

            self._mac_receiver = None
            self._name_receiver = None

    def _read_from_pickle(self):
        try:
            pickle_path = self.get_pickle_path()
            if DEBUG:
                print(f"Loading from pickle: {pickle_path}")
            self.df = pd.read_pickle(pickle_path)

        except Exception as e:
            print(f"Error loading pickle: {e}, reparsing CSV...")
            raise e

    def _save_to_pickle(self):
        self.df.to_pickle(self.get_pickle_path())

    def _read_from_csv(self):
        # only parse file the first time -> pickle keeps format
        print(f"load from csv: {self._path}")
        cols = ["timestamp_pc", "temperature", "humidity", "pressure"]

        try:
            self.df = pd.read_csv(self._path, names=cols, header=0, dtype=str)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return

        # Check if last row contains the marker "END OF RECORDING"
        if not self.df.iloc[-1].astype(str).str.contains("END OF RECORDING").any():
            print(f"\n path: {self._path} \n")
            raise Exception("DataFrame invalid: no END OF RECORDING marker.")

        numeric_cols = ["temperature", "humidity", "pressure"]
        self.df[numeric_cols] = self.df[numeric_cols].apply(
            pd.to_numeric, errors="coerce"
        )
        self.df["temperature"] = pd.to_numeric(
            self.df["temperature"], errors="coerce"
        ).astype("Float32")
        self.df["humidity"] = pd.to_numeric(
            self.df["humidity"], errors="coerce"
        ).astype("Float32")
        self.df["pressure"] = pd.to_numeric(
            self.df["pressure"], errors="coerce"
        ).astype("Float32")
        self.df["timestamp_pc"] = pd.to_datetime(self.df["timestamp_pc"], errors="coerce")
        self.df["mask"] = True
        # self._update_time()

        self.df.dropna(subset=cols, inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self._save_to_pickle()

    def read_csv_sanitized(self):
        if not FORCE_READ_CSV and self.get_pickle_path().is_file():
            try:
                self._read_from_pickle()
            except:
                self._read_from_csv()
        else:
            self._read_from_csv()

    def get_pickle_path(self):
        return Path(self._path.parent, "." + self._path.stem + ".pkl")


class _MetaDataRecordingMinix:
    @ensure_data_loaded
    def get_duration(self, as_str=False):
        if len(self.df) > 2:
            if self._duration_ms is None:
                timestamps_ms = self.df["timestamp_pc"].astype("int64") // 10**6
                self._duration_ms = timestamps_ms.iloc[-1] - timestamps_ms.iloc[0]
            return (
                f"{datetime.timedelta(milliseconds=int(self._duration_ms))}"
                if as_str
                else self._duration_ms
            )
        return f"{None}" if as_str else None

    @ensure_data_loaded
    def get_mean_temperature(self, as_str=False):
        if not self.df.empty:
            if self._mean_temperature is None:
                self._mean_temperature = np.mean(self.df["temperature"])
            return f"{self._mean_temperature:.2f} °C" if as_str else self._mean_temperature
        return f"{None}" if as_str else None

    @ensure_data_loaded
    def get_min_temperature(self, as_str=False):
        if not self.df.empty:
            if self._min_temperature is None:
                self._min_temperature = np.min(self.df["temperature"])
            return f"{self._min_temperature:.2f} °C" if as_str else self._min_temperature
        return f"{None}" if as_str else None

    @ensure_data_loaded
    def get_max_temperature(self, as_str=False):
        if not self.df.empty:
            if self._max_temperature is None:
                self._max_temperature = np.max(self.df["temperature"])
            return f"{self._max_temperature:.2f} °C" if as_str else self._max_temperature
        return f"{None}" if as_str else None

    @ensure_data_loaded
    def get_mean_humidity(self, as_str=False):
        if not self.df.empty:
            if self._mean_humidity is None:
                self._mean_humidity = np.mean(self.df["humidity"])
            return f"{self._mean_humidity:.2f} %" if as_str else self._mean_humidity
        return f"{None}" if as_str else None

    @ensure_data_loaded
    def get_min_humidity(self, as_str=False):
        if not self.df.empty:
            if self._min_humidity is None:
                self._min_humidity = np.min(self.df["humidity"])
            return f"{self._min_humidity:.2f} %" if as_str else self._min_humidity
        return f"{None}" if as_str else None

    @ensure_data_loaded
    def get_max_humidity(self, as_str=False):
        if not self.df.empty:
            if self._max_humidity is None:
                self._max_humidity = np.max(self.df["humidity"])
            return f"{self._max_humidity:.2f} %" if as_str else self._max_humidity
        return f"{None}" if as_str else None

    @ensure_data_loaded
    def get_mean_pressure(self, as_str=False):
        if not self.df.empty:
            if self._mean_pressure is None:
                self._mean_pressure = np.mean(self.df["pressure"])
            return f"{self._mean_pressure:.2f} Pa" if as_str else self._mean_pressure
        return f"{None}" if as_str else None

    @ensure_data_loaded
    def get_min_pressure(self, as_str=False):
        if not self.df.empty:
            if self._min_pressure is None:
                self._min_pressure = np.min(self.df["pressure"])
            return f"{self._min_pressure:.2f} Pa" if as_str else self._min_pressure
        return f"{None}" if as_str else None

    @ensure_data_loaded
    def get_max_pressure(self, as_str=False):
        if not self.df.empty:
            if self._max_pressure is None:
                self._max_pressure = np.max(self.df["pressure"])
            return f"{self._max_pressure:.2f} Pa" if as_str else self._max_pressure
        return f"{None}" if as_str else None

class RecordingEnvironment(
    _InitRecordingMinix, _ReadEnvironmentMinix, _MetaDataRecordingMinix
):
    def __init__(self, session, path: Path, df=None):
        self.session = session
        self._path = path
        self.df = df
        if df is not None:
            self.df.reset_index(drop=True, inplace=True)
        self.parse_receiver()
        self.reset()

    def read_from_storage(self):
        self.read_csv_sanitized()

    @ensure_data_loaded
    def get_df(self):
        return self.df

    @ensure_data_loaded
    def __str__(self):
        to_return = "------------------------------\n"
        if not self.df.empty:
            to_return += f"{self._path} \n \
                receiver: {self._name_receiver} [{self._mac_receiver}] \n \
                duration: {self.get_duration(as_str=True)} \n \
                temperature mean:  {self.get_mean_temperature(True)} - min: {self.get_min_temperature(True)} - max: {self.get_max_temperature(True)} \n \
                humidity mean:  {self.get_mean_humidity(True)} - min: {self.get_min_humidity(True)} - max: {self.get_max_humidity(True)} \n \
                pressure mean:  {self.get_mean_pressure(True)} - min: {self.get_min_pressure(True)} - max: {self.get_max_pressure(True)} \n"
        else:
            to_return += f"{self._path} empty"
        return to_return
