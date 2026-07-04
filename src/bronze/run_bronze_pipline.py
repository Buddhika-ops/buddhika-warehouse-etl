from .load_bronze import load_attendance,load_employees,load_sales
from utils.logger import get_logger

logger = get_logger(__name__,'bronze')



def bronze_pipeline(batch_id):
    try:
        logger.info(f"[BRONZE][PIPELINE][{batch_id}] STARTED")
        logger.info(f"[BRONZE][EMPLOYEES][{batch_id}] Loading started")
        load_employees(logger,batch_id)
        logger.info(f"[BRONZE][EMPLOYEES][{batch_id}] Loading completed")

        logger.info(f"[BRONZE][ATTENDANCE][{batch_id}] Loading started")
        load_attendance(logger,batch_id)
        logger.info(f"[BRONZE][ATTENDANCE][{batch_id}] Loading completed")

        logger.info(f"[BRONZE][SALES][{batch_id}] Loading started")
        load_sales(logger,batch_id)
        logger.info(f"[BRONZE][[SALES]][{batch_id}] Loading completed")
        logger.info(f"[BRONZE][PIPELINE][{batch_id}] Completed")
    except Exception as e:
        logger.exception(f"[BRONZE][PIPELINE][{batch_id}] Failed {e}")
        raise