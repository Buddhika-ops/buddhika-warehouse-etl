import sys
import os

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from utils.db_engine import get_engine
from utils.logger import get_logger

logger = get_logger()
engine = get_engine()


def truncate_silver_tables():
    silver_tables = [
        "silver_employees",
        "silver_employees_rejected",
        "silver_sales",
        "silver_sales_rejected",
        "silver_attendance",
        "silver_attendance_rejected"
        
    ]

    logger.info("[UTILS] Truncating all Silver tables...")
    try:
        with engine.begin() as connection:
            for table in silver_tables:
                connection.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                logger.info(f"[UTILS] Truncated table: {table}")

            # Reset watermarks in etl_metadata
            connection.execute(
                text(
                    """
                    UPDATE etl_metadata
                    SET last_loaded_timestamp = '2020-01-01 00:00:00'
                    """
                )
            )
            logger.info("[UTILS] Reset all ETL metadata watermarks to 2020-01-01 00:00:00")

        logger.info("[UTILS] All Silver tables truncated successfully.")
    except Exception as e:
        logger.error(f"[UTILS] Truncation failed | error={e}")


if __name__ == "__main__":
    truncate_silver_tables()
