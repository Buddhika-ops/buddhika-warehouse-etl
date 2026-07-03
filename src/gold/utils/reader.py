import pandas as pd

def get_silver_table_reader(table_name, engine):
    read_query =f"""
    SELECT * 
    FROM {table_name};
    """
    df = pd.read_sql(read_query,engine)

    return df.copy()
