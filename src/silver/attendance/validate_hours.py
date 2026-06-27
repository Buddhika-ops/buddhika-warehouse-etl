# validate_hours.py
def remove_invalid_hours(df):
    return df[
        (df["attendance_hours"] >= 0)
        &
        (df["attendance_hours"] <= 24)
    ]