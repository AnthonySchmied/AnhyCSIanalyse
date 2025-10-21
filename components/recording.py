from pathlib import Path
import pandas as pd
import numpy as np
import datetime
import copy
import ast
import re


class Recording:
    def __init__(self, session, path: Path, df=None):
        self.session = session
        self._path = path
        self.df = df
        self.parse_sender_receiver()
        self.reset()
        self._no_tx_counter = None
        if df is None:
            self.read_csv_santizied()

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

    def copy(self):
        """
        Returns a deep copy of the Recording instance, including a copy of the DataFrame.
        """
        df_copy = self.df.copy(deep=True) if self.df is not None else None
        new_instance = Recording(self.session, self._path, df_copy)
        # Copy cached/calculated attributes if needed
        new_instance._duration_ms = copy.deepcopy(self._duration_ms)
        new_instance._tx_packets_count = copy.deepcopy(self._tx_packets_count)
        new_instance._tx_packets_lost = copy.deepcopy(self._tx_packets_lost)
        new_instance._tx_packets_lost_ratio = copy.deepcopy(self._tx_packets_lost_ratio)
        new_instance._rx_packets_count = copy.deepcopy(self._rx_packets_count)
        new_instance._rx_packets_lost = copy.deepcopy(self._rx_packets_lost)
        new_instance._rx_packets_lost_ratio = copy.deepcopy(self._rx_packets_lost_ratio)
        new_instance._frequencies = copy.deepcopy(self._frequencies)
        new_instance._mean_tx_interval = copy.deepcopy(self._mean_tx_interval)
        new_instance._median_tx_interval = copy.deepcopy(self._median_tx_interval)
        new_instance._max_tx_interval = copy.deepcopy(self._max_tx_interval)
        new_instance._min_tx_interval = copy.deepcopy(self._min_tx_interval)
        new_instance._mean_rx_interval = copy.deepcopy(self._mean_rx_interval)
        new_instance._median_rx_interval = copy.deepcopy(self._median_rx_interval)
        new_instance._max_rx_interval = copy.deepcopy(self._max_rx_interval)
        new_instance._min_rx_interval = copy.deepcopy(self._min_rx_interval)
        if self._subrecordings_split_by_freq is not None:
            new_instance._subrecordings_split_by_freq = [
                rec.copy() for rec in self._subrecordings_split_by_freq
            ]
        else:
            new_instance._subrecordings_split_by_freq = None
        return new_instance

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

    def push_id_to_session(
        self, instance, mac_receiver, name_receiver, mac_sender, name_sender
    ):
        self.parent.push_id_to_session(
            instance, mac_receiver, name_receiver, mac_sender, name_sender
        )

    def read_csv_santizied(self):
        pickle_path = Path(self._path.parent, "." + self._path.stem + ".pkl")
        
        if pickle_path.is_file():
            try:
                print(f"Loading from pickle: {pickle_path}")
                self.df = pd.read_pickle(pickle_path)
            except Exception as e:
                print(f"Error loading pickle: {e}, reparsing CSV...")
                raise e
        else:
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
            self.df = self.df[self.df["tx_frequency"].between(0, 500)]
            self.df = self.df[self.df["tx_counter"].between(0, 1e7)]
            self.df = self.df[self.df["rx_counter"].between(0, 1e7)]
            self.df["amplitude"] = self.df["amplitude"].apply(ast.literal_eval)
            self.df.dropna(subset=cols, inplace=True)
            self.df.reset_index(drop=True, inplace=True)

            self.df.to_pickle(pickle_path)

    # ========== Tree Traversal ==========

    def get_senders_name_mac(self):
        return (self._name_sender, self._mac_sender)

    def get_receivers_name_mac(self):
        return (self._name_receiver, self._mac_receiver)

    def get_recording(self, sender_mac=None, receiver_mac=None, freqs=None):
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
                if sender_mac == self._mac_sender and receiver_mac == self._mac_receiver:
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
                


            # if sender_mac is not None and receiver_mac is not None and self._mac_sender == sender_mac and self._mac_receiver == receiver_mac:
            #     to_return.append(self)
            # elif (
            #     receiver_mac is None and
            #     self._mac_sender == sender_mac
            #     and self._frequencies[0] in freqs
            # ):
            #     to_return.append(self)
            # elif (
            #     sender_mac is None and
            #     self._mac_receiver == receiver_mac
            #     and self._frequencies[0] in freqs
            # ):
            #     to_return.append(self)
        
        
        return to_return

    def split_and_cut_subrecordings(self, cut_first_ms, total_length):
        self.split_by_frequency()
        for sub_rec in self.get_subrecordings():
            sub_rec.cut_length_ms(cut_first_ms, total_length)
            # sub_rec.remove_first_ms(cut_first_ms)
            # sub_rec.cut_on_end_to_length_ms(total_length)

    # ========== Statistics ==========
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
                    self._subrecordings_split_by_freq.append(sub_rec)
                    split_begin_index = idx
                    frequencies.append(freq)
                    last_freq = freq
            sub_rec = Recording(
                self.session,
                self._path,
                self.df[split_begin_index : len(self.df)].copy(),
            )
            self._subrecordings_split_by_freq.append(sub_rec)
            if len(self._subrecordings_split_by_freq) < 1:
                self._subrecordings_split_by_freq = []
            elif drop_first_last and len(self._subrecordings_split_by_freq) >= 2:
                self._subrecordings_split_by_freq.pop(0)
                self._subrecordings_split_by_freq.pop()
        # else:
        #     self._subrecordings_split_by_freq = None

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

    def remove_subcarrier(self, index: list):
        pass

    def cut_length_ms(self, front_padding_ms, length_ms):
        if not self.df.empty and self.get_duration() > front_padding_ms + length_ms:
            time_slice_begin = self.df.iloc[0]["rx_time"] + front_padding_ms * 1e3
            time_slice_end = time_slice_begin + length_ms * 1e3
            df_cut_front = self.df[self.df["rx_time"] >= time_slice_begin].reset_index(drop=True)
            self.df = df_cut_front[df_cut_front["rx_time"] <= time_slice_end].reset_index(drop=True)
            self.reset()

    def get_amplitudes(self):
        if self._amplitudes is None and not int(self.df.iloc[-1]["tx_counter"]) == 0:
            self._amplitudes = {}
            subcarry_count = len(self.df.get("amplitude")[0])
            for subcarry_index in range(subcarry_count):
                self._amplitudes[subcarry_index+1] = []
            for i in range(len(self.df)):
                for subcarry_index in range(subcarry_count):
                    self._amplitudes[subcarry_index+1].append(
                        self.df.get("amplitude")[i][subcarry_index]
                    )
        return self._amplitudes
