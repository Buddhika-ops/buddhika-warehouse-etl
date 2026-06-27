
import pandas as pd

def convert_attendance_types(df):
    df = df.copy()

    df["employee_id"] = pd.to_numeric(
        df["employee_id"],
        errors="coerce"
    )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df["attendance_hours"] = pd.to_numeric(
        df["attendance_hours"],
        errors="coerce"
    )

    return df