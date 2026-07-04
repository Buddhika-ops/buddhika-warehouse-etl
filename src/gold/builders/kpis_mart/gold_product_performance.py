
from utils.db_engine import get_engine
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df



engine = get_engine()


def gold_product_performance(logger,batch_id):
    try:
        gold_fact_sales = get_silver_table_reader('gold_fact_sales',engine= engine)

        if gold_fact_sales.empty:
            logger.warning(f"[GOLD][gold_product_performance][{batch_id}] No data found in gold_fact_sales")
            return
               
       

        gold_fact_sales = gold_fact_sales.groupby('product_id').agg(
            total_quantity_sold =('quantity',   'sum'),
            total_revenue = ('total_amount',    'sum'),
            num_transactions = ('sale_id',  'nunique'),
            num_employees_selling = ('employee_id', 'nunique')
        ).reset_index()

        gold_fact_sales['avg_amount_per_sale'] = (
            gold_fact_sales['total_revenue'] / gold_fact_sales['total_quantity_sold']
        )
        
        gold_fact_sales['revenue_rank'] = (
            gold_fact_sales['total_revenue'].rank(method = 'dense', ascending = False).astype(int)
        )
        gold_fact_sales = gold_fact_sales.sort_values(
            'revenue_rank'
        ).reset_index(drop = True)
        
        df_gold = gold_fact_sales.fillna({
            'total_quantity_sold':0,
            'total_revenue':0,
            'num_transactions':0,
            'num_employees_selling':0,
            'avg_amount_per_sale':0,
            'revenue_rank':0
        })

        df_gold = df_gold[[
            'product_id',
            'total_quantity_sold',
            'total_revenue',
            'num_transactions',
            'num_employees_selling',
            'avg_amount_per_sale',
            'revenue_rank'
        ]]

        write_gold_data_df('gold_product_performance',df=df_gold,engine=engine)

        return len(df_gold)

    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_product_performance][{batch_id}] {e}")
        raise