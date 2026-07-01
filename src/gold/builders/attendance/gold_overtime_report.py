import pandas as pd
import logging
from src.gold.utils.writer import write_gold_data_df
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.gold_logger import log_build 

logger = logging.getLogger(__name__) 
OVERTIME_THRESHOLD_HOURS = 10

def gold_attendance_monthly():
    try:
        silver_df_emplyees = get_silver_table_reader('silver_employees')
        silver_df_attendeace = get_silver_table_reader('silver_attendance')

        if silver_df_attendeace.empty:
            logger.warning("[gold_overtime_report] No data found in silver_attendeace")
            return
        
        gold_df_emplyees = silver_df_emplyees.copy()
        gold_df_attendance = silver_df_attendeace.copy()

        gold_df_attendance['date'] = pd.to_datetime(gold_df_attendance['date'])
        gold_df_attendance['year'] = gold_df_attendance['date'].dt.year
        gold_df_attendance['month'] = gold_df_attendance['date'].dt.month

        gold_df_attendance['had_overtime'] = gold_df_attendance['overtime'] > 0

        gold_df_attendance = gold_df_attendance.groupby(['employee_id','year','month']).agg(
            overtime_hours = ('overtime' ,       'sum'),
            overtime_days = ('had_overtime',        'sum'),
        ).reset_index()

        gold_df_attendance['overtime_flag'] = gold_df_attendance['overtime_hours'] > OVERTIME_THRESHOLD_HOURS

        df_gold = gold_df_attendance.merge(
            gold_df_emplyees[['employee_id', 'name', 'department']],
            on = 'employee_id',
            how = 'left'
        )

        df_gold = df_gold[[
            'employee_id',
            'name',
            'department',
            'year',
            'month',
            'overtime_hours',
            'overtime_days',
            'overtime_flag',
        ]]
        write_gold_data_df("gold_overtime_report",df_gold)

        log_build("gold_overtime_report", df_gold)

        
    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_attendance_monthly] {e}")
        raise
    
