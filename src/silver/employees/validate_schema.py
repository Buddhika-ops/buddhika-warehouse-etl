import pandas as pd

def validate_schema(df):
    required_columns = [
        "employee_id",
        "name",
        "age",
        "years_of_experience",
        "salary",
        "department",
        "city",
        "ingestion_date"
    ]
    if df is None or df.empty:
        raise ValueError("[SCHEMA VALIDATION] DataFrame is empty or None")
    
    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"[SCHEMA VALIDATION] Missing required columns: {missing_columns}"
        )
    
    critical_cols = ["employee_id", "name"]
    for col in critical_cols:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            import logging
            logging.getLogger().warning(
                f"[SCHEMA VALIDATION] Critical column '{col}' has {null_count} NULL(s) — routing to rejected loader"
            )
 
    return True