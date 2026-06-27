# add_derived_columns.py
import pandas as pd

def add_derived_columns(df):
    df = df.copy()

    df["attendance_status"] = (
        df["attendance_hours"] >= 8
    ).map({
        True: "FULL_DAY",
        False: "PARTIAL_DAY"
    })

    df["overtime"] = (
        df["attendance_hours"] - 8
    ).clip(lower=0)

    df["ingestion_date"] = pd.Timestamp.now()

    return df