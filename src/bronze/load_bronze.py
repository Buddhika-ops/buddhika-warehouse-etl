import pandas as pd
from utils.logger import get_logger
from src.db_engine import get_engine
from sqlalchemy import text

logger = get_logger()
engine = get_engine()


def load_employees():
    try:
        logger.info("[BRONZE][EMPLOYEES] load started")

        df = pd.read_csv("data/employee_data.csv")
        df['ingestion_date'] = pd.Timestamp.now()
        with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE bronze_employees"))
            df.to_sql("bronze_employees", connection, if_exists="append", index=False)

        logger.info(f"[BRONZE][EMPLOYEES] load completed | rows={len(df)}")
    except Exception as e:
        logger.error(f"[BRONZE][EMPLOYEES] load failed | error={e}")



def load_sales():
    try:
        logger.info("[BRONZE][SALES] load started")

        chunk_size = 50000
        total = 0
        with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE bronze_sales"))

            for chunk in pd.read_csv("data/sales.csv", chunksize=chunk_size):
                try:
                    chunk['ingestion_date'] = pd.Timestamp.now()
                    chunk.to_sql("bronze_sales", connection, if_exists="append", index=False)

                    total += len(chunk)
                    logger.info(f"[BRONZE][SALES] chunk inserted | rows={len(chunk)}")
                except Exception as e:
                    logger.error(f"[BRONZE][SALES] chunk insert failed | error={e}")
        logger.info(f"[BRONZE][SALES] load completed | rows={total}")
    except Exception as e:
        logger.error(f"[BRONZE][SALES] load failed | error={e}")


def load_attendance():
    logger.info("starting attendance load into bronze_attendance table")
    chunk_size = 50000
    total = 0

    try:
        with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE bronze_attendance"))
            for chunk in pd.read_csv("data/attendance.csv", chunksize=chunk_size):
                try:
                    chunk['ingestion_date'] = pd.Timestamp.now()
                    chunk.to_sql("bronze_attendance", connection, if_exists="append",index=False)

                    total += len(chunk)
                    logger.info(f"inserted chunk: {len(chunk)} rows")
                except Exception as e:
                    logger.error(f"sales loading into bronze_attendance faild:{e}")

        logger.info(f"attendance loaded into bronze_attendance successfuly:{total} rows")

    except Exception as e:
        logger.error(f"attendance load into bronze_attendance failed: {e}")