import pandas as pd
import logging
from utils.db_engine import get_engine
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df



engine = get_engine()
logger = logging.getLogger(__name__) 

def gold_city_sales_performance():
    try:
        gold_fact_sales = get_silver_table_reader('gold_fact_sales',engine= engine)

        if gold_fact_sales.empty:
            logger.warning("[gold_city_sales_performance] No data found in gold_fact_sales")
            return
        
        gold_dim_employees = get_silver_table_reader('gold_dim_employees',engine=engine)

        gold_fact_sales = gold_fact_sales.merge(
            gold_dim_employees[['employee_id','city']],
            on = 'employee_id',
            how = 'left'
        )

        gold_fact_sales_agg = gold_fact_sales.groupby('city').agg(
            total_sales_amount = ('total_amount',   'sum'),
            total_quantity_sold = ('quantity',  'sum'),
            total_transactions = ('sale_id',     'nunique'),
            num_employees = ('employee_id',     'nunique')           
        ).reset_index()

        gold_fact_sales_agg['avg_sales_per_employee'] =(
            gold_fact_sales_agg['total_sales_amount']/gold_fact_sales_agg['num_employees']
        ).round(0)

        
        df_gold = gold_fact_sales_agg.fillna({
            'total_sales_amount':0,
            'num_employees':0,
            'avg_sales_per_employee':0,
            'total_quantity_sold':0,
            'total_transactions':0
        })

        df_gold = df_gold[[
            'city',
            'total_sales_amount',
            'num_employees',
            'avg_sales_per_employee',
            'total_quantity_sold',
            'total_transactions'
        ]]
        

        write_gold_data_df('gold_city_sales_performance',df=df_gold,engine=engine)

        logger.info(f'[gold_city_sales_performance] cleaning completed | rows={len(df_gold)}')

    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_city_sales_performance] {e}")
        raise
    