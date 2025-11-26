import datetime


class MetadataUnpack:
    _receivers = {
        3: ("Recv-3", "46e648"),
        2: ("Recv-2", "73d1b8"),
        1: ("Recv-1", "46ef78"),
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
    def receivers_pack(recvs):
        pack = []
        for key, value in MetadataUnpack._receivers.items():
            if value in recvs:
                pack.append(key)
        return pack

    @staticmethod
    def days_pack(days):
        pack = []
        for key, value in MetadataUnpack._days.items():
            if value in days:
                pack.append(key)
        return pack

    @staticmethod
    def names_pack(names):
        pack = []
        for key, value in MetadataUnpack._names.items():
            if value in names:
                pack.append(key)
        return pack

    @staticmethod
    def receivers_key_from_unpacked(recvs):
        fingerprint = "r"
        for key, value in MetadataUnpack._receivers.items():
            if value in recvs:
                fingerprint += f"{key}"
        return fingerprint

    @staticmethod
    def days_key_from_unpacked(days):
        fingerprint = "d"
        for key, value in MetadataUnpack._days.items():
            if value in days:
                fingerprint += f"{key}_"
        return fingerprint[:-1]

    @staticmethod
    def names_key_from_unpacked(names):
        fingerprint = ""
        for key, value in MetadataUnpack._names.items():
            if value in names:
                fingerprint += f"{key}_"
        return fingerprint[:-1]

    @staticmethod
    def receivers_key_from_packed(recvs):
        fingerprint = "r"
        for key, _ in MetadataUnpack._receivers.items():
            if key in recvs:
                fingerprint += f"{key}"
        return fingerprint

    @staticmethod
    def days_key_from_packed(days):
        fingerprint = "d"
        for key, _ in MetadataUnpack._days.items():
            if key in days:
                fingerprint += f"{key}_"
        return fingerprint[:-1]

    @staticmethod
    def names_key_from_packed(names):
        fingerprint = ""
        for key, _ in MetadataUnpack._names.items():
            if key in names:
                fingerprint += f"{key}_"
        return fingerprint[:-1]

    @staticmethod
    def unique(lst):
        flat = [x for item in lst for x in (item if isinstance(item, list) else [item])]
        return list(dict.fromkeys(flat))
