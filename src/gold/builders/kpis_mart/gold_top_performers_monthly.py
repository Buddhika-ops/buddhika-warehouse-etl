import pandas as pd
from utils.db_engine import get_engine
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df



engine = get_engine()


def gold_top_performers_monthly(logger,batch_id):
    try:
        gold_fact_sales = get_silver_table_reader('gold_fact_sales',engine= engine)

        if gold_fact_sales.empty:
            logger.warning(f"[GOLD][gold_top_performers_monthly][{batch_id}] No data found in gold_fact_sales")
            return

        gold_dim_date = get_silver_table_reader('gold_dim_date',engine= engine)
       

        gold_dim_date['date_key'] = pd.to_datetime(gold_dim_date['date_key']).dt.date
        gold_fact_sales['date_key'] = pd.to_datetime(gold_fact_sales['date_key']).dt.date
        
        gold_fact_sales = gold_fact_sales.merge(
            gold_dim_date[['date_key','year','month']],
            on = 'date_key',
            how = 'left'
        )

        df_gold = gold_fact_sales.groupby(
            ['employee_id','year','month']
        ).agg(
            total_sales_amount = ('total_amount',    'sum')
        ).reset_index()

        df_gold['sales_rank'] = (
            df_gold['total_sales_amount'].rank(method ='dense', ascending = True)
        )

        df_gold = df_gold.sort_values(
            'sales_rank'
        ).reset_index(drop = True)

        df_gold = df_gold.fillna({
            'total_sales_amount':0,
            'sales_rank':0
        })

        df_gold = df_gold[[
            'year',
            'month',
            'employee_id',
            'total_sales_amount',
            'sales_rank'
        ]]

        write_gold_data_df('gold_top_performers_monthly',df=df_gold,engine=engine)

        return len(df_gold)

    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_top_performers_monthly][{batch_id}] {e}")
        raise
    