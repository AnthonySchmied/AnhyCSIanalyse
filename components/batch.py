from datetime import datetime

from components.metadata_unpack import MetadataUnpack as MDP

DEBUG = False

class _BatchSesLabel():
    def __init__(self, batchses, day, names, recvs, datetime, freq):
        self._batchses = batchses
        self._id = None
        self._day = day
        self._names = names
        self._recvs = recvs
        self._datetime = datetime
        self._freq = freq

    def get_day(self):
        return self._day

    def get_names(self):
        return self._names

    def get_recvs(self):
        return self._recvs

    def get_datetime(self):
        return self._datetime

    def get_frequency(self):
        return self._freq

    def __str__(self):
        if self._id is None:
            self._id = f"{MDP.days_key_from_packed(self._day)}-{MDP.names_key_from_packed(self._names)}-{MDP.receivers_key_from_packed(self._recvs)}-{str(self._freq)}Hz-{str(self._datetime)}"
        return self._id

class _BatchSes:
    def __init__(self, ses):
        self._ses = ses
        self._id = None

    def load_from_storage_freq(self, freq):
        self._rec = self._ses.get_recording_freq(freq)
        self._freq = freq
        self._id = None

    def get_masked_amplitude(self, start_time, offset, length):
        if DEBUG:
            print(f"time: {start_time} - offset: {offset} - length: {length}")
        self._rec.set_mask_frames_at_time(start_time, offset, length)
        return self._rec.get_amplitudes()

    def get_days(self):
        return self._rec.get_date_packed()

    def get_names(self):
        return self._rec.get_name_packed()

    def get_recvs(self):
        return self._rec.get_recv_packed()

    def get_datetime(self):
        return self._rec.get_datetime()
    
    def get_frequency(self):
        return self._freq

    def get_id(self):
        if self._id is None:
            days = self.get_days()
            names = self.get_names()
            recvs = self.get_recvs()
            datetime = self.get_datetime()
            freq = self.get_frequency()
            self._id = _BatchSesLabel(self, days, names, recvs, datetime, freq)
        return self._id


class Batch:
    def __init__(self, recs):
        recs.sort(
            key=lambda item: item.get_receivers_name_mac()[0],
            reverse=True,
        )
        self._recs = [_BatchSes(rec) for rec in recs]
        self._id = None

    def load_from_storage_freq(self, freq):
        time = datetime.now()
        for rec in self._recs:
            rec.load_from_storage_freq(freq)
        if DEBUG:
            print(f"loaded batch in {datetime.now()-time}")

    def get_masked_amplitude(self, start_time, offset, length):
        return [
            rec.get_masked_amplitude(start_time, offset, length) for rec in self._recs
        ]

    def __len__(self):
        return len(self._recs)

    def get_id(self):
        if self._id is None:
            days = MDP.unique([ses.get_days() for ses in self._recs])
            names = MDP.unique([ses.get_names() for ses in self._recs])
            recvs = MDP.unique([ses.get_recvs() for ses in self._recs])
            datetimes = MDP.unique([ses.get_datetime() for ses in self._recs])
            self._id = f"{MDP.days_key_from_packed(days)}-{MDP.names_key_from_packed(names)}-{MDP.receivers_key_from_packed(recvs)}-{str(datetimes[0])}"
        return self._id

    def __iter__(self):
        return iter(self._recs)

    def __getitem__(self, key):
        return self._recs[key]