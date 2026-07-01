import pandas as pd
import logging
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df
from src.gold.utils.gold_logger import log_build
from src.db_engine import get_engine

logger = logging.getLogger(__name__) 
engine = get_engine()

def gold_workforce_summary():
    try:
        df = get_silver_table_reader('silver_employees')

        if df.empty:
            logger.warning("[gold_workforce_summary] No data found in silver_employees")
            return

        df_gold = df.copy()
        df_gold = df.groupby('department').agg(
            headcount = ("employee_id",  "count"),
            avg_salary = ("salary",  "mean"),
            min_salary = ("salary",  "min"),
            max_salary = ("salary",  "max"),
            avg_age = ("age",    "mean"),
            avg_experience = ("years_of_experience", "mean")
        ).reset_index()

        df_gold['avg_salary'] = df_gold['avg_salary'].round(2)
        df_gold['min_salary'] = df_gold['min_salary'].round(2)
        df_gold['max_salary'] = df_gold['max_salary'].round(2)

        df_gold['avg_age'] = df_gold['avg_age'].round(2)
        df_gold['avg_experience'] = df_gold['avg_experience'].round(2)

        write_gold_data_df('gold_workforce_summary',df_gold)

        log_build("gold_workforce_summary",df_gold)

    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_workforce_summary] {e}")
        raise
