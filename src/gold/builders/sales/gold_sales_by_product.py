import pandas as pd
import logging
from src.gold.utils.writer import write_gold_data_df
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.gold_logger import log_build 

logger = logging.getLogger(__name__)

def gold_sales_by_product():
    try:
        silver_df_sales = get_silver_table_reader('silver_sales')

        if silver_df_sales.empty:
            logger.warning("[gold_sales_by_product] No data found in silver_sales")
            return
        
        gold_df_sales = silver_df_sales.copy()

        gold_df_sales['date'] = pd.to_datetime(gold_df_sales['date'])
        gold_df_sales['year'] = gold_df_sales['date'].dt.year
        gold_df_sales['month'] = gold_df_sales ['date'].dt.month

        df_gold = gold_df_sales.groupby(['product','year','month']).agg(
            total_amount = ('amount',        'sum'),
            num_sales = ('sale_id',     'count'),
            num_employees = ('employee_id',     'nunique')
        ).reset_index()

        df_gold['avg_amount'] = (df_gold['total_amount']/ df_gold['num_sales']).round(2)

        df_gold = df_gold[[
            'product',
            'year',
            'month',
            'total_amount',
            'num_sales',
            'avg_amount',
            'num_employees'
        ]]

        write_gold_data_df("gold_sales_by_product",df_gold)

        log_build("gold_sales_by_product", df_gold)

    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_sales_by_product] {e}")
        raise

    