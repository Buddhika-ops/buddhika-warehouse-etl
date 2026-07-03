import pandas as pd
import logging
from utils.db_engine import get_engine
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df



engine = get_engine()
logger = logging.getLogger(__name__) 

def gold_fact_attendance():
    try:
        df_gold = get_silver_table_reader('silver_attendance',engine= engine)

        if df_gold.empty:
            logger.warning("[gold_fact_attendance] No data found in silver_attendance")
            return
        
        gold_dim_employee = get_silver_table_reader('gold_dim_employees',engine=engine)
        gold_dim_date = get_silver_table_reader('gold_dim_date',engine=engine)

        df_gold['date'] = pd.to_datetime(df_gold['date']).dt.date
        gold_dim_date['date_key'] = pd.to_datetime(gold_dim_date['date_key']).dt.date

        df_gold = df_gold.merge(
            gold_dim_employee[['employee_id']],
            on = 'employee_id',
            how = 'left'
        )

        df_gold = df_gold.merge(
            gold_dim_date[['date_key']],
            left_on = 'date',
            right_on = 'date_key',
            how = 'left'
        )
        df_gold['attendance_hours'] = df_gold['attendance_hours']- df_gold['overtime']

        df_gold['is_present'] = df_gold['attendance_status'].isin(
            ['Present','Half-day','Late']
        )
        df_gold = df_gold[[
            'employee_id',
            'date_key',
            'attendance_hours',
            'attendance_status',
            'overtime',
            'is_present'
        ]]

        write_gold_data_df('gold_fact_attendance',df=df_gold,engine=engine)

        logger.info(f'[gold_fact_attendance] cleaning completed | rows={len(df_gold)}')

    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_fact_attendance] {e}")
        raise
    