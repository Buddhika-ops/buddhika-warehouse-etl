import pandas as pd
from src.db_engine import get_engine

engine = get_engine()

def write_gold_data_df(table_name,df):
    df.to_sql(
        table_name,
        engine,
        if_exists = 'replace',
        chunksize = 100000
    )