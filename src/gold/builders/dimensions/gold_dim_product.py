from utils.db_engine import get_engine
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df

engine = get_engine()

def gold_dim_product(logger,batch_id):
    try:
        category_map = {
            "Laptop": "Computers",
            "Desktop Pc": "Computers",
            "Mouse": "Accessories",
            "Keyboard": "Accessories",
            "Monitor": "Displays",
            "Phone": "Mobile Devices",
            "Tablet": "Mobile Devices",
            "Printer": "Office Equipment",
            "Webcam": "Accessories",
            "Headset": "Accessories",
            "Docking Station": "Accessories",
            "External Ssd": "Storage",
            "Router": "Networking",
            "Server Rack Unit": "Networking",
            "Network Switch": "Networking",
            "Software License (Annual)": "Software",
            "Support & Maintenance Plan": "Services",
            "Extended Warranty": "Services",
        }

        df_gold = get_silver_table_reader('silver_sales',engine= engine)
        
        if df_gold.empty:
            logger.warning(f"[GOLD][gold_dim_product][{batch_id}] No data found in silver_sales")
            return

        df_gold = (
            df_gold.drop_duplicates(subset=['product'])
            .sort_values('product')
            .reset_index(drop=True)
        )

        df_gold ['product_id'] = df_gold.index + 1000

        df_gold['category'] = (
            df_gold['product'].map(category_map).fillna('Others')
        )

        df_gold.rename(columns= {'product': 'product_name'},inplace=True)

        df_gold = df_gold[[
            'product_id',
            'product_name',
            'category'
        ]]

        write_gold_data_df('gold_dim_product',df=df_gold,engine=engine)
        return len(df_gold)
    
    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_dim_product][{batch_id}] {e}")
        raise

