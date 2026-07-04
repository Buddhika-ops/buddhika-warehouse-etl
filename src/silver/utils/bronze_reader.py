import pandas as pd
from sqlalchemy import text
from utils.watermark import get_last_watermark

def get_bronze_table_reader(table_name, engine,watermark):

    last_read_date = get_last_watermark(watermark)

    read_query =text(f"""
    SELECT * 
    FROM {table_name}
    WHERE ingestion_date > :last_read_date;
    """)

    df = pd.read_sql(read_query, engine, params={"last_read_date": last_read_date})

    return df.copy()
