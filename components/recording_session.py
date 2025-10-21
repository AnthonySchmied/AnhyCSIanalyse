from pathlib import Path
from datetime import datetime
import re

from components.recording import Recording


class RecordingSession:
    def __init__(self, directory: Path):
        super().__init__()

        self.recordings = []
        self.environment = None
        self.respiration = []
        self._datetime, self._name = self.parse_datetime_name(directory.name)

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

    def parse_datetime_name(self, filename: str):
        # (\d{8})_(\d{6}) -> date + time
        # _(.*) -> rest of the filename as name
        pattern = r"(\d{8})_(\d{6})_(.*)$"
        
        match = re.match(pattern, filename)
        if not match:
            raise ValueError(f"Filename does not match expected format: {filename}")
        
        date_str, time_str, name = match.groups()
        dt = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
        return dt, name

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

    def get_recording(self, sender_mac=None, receiver_mac=None, freqs=None):
        to_return = []
        [
            to_return.extend(rec.get_recording(sender_mac, receiver_mac, freqs))
            for rec in self.recordings
        ]
        return to_return

    def split_and_cut_subrecordings(self, cut_first_ms, total_length):
        [
            rec.split_and_cut_subrecordings(cut_first_ms, total_length)
            for rec in self.recordings
        ]

    def remove_subcarrier(self, index: list):
        [rec.remove_subcarrier(index) for rec in self.recordings]
