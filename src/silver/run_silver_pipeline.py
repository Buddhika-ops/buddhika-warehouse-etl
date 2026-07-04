from src.silver.transformations.employees.clean_employees import employees
from src.silver.transformations.attendance.clean_attendance import attendance
from src.silver.transformations.sales.clean_sales import sales
from utils.logger import get_logger

logger = get_logger(__name__,'silver')

def silver_pipline(batch_id):
    try:
        
        logger.info(f"[SILVER][PIPELINE][{batch_id}] STARTED")
        
        logger.info(f"[SILVER][EMPLOYEES][{batch_id}] Loading started")
        employees(logger,batch_id)
        logger.info(f"[SILVER][EMPLOYEES][{batch_id}] Loading completed")

        logger.info(f"[SILVER][ATTENDANCE][{batch_id}] Loading started")
        attendance(logger,batch_id)
        logger.info(f"[SILVER][ATTENDANCE][{batch_id}] Loading completed")

        logger.info(f"[SILVER][SALES][{batch_id}] Loading started")
        sales(logger,batch_id)
        logger.info(f"[SILVER][SALES][{batch_id}] Loading completed")

        logger.info(f"[SILVER][PIPELINE][{batch_id}] END")
        
    except Exception as e:
        logger.exception(f"[GOLD][PIPELINE] Failed {e}")