import pandas as pd
import logging
from utils.db_engine import get_engine
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df



engine = get_engine()
logger = logging.getLogger(__name__) 

def gold_department_monthly_sales():
    try:
        gold_fact_sales = get_silver_table_reader('gold_fact_sales',engine= engine)

        if gold_fact_sales.empty:
            logger.warning("[gold_department_monthly_sales] No data found in gold_fact_sales")
            return
        
        gold_dim_employees = get_silver_table_reader('gold_dim_employees',engine= engine)
        gold_dim_date = get_silver_table_reader('gold_dim_date',engine= engine)

        gold_dim_date['date_key'] = pd.to_datetime(gold_dim_date['date_key']).dt.date
        gold_fact_sales['date_key'] = pd.to_datetime(gold_fact_sales['date_key']).dt.date

        gold_fact_sales = gold_fact_sales.merge(
            gold_dim_date[['date_key','year','month']],
            on = 'date_key',
            how = 'left'
        )

        gold_fact_sales = gold_fact_sales.merge(
            gold_dim_employees[['employee_id','department']],
            on = ['employee_id'],
            how = 'left',
        )
        
        df_gold = gold_fact_sales.groupby(
            ['year','month','department']
        ).agg(
            total_sales_amount = ('total_amount',    'sum'),
            total_quantity_sold = ('quantity',   'sum'),
            active_employees = ('employee_id',   'nunique')
        ).reset_index()

        df_gold['avg_sales_per_employee'] = (
            (df_gold['total_sales_amount'] / df_gold['active_employees'])* 100
        ).round(2)

        df_gold = df_gold.fillna({
            'total_sales_amount':0,
            'total_quantity_sold':0,
            'active_employees':0,
            'avg_sales_per_employee':0
        })

        df_gold = df_gold[[
            'department',
            'year',
            'month',
            'total_sales_amount',
            'total_quantity_sold',
            'active_employees',
            'avg_sales_per_employee'
        ]]
    
        write_gold_data_df('gold_department_monthly_sales',df=df_gold,engine=engine)

        logger.info(f'[gold_department_monthly_sales] cleaning completed | rows={len(df_gold)}')

    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_department_monthly_sales] {e}")
        raise