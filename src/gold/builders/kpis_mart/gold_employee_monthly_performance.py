import pandas as pd
import logging
from utils.db_engine import get_engine
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df



engine = get_engine()
logger = logging.getLogger(__name__) 

def gold_employee_monthly_performance():
    try:
        gold_fact_attendance = get_silver_table_reader('gold_fact_attendance',engine= engine)

        if gold_fact_attendance.empty:
            logger.warning("[gold_employee_monthly_performance] No data found in gold_fact_attendance")
            return
        
        gold_fact_sales = get_silver_table_reader('gold_fact_sales',engine= engine)
        gold_dim_date = get_silver_table_reader('gold_dim_date',engine= engine)

        gold_fact_attendance['date_key'] = pd.to_datetime(gold_fact_attendance['date_key']).dt.date
        gold_dim_date['date_key'] = pd.to_datetime(gold_dim_date['date_key']).dt.date
        gold_fact_sales['date_key'] = pd.to_datetime(gold_fact_sales['date_key']).dt.date


        gold_fact_attendance = gold_fact_attendance.merge(
            gold_dim_date[['date_key','year','month']],
            on = 'date_key',
            how = 'left'
        )

        gold_fact_attendance_agg = gold_fact_attendance.groupby(
            ['employee_id','year','month']    
        ).agg(
            total_attendance_hours = ('attendance_hours',   'sum'),
            days_present = ('is_present',   'sum'),
            total_overtime_hours = ('overtime',   'sum'),
            days_absent = ('is_present',lambda x:(~x).sum() )
        ).reset_index()
       

        gold_fact_sales = gold_fact_sales.merge(
            gold_dim_date[['date_key','year','month']],
            on = 'date_key',
            how = 'left'
        )

        gold_fact_sales_agg = gold_fact_sales.groupby(
            ['employee_id','year','month']
        ).agg(
            total_sales_amount = ('total_amount',    'sum'),
            total_quantity_sold = ('quantity',  'sum'),
            num_sales_transactions = ('sale_id',    'count')
        ).reset_index()

        
        
        
        df_gold = gold_fact_sales_agg.merge(
            gold_fact_attendance_agg,
            on = ['employee_id', 'year','month'],
            how = 'outer'
        )


        df_gold['attendance_rate'] = (
            (df_gold['days_present'] / (df_gold['days_present'] + df_gold['days_absent']))*100         
        ).round(2)

        df_gold['sales_per_attendance_hour'] = (
            df_gold['total_quantity_sold'] / (df_gold['total_attendance_hours'] + df_gold['total_overtime_hours'])
        ).round(2)

        df_gold = df_gold.fillna({
            'total_attendance_hours':0,
            'sales_per_attendance_hour':0,
            'days_present':0,
            'total_overtime_hours':0,
            'days_absent':0,
            'total_sales_amount':0,
            'total_quantity_sold':0,
            'num_sales_transactions':0,
            'attendance_rate':0
        })

        df_gold = df_gold[[
            'employee_id',
            'year',
            'month',
            'total_sales_amount',
            'total_quantity_sold',
            'num_sales_transactions',
            'total_attendance_hours',
            'days_present',
            'days_absent',
            'total_overtime_hours',
            'attendance_rate',
            'sales_per_attendance_hour'
        ]]
        
       
        write_gold_data_df('gold_employee_monthly_performance',df=df_gold,engine=engine)

        logger.info(f'[gold_employee_monthly_performance] cleaning completed | rows={len(df_gold)}')

    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_employee_monthly_performance] {e}")
        raise
    