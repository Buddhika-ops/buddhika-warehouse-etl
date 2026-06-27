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

    # >> Clean string columns
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        df[col] = (
            df[col].astype(str).str.strip().replace(invalid_strings, pd.NA)
        )

    # >> Clean INT columns
    int_cols = df.select_dtypes(include=["int64", "int32"]).columns
    for col in int_cols:
        df[col] = pd.to_numeric(df[col],errors="coerce").astype("Int64")


    # >> remove negative or impossible IDs   
    if "employee_id" in df.columns:
        df.loc[df["employee_id"] <= 0, "employee_id"] = pd.NA

    if "age" in df.columns:
        df.loc[(df["age"] < 0) | (df["age"] > 100), "age"] = pd.NA

    if "years_of_experience" in df.columns:
        df.loc[(df["years_of_experience"] < 0), "years_of_experience"] = pd.NA

    if "salary" in df.columns:
        df.loc[df["salary"] < 0, "salary"] = pd.NA

    # >> drop fully empty rows
    df = df.dropna(how="all")

    return df


