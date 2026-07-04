import pandas as pd
from utils.watermark import get_last_watermark
from sqlalchemy import text

def get_silver_table_reader(table_name, engine, watermark = None):
    if watermark:
        last_read_date = get_last_watermark(watermark)

        read_query =text(f"""
        SELECT * 
        FROM {table_name}
        WHERE ingestion_date > :last_read_date;
        """)
        df = pd.read_sql(read_query,engine,params={"last_read_date":last_read_date})
    else:
        read_query =text(f"""
        SELECT * 
        FROM {table_name}
        """)
        df = pd.read_sql(read_query,engine)
    return df.copy()
