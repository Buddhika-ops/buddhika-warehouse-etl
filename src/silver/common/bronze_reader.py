import pandas as pd
from utils.db_engine import get_engine

engine = get_engine()

def get_bronze_table_reader(table_name):
    read_query =f"""
    SELECT * 
    FROM {table_name};
    """

    df = pd.read_sql(read_query,engine)

    return df
