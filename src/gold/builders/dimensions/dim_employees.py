import pandas as pd
import logging
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.gold_logger import log_build
from src.gold.utils.writer import write_gold_data_df

from src.db_engine import get_engine

logger = logging.getLogger(__name__) 
engine = get_engine()

def gold_dim_employees():
    try:
        df = get_silver_table_reader('silver_employees')
       

        if df.empty:
            logger.warning("[gold_dim_employees] No data found in silver_employees")
            return
        df_gold = df.copy()
        
        df_gold = df_gold.rename(columns={
            "name":"full_name",         
            "years_of_experience":"experience_years",  
            "salary":"monthly_salary",
            "join_date_estimated":"join_date", 
        })
     

         
        df_gold['salary_band'] = pd.cut(
            df_gold['monthly_salary'],
            bins=[0, 50000, 90000, 150000,float('inf')],
            labels=["Junior", "Mid", "Senior", "Executive"]
        ) 

        df_gold['experience_band'] = pd.cut(
            df_gold['experience_years'],
            [-1,5,10,float('inf')],
            labels=["Entry", "Mid", "Senior"]
        )

        df_gold = df_gold[[
            "employee_id",
            "full_name",
            "department",
            "age",
            "experience_years",
            "monthly_salary",
            "city",
            "join_date",
            "salary_band",
            "experience_band"
        ]]
        
        write_gold_data_df("gold_dim_employees",df_gold)
        
        log_build("gold_dim_employees",df_gold)

    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_dim_employees] {e}")
        raise
