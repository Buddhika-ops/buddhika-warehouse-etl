from utils.logger import get_logger

from src.gold.builders.dimensions.gold_dim_employees import gold_dim_employees
from src.gold.builders.dimensions.gold_dim_product import gold_dim_product
from src.gold.builders.dimensions.gold_dim_date import gold_dim_date
from src.gold.builders.fact.gold_fact_sales import gold_fact_sales 
from src.gold.builders.fact.gold_fact_attendance import gold_fact_attendance
from src.gold.builders.kpis_mart.gold_employee_monthly_performance import gold_employee_monthly_performance
from src.gold.builders.kpis_mart.gold_department_monthly_sales import gold_department_monthly_sales
from src.gold.builders.kpis_mart.gold_monthly_company_summary import gold_monthly_company_summary
from src.gold.builders.kpis_mart.gold_product_performance import gold_product_performance
from src.gold.builders.kpis_mart.gold_city_sales_performance import gold_city_sales_performance
from src.gold.builders.kpis_mart.gold_employee_attendance_summary import gold_employee_attendance_summary
from src.gold.builders.kpis_mart.gold_top_performers_monthly import gold_top_performers_monthly
from src.gold.builders.kpis_mart.gold_data_quality_summary import gold_data_quality_summary


logger = get_logger(__name__,'gold')
def gold_pipline(batch_id):
    try:
        logger.info("[GOLD][PIPELINE] STARTED")
        
        gold_jobs =[  
            ("DIM_EMPLOYEES",gold_dim_employees),
            ("DIM_PRODUCT",gold_dim_product),
            ("DIM_DATE",gold_dim_date),
            ("FACT_SALES",gold_fact_sales),
            ("FACT_ATTENDANCE",gold_fact_attendance),
            ("EMPLOYEE_MONTHLY_PERFORMANCE",gold_employee_monthly_performance),
            ("DEPARTMENT_MONTHLY_SALES",gold_department_monthly_sales),
            ("MONTHLY_COMPANY_SUMMARY",gold_monthly_company_summary),
            ("PRODUCT_PERFORMANCE",gold_product_performance),
            ("CITY_SALES_PERFORMANCE",gold_city_sales_performance),
            ("EMPLOYEE_ATTENDANCE_SUMMARY",gold_employee_attendance_summary),
            ("TOP_PERFORMERS_MONTHLY",gold_top_performers_monthly),
            ("DATA_QUALITY_SUMMARY",gold_data_quality_summary)
        ]

        for name,job in  gold_jobs:
            logger.info(f"[GOLD][{name}][{batch_id}] Build started")

            rows_count = job(logger,batch_id)

            logger.info(f"[GOLD][{name}][{batch_id}] Build completed | rows={rows_count}")
            logger.info(f"[GOLD][{name}] Build completed")
        logger.info("[GOLD][PIPELINE] Completed")    
    except Exception as e:
        logger.exception(f"[GOLD][PIPELINE] Failed {e}")
   
