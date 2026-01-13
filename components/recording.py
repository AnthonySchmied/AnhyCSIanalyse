from pathlib import Path
from components.amplitudes import Amplitudes
from components.phases import Phases
from components.complex_values import ComplexValues
from components.metadata_unpack import MetadataUnpack as MDP
import pandas as pd
import numpy as np
import datetime
import ast
import re

# FORCE_READ_CSV = True
FORCE_READ_CSV = False

DEBUG = False

def ensure_data_loaded(func):
    def wrapper(self, *args, **kwargs):
        if getattr(self, "df", None) is None or getattr(self, "df", None).empty:
            self.read_from_storage()
        return func(self, *args, **kwargs)

    return wrapper


class _InitRecordingMinix:
    def reset(self):
        self._duration_ms = None
        self._tx_packets_count = None
        self._tx_packets_lost = None
        self._tx_packets_lost_ratio = None
        self._rx_packets_count = None
        self._rx_packets_lost = None
        self._rx_packets_lost_ratio = None
        self._frequencies = None
        self._mean_tx_interval = None
        self._median_tx_interval = None
        self._max_tx_interval = None
        self._min_tx_interval = None
        self._mean_rx_interval = None
        self._median_rx_interval = None
        self._max_rx_interval = None
        self._min_rx_interval = None
        self._subrecordings_split_by_freq = None
        self._amplitudes = None
        self._mean_amplitudes = None


