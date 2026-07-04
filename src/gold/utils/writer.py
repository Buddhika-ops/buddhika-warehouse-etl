import pandas as pd

def write_gold_data_df(table_name,df,engine):
    df.to_sql(
        table_name,
        engine,
        if_exists = 'append',
        chunksize = 100000,
        index=False
    )