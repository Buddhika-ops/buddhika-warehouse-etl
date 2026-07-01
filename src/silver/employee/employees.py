import pandas as pd
from sqlalchemy import text
from src.db_engine import get_engine
from datetime import datetime
from utils.logger import get_logger
from utils.watermark import get_last_watermark, update_watermark
from utils.log_step import log_step
from src.silver.employee.validate_schema import validate_schema
from src.silver.employee.normalize_invalid_values import normalize_invalid_values
from src.silver.employee.apply_employee_range_validation import apply_employee_range_validation
from src.silver.employee.silver_employees_rejected import load_rejected_employees
from src.silver.employee.remove_salary_outliers_iqr import remove_salary_outliers_iqr

logger = get_logger()
engine = get_engine()
last_run = get_last_watermark("bronze_employees")
current_year = datetime.now().year


def clean_bronze_employees_table():
    logger.info("[SILVER][EMPLOYEES] cleaning started")
    try:
        query = text("""
            SELECT *
            FROM bronze_employees
            WHERE ingestion_date > :last_run
        """)

        chunk = pd.read_sql(query, engine, params={"last_run": last_run}, chunksize=50000)
        raw_rows = 0
        final_rows = 0

        for df in chunk:
            if df.empty:
                logger.info("[SILVER][EMPLOYEES] Chunk is empty, skipping.")
                continue

            raw_rows += len(df)
            log_step("RAW_LOAD", df, df)

            # >> SCHEMA VALIDATION
            before_schema_df = df
            validate_schema(df)
            log_step("SCHEMA_VALIDATION", before_schema_df, df)

            # >> NORMALIZATION
            before_normalization_df = df
            df = normalize_invalid_values(df)
            log_step("NORMALIZATION", before_normalization_df, df)

            # >> REJECTED CAPTURE
            before_rejected_df = df
            load_rejected_employees(df)
            log_step("REJECTED_CAPTURE", before_rejected_df, df)

            # >> RANGE VALIDATION
            before_range_df = df
            df = apply_employee_range_validation(df)
            log_step("RANGE_VALIDATION", before_range_df, df)

            # >> OUTLIER REMOVAL
            before_outlier_df = df
            df = remove_salary_outliers_iqr(df)
            log_step("OUTLIER_REMOVAL", before_outlier_df, df)

            df["join_date_estimated"] = current_year - df["years_of_experience"]
            df["ingestion_date"] = pd.Timestamp.now()

            logger.info(f"[SILVER][EMPLOYEES] cleaning completed | rows={len(df)}")

            upsert_query = text("""
                INSERT INTO silver_employees (
                    employee_id,
                    name,
                    department,
                    age,
                    years_of_experience,
                    salary,
                    city,
                    join_date_estimated,
                    ingestion_date
                )
                VALUES (
                    :employee_id,
                    :name,
                    :department,
                    :age,
                    :years_of_experience,
                    :salary,
                    :city,
                    :join_date_estimated,
                    :ingestion_date
                )
                ON CONFLICT (employee_id)
                DO UPDATE SET
                    name                = EXCLUDED.name,
                    department          = EXCLUDED.department,
                    age                 = EXCLUDED.age,
                    years_of_experience = EXCLUDED.years_of_experience,
                    salary              = EXCLUDED.salary,
                    city                = EXCLUDED.city,
                    join_date_estimated = EXCLUDED.join_date_estimated,
                    ingestion_date      = EXCLUDED.ingestion_date
            """)

            records = df.where(pd.notna(df), None).to_dict(orient="records")
            with engine.begin() as connection:
                connection.execute(upsert_query, records)

            logger.info(f"[SILVER][EMPLOYEES] load completed | rows={len(df)}")
            final_rows += len(df)

        score = (final_rows / raw_rows) * 100 if raw_rows > 0 else 0
        logger.info(f"[DATA QUALITY SCORE] {score:.2f}%")
        update_watermark("bronze_employees")

    except Exception as e:
        logger.error(f"[SILVER][EMPLOYEES] load failed | error={e}")