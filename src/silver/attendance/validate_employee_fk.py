# validate_employee_fk.py
def validate_employee_fk(df, employee_df):
    mask = df["employee_id"].isin(employee_df["employee_id"])
    return df[mask]