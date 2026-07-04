from src.silver.common.validators import (
    validate_schema,
    validate_range,
    validate_not_null
    )
from src.silver.transformations.employees.load_employees import upsert_employees
from src.silver.common.rejected import capture_rejected
from utils.db_engine import get_engine
from src.silver.utils.bronze_reader import get_bronze_table_reader
from datetime import datetime
from utils.watermark import update_watermark

engine = get_engine()
 

def employees(logger,batch_id):
    required_columns = [
        'employee_id',
        'name',
        'age',
        'years_of_experience',
        'salary',
        'department',
        'city',
        'ingestion_date'
    ]
    df_silver = get_bronze_table_reader('bronze_employees', engine=engine,watermark='silver_employees')

    before = len(df_silver)
    logger.info(f'[SILVER][EMPLOYEES][{batch_id}] cleaning started | rows={before}')

    if before == 0:
        logger.warning('[SILVER][EMPLOYEES] Chunk is empty, skipping.')
        return

    validate_schema(required_columns,df_silver)

    mask_valid = ~df_silver['employee_id'].duplicated(keep="first")
    df_silver = capture_rejected(
        logger= logger,
        df = df_silver,
        mask_valid = mask_valid,
        reason='duplicate employee_id',
        reject_table='silver_employees_rejected',
        engine=engine,
    )

    mask_valid = (
        validate_not_null(df_silver,'employee_id') &
        validate_not_null(df_silver,'name')
        )
    df_silver = capture_rejected(
        logger= logger,
        df = df_silver,
        mask_valid = mask_valid,
        reason= 'missing employee_id or name',
        reject_table = 'silver_employees_rejected',
        engine = engine
    )

    mask_valid =  validate_not_null(df_silver,'department')
    df_silver = capture_rejected(
        logger= logger,
        df = df_silver,
        mask_valid = mask_valid,
        reason= 'missing department',
        reject_table = 'silver_employees_rejected',
        engine = engine
    )

    age_mask = validate_range(df_silver,'age',max_value=70,min_value=18)
    salary_mask = validate_range(df_silver, 'salary',min_value=5000 ,max_value= 400000)
    mask_valid = age_mask & salary_mask
    df_silver = capture_rejected(
        logger= logger,
        df = df_silver,
        mask_valid = mask_valid,
        reason = 'age or salary out of range',
        reject_table = 'silver_employees_rejected',
        engine = engine
        )

    df_silver['department'] = df_silver['department'].str.strip()
    df_silver['name'] = df_silver['name'].str.strip()
    df_silver['city'] = df_silver['city'].str.strip()

    df_silver['ingestion_date'] = datetime.utcnow()

    logger.info(f'[SILVER][EMPLOYEES][{batch_id}] cleaning completed | rows={len(df_silver)}')
 
    if len(df_silver) == 0:
        logger.info(f'[SILVER][EMPLOYEES][{batch_id}] no valid rows to load, skipping insert')
        return
    try:
        logger.info(f'[SILVER][EMPLOYEES][{batch_id}] loading start')
        update_watermark(table_name='silver_employees',status='RUNNING',batch_id=batch_id,row_count=len(df_silver))

        upsert_employees(df_silver,engine)

        update_watermark(table_name='silver_employees',status='SUCCESS',batch_id=batch_id,row_count=len(df_silver))
        logger.info(f'[SILVER][EMPLOYEES][{batch_id}] loading completed')
    except Exception as e:
        logger.error(f'[SILVER LOAD FAILD: silver_employees][{batch_id}] {e}')
        update_watermark(table_name='silver_employees',status='FAILD',batch_id=batch_id,row_count=len(df_silver))
        raise
   

