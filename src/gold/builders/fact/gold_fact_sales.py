import pandas as pd
import logging
from utils.db_engine import get_engine
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df
from datetime import datetime


engine = get_engine()
logger = logging.getLogger(__name__) 

def gold_fact_sales():
    try:
        df_gold = get_silver_table_reader('silver_sales',engine= engine)

        if df_gold.empty:
            logger.warning("[gold_fact_sales] No data found in silver_sales")
            return
        
        gold_dim_employee = get_silver_table_reader('gold_dim_employees',engine=engine)
        gold_dim_product = get_silver_table_reader('gold_dim_product',engine=engine)
        gold_dim_date = get_silver_table_reader('gold_dim_date',engine=engine)

        df_gold['date'] = pd.to_datetime(df_gold['date'])

        df_gold = df_gold.merge(
            gold_dim_employee[['employee_id']],
            on = 'employee_id',
            how = 'left'
        )

        df_gold = df_gold.merge(
            gold_dim_product[['product_id','product_name']],
            left_on = 'product',
            right_on = 'product_name',
            how = 'left'
        ).drop(columns=['product_name'])

   
        df_gold = df_gold.merge(
            gold_dim_date[['date_key']],
            left_on = 'date',
            right_on = 'date_key',
            how = 'left'
        )
        df_gold = df_gold.rename(columns = {'amount': 'total_amount'})
        df_gold['unit_price'] = df_gold['total_amount'] / df_gold['quantity']
        df_gold['ingestion_date'] = datetime.utcnow()
        df_gold = df_gold[[
            'sale_id',
            'employee_id',
            'product_id',
            'date_key',
            'quantity',
            'total_amount',
            'unit_price',
            'ingestion_date'

        ]]


        write_gold_data_df('gold_fact_sales',df=df_gold,engine=engine)

        logger.info(f'[gold_fact_sales] cleaning completed | rows={len(df_gold)}')

    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_fact_sales] {e}")
        raise