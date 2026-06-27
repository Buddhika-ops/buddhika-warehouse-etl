from sqlalchemy import text
from src.db_engine import get_engine

engine = get_engine()


def get_last_watermark(table_name: str):
    query = text(
        """
            SELECT last_loaded_timestamp
            FROM etl_metadata
            WHERE table_name = :table_name
        """
    )
    with engine.connect() as connection:
        result = connection.execute(query, {"table_name": table_name}).fetchone()
    if result is None:
        return None
    return result[0]


def update_watermark(table_name: str):
    query = text("""
        INSERT INTO etl_metadata (table_name, last_loaded_timestamp)
        VALUES (:table_name, NOW())
        ON CONFLICT (table_name)
        DO UPDATE SET last_loaded_timestamp = NOW()
    """)

    with engine.begin() as connection:
        connection.execute(query, {"table_name": table_name})