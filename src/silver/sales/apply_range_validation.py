def apply_range_validation(df):
    return df[
        df["amount"].notna() &
        (df["amount"] >= 0) &
        (df["amount"] <= 1_000_000)
    ].copy()