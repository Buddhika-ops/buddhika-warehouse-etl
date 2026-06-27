import pandas as pd
from sqlalchemy import text
from src.db_engine import get_engine
from datetime import datetime
from utils.logger import get_logger
from utils.watermark import get_last_watermark, update_watermark
from utils.log_step import log_step
from src.silver.attendance.add_derived_columns import add_derived_columns
from src.silver.attendance.convert_types import convert_attendance_types
from src.silver.attendance.filter_dates import remove_future_dates
from src.silver.attendance.load_rejected_attendance import load_rejected_attendance
from src.silver.attendance.validate_employee_fk import validate_employee_fk
from src.silver.attendance.validate_hours import remove_invalid_hours
from src.silver.attendance.validate_schema import validate_schema

logger = get_logger()
engine = get_engine()
last_run = get_last_watermark("bronze_attendance")


def clean_bronze_attendance_table():
    logger.info("[SILVER][ATTENDANCE] cleaning started")
    try:
        with engine.connect() as connection:
            silver_employee_df = pd.read_sql("SELECT employee_id FROM silver_employees", connection)

        query = text("""
            SELECT *
            FROM bronze_attendance
            WHERE ingestion_date > :last_run
        """)

        chunk = pd.read_sql(query, engine, params={"last_run": last_run}, chunksize=50000)
        raw_rows = 0
        final_rows = 0

        for df in chunk:
            if df.empty:
                logger.info("[SILVER][ATTENDANCE] Chunk is empty, skipping.")
                continue

            raw_rows += len(df)
            log_step("RAW_LOAD", df, df, logger)

            # >> TYPE CONVERSION
            before_conversion_df = df
            df = convert_attendance_types(df)
            log_step("TYPE_CONVERSION", before_conversion_df, df, logger)

            # >> SCHEMA VALIDATION
            before_schema_df = df
            validate_schema(df)
            log_step("SCHEMA_VALIDATION", before_schema_df, df, logger)

            # >> REJECTED CAPTURE
            before_rejected_df = df
            load_rejected_attendance(df, silver_employee_df)
            log_step("REJECTED_CAPTURE", before_rejected_df, df, logger)

            # >> FK VALIDATION
            before_fk_df = df
            df = validate_employee_fk(df, silver_employee_df)
            log_step("FK_VALIDATION", before_fk_df, df, logger)

            # >> HOURS VALIDATION
            before_hours_df = df
            df = remove_invalid_hours(df)
            log_step("HOURS_VALIDATION", before_hours_df, df, logger)

            # >> DATE FILTER
            before_date_df = df
            df = remove_future_dates(df)
            log_step("DATE_FILTER", before_date_df, df, logger)

            # >> DERIVED COLUMNS
            before_derived_df = df
            df = add_derived_columns(df)
            log_step("DERIVED_COLUMNS", before_derived_df, df, logger)

            logger.info(f"[SILVER][ATTENDANCE] cleaning completed | rows={len(df)}")

            upsert_query = text("""
                INSERT INTO silver_attendance (
                    employee_id,
                    date,
                    attendance_hours,
                    ingestion_date,
                    attendance_status,
                    overtime
                )
                VALUES (
                    :employee_id,
                    :date,
                    :attendance_hours,
                    :ingestion_date,
                    :attendance_status,
                    :overtime
                )
                ON CONFLICT (employee_id, date)
                DO UPDATE SET
                    employee_id     = EXCLUDED.employee_id,
                    date            = EXCLUDED.date,
                    attendance_hours = EXCLUDED.attendance_hours,
                    ingestion_date  = EXCLUDED.ingestion_date,
                    attendance_status = EXCLUDED.attendance_status,
                    overtime        = EXCLUDED.overtime
            """)

            records = df.where(pd.notna(df), None).to_dict(orient="records")
            with engine.begin() as connection:
                connection.execute(upsert_query, records)

            logger.info(f"[SILVER][ATTENDANCE] load completed | rows={len(df)}")
            final_rows += len(df)

        score = (final_rows / raw_rows) * 100 if raw_rows > 0 else 0
        logger.info(f"[DATA QUALITY SCORE] {score:.2f}%")
        update_watermark("bronze_attendance")

    except Exception as e:
        logger.error(f"[SILVER][ATTENDANCE] load failed | error={e}")