class _ReadRecordingMinix:
    def parse_sender_receiver(self):
        m = re.match(
            r"^csi_([0-9a-fA-F]{6})_([^_]+)-([0-9a-fA-F]{6})_([^_]+)\.csv$",
            self._path.name,
        )
        if m:
            (
                self._mac_receiver,
                self._name_receiver,
                self._mac_sender,
                self._name_sender,
            ) = (m.group(1), m.group(2), m.group(3), m.group(4))
        else:
            self._mac_receiver = None
            self._name_receiver = None
            self._mac_sender = None
            self._name_sender = None

    def _read_from_pickle(self):
        try:
            pickle_path = self.get_pickle_path()
            if DEBUG:
                print(f"Loading from pickle: {pickle_path}")
            self.df = pd.read_pickle(pickle_path)

            # data_bundle = joblib.load("dataset.joblib")
            # self.df = data_bundle["main"]
            # if len(data_bundle["sub"].keys()) > 0:
            #     self._subrecordings_split_by_freq = []
            # for key in data_bundle["sub"].keys():
            #     sub_rec = Recording(
            #             self.session,
            #             self._path,
            #             data_bundle["sub"][key]
            #         )
            #     print(sub_rec.df.head())
            #     self._subrecordings_split_by_freq.append(sub_rec)
        except Exception as e:
            print(f"Error loading pickle: {e}, reparsing CSV...")
            raise e

    def _save_to_pickle(self):
        # data = {"main": self.df, "sub": {}}
        # if self._subrecordings_split_by_freq is not None:
        #     for subrec in self._subrecordings_split_by_freq:
        #         data["sub"][int(subrec.get_frequencies()[0])] = subrec.df
        # joblib.dump(data, self.get_pickle_path())
        
        self.df.to_pickle(self.get_pickle_path())

    def _read_from_csv(self):
        # only parse file the first time -> pickle keeps format
        print(f"load from csv: {self._path}")
        cols = [
            "timestamp_pc",
            "receiver_mac",
            "sender_mac",
            "tx_counter",
            "rx_counter",
            "tx_time",
            "rx_time",
            "tx_frequency",
            "rssi",
            "noise_floor",
            "raw_data",
            "amplitude",
            "phase",
        ]

        try:
            self.df = pd.read_csv(self._path, names=cols, header=0, dtype=str)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return

        # Check if last row contains the marker "END OF RECORDING"
        if not self.df.iloc[-1].astype(str).str.contains("END OF RECORDING").any():
            print(f"\n path: {self._path} \n")
            raise Exception("DataFrame invalid: no END OF RECORDING marker.")

        numeric_cols = [
            "tx_counter",
            "rx_counter",
            "tx_time",
            "rx_time",
            "tx_frequency",
            "rssi",
            "noise_floor",
        ]
        self.df[numeric_cols] = self.df[numeric_cols].apply(
            pd.to_numeric, errors="coerce"
        )
        self.df["rx_time"] = pd.to_numeric(self.df["rx_time"], errors="coerce").astype(
            "Int64"
        )
        self.df["tx_time"] = pd.to_numeric(self.df["tx_time"], errors="coerce").astype(
            "Int64"
        )
        self.df["mask"] = True
        self._update_time()
        self.df = self.df[self.df["tx_frequency"].between(0, 500)]
        self.df = self.df[self.df["tx_counter"].between(0, 1e7)]
        self.df = self.df[self.df["rx_counter"].between(0, 1e7)]
        self.df["amplitude"] = self.df["amplitude"].apply(ast.literal_eval)
        self.df["phase"] = self.df["phase"].apply(ast.literal_eval)
        self.df["raw_data"] = self.df["raw_data"].apply(ast.literal_eval)
        self.df["complex"] = [
            ([complex(row[i], row[i + 1]) for i in range(0, len(row), 2)])
            for row in self.df["raw_data"]
        ]
        self.df.dropna(subset=cols, inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self._save_to_pickle()

    def read_csv_santizied(self):
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
                self._duration_ms = (
                    self.df.iloc[-1]["rx_time"] - self.df.iloc[0]["rx_time"]
                ) / 1e3
            return (
                f"{datetime.timedelta(milliseconds=self._duration_ms)}"
                if as_str
                else self._duration_ms
            )
        return f"{None}" if as_str else None

    def get_tx_packets_count(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["tx_counter"]) == 0:
            if self._tx_packets_count is None:  # calculate if necessary
                first_index = self.df.iloc[0]["tx_counter"]
                last_index = self.df.iloc[-1]["tx_counter"]
                self._tx_packets_count = int(last_index - first_index + 1)
            return f"{self._tx_packets_count}" if as_str else self._tx_packets_count
        return f"{None}" if as_str else None

    def get_tx_packets_lost(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["tx_counter"]) == 0:
            if self._tx_packets_lost is None:  # calculate if necessary
                self.get_tx_packets_count()
                self._tx_packets_lost = int(
                    self._tx_packets_count - len(self.df["tx_counter"])
                )
            return f"{self._tx_packets_lost}" if as_str else self._tx_packets_lost
        return f"{None}" if as_str else None

    def get_tx_lost_ratio(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["tx_counter"]) == 0:
            if self._tx_packets_lost_ratio is None:  # calculate if necessary
                if self._tx_packets_lost_ratio is None:
                    self.get_tx_packets_count()
                    self._tx_packets_lost_ratio = (
                        self.get_tx_packets_lost() / self.get_tx_packets_count() * 100
                    )
            return (
                f"{self._tx_packets_lost_ratio:.2f} %"
                if as_str
                else self._tx_packets_lost_ratio
            )
        return f"{None}" if as_str else None

    def get_rx_packets_count(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["rx_counter"]) == 0:
            if self._rx_packets_count is None:  # calculate if necessary
                first_index = int(self.df.iloc[0]["rx_counter"])
                last_index = int(self.df.iloc[-1]["rx_counter"])
                self._rx_packets_count = last_index - first_index + 1
            return f"{self._rx_packets_count}" if as_str else self._rx_packets_count
        return f"{None}" if as_str else None

    def get_rx_packets_lost(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["rx_counter"]) == 0:
            if self._rx_packets_lost is None:  # calculate if necessary
                self.get_rx_packets_count()
                self._rx_packets_lost = self._rx_packets_count - len(
                    self.df["rx_counter"]
                )
            return f"{self._rx_packets_lost}" if as_str else self._rx_packets_lost
        return f"{None}" if as_str else None

    def get_rx_lost_ratio(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["rx_counter"]) == 0:
            if self._rx_packets_lost_ratio is None:  # calculate if necessary
                self.get_rx_packets_count()
                self._rx_packets_lost_ratio = (
                    self.get_rx_packets_lost() / self.get_rx_packets_count() * 100
                )
            return (
                f"{self._rx_packets_lost_ratio:.2f} %"
                if as_str
                else self._rx_packets_lost_ratio
            )
        return f"{None}" if as_str else None

    def get_mean_tx_interval(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["tx_counter"]) == 0:
            if self._mean_tx_interval is None:  # calculate if necessary
                tx_intervals = []
                last_tx_time = self.df.iloc[0]["tx_time"]
                for tx_time in self.df["tx_time"][1:-1]:
                    tx_intervals.append(tx_time - last_tx_time)
                    last_tx_time = tx_time
                if len(tx_intervals) > 0:
                    self._mean_tx_interval = (
                        sum(tx_intervals) / len(tx_intervals)
                    ) / 1e3
                    intervals_sorted = sorted(tx_intervals)
                    self._median_tx_interval = np.median(tx_intervals) / 1e3
                    self._max_tx_interval = [i / 1e3 for i in intervals_sorted[-10:]]
                    self._min_tx_interval = [i / 1e3 for i in intervals_sorted[:10]]
                    return (
                        f"{self._mean_tx_interval:.2f} ms"
                        if as_str
                        else self._mean_tx_interval
                    )
                return f"{None}" if as_str else None
            return (
                f"{self._mean_tx_interval:.2f} ms" if as_str else self._mean_tx_interval
            )
        return f"{None}" if as_str else None

    def get_median_tx_intervall(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["tx_counter"]) == 0:
            if self._median_tx_interval is None:  # calculate if necessary
                self.get_mean_tx_interval()
            return (
                f"{self._median_tx_interval} ms" if as_str else self._median_tx_interval
            )
        return f"{None}" if as_str else None

    def get_max_tx_interval(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["tx_counter"]) == 0:
            if self._max_tx_interval is None:  # calculate if necessary
                self.get_mean_tx_interval()
            return f"{self._max_tx_interval} ms" if as_str else self._max_tx_interval
        return f"{None}" if as_str else None

    def get_min_tx_interval(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["tx_counter"]) == 0:
            if self._min_tx_interval is None:  # calculate if necessary
                self.get_mean_tx_interval()
            return f"{self._min_tx_interval} ms" if as_str else self._min_tx_interval
        return f"{None}" if as_str else None

    def get_mean_rx_interval(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["rx_counter"]) == 0:
            if self._mean_rx_interval is None:  # calculate if necessary
                rx_intervals = []
                last_rx_time = self.df.iloc[0]["rx_time"]
                for rx_time in self.df["rx_time"][1:-1]:
                    rx_intervals.append(rx_time - last_rx_time)
                    last_rx_time = rx_time
                if len(rx_intervals) > 0:
                    self._mean_rx_interval = (
                        sum(rx_intervals) / len(rx_intervals)
                    ) / 1e3
                    intervals_sorted = sorted(rx_intervals)
                    self._median_rx_interval = np.median(rx_intervals) / 1e3
                    self._max_rx_interval = [i / 1e3 for i in intervals_sorted[-10:]]
                    self._min_rx_interval = [i / 1e3 for i in intervals_sorted[:10]]
                    return (
                        f"{self._mean_rx_interval:.2f} ms"
                        if as_str
                        else self._mean_rx_interval
                    )
        return f"{None}" if as_str else None

    def get_median_rx_intervall(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["rx_counter"]) == 0:
            if self._median_rx_interval is None:  # calculate if necessary
                self.get_mean_rx_interval()
            return (
                f"{self._median_rx_interval} ms" if as_str else self._median_rx_interval
            )
        return f"{None}" if as_str else None

    def get_max_rx_interval(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["rx_counter"]) == 0:
            if self._max_rx_interval is None:  # calculate if necessary
                self.get_mean_rx_interval()
            return f"{self._max_rx_interval} ms" if as_str else self._max_rx_interval
        return f"{None}" if as_str else None

    def get_min_rx_interval(self, as_str=False):
        if not self.df.empty and not int(self.df.iloc[-1]["rx_counter"]) == 0:
            if self._min_rx_interval is None:  # calculate if necessary
                self.get_mean_rx_interval()
            return f"{self._min_rx_interval} ms" if as_str else self._min_rx_interval
        return f"{None}" if as_str else None

    def get_frequencies(self) -> list:
        if self._frequencies is None:
            frequencies = []
            last_freq = None
            for freq in self.df["tx_frequency"]:
                if freq == 0:  # set fritzbox freq to 10 Hz
                    freq = 10
                if freq != last_freq:
                    frequencies.append(freq)
                    last_freq = freq
            self._frequencies = frequencies
        return self._frequencies

    # def get_mean_amplitude_per_id(self):
    #     if self._mean_amplitudes is None and not self.df.empty:
    #         if self._amplitudes is None:
    #             self.get_amplitudes()
    #         self._mean_amplitudes = {}
    #         for subcarry_index, values in self._amplitudes.items():
    #             if not subcarry_index in self._remove_subcarrier_id:
    #                 self._mean_amplitudes[subcarry_index] = float(np.mean(values))
    #     return self._mean_amplitudes

    def get_datetime_name(self):
        if not self.session is None:
            return self.session._datetime, self.session._name
        return None, None

    def get_datetime(self):
        return self.session.get_datetime()

    def get_date(self):
        return self.session.get_date()

    def get_time(self):
        return self.session.get_time()

    def get_name(self):
        return self.session.get_name()

    def get_mode(self):
        return self.session.get_mode()

    def get_id(self):
        return f"{self.get_datetime()} {self.get_name()} {self.get_frequencies()} {self.get_receivers_name_mac()[0]}"

    def get_label(self):
        return f"{MDP.names_pack([self.get_name()])}_{MDP.days_pack([self.get_date()])}"


    def get_date_packed(self):
        return MDP.days_pack([self.get_date()])

    def get_name_packed(self):
        return MDP.names_pack([self.get_name()])

    def get_recv_packed(self):
        return MDP.receivers_pack([self.get_receivers_name_mac()])

class _TreeTraversaRecordinglMinix:
    @ensure_data_loaded
    def get_recording_freq(self, freq):
        if len(self.get_frequencies()) > 1:
            self.split_by_frequency()
            for rec in self._subrecordings_split_by_freq:
                sub_rec = rec.get_recording_freq(freq)
                if sub_rec is not None:
                    return sub_rec
        else:
            if self.get_frequencies()[0] == freq:
                return self
            else:
                return None
        
    # Obsolete
    @ensure_data_loaded
    def get_recording(self, freqs=None, sender_mac=None, receiver_mac=None):
        to_return = []
        self.get_frequencies()
        if len(self._frequencies) > 1:
            self.split_by_frequency()
            [
                to_return.extend(rec.get_recording(sender_mac, receiver_mac, freqs))
                for rec in self._subrecordings_split_by_freq
            ]
        else:
            if sender_mac is not None and receiver_mac is not None:
                if (
                    sender_mac == self._mac_sender
                    and receiver_mac == self._mac_receiver
                ):
                    if self._frequencies[0] in freqs:
                        to_return.append(self)
                return to_return
            elif receiver_mac is None and sender_mac == self._mac_sender:
                if self._frequencies[0] in freqs:
                    to_return.append(self)
                return to_return
            elif sender_mac is None and receiver_mac == self._mac_receiver:
                if self._frequencies[0] in freqs:
                    to_return.append(self)
            elif sender_mac is None and receiver_mac is None:
                if self._frequencies[0] in freqs:
                    to_return.append(self)
        return to_return

    def get_recordings_filtered(self, senders, receivers):
        if (
            self.get_senders_name_mac() in senders
            and self.get_receivers_name_mac() in receivers
        ):
            return self
        else:
            return None

    def get_subrecordings(self):
        return (
            self._subrecordings_split_by_freq
            if self._subrecordings_split_by_freq is not None
            else []
        )

    def get_subrecording_by_freq(self, freq):
        if self._subrecordings_split_by_freq is not None:
            for rec in self._subrecordings_split_by_freq:
                if freq in rec.get_frequencies():
                    return rec

    def get_senders_name_mac(self):
        return (self._name_sender, self._mac_sender)

    def get_receivers_name_mac(self):
        return (self._name_receiver, self._mac_receiver)


class _AlterRecordingMinix:
    @ensure_data_loaded
    def split_by_frequency(self, drop_first_last=True):
        if (
            not self.df.empty
            and self._subrecordings_split_by_freq is None
            and not self.df.iloc[-1]["tx_frequency"] == 0
        ):
            frequencies = []
            self._subrecordings_split_by_freq = []
            last_freq = self.df.iloc[0].get("tx_frequency")
            split_begin_index = 0
            for idx, row in self.df.iterrows():
                freq = row.get("tx_frequency")
                if freq != last_freq:
                    sub_rec = Recording(
                        self.session,
                        self._path,
                        self.df[split_begin_index : idx - 1].copy(),
                    )
                    sub_rec.remove_subcarrier(self._remove_subcarrier_id)
                    self._subrecordings_split_by_freq.append(sub_rec)
                    split_begin_index = idx
                    frequencies.append(freq)
                    last_freq = freq
            sub_rec = Recording(
                self.session,
                self._path,
                self.df[split_begin_index : len(self.df)].copy(),
            )
            sub_rec.remove_subcarrier(self._remove_subcarrier_id)
            self._subrecordings_split_by_freq.append(sub_rec)
            if len(self._subrecordings_split_by_freq) < 1:
                self._subrecordings_split_by_freq = []
            elif drop_first_last and len(self._subrecordings_split_by_freq) >= 2:
                self._subrecordings_split_by_freq.pop(0)
                self._subrecordings_split_by_freq.pop()
            self._update_time()
            self._save_to_pickle()

    @ensure_data_loaded
    def remove_subcarrier(self, index: list):
        self._remove_subcarrier_id.extend(index)
        if self._subrecordings_split_by_freq is not None:
            for rec in self._subrecordings_split_by_freq:
                rec.remove_subcarrier(index)

    @ensure_data_loaded
    def cut_length_ms(self, front_padding_ms, length_ms):
        if not self.df.empty and self.get_duration() > front_padding_ms + length_ms:
            time_slice_begin = self.df.iloc[0]["rx_time"] + (front_padding_ms * 10**3)
            time_slice_end = time_slice_begin + (length_ms * 10**3)
            df_cut_front = self.df[self.df["rx_time"] >= time_slice_begin].reset_index(
                drop=True
            )
            self.df = df_cut_front[
                df_cut_front["rx_time"] <= time_slice_end
            ].reset_index(drop=True)
            self._update_time()
            self.reset()

    def split_and_cut_subrecordings(self, cut_first_ms, total_length):
        self.split_by_frequency()
        for sub_rec in self.get_subrecordings():
            sub_rec.cut_length_ms(cut_first_ms, total_length)

    @ensure_data_loaded
    def set_mask_frames_at_time(self, time, frames_offset_count=0, frames_count=1):
        self.df["mask"] = False
        # print(self.df.loc[-4:, ["rx_time", "time", "mask", "tx_frequency"]])
        self._update_time()
        # print(self.df.loc[-4:, ["rx_time", "time", "mask", "tx_frequency"]])

        mask_indices = self.df.index[self.df["time"] >= (time * 10**3)].tolist()
        # print(mask_indices[:5])
        mask_indices = mask_indices[frames_offset_count:]
        # print("indeces")
        # print(mask_indices[:5])
        # print(time)
        for idx in mask_indices[:frames_count]:
            self.df.at[idx, "mask"] = True
            # print(self.df.loc[idx, ["rx_time", "time", "mask", "tx_frequency"]])

    def _update_time(self):
        self.df["time"] = self.df["rx_time"] - self.df["rx_time"].iloc[0]

        # print(self.get_frequencies())
        # print(self.df.loc[:4, ["rx_time", "time", "mask", "tx_frequency"]])
        # print(self.df.loc[-4:, ["rx_time", "time", "mask", "tx_frequency"]])


class _OperatorMinix:

    # def __add__(self, other):
    #     if isinstance(other, float) or isinstance(other, int):
    #         return Recording(self.)
    #         new_df = self.df[self.columns] + other
    #         return self.__class__(new_df, self.recording, self.columns)
    #     elif isinstance(other, SignalData):
    #         common_cols = list(set(self.columns) & set(other.columns))
    #         new_df = self.df[common_cols].add(other.df[common_cols])
    #         return self.__class__(new_df.dropna(), other.recording, other.columns)
    #     else:
    #         return NotImplemented

    pass

    # def __sub__(self, other):
    #     if isinstance(other, float) or isinstance(other, int):
    #         new_df = self.df[self.columns] - other
    #         return self.__class__(new_df, self.recording, self.columns)
    #     elif isinstance(other, SignalData):
    #         common_cols = list(set(self.columns) & set(other.columns))
    #         new_df = self.df[common_cols].sub(other.df[common_cols])
    #         return self.__class__(new_df.dropna(), other.recording, other.columns)
    #     else:
    #         return NotImplemented

    # def __mul__(self, other):
    #     if isinstance(other, (float, int)):
    #         new_df = self.df[self.columns] * other
    #         return self.__class__(new_df, self.recording, self.columns)
    #     elif isinstance(other, SignalData):
    #         common_cols = list(set(self.columns) & set(other.columns))
    #         new_df = self.df[common_cols].mul(other.df[common_cols], fill_value=0)
    #         new_df = new_df.dropna()
    #         return self.__class__(new_df, self.recording, common_cols)
    #     else:
    #         return NotImplemented

    # def __truediv__(self, other):
    #     if isinstance(other, (float, int)):
    #         if other == 0:
    #             raise ZeroDivisionError("division by zero")
    #         new_df = self.df[self.columns] / other
    #         return self.__class__(new_df, self.recording, self.columns)
    #     elif isinstance(other, SignalData):
    #         common_cols = list(set(self.columns) & set(other.columns))
    #         new_df = self.df[common_cols].div(other.df[common_cols], fill_value=np.nan)
    #         new_df = new_df.dropna()
    #         return self.__class__(new_df, self.recording, common_cols)
    #     else:
    #         return NotImplemented


class Recording(
    _InitRecordingMinix,
    _ReadRecordingMinix,
    _MetaDataRecordingMinix,
    _TreeTraversaRecordinglMinix,
    _AlterRecordingMinix,
    _OperatorMinix,
):
    def __init__(self, session, path: Path, df=None):
        self.session = session
        self._path = path
        self.df = df
        if df is not None:
            self.df.reset_index(drop=True, inplace=True)
        self.parse_sender_receiver()
        self.reset()
        self._no_tx_counter = None
        self._remove_subcarrier_id = []

        # self.split_by_frequency()

    def read_from_storage(self):
        time1 = datetime.datetime.now()
        self.read_csv_santizied()
        if DEBUG:
            print(f"took: {datetime.datetime.now()-time1} loading {self.get_pickle_path()}")

    @ensure_data_loaded
    def __str__(self):
        to_return = "------------------------------\n"
        if not self.df.empty:
            to_return += f"{self._path} \n \
                sender: {self._name_sender} [{self._mac_sender}] \n \
                receiver: {self._name_receiver} [{self._mac_receiver}] \n \
                duration: {self.get_duration(as_str=True)} \t\t\t frequencies: {self.get_frequencies()}\n \
                tx_packets: {self.get_tx_packets_count(as_str=True)} \t tx_packets_lost: {self.get_tx_packets_lost(as_str=True)} \t tx_lost_ratio: {self.get_tx_lost_ratio(as_str=True)}\n \
                rx_packets: {self.get_rx_packets_count(as_str=True)} \t rx_packets_lost: {self.get_rx_packets_lost(as_str=True)} \t rx_lost_ratio: {self.get_rx_lost_ratio(as_str=True)}\n \
                mean_rx: {ſelf.get_mean_rx_interval(as_str=True)} \t meadian_rx: {self.get_median_rx_intervall(as_str=True)} \n \
                min_rx_intervals: {self.get_min_rx_interval(as_str=True)} \n \
                max_rx_intervals: {self.get_max_rx_interval(as_str=True)} \n \
                mean_tx: {ſelf.get_mean_tx_interval(as_str=True)} \t meadian_tx: {self.get_median_tx_intervall(as_str=True)} \n"  # min_tx_intervals: {ſelf.get_min_tx_interval(as_str=True)} \n \
            # max_tx_intervals: {ſelf.get_max_tx_interval(as_str=True)} \n"
            if self._subrecordings_split_by_freq is not None:
                to_return += f"\t\t num_subrecordings: {len(self._subrecordings_split_by_freq)}\n"
                for rec in self._subrecordings_split_by_freq:
                    to_return += f"{str(rec)}"
                to_return += "------------------------------\n"
            else:
                to_return += "------------------------------\n"
        else:
            to_return += f"{self._path} empty"
        return to_return

    def get_copy(self):
        return self.__class__(self.session, self._path, self.df.copy())

    @ensure_data_loaded
    def get_amplitudes(self):
        return Amplitudes(self.df, rec=self)

    @ensure_data_loaded
    def get_phases(self):
        return Phases(self.df, rec=self)

    @ensure_data_loaded
    def get_complex_values(self):
        return ComplexValues(self.df, rec=self)

    @ensure_data_loaded
    def save_to_file_if_split(self):
        if len(self.get_frequencies()) == 1:
            path = Path(
                self._path.parent,
                f"cutcsi_{int(self._frequencies[0])}{self._path.stem[3:]}.pkl",
            )
            self.df.to_pickle(path)
        else:
            [rec.save_to_file_if_split() for rec in self._subrecordings_split_by_freq]
