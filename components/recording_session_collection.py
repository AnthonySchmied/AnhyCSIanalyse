from components.recording_session import RecordingSession



class RecordingSessionCollection:
    def __init__(self, paths: list, names: list, modes: list):
        self._sessions = []
        for path in paths:
            for folder in path.iterdir():
                _, name, mode = RecordingSession.parse_datetime_name_mode(folder.name)
                if mode in modes:
                    if mode == "empty":
                        self._sessions.append(RecordingSession(folder))
                    elif name in names:
                        self._sessions.append(RecordingSession(folder))

    def get_sessions(self):
        return self._sessions
    
    def sort_by_name_asc(self):
        self._sessions.sort(key=lambda item: item.get_name())