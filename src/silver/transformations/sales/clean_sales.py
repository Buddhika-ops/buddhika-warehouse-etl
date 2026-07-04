import pandas as pd
from utils.db_engine import get_engine
from src.silver.utils.bronze_reader import get_bronze_table_reader
from src.silver.common.validators import (
    validate_schema,
    validate_not_null,
    validate_fk,
    validate_no_future_date,
    validate_range,
    validate_outliers_iqr
    )
from datetime import datetime
from src.silver.common.rejected import capture_rejected
from src.silver.transformations.sales.load_sales import upsert_sales
from utils.watermark import update_watermark

engine = get_engine()

def sales(logger,batch_id):

    required_columns =[
        'sale_id',
        'employee_id',
        'product',
        'quantity',
        'amount',
        'date'
    ]
    
    df_silver = get_bronze_table_reader('bronze_sales',engine = engine,watermark= "silver_sales")
    
    before = len(df_silver)
    logger.info(f'[SILVER][SALES][{batch_id}] cleaning started | rows={before}')
    
    if before == 0:
        logger.warning('[SILVER][SALES] Chunk is empty, skipping.')
        return
    
    validate_schema(required_columns,df_silver)

    df_silver['product'] = df_silver['product'].str.strip().str.title()

    df_silver['employee_id'] = pd.to_numeric(df_silver['employee_id'], errors='coerce')
    df_silver['quantity'] = pd.to_numeric(df_silver['quantity'], errors='coerce')
    df_silver['amount'] = pd.to_numeric(df_silver['amount'], errors='coerce')

    df_silver['date'] = pd.to_datetime(df_silver['date'], errors='coerce')

    mask_valid = ~df_silver.duplicated('sale_id', keep = 'first')
    df_silver = capture_rejected(
        logger = logger,
        df = df_silver,
        mask_valid= mask_valid,
        reason= 'duplicate sales',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )
    valid_id = pd.read_sql('select employee_id from silver_employees',engine)['employee_id']
    mask_valid = validate_fk(df_silver=df_silver,column='employee_id', valid_id=valid_id)
    df_silver= capture_rejected(
        logger = logger,
        df = df_silver,
        mask_valid= mask_valid,
        reason= 'employee_id not found in silver_employees',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )


    employee_id_mask = validate_not_null(df_silver=df_silver , column= 'employee_id')
    date_mask = validate_not_null(df_silver= df_silver , column= 'date')
    mask_valid = employee_id_mask & date_mask
    df_silver= capture_rejected(
        logger = logger,
        df = df_silver,
        mask_valid= mask_valid,
        reason= 'missing employee_id or date',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )

    quantity_mask = validate_not_null(df_silver=df_silver , column= 'quantity')
    amount_mask = validate_not_null(df_silver= df_silver , column= 'amount')
    mask_valid = quantity_mask & amount_mask
    df_silver= capture_rejected(
        logger = logger,
        df = df_silver,
        mask_valid= mask_valid,
        reason= 'missing quantity_mask or amount',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )
    
    mask_valid = validate_not_null(df_silver= df_silver , column= 'product')
    df_silver= capture_rejected(
        logger = logger,
        df = df_silver,
        mask_valid= mask_valid,
        reason= 'missing product',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )

    mask_valid = validate_no_future_date(df_silver=df_silver,column='date')
    df_silver= capture_rejected(
        logger = logger,
        df = df_silver,
        mask_valid= mask_valid,
        reason= 'future date',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )

    mask_valid =  validate_range(df_silver=df_silver,column='quantity',min_value= 0)
    df_silver= capture_rejected(
        logger = logger,
        df = df_silver,
        mask_valid= mask_valid,
        reason= ' quantity of range',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )

    mask_valid = validate_range(df_silver=df_silver,column= 'amount',min_value= 0)
    df_silver= capture_rejected(
        logger = logger,
        df = df_silver,
        mask_valid= mask_valid,
        reason= ' amount of range',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )


    mask_valid = validate_outliers_iqr(df_silver= df_silver,column= 'quantity')
    df_silver= capture_rejected(
        logger = logger,
        df = df_silver,
        mask_valid= mask_valid,
        reason= 'quantity outlier (IQR)',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )

    # mask_valid = validate_outliers_iqr(df_silver= df_silver,column= 'amount')
    # df_silver= capture_rejected(
    #     logger = logger,
    #     df = df_silver,
    #     mask_valid= mask_valid,
    #     reason= 'amount outlier (IQR)',
    #     reject_table= 'silver_sales_rejected',
    #     engine= engine
    # )

    df_silver['ingestion_date'] = datetime.utcnow()
    
    logger.info(f'[SILVER][SALES][{batch_id}] cleaning completed | rows={len(df_silver)}')

    if len(df_silver) == 0:
        logger.info(f'[SILVER][SALES][{batch_id}] no valid rows to load, skipping insert')
        return
    

    try:
        logger.info(f'[SILVER][SALES][{batch_id}] loading start')
        update_watermark(table_name='silver_sales',status='RUNNING',batch_id=batch_id,row_count=len(df_silver))

        upsert_sales(df_silver, engine)

        update_watermark(table_name='silver_sales',status='SUCCESS',batch_id=batch_id,row_count=len(df_silver))

        logger.info(f'[SILVER][SALES][{batch_id}] loading completed')
    except Exception as e:
        logger.error(f'[SILVER LOAD FAILD: silver_sales][{batch_id}]{e}')
        update_watermark(table_name='silver_sales',status='FAILD',batch_id=batch_id,row_count=len(df_silver))
        raise
