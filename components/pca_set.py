from components.metadata_unpack import MetadataUnpack
from components.recording_session_collection import RecordingSessionCollection
from components.sens_ops import SensOps as so
from pathlib import Path
class PcaSet():
    def __init__(self, session_coll, receivers, dates, names):
        self._session_coll = session_coll
        self._receivers = MetadataUnpack.receivers_unpack(receivers)
        self._days = MetadataUnpack.days_unpack(dates)
        self._names = MetadataUnpack.names_unpack(names)
        self._senders = [("Sender-1", "75eb44")]
        self._modes = ["empty", "1 person", "2 person"]
        self._get_recodings()

    def _get_recodings(self):
        self._sessions = []
        for ses in filter(
            lambda ses: RecordingSessionCollection.applyFilter(
                ses,
                senders=self._senders,
                receivers=self._receivers,
                dates=self._days,
                names=self._names,
                modes=self._modes,
            ),
            self._session_coll.get_recordings_set(),
        ):
            self._sessions.append(ses)

    def compute_pca(self, freq, mask_time, mask_offset, mask_frames):
        results = []
        self.freqs = freq
        for ses in self._sessions:
            rec = ses.get_recording(freqs=[freq])[0]
            print(rec.get_frequencies())
            print(rec.get_id())
            rec.set_mask_frames_at_time(mask_time, mask_offset, mask_frames);
            data = rec.get_amplitudes()
            print(data.df.head())
            results.append(so.pca(data))
        return results
    
    def get_save_path(self, i):
        file = f"{MetadataUnpack.names_pack(self._names)}_{self.freqs}_{MetadataUnpack.days_pack(self._days)}_{i}.png"
        return Path("plots", "pca", file)
