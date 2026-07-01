import pandas as pd
import logging
from src.gold.utils.writer import write_gold_data_df
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.gold_logger import log_build 

logger = logging.getLogger(__name__) 

def gold_attendance_monthly():
    try:
        silver_df_emplyees = get_silver_table_reader('silver_employees')
        silver_df_attendeace = get_silver_table_reader('silver_attendance')

        if silver_df_attendeace.empty:
            logger.warning("[gold_attendance_monthly] No data found in silver_attendeace")
            return
        
        gold_df_emplyees = silver_df_emplyees.copy()
        gold_df_attendance = silver_df_attendeace.copy()

        gold_df_attendance['date'] = pd.to_datetime(gold_df_attendance['date'])
        gold_df_attendance['year'] = gold_df_attendance['date'].dt.year
        gold_df_attendance['month'] = gold_df_attendance['date'].dt.month

        gold_df_attendance['is_present'] = gold_df_attendance['attendance_status'].str.upper() == "FULL_DAY"
        gold_df_attendance['is_partial'] = gold_df_attendance['attendance_status'].str.upper() == "PARTIAL_DAY"
        
        gold_df_attendance['attendance_hours'] = gold_df_attendance['attendance_hours'] - gold_df_attendance['overtime']

        gold_df_attendance = gold_df_attendance.groupby(['employee_id','year','month']).agg(
            total_hours = ('attendance_hours',       'sum'),
            overtime_hours = ('overtime' ,       'sum'),
            days_present = ('is_present',        'sum'),
            days_partial = ('is_partial',      'sum'),
            total_days = ('date',        'count')
        ).reset_index()

        gold_df_attendance['attendance_rate'] = (
            (gold_df_attendance['days_present'] / gold_df_attendance['total_days'])* 100 
        ).round(2)

        gold_df_attendance['partial_day_rate'] = (
            (gold_df_attendance['days_partial']/ gold_df_attendance['total_days'])* 100
        ).round(2)

        gold_df_attendance = gold_df_attendance.drop(columns = ['total_days'])

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
            'total_hours',
            'overtime_hours',
            'days_present',
            'days_partial',
            'attendance_rate',
            'partial_day_rate'
        ]]
        write_gold_data_df("gold_attendance_monthly",df_gold)

        log_build("gold_attendance_monthly", df_gold)

        
    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_attendance_monthly] {e}")
        raise
    