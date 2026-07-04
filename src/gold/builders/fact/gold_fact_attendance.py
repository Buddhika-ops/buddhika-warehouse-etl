import pandas as pd
from utils.db_engine import get_engine
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df
from datetime import datetime
from utils.watermark import update_watermark

engine = get_engine()


def gold_fact_attendance(logger,batch_id):
    try:
        df_gold = get_silver_table_reader('silver_attendance',engine= engine,watermark="gold_fact_attendance")

        if df_gold.empty:
            logger.warning(f"[GOLD][gold_fact_attendance][{batch_id}] No data found in silver_attendance")
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

        df_gold['ingestion_date'] = datetime.utcnow()
        df_gold = df_gold[[
            'employee_id',
            'date_key',
            'attendance_hours',
            'attendance_status',
            'overtime',
            'is_present',
            'ingestion_date'
        ]]

        update_watermark(table_name='gold_fact_attendance',status='RUNNING',batch_id=batch_id,row_count=len(df_gold))
        write_gold_data_df('gold_fact_attendance',df=df_gold,engine=engine)
        update_watermark(table_name='gold_fact_attendance',status='SUCCESS',batch_id=batch_id,row_count=len(df_gold))
        return len(df_gold)
    
    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_fact_attendance][{batch_id}] {e}")
        update_watermark(table_name='gold_fact_attendance',status='FAILD',batch_id=batch_id,row_count=len(df_gold))
        raise
    