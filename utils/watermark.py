import pandas as pd
from sqlalchemy import text
from utils.db_engine import get_engine

engine = get_engine()


def get_last_watermark(watermark):
    table_name = watermark
    query = text(
        """
            SELECT last_loaded_timestamp
            FROM etl_metadata
            WHERE table_name = :table_name
        """
    )
    with engine.begin() as connection:
        result = connection.execute(query, {"table_name": table_name}).fetchone()
    if result is None:
        return pd.Timestamp("2000-01-01")
    return result[0]


def update_watermark(table_name,status,batch_id,row_count):
    query = text("""
        INSERT INTO etl_metadata (
                 table_name, 
                 last_loaded_timestamp,
                 status,
                 batch_id,
                 row_count
                 )
        VALUES (
                 :table_name,
                  NOW(),
                 :status,
                 :batch_id,
                 :row_count
                 )
        ON CONFLICT (table_name)
        DO UPDATE SET 
                 last_loaded_timestamp = NOW(),
                 status = :status,
                 batch_id = :batch_id,
                 row_count = :row_count
    """)

    with engine.begin() as connection:
        connection.execute(query, {
            "table_name": table_name,
            "status": status,
            "batch_id":batch_id,
            "row_count":row_count
            })