import pandas as pd
from datetime import datetime
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df
from utils.db_engine import get_engine

engine = get_engine()
def gold_dim_employees(logger,batch_id):
    try:
        dept_code_map = {
            "Inside Sales": "INS",
            "Field Sales": "FLS",
            "Enterprise Sales": "ENT",
            "SMB Sales": "SMB",
            "Channel Sales": "CHN",
            "Customer Success & Renewals": "CSR"
        }

        df_gold = get_silver_table_reader('silver_employees',engine=engine)
       
        if df_gold.empty:
            logger.warning(f"[GOLD][DIM_EMPLOYEES][{batch_id}] No data found in silver_employees")
            return     
        
        df_gold = df_gold.rename(columns={
            "name":"full_name",         
            "years_of_experience":"experience_years",  
            "salary":"monthly_salary"    
        })

        df_gold["department_code"] = df_gold["department"].map(dept_code_map)
        df_gold["employee_code"] = (
            df_gold["department_code"] + "-" + df_gold["employee_id"].astype(str)
        )
        df_gold['age_group'] = pd.cut(
            df_gold['age'],
            bins = [0,25,34,44,54,float('inf')],
            labels=['<25','25-34','35-44','45-54','55+'],
            right=False
        )
        
        df_gold['salary_band'] = pd.cut(
            df_gold['monthly_salary'],
            bins=[0, 50000, 90000, 150000,float('inf')],
            labels=["Q1", "Q2", "Q3", "Q4"]
        ) 

        df_gold['experience_level'] = pd.cut(
            df_gold['experience_years'],
            bins=[-1,2,5,10,float('inf')],
            labels=["Junior", "Mid", "Senior","Expert"]
        )

        df_gold["updated_at"] = datetime.utcnow()


        df_gold = df_gold[[
            "employee_id",
            "employee_code",
            "full_name",
            "department",
            "age",
            "experience_years",
            "monthly_salary",
            "city",
            "age_group",
            "salary_band",
            "experience_level",
            "updated_at"
        ]]
        
        write_gold_data_df("gold_dim_employees",df = df_gold,engine = engine)
        
        return len(df_gold)
    
    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_dim_employees][{batch_id}] {e}")
        raise
