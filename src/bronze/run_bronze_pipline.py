from .load_bronze import load_attendance,load_employees,load_sales
from utils.logger import get_logger

logger = get_logger(__name__,'bronze')

logger.info(f"[BRONZE][PIPLINE] STARTED")

def run_bronze_pipeline():
    try:
        logger.info(f"[BRONZE][EMPLOYEES] Loading started")
        load_employees(logger)
        logger.info("[BRONZE][EMPLOYEES] Loading completed")

        logger.info(f"[BRONZE][EMPLOYEES] Loading started")
        load_attendance(logger)
        logger.info("[BRONZE][ATTENDANCE] Loading completed")

        logger.info(f"[BRONZE][[SALES]] Loading started")
        load_sales(logger)
        logger.info(f"[BRONZE][[SALES]] Loading completed")

    except Exception as e:
        logger.exception(f"[BRONZE][PIPELINE] Failed {e}")
        raise