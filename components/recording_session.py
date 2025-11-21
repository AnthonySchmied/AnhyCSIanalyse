from pathlib import Path
from datetime import datetime
import re

from components.recording import Recording


class RecordingSession:
    def __init__(self, directory):
        super().__init__()

        directory = Path(directory)
        self.recordings = []
        self.environment = None
        self.respiration = []
        self._datetime, self._name, self._mode = self.parse_datetime_name_mode(
            directory.name
        )

        # print(self._datetime)
        # print(self._name)
        # print(self._mode)
        # print("--------------")

        for file_path in directory.iterdir():
            if file_path.suffix == ".csv":
                if file_path.is_file():
                    if "env_" in file_path.name:
                        pass
                    elif "csi_" in file_path.name:
                        rec = Recording(self, file_path)
                        self.recordings.append(rec)
                    elif "rsp_" in file_path.name:
                        print(file_path)

    def __str__(self):
        return "\n".join(str(rec) for rec in self.recordings)

    @staticmethod
    def parse_datetime_name_mode(filename: str):
        # Handles cases like:
        # 20251104_125744_estelle-ian_2 person_static
        # 20251104_125120_estelle-1 person_static
        # 20251104_124422_empty_static
        pattern = r"(\d{8})_(\d{6})_((?:[\w-]+))[-_](2 person|1 person|empty)_(.*)$"
        match = re.match(pattern, filename, re.IGNORECASE)
        if match:
            date_str, time_str, name, mode, _ = match.groups()
            dt = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
            return dt, name, mode
        # fallback for 'empty' with no dash
        pattern_empty = r"(\d{8})_(\d{6})_(empty)_(.*)$"
        match = re.match(pattern_empty, filename, re.IGNORECASE)
        if match:
            date_str, time_str, name, _ = match.groups()
            dt = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
            return dt, name, "empty"
        raise ValueError(f"Filename does not match expected format: {filename}")

    def get_senders_name_mac(self):
        entries = [rec.get_senders_name_mac() for rec in self.recordings]
        unique_entries = list({entry for entry in entries})
        return unique_entries

    def get_receivers_name_mac(self):
        entries = [rec.get_receivers_name_mac() for rec in self.recordings]
        unique_entries = list({entry for entry in entries})
        return unique_entries

    def get_frequencies(self):
        entries = [rec.get_frequencies() for rec in self.recordings]
        unique_freqs = sorted({freq for sublist in entries for freq in sublist})
        return unique_freqs

    def get_recordings_filtered(self, dates, names, modes, senders, receivers):
        if (
            self._datetime.date() in dates
            and self._name in names
            and self._mode in modes
        ):
            return [
                rec.get_recordings_filtered(senders, receivers)
                for rec in self.recordings
            ]
        else:
            return []

    def get_recording(self, sender_mac=None, receiver_mac=None, freqs=None):
        to_return = []
        [
            to_return.extend(rec.get_recording(sender_mac, receiver_mac, freqs))
            for rec in self.recordings
        ]
        return to_return

    def get_recordings_set(self):
        return [rec for rec in self.recordings]

    def split_and_cut_subrecordings(self, cut_first_ms, total_length):
        [
            rec.split_and_cut_subrecordings(cut_first_ms, total_length)
            for rec in self.recordings
        ]

    def split_by_frequency(self):
        [rec.split_by_frequency() for rec in self.recordings]

    def remove_subcarrier(self, index: list):
        [rec.remove_subcarrier(index) for rec in self.recordings]

    def save_split_by_frequency_to_file(self):
        self.split_by_frequency()
        for rec in self.recordings:
            rec.save_to_file_if_split()

    def get_datetime(self):
        return self._datetime

    def get_date(self):
        return self._datetime.date()
    
    def get_time(self):
        return self._datetime.time()

    def get_name(self):
        return self._name

    def get_mode(self):
        return self._mode
