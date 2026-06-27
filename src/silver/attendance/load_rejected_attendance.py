import pandas as pd
from sqlalchemy import text
from src.db_engine import get_engine
from utils.logger import get_logger

engine = get_engine()
logger = get_logger()
current_date = pd.Timestamp.today().normalize()
min_date = pd.Timestamp("2020-01-01")


def load_rejected_attendance(df, silver_employees_df):
    logger.info("[SILVER][ATTENDANCE][REJECTED] process started")
    try:
        rejected_df = df.copy()
        rejected_df["rejection_reason"] = ""

        valid_employee_ids = set(silver_employees_df["employee_id"]) 
        def build_reason(row):
            reasons = []

            employee_id_invalid = pd.isna(row["employee_id"]) or row["employee_id"] <= 0
            if employee_id_invalid:
                reasons.append("invalid_employee_id")

            
            if pd.isna(row["date"]):
                reasons.append("invalid_date")
            elif row["date"] > current_date or row["date"] < min_date:
                reasons.append("invalid_date")

            
            if pd.isna(row["attendance_hours"]):
                reasons.append("missing_attendance_hours")
            elif row["attendance_hours"] < 0 or row["attendance_hours"] > 24:
                reasons.append("invalid_attendance_hours")

            if not employee_id_invalid and row["employee_id"] not in valid_employee_ids:
                reasons.append("employee_not_in_silver_employees")

            return ",".join(reasons)

        rejected_df["rejection_reason"] = rejected_df.apply(build_reason, axis=1)
        rejected_df["rejected_at"] = pd.Timestamp.now()
        rejected_df = rejected_df[rejected_df["rejection_reason"] != ""].copy()

        upsert_query = text("""
            INSERT INTO silver_attendance_rejected (
                employee_id,
                date,
                attendance_hours,
                ingestion_date,
                rejection_reason,
                rejected_at
            )
            VALUES (
                :employee_id,
                :date,
                :attendance_hours,
                :ingestion_date,
                :rejection_reason,
                :rejected_at
            )
            ON CONFLICT (employee_id, date)
            DO UPDATE SET
                attendance_hours = EXCLUDED.attendance_hours,
                ingestion_date   = EXCLUDED.ingestion_date,
                rejection_reason = EXCLUDED.rejection_reason,
                rejected_at      = EXCLUDED.rejected_at
        """)

        if not rejected_df.empty:
            records = rejected_df.where(pd.notna(rejected_df), None).to_dict(orient="records")
            with engine.begin() as connection:
                connection.execute(upsert_query, records)

        logger.info(f"[SILVER][ATTENDANCE][REJECTED] load completed | rows={len(rejected_df)}")

    except Exception as e:
        logger.error(f"[SILVER][ATTENDANCE][REJECTED] failed | error={e}")