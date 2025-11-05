from pathlib import Path
from components.recording_session import RecordingSession
import io
import sys
import pandas as pd

dir = Path("rec/02_recording")

recording_sessions = []

def save_stats_to_file(path, session):
    with open(Path(path, "stats.txt"), "w") as f:
        f.write(str(session))

def clean_dir(path):
    print(path)
    for file in path.iterdir():
        if file.is_file():
            print(file)
            if "776c92_Fritzbox" in file.name:
                print(f"deleted: {file}")
                file.unlink()
            if "rsp_" in file.name:
                print(f"deleted: {file}")
                file.unlink()
            if ".csi_" in file.name:
                print(f"deleted: {file}")
                file.unlink()


for folder in dir.iterdir():
    clean_dir(folder)
    session = RecordingSession(folder)
    session.save_split_by_frequency_to_file()
    save_stats_to_file(folder, session)
    print(folder)
    clean_dir(folder)

for folder in dir.iterdir():
    for cutcsi in folder.iterdir():
        if cutcsi.suffix == ".pkl":
            if "cutcsi_" in cutcsi.name:
                df = pd.read_pickle(cutcsi)
                print(df)