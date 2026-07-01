from utils.logger import get_logger

from src.gold.builders.dimensions.dim_employees import gold_dim_employees
from src.gold.builders.kpis.gold_workforce_summary import gold_workforce_summary
from src.gold.builders.kpis.gold_salary_bands import gold_salary_bands
from src.gold.builders.attendance.gold_attendance_daily import gold_attendance_daily
from src.gold.builders.attendance.gold_attendance_monthly import gold_attendance_monthly
from src.gold.builders.attendance.gold_overtime_report import gold_attendance_monthly
from src.gold.builders.sales.gold_sales_daily import gold_sales_daily
from src.gold.builders.sales.gold_sales_by_employee import gold_sales_by_employee
from src.gold.builders.sales.gold_sales_by_product import gold_sales_by_product

logger = get_logger()
def gold_pipline():
    logger.info("[GOLD_PIPELINE] STARTED")
    
    # gold_dim_employees()
    # gold_workforce_summary()
    # gold_salary_bands()
    # gold_attendance_daily()
    # gold_attendance_monthly()
    # gold_attendance_monthly()
    # gold_sales_daily()
    # gold_sales_by_employee()
    gold_sales_by_product()

    logger.info("[GOLD_PIPELINE] END")
