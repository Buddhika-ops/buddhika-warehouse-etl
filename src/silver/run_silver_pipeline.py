from src.silver.transformations.employees.clean_employees import employees
from src.silver.transformations.attendance.clean_attendance import attendance
from src.silver.transformations.sales.clean_sales import sales
from utils.logger import get_logger

logger = get_logger()

def silver_pipline():
    logger.info("[SILVER_PIPELINE] STARTED")
    # employees()
    # attendance()
    sales()
    logger.info("[SILVER_PIPELINE] END")