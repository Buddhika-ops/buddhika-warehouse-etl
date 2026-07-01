import pandas as pd
import logging
from src.gold.utils.writer import write_gold_data_df
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.gold_logger import log_build 

logger = logging.getLogger(__name__)

def gold_sales_by_employee():
    try:
        silver_df_emplyees = get_silver_table_reader('silver_employees')
        silver_df_sales = get_silver_table_reader('silver_sales')

        if silver_df_sales.empty:
            logger.warning("[gold_sales_by_employee] No data found in silver_sales")
            return

        gold_df_emplyees = silver_df_emplyees.copy()
        gold_df_sales = silver_df_sales.copy()

        gold_df_sales['date'] = pd.to_datetime(gold_df_sales['date'])
        gold_df_sales['year'] = gold_df_sales['date'].dt.year
        gold_df_sales['month'] = gold_df_sales ['date'].dt.month

        gold_df_sales = gold_df_sales.groupby(['employee_id', 'year', 'month']).agg(
            total_sales = ('amount',        'sum'),
            num_orders = ('sale_id',     'count')
        ).reset_index()

        gold_df_sales['avg_order_value'] = (gold_df_sales['total_sales']/ gold_df_sales['num_orders']).round(2)

        df_gold = gold_df_sales.merge(
            gold_df_emplyees[['employee_id','name']],
            on = 'employee_id',
            how = 'left'
            )
        
        df_gold = df_gold[[
            'employee_id',
            'name',
            'year',
            'month',
            'total_sales',
            'num_orders',
            'avg_order_value'
        ]]

        write_gold_data_df("gold_sales_by_employee",df_gold)
        log_build("gold_sales_by_employee", df_gold)

    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_sales_by_employee] {e}")
        raise
