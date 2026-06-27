import pandas as pd

def validate_schema(df):
    required_columns = [
        "sale_id",
        "employee_id",
        "product",
        "amount",
        "date",
        "ingestion_date",
    ]

    if df is None or df.empty:
        raise ValueError("[SCHEMA VALIDATION] DataFrame is empty or None")
    
    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"[SCHEMA VALIDATION] Missing required columns: {missing_columns}"
        )
    
    # >>Only sale_id is truly critical — missing means we can't identify the record
    critical_cols = ["sale_id"]
    for col in critical_cols:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            import logging
            logging.getLogger().warning(
                f"[SCHEMA VALIDATION] Critical column '{col}' has {null_count} NULL(s) — routing to rejected loader"
            )
 
    return True
 