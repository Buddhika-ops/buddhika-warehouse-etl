import pandas as pd
from utils.db_engine import get_engine
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df



engine = get_engine()

def gold_employee_attendance_summary(logger,batch_id):
    try:
        gold_fact_attendance = get_silver_table_reader('gold_fact_attendance',engine= engine)

        if gold_fact_attendance.empty:
            logger.warning(f"[GOLD][gold_employee_attendance_summary][{batch_id}] No data found in gold_fact_attendance")
            return
        
        gold_dim_date = get_silver_table_reader('gold_dim_date',engine= engine)
    
        gold_dim_date['date_key'] = pd.to_datetime(gold_dim_date['date_key']).dt.date
        gold_fact_attendance['date_key'] = pd.to_datetime(gold_fact_attendance['date_key']).dt.date

        gold_fact_attendance = gold_fact_attendance.merge(
            gold_dim_date[['date_key','year','month']],
            on ='date_key',
            how = 'left'
        )

        gold_fact_attendance_agg = gold_fact_attendance.groupby(
            ['employee_id','year','month']
        ).agg(
            total_days_recorded = ('date_key',    'count'),
            days_present = ('is_present',lambda x: (x == True).sum()),
            days_absent = ('is_present',lambda x: (~x).sum()),
            total_hours = ('attendance_hours',  'sum'),
            total_overtime_hours = ('overtime', 'sum')
        ).reset_index() 

        gold_fact_attendance_agg['attendance_rate'] = (
            (gold_fact_attendance_agg['days_present'] / gold_fact_attendance_agg['total_days_recorded'])* 100
        )

        gold_fact_attendance_agg['avg_daily_hours'] =(
            gold_fact_attendance_agg['total_hours']/ gold_fact_attendance_agg['total_days_recorded']
        ).round(2)

        df_gold = gold_fact_attendance_agg.fillna({
            'total_days_recorded':0,
            'days_present':0,
            'days_absent':0,
            'total_hours':0,
            'total_overtime_hours':0,
            'attendance_rate':0,
            'avg_daily_hours':0
        })

        df_gold = df_gold[[
            'employee_id',
            'year',
            'month',
            'total_days_recorded',
            'days_present',
            'days_absent',
            'attendance_rate',
            'total_hours',
            'total_overtime_hours',
            'avg_daily_hours'
        ]]



        write_gold_data_df('gold_employee_attendance_summary',df=df_gold,engine=engine)
        return len(df_gold)
        
    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_employee_attendance_summary][{batch_id}]{e}")
        raise