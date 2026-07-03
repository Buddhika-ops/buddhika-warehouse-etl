import pandas as pd
from src.silver.utils.bronze_reader import get_bronze_table_reader
import logging
from src.silver.common.validators import (
    validate_schema,
    validate_not_null,
    validate_fk,
    validate_no_future_date
)
from utils.db_engine import get_engine
from src.silver.common.rejected import capture_rejected
from src.silver.transformations.attendance.load_attendance import upsert_attendance
from datetime import datetime


engine = get_engine()
logger = logging.getLogger(__name__) 

def attendance():
    required_columns =[
        'employee_id', 
        'date', 
        'attendance_hours'
    ]

    df = get_bronze_table_reader('bronze_attendance',engine=engine)
    df_silver = df.copy()
    before = len(df_silver)

    if before == 0:
        logger.info('[SILVER][ATTENDANCE] Chunk is empty, skipping.')
        logger.info('[DATA QUALITY SCORE] 0.00%')
        return
    
    validate_schema(required_columns, df_silver)

    df_silver['employee_id'] = pd.to_numeric(df_silver['employee_id'], errors='coerce')
    df_silver['attendance_hours'] = pd.to_numeric(df_silver['attendance_hours'], errors='coerce')
    df_silver['date'] = pd.to_datetime(df_silver['date'], errors='coerce')

    mask_valid = ~df_silver.duplicated(subset=['employee_id','date'], keep='first')
    df_silver = capture_rejected(
        df=df_silver,
        mask_valid=mask_valid,
        reason='duplicate attendance',
        reject_table='silver_attendance_rejected',
        engine=engine
    )
    
    employee_id_mask = validate_not_null(df_silver, 'employee_id')
    date_mask = validate_not_null(df_silver, 'date')
    mask_valid = employee_id_mask & date_mask
    df_silver = capture_rejected(
        df=df_silver,
        mask_valid=mask_valid,
        reason='missing employee_id or date',
        reject_table='silver_attendance_rejected',
        engine=engine
    )

    valid_id = get_bronze_table_reader('silver_employees', engine=engine)['employee_id']
    mask_valid = validate_fk(df_silver, 'employee_id', valid_id)
    df_silver = capture_rejected(
        df=df_silver,
        mask_valid=mask_valid,
        reason='employee_id not found in silver_employees',
        reject_table='silver_attendance_rejected',
        engine=engine
    )


    mask_valid = df_silver['attendance_hours'].between(0,24)
    df_silver = capture_rejected(
        df=df_silver,
        mask_valid=mask_valid,
        reason='attendance_hours out of range',
        reject_table='silver_attendance_rejected',
        engine=engine
    )

    mask_valid = validate_no_future_date(df_silver, 'date')
    df_silver = capture_rejected(
        df=df_silver,
        mask_valid=mask_valid,
        reason='future date',
        reject_table='silver_attendance_rejected',
        engine=engine
    )

    df_silver['attendance_status'] = df_silver['attendance_hours'].apply(__derive_status)
    df_silver['overtime'] = (df_silver['attendance_hours'].fillna(0) - 8).clip(lower=0)

    df_silver['ingestion_date'] = datetime.utcnow()

    logger.info(f'[SILVER][ATTENDANCE] cleaning completed | rows={len(df_silver)}')

    if len(df_silver) == 0:
        logger.info('[SILVER][ATTENDANCE] no valid rows to load, skipping insert')
        return
    
    try:
        upsert_attendance(df_silver, engine)
    except Exception as e:
        logger.error(f'[SILVER][ATTENDANCE] load failed | error={e}')
        raise




def __derive_status(hours):
    if pd.isna(hours):
        return 'Absent'
    if hours < 5:
        return 'Half-day'
    return 'Present'













