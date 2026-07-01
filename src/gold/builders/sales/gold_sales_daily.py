import pandas as pd
import logging
from src.gold.utils.writer import write_gold_data_df
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.gold_logger import log_build 

logger = logging.getLogger(__name__)

def gold_sales_daily():
    try:
        silver_df_emplyees = get_silver_table_reader('silver_employees')
        silver_df_sales = get_silver_table_reader('silver_sales')

        if silver_df_sales.empty:
            logger.warning("[gold_sales_daily] No data found in silver_sales")
            return

        gold_df_emplyees = silver_df_emplyees.copy()
        gold_df_sales = silver_df_sales.copy()

        df_gold = gold_df_sales.merge(
            gold_df_emplyees[['employee_id','name','department']],
            on = 'employee_id',
            how = 'left'
        )
        
        df_gold = df_gold[[
            'sale_id',
            'employee_id',
            'name',
            'department',
            'product',
            'amount',
            'date',
            'ingestion_date'
        ]]
    
        write_gold_data_df('gold_sales_daily', df_gold)
        log_build("gold_overtime_report", df_gold)
            
    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_sales_daily] {e}")
        raise