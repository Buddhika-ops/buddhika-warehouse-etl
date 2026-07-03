import pandas as pd
from utils.db_engine import get_engine



engine = get_engine()


def load_employees(logger):
    try:
    
        df = pd.read_csv("data/employee_data.csv")
        df['ingestion_date'] = pd.Timestamp.now()
        with engine.begin() as connection:
            df.to_sql("bronze_employees", connection, if_exists="append", index=False)

        logger.info(f"[BRONZE][EMPLOYEES] rows_written={len(df)}")
    except Exception as e:
        logger.error(f"[BRONZE][EMPLOYEES] load failed | error={e}")



def load_sales(logger):
    try:

        chunk_size = 50000
        total = 0
        with engine.begin() as connection:

            for chunk in pd.read_csv("data/sales.csv", chunksize=chunk_size):
                chunk['ingestion_date'] = pd.Timestamp.now()
                chunk.to_sql("bronze_sales", connection, if_exists="append", index=False)
                total += len(chunk)      
        logger.info(f"[BRONZE][SALES] rows_written={total}")

    except Exception as e:
        logger.error(f"[BRONZE][SALES] load failed | error={e}")


def load_attendance(logger):
    chunk_size = 50000
    total = 0

    try:
        with engine.begin() as connection:
          
            for chunk in pd.read_csv("data/attendance.csv", chunksize=chunk_size):
                chunk['ingestion_date'] = pd.Timestamp.now()
                chunk.to_sql("bronze_attendance", connection, if_exists="append",index=False)
                total += len(chunk)                   
        logger.info(f"[BRONZE][ATTENDANCE] rows_written={total}")

    except Exception as e:
        logger.error(f"[BRONZE][ATTENDANCE] load failed | error={e}")