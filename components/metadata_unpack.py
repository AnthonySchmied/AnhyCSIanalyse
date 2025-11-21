import datetime


class MetadataUnpack:
    _receivers = {
        1: ("Recv-1", "46ef78"),
        2: ("Recv-2", "73d1b8"),
        3: ("Recv-3", "46e648"),
    }

    _days = {
        1: datetime.date(2025, 11, 4),
        2: datetime.date(2025, 11, 5),
        3: datetime.date(2025, 11, 11),
        4: datetime.date(2025, 11, 12),
    }

    _names = {
        "emt": "empty",
        "e": "estelle",
        "ei": "estelle-ian",
        "ie": "ian-estelle",
        "i": "ian",
        "h": "hussein",
        "ha": "hussein-anthony",
        "ah": "anthony-hussein",
        "a": "anthony",
    }

    @staticmethod
    def receivers_unpack(recv_ids):
        return [MetadataUnpack._receivers[id] for id in recv_ids]

    @staticmethod
    def days_unpack(day_ids):
        return [MetadataUnpack._days[id] for id in day_ids]

    @staticmethod
    def names_unpack(names_ids):
        return [MetadataUnpack._names[id] for id in names_ids]

    @staticmethod
    def receivers_pack(recv_unpacked):
        fingerprint = ""
        for key, value in MetadataUnpack._receivers.items():
            if value in recv_unpacked:
                fingerprint += f"r{key}"
        return fingerprint[:-1]

    @staticmethod
    def days_pack(days_unpacked):
        fingerprint = ""
        for key, value in MetadataUnpack._days.items():
            if value in days_unpacked:
                fingerprint += f"d{key}_"
        return fingerprint[:-1]

    @staticmethod    
    def names_pack(names_unpacked):
        fingerprint = ""
        for key, value in MetadataUnpack._names.items():
            if value in names_unpacked:
                fingerprint += f"{key}_"
        return fingerprint[:-1]
