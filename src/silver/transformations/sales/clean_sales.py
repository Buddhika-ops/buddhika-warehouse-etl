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
import logging
from datetime import datetime
from src.silver.common.rejected import capture_rejected
from src.silver.transformations.sales.load_sales import upsert_sales

logger = logging.getLogger(__name__) 
engine = get_engine()

def sales():

    required_columns =[
        'sale_id',
        'employee_id',
        'product',
        'quantity',
        'amount',
        'date'
    ]

    df = get_bronze_table_reader('bronze_sales',engine = engine )
    df_silver = df.copy()
    before = len(df_silver)
    
    if before == 0:
        logger.info('[SILVER][SALES] Chunk is empty, skipping.')
        logger.info('[DATA QUALITY SCORE] 0.00%')
        return
    
    validate_schema(required_columns,df_silver)

    df_silver['product'] = df_silver['product'].str.strip().str.title()

    df_silver['employee_id'] = pd.to_numeric(df_silver['employee_id'], errors='coerce')
    df_silver['quantity'] = pd.to_numeric(df_silver['quantity'], errors='coerce')
    df_silver['amount'] = pd.to_numeric(df_silver['amount'], errors='coerce')

    df_silver['date'] = pd.to_datetime(df_silver['date'], errors='coerce')

    mask_valid = ~df_silver.duplicated('sale_id', keep = 'first')
    df_silver = capture_rejected(
        df = df_silver,
        mask_valid= mask_valid,
        reason= 'duplicate sales',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )
    valid_id = get_bronze_table_reader('silver_employees',engine=engine)['employee_id']
    mask_valid = validate_fk(df_silver=df_silver,column='employee_id', valid_id=valid_id)
    df_silver= capture_rejected(
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
        df = df_silver,
        mask_valid= mask_valid,
        reason= 'missing quantity_mask or amount',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )
    
    mask_valid = validate_not_null(df_silver= df_silver , column= 'product')
    df_silver= capture_rejected(
        df = df_silver,
        mask_valid= mask_valid,
        reason= 'missing product',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )

    mask_valid = validate_no_future_date(df_silver=df_silver,column='date')
    df_silver= capture_rejected(
        df = df_silver,
        mask_valid= mask_valid,
        reason= 'future date',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )

    mask_valid =  validate_range(df_silver=df_silver,column='quantity',min_value= 0)
    df_silver= capture_rejected(
        df = df_silver,
        mask_valid= mask_valid,
        reason= ' quantity of range',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )

    mask_valid = validate_range(df_silver=df_silver,column= 'amount',min_value= 0)
    df_silver= capture_rejected(
        df = df_silver,
        mask_valid= mask_valid,
        reason= ' amount of range',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )


    mask_valid = validate_outliers_iqr(df_silver= df_silver,column= 'quantity')
    df_silver= capture_rejected(
        df = df_silver,
        mask_valid= mask_valid,
        reason= 'quantity outlier (IQR)',
        reject_table= 'silver_sales_rejected',
        engine= engine
    )

    # mask_valid = validate_outliers_iqr(df_silver= df_silver,column= 'amount')
    # df_silver= capture_rejected(
    #     df = df_silver,
    #     mask_valid= mask_valid,
    #     reason= 'amount outlier (IQR)',
    #     reject_table= 'silver_sales_rejected',
    #     engine= engine
    # )

    df_silver['ingestion_date'] = datetime.utcnow()
    
    logger.info(f'[SILVER][SALES] cleaning completed | rows={len(df_silver)}')

    if len(df_silver) == 0:
        logger.info('[SILVER][SALES] no valid rows to load, skipping insert')
        return
    

    try:
        upsert_sales(df_silver, engine)
    except Exception as e:
        logger.error(f'[SILVER][SALES] load failed | error={e}')
        raise
