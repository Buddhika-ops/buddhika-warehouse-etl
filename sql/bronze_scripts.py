from sqlalchemy import text
from utils.db_engine import get_engine
from utils.logger import get_logger

logger = get_logger()
engine = get_engine()


def create_bronze_employees_table():
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE bronze_employees"))
            connection.execute(
                text(
                    """
                    CREATE TABLE bronze_employees (
                        employee_id INT,
                        name TEXT,
                        department TEXT,
                        age INT,
                        years_of_experience INT,
                        salary INT,
                        city TEXT,
                        ingestion_date TIMESTAMP
                    )
                    """
                )
            )

        logger.info("[BRONZE][EMPLOYEES] table created")
    except Exception as e:
        logger.error(f"[BRONZE][EMPLOYEES] table creation failed | error={e}")

def create_bronze_sales_table():
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE IF EXISTS bronze_sales"))
            connection.execute(
                text(
                    """
                    CREATE TABLE bronze_sales (
                        sale_id INT,
                        employee_id INT,
                        product TEXT,
                        amount NUMERIC(12,2),
                        date DATE,
                        ingestion_date TIMESTAMP
                    )
                    """
                )
            )
        logger.info("[BRONZE][SALES] table created")
    except Exception as e:
        logger.error(f"[BRONZE][SALES] table creation failed | error={e}")


def create_bronze_attendace_table():
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE IF EXISTS bronze_attendance"))

            connection.execute(
                text(
                    """
                    CREATE TABLE bronze_attendance (
                        employee_id INT,
                        date DATE,
                        attendance_hours INT,
                        ingestion_date TIMESTAMP
                    )
                    """
                )
            )
        logger.info("[BRONZE][ATTENDANCE] table created")
    except Exception as e:
        logger.error(f"[BRONZE][ATTENDANCE] table creation failed | error={e}")






