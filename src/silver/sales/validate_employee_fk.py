def validate_employee_fk(df, valid_employee_ids):
    return df[df["employee_id"].isin(valid_employee_ids)].copy()