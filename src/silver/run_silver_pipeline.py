from src.silver.employees import employees
from utils.logger import get_logger

logger = get_logger()

def silver_pipline():
    logger.info("[GOLD_PIPELINE] STARTED")
    employees()
    logger.info("[GOLD_PIPELINE] END")