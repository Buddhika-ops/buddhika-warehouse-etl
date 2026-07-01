import logging
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df
from src.gold.utils.gold_logger import log_build 

logger = logging.getLogger(__name__) 


def gold_attendance_daily():
    try:
        silver_df_emplyees = get_silver_table_reader('silver_employees')
        silver_df_attendeace = get_silver_table_reader('silver_attendance')
        if silver_df_attendeace.empty:
            logger.warning("[gold_salary_bands] No data found in silver_attendeace")
            return
        
        gold_df_emplyees = silver_df_emplyees.copy()
        gold_df_attendance = silver_df_attendeace.copy()

        df_gold = gold_df_attendance.merge(
            gold_df_emplyees[['employee_id','name','department']],
            on = 'employee_id',
            how = 'left'
        )

        df_gold = df_gold[[
            'employee_id',
            'name',
            'department',
            'date',
            'attendance_hours',
            'attendance_status',
            'overtime',
            'ingestion_date'
        ]]

        write_gold_data_df("gold_attendance_daily",df_gold)

        log_build("gold_attendance_daily", df_gold)
    
    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_attendance_daily] {e}")
        raise
    