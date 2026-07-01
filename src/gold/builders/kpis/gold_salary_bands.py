import pandas as pd
import numpy as np
import logging
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df
from src.gold.utils.gold_logger import log_build
from src.db_engine import get_engine

logger = logging.getLogger(__name__) 
engine = get_engine()

def gold_salary_bands():
    try:
        df = get_silver_table_reader('silver_employees')

        if df.empty:
            logger.warning("[gold_salary_bands] No data found in silver_employees")
            return
        df_gold = df.copy()

        conditions = [
                df_gold["salary"] <= 50000,
                df_gold["salary"] <= 90000,
                df_gold["salary"] >  90000,
            ]
        choices = ["Junior", "Mid", "Senior"]

        df_gold["band"] = np.select(conditions, choices, default="Unknown")


        df_gold = df_gold.groupby(["department", "band"], observed=True).agg({
            "salary": ["min", "max", "mean", "median"],
            "employee_id": "count",
        }).reset_index()

        df_gold.columns = [
            "department",
            "band",
            "min_salary",
            "max_salary",
            "avg_salary",
            "median_salary",
            "employee_count",
        ]

        df_gold['avg_salary'] = df_gold['avg_salary'].round(2)
        df_gold['min_salary'] = df_gold['min_salary'].round(2)
        df_gold['max_salary'] = df_gold['max_salary'].round(2)
        df_gold["median_salary"] = df_gold["median_salary"].round(2)

        write_gold_data_df('gold_salary_bands',df_gold)

        log_build("gold_salary_bands", df_gold)

    except Exception as e:
        logger.error(f"[GOLD BUILD FAILED: gold_salary_bands] {e}")
        raise