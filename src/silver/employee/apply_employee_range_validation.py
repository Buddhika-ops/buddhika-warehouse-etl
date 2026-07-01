import pandas as pd


def get_employee_range_validation_mask(df: pd.DataFrame) -> pd.Series:
    return (
        # >> employee_id
        (df["employee_id"].notna()) &
        (df["employee_id"] > 0) &

        # >> age
        (df["age"].notna()) &
        (df["age"].between(18, 70)) &

        # >> years_of_experience
        (df["years_of_experience"].notna()) &
        (df["years_of_experience"].between(0, 50)) &

        # >> salary
        (df["salary"].notna()) &
        (df["salary"].between(10000, 1_000_000)) &

        # >> business rules
        (df["years_of_experience"] < df["age"]) &
        ((df["age"] - df["years_of_experience"]) >= 18)
    )


def apply_employee_range_validation(df: pd.DataFrame) -> pd.DataFrame:
    return df[get_employee_range_validation_mask(df)].copy()