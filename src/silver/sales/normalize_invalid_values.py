import pandas as pd 


def normalize_invalid_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    invalid_strings = [
        "", " ", "NA", "N/A", "NULL", "null",
        "none", "None", "unknown", "UNKNOWN", "?",
        "-", "--", "nan"
    ]

    # >> Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # >> Replace invalid string values globally
    df = df.replace(invalid_strings, pd.NA)

    # >> Clean known text columns (strip whitespace on non-null values only)
    text_cols = ["product"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].where(df[col].isna(), df[col].astype(str).str.strip())
            df[col] = df[col].replace(invalid_strings, pd.NA)

    # >> Clean INT columns
    for col in ["sale_id", "employee_id", "amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # >> Clean date column
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # >> remove negative or impossible IDs 
    if "sale_id" in df.columns:
        df.loc[df["sale_id"] < 0, "sale_id"] = pd.NA

    if "employee_id" in df.columns:
        df.loc[df["employee_id"] <= 0, "employee_id"] = pd.NA

    if "amount" in df.columns:
        df.loc[df["amount"] < 0, "amount"] = pd.NA


    # >> drop fully empty rows
    df = df.dropna(how="all")

    return df


