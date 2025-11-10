from components.recording_session_collection import RecordingSessionCollection
from pathlib import Path
import datetime
import numpy as np
from components.sens_ops import SensOps as so

session_coll = RecordingSessionCollection(
    [Path("rec/01_recording/"), Path("rec/02_recording/")]
)

with open("dom_freqs.csv", "w") as f:
    f.write("Dominant frequencies:\n")

    for ses in filter(
        lambda ses: RecordingSessionCollection.applyFilter(
            ses,
            senders=[("Sender-1", "75eb44")],
            receivers=[
                ("Recv-1", "46ef78"),
                ("Recv-2", "73d1b8"),
                ("Recv-3", "46e648"),
            ],
            dates=[datetime.date(2025, 11, 5), datetime.date(2025, 11, 4)],
            names=["anthony", "empty"],
            modes=["1 person"],
        ),
        session_coll.get_recordings_set(),
    ):
        ses.split_by_frequency()
        rec = ses.get_recording(freqs=[100])[0].get_amplitudes()
        # rec = so.center(rec)
        fft = so.calculate_ftt(rec)

        dominant_freqs = []
        for col in rec.columns:
            print(col)
            print(fft[col])
            dominant_freqs.append(fft[col]["freqs"][np.argmax(fft[col]["magnitude"])])

        # for key in fft:
        #     magnitudes = fft[key]["magnitude"]
        #     freqs = fft[key]["freqs"]
        #     dominant_freq = freqs[np.argmax(magnitudes)]
        #     dominant_freqs.append(dominant_freq)
        #     print(dominant_freqs)
        print(dominant_freqs)
        exit()