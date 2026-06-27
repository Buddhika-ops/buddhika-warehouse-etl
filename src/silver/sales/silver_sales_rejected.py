import pandas as pd
from sqlalchemy import text
from src.db_engine import get_engine
from utils.logger import get_logger

engine = get_engine()
logger = get_logger()
current_date = pd.Timestamp.today().normalize()
min_date = pd.Timestamp("2020-01-01")


def load_rejected_sales(df, silver_employee_df):
    logger.info("[SILVER][SALES][REJECTED] process started")
    try:
        rejected_df = df.copy()
        rejected_df["rejection_reason"] = ""

        valid_employee_ids = set(silver_employee_df["employee_id"])

        def build_reason(row):
            reasons = []

            employee_id_invalid = pd.isna(row["employee_id"]) or row["employee_id"] <= 0
            if employee_id_invalid:
                reasons.append("invalid_employee_id")

            if pd.isna(row["sale_id"]) or row["sale_id"] <= 0:
                reasons.append("invalid_sale_id")

            if pd.isna(row["product"]):
                reasons.append("empty_product")

            if pd.isna(row["amount"]) or row["amount"] <= 0:
                reasons.append("invalid_amount")

            if pd.isna(row["date"]):
                reasons.append("invalid_date")
            elif row["date"] > current_date or row["date"] < min_date:
                reasons.append("invalid_date")

            if not employee_id_invalid and row["employee_id"] not in valid_employee_ids:
                reasons.append("employee_not_in_silver_employees")

            return ",".join(reasons)

        rejected_df["rejection_reason"] = rejected_df.apply(build_reason, axis=1)
        rejected_df["rejected_at"] = pd.Timestamp.now()
        rejected_df = rejected_df[rejected_df["rejection_reason"] != ""].copy()

        upsert_query = text("""
            INSERT INTO silver_sales_rejected (
                sale_id,
                employee_id,
                product,
                amount,
                date,
                rejection_reason,
                rejected_at
            )
            VALUES (
                :sale_id,
                :employee_id,
                :product,
                :amount,
                :date,
                :rejection_reason,
                :rejected_at
            )
            ON CONFLICT (sale_id)
            DO UPDATE SET
                employee_id      = EXCLUDED.employee_id,
                product          = EXCLUDED.product,
                amount           = EXCLUDED.amount,
                date             = EXCLUDED.date,
                rejection_reason = EXCLUDED.rejection_reason,
                rejected_at      = EXCLUDED.rejected_at
        """)

        if not rejected_df.empty:
            records = rejected_df.where(pd.notna(rejected_df), None).to_dict(orient="records")
            with engine.begin() as connection:
                connection.execute(upsert_query, records)

        logger.info(f"[SILVER][SALES][REJECTED] load completed | rows={len(rejected_df)}")

    except Exception as e:
        logger.error(f"[SILVER][SALES][REJECTED] failed | error={e}")