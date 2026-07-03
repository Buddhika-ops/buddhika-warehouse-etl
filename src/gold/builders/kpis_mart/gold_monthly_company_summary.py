import pandas as pd
import logging
from utils.db_engine import get_engine
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df



engine = get_engine()
logger = logging.getLogger(__name__) 

def gold_monthly_company_summary():
    try:
        gold_fact_sales = get_silver_table_reader('gold_fact_sales',engine= engine)

        if gold_fact_sales.empty:
            logger.warning("[gold_monthly_company_summary] No data found in gold_fact_sales")
            return

        gold_dim_date = get_silver_table_reader('gold_dim_date',engine= engine)
        gold_fact_attendance = get_silver_table_reader('gold_fact_attendance',engine= engine)

        gold_dim_date['date_key'] = pd.to_datetime(gold_dim_date['date_key']).dt.date
        gold_fact_sales['date_key'] = pd.to_datetime(gold_fact_sales['date_key']).dt.date
        gold_fact_attendance['date_key'] = pd.to_datetime(gold_fact_attendance['date_key']).dt.date

        gold_fact_sales = gold_fact_sales.merge(
            gold_dim_date[['date_key','year','month']],
            on = 'date_key',
            how = 'left'
        )
        gold_fact_sales_agg = gold_fact_sales.groupby(
            ['year','month']
        ).agg(
            total_sales_amount = ('total_amount',   'sum'),
            total_quantity_sold= ('quantity',    'sum'),
            total_transactions = ('sale_id',    'count'),
            active_employees = ('employee_id',  'nunique')
        ).reset_index()

        gold_fact_attendance = gold_fact_attendance.merge(
            gold_dim_date[['date_key','year','month']],
            on = 'date_key',
            how = 'left'
        )
        gold_fact_attendance_agg = gold_fact_attendance.groupby(
            ['year','month']
        ).agg(
            avg_attendance_rate = ('is_present',    'mean'),
            total_overtime_hours = ('overtime',     'sum')
        ).reset_index()

        gold_fact_attendance_agg['avg_attendance_rate'] = (
            gold_fact_attendance_agg['avg_attendance_rate'] * 100
        )


        df_gold = gold_fact_sales_agg.merge(
            gold_fact_attendance_agg,
            on = ['year','month'],
            how = 'outer'
        )

        df_gold = df_gold.sort_values(
            ['year','month']
        ).reset_index(drop = True)

        df_gold['mom_sales_growth_pct'] = (
            df_gold['total_sales_amount']
            .pct_change()
            .mul(100)
            .round(2)
        )


        df_gold = df_gold.fillna({
            'total_sales_amount':0,
            'total_quantity_sold':0,
            'total_transactions':0,
            'active_employees':0,
            'avg_attendance_rate':0,
            'total_overtime_hours':0,
            'mom_sales_growth_pct':0
        })

        df_gold =df_gold[[
            'year',
            'month',
            'total_sales_amount',
            'total_quantity_sold',
            'total_transactions',
            'active_employees',
            'avg_attendance_rate',
            'total_overtime_hours',
            'mom_sales_growth_pct'
        ]]

        write_gold_data_df('gold_monthly_company_summary',df=df_gold,engine=engine)

        logger.info(f'[gold_monthly_company_summary] cleaning completed | rows={len(df_gold)}')

    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_monthly_company_summary] {e}")
        raise
    