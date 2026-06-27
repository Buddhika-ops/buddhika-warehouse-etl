import pandas as pd

def remove_future_dates(df):
    today = pd.Timestamp.today().normalize()

    return df[
        df["date"] <= today
    ]