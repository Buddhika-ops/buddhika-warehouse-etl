import pandas as pd
from sqlalchemy import text
from src.db_engine import get_engine
from utils.logger import get_logger
from src.silver.employee.apply_employee_range_validation import get_employee_range_validation_mask

engine = get_engine()
logger = get_logger()


def load_rejected_employees(df):
    logger.info("[SILVER][EMPLOYEES][REJECTED] process started")
    try:
        rejected_df = df.copy()
        rejected_df["rejection_reason"] = ""

        validation_mask = get_employee_range_validation_mask(rejected_df)
        rejected_df = rejected_df[~validation_mask].copy()

        def build_reason(row):
            reasons = []

            if pd.isna(row["employee_id"]) or row["employee_id"] <= 0:
                reasons.append("invalid_employee_id")

            if pd.isna(row["age"]) or row["age"] < 18 or row["age"] > 70:
                reasons.append("invalid_age")

            if pd.isna(row["years_of_experience"]) or row["years_of_experience"] < 0 or row["years_of_experience"] > 50:
                reasons.append("invalid_experience")

            if pd.isna(row["salary"]) or row["salary"] < 10000 or row["salary"] > 1_000_000:
                reasons.append("invalid_salary")

            if (
                pd.notna(row["age"]) and pd.notna(row["years_of_experience"])
                and (
                    row["years_of_experience"] >= row["age"]
                    or (row["age"] - row["years_of_experience"]) < 18
                )
            ):
                reasons.append("experience_age_rule_violation")

            return ",".join(reasons)

        rejected_df["rejection_reason"] = rejected_df.apply(build_reason, axis=1)
        rejected_df["rejected_at"] = pd.Timestamp.now()

        upsert_query = text("""
            INSERT INTO silver_employees_rejected (
                employee_id,
                name,
                department,
                age,
                years_of_experience,
                salary,
                city,
                rejection_reason,
                rejected_at
            )
            VALUES (
                :employee_id,
                :name,
                :department,
                :age,
                :years_of_experience,
                :salary,
                :city,
                :rejection_reason,
                :rejected_at
            )
            ON CONFLICT (employee_id)
            DO UPDATE SET
                name                = EXCLUDED.name,
                department          = EXCLUDED.department,
                age                 = EXCLUDED.age,
                years_of_experience = EXCLUDED.years_of_experience,
                salary              = EXCLUDED.salary,
                city                = EXCLUDED.city,
                rejection_reason    = EXCLUDED.rejection_reason,
                rejected_at         = EXCLUDED.rejected_at
        """)

       
        if not rejected_df.empty:
            records = rejected_df.where(pd.notna(rejected_df), None).to_dict(orient="records")
            with engine.begin() as connection:
                connection.execute(upsert_query, records)

        logger.info(f"[SILVER][EMPLOYEES][REJECTED] completed | rows={len(rejected_df)}")

    except Exception as e:
        logger.error(f"[SILVER][EMPLOYEES][REJECTED] failed | error={e}")