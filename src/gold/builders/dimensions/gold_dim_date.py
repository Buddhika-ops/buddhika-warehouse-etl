import pandas as pd
from utils.db_engine import get_engine
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df

engine = get_engine()


def gold_dim_date(logger,batch_id):
    try:
        df_silver_sales = get_silver_table_reader('silver_sales',engine= engine)
        df_silver_attendence = get_silver_table_reader('silver_attendance',engine= engine)

        min_date = min(df_silver_sales['date'].min(),df_silver_attendence['date'].min())
        max_date = max(df_silver_sales['date'].max(),df_silver_attendence['date'].max())

        dates = pd.date_range(start=min_date,end=max_date,freq='D')

        df_gold = pd.DataFrame({
            'date_key': dates,
            'year': dates.year,
            'quarter': dates.quarter,
            'month': dates.month,
            'month_name':dates.strftime('%B'),
            'week_of_year':dates.isocalendar().week,
            'day':dates.day,
            'day_of_week':dates.isocalendar().day,
            'day_name': dates.strftime('%A'),
            'is_weekend': dates.isocalendar().day.isin([6,7])
        })


        write_gold_data_df('gold_dim_date',df=df_gold,engine=engine)
        return len(df_gold)
    
    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_dim_date][{batch_id}] {e}")
        raise