import pandas as pd
from sqlalchemy import text
from src.db_engine import get_engine
from datetime import datetime
from utils.logger import get_logger
from utils.watermark import get_last_watermark, update_watermark
from utils.log_step import log_step
from src.silver.sales.normalize_invalid_values import normalize_invalid_values
from src.silver.sales.validate_schema import validate_schema
from src.silver.sales.silver_sales_rejected import load_rejected_sales
from src.silver.sales.apply_range_validation import apply_range_validation
from src.silver.sales.remove_outliers_iqr import remove_outliers_iqr
from src.silver.sales.validate_employee_fk import validate_employee_fk

logger = get_logger()
engine = get_engine()
last_run = get_last_watermark("bronze_sales")


def clean_bronze_sales_table():
    logger.info("[SILVER][SALES] cleaning started")
    try:
        with engine.connect() as connection:
            silver_employee_df = pd.read_sql("SELECT employee_id FROM silver_employees", connection)

        query = text("""
            SELECT *
            FROM bronze_sales
            WHERE ingestion_date > :last_run
        """)

        chunk = pd.read_sql(query, engine, params={"last_run": last_run}, chunksize=50000)
        raw_rows = 0
        final_rows = 0

        for df in chunk:
            if df.empty:
                logger.info("[SILVER][SALES] Chunk is empty, skipping.")
                continue

            raw_rows += len(df)
            log_step("RAW_LOAD", df, df, logger)

            # >> NORMALIZATION
            before_normalization_df = df
            df = normalize_invalid_values(df)
            log_step("NORMALIZATION", before_normalization_df, df, logger)

            # >> SCHEMA VALIDATION
            before_schema_df = df
            validate_schema(df)
            log_step("SCHEMA_VALIDATION", before_schema_df, df, logger)

            # >> REJECTED CAPTURE
            before_rejected_df = df
            load_rejected_sales(df, silver_employee_df)
            log_step("REJECTED_CAPTURE", before_rejected_df, df, logger)

            # >> RANGE VALIDATION
            before_range_df = df
            df = apply_range_validation(df)
            log_step("RANGE_VALIDATION", before_range_df, df, logger)

            # >> OUTLIER REMOVAL
            before_outlier_df = df
            df = remove_outliers_iqr(df)
            log_step("OUTLIER_REMOVAL", before_outlier_df, df, logger)

            # >> FK VALIDATION
            before_fk_df = df
            df = validate_employee_fk(df, silver_employee_df["employee_id"])
            log_step("FK_VALIDATION", before_fk_df, df, logger)

            df["ingestion_date"] = pd.Timestamp.now()

            logger.info(f"[SILVER][SALES] cleaning completed | rows={len(df)}")

            upsert_query = text("""
                INSERT INTO silver_sales (
                    sale_id,
                    employee_id,
                    product,
                    amount,
                    date,
                    ingestion_date
                )
                VALUES (
                    :sale_id,
                    :employee_id,
                    :product,
                    :amount,
                    :date,
                    :ingestion_date
                )
                ON CONFLICT (sale_id)
                DO UPDATE SET
                    employee_id    = EXCLUDED.employee_id,
                    product        = EXCLUDED.product,
                    amount         = EXCLUDED.amount,
                    date           = EXCLUDED.date,
                    ingestion_date = EXCLUDED.ingestion_date
            """)

            records = df.where(pd.notna(df), None).to_dict(orient="records")
            with engine.begin() as connection:
                connection.execute(upsert_query, records)

            logger.info(f"[SILVER][SALES] load completed | rows={len(df)}")
            final_rows += len(df)

        score = (final_rows / raw_rows) * 100 if raw_rows > 0 else 0
        logger.info(f"[DATA QUALITY SCORE] {score:.2f}%")
        update_watermark("bronze_sales")

    except Exception as e:
        logger.error(f"[SILVER][SALES] load failed | error={e}")