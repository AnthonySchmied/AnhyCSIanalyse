from components.recording_session import RecordingSession

class RecordingSessionCollection:
    def __init__(self, paths: list):
        self._sessions = []
        for path in paths:
            for folder in path.iterdir():
                self._sessions.append(RecordingSession(folder))

    def get_sessions(self):
        return self._sessions
    
    def get_recordings_set(self):
        to_return = []
        [to_return.extend(sess.get_recordings_set()) for sess in self._sessions]
        return to_return

    def get_recordings_filtered(
        self, dates=[], names=[], modes=[], senders=[], receivers=[]
    ):
        # Flatten the list of lists and filter out None
        rec_lists = [
            sess.get_recordings_filtered(dates, names, modes, senders, receivers)
            for sess in self._sessions
        ]
        flat_recs = [rec for sublist in rec_lists for rec in sublist if rec is not None]
        return flat_recs

    def sort_by_name_asc(self):
        self._sessions.sort(key=lambda item: item.get_name())

    def get_datetimes(self):
        return list(set([sess.get_datetime() for sess in self._sessions]))

    def get_dates(self):
        return list(set([sess.get_date() for sess in self._sessions]))

    def get_names(self):
        return list(set([sess.get_name() for sess in self._sessions]))

    def get_modes(self):
        return list(set([sess.get_mode() for sess in self._sessions]))

    def get_senders_name_mac(self):
        entries = [sess.get_senders_name_mac() for sess in self._sessions]
        flat_entries = [item for sublist in entries for item in sublist]
        unique_entries = list({tuple(entry) for entry in flat_entries})
        return unique_entries

    def get_receivers_name_mac(self):
        entries = [sess.get_receivers_name_mac() for sess in self._sessions]
        flat_entries = [item for sublist in entries for item in sublist]
        unique_entries = list({tuple(entry) for entry in flat_entries})
        return unique_entries

    @staticmethod
    def applyFilter(ses, senders=[], receivers=[], dates=[], names=[], modes=[]):
            if (
                ses.get_senders_name_mac() in senders
                and ses.get_receivers_name_mac() in receivers
                and ses.get_date() in dates
                and ses.get_name() in names
                and ses.get_mode() in modes
            ):
                return True
            return False