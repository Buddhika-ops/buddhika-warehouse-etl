from sqlalchemy import text
from src.db_engine import get_engine
from utils.logger import get_logger

logger = get_logger()
engine = get_engine()


def create_silver_employees_table():
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE IF EXISTS silver_employees"))
            connection.execute(
                text(
                    """
                    CREATE TABLE silver_employees (
                        employee_id INT PRIMARY KEY,
                        name TEXT,
                        department TEXT,
                        age INT,
                        years_of_experience INT,
                        salary INT,
                        city TEXT,
                        join_date_estimated INT,
                        ingestion_date TIMESTAMP
                    )
                    """
                )
            )

        logger.info("[SILVER][EMPLOYEES] table created successfully")
    except Exception as e:
        logger.error(f"[SILVER][EMPLOYEES] table creation failed | error={e}")


def create_silver_sales_table():
    logger.info("[SILVER][SALES] table creation started")

    try:
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE IF EXISTS silver_sales"))

            connection.execute(
                text(
                    """
                    CREATE TABLE silver_sales (
                        sale_id INT PRIMARY KEY,
                        employee_id INT,
                        product VARCHAR(100),
                        amount NUMERIC(12,2),
                        date DATE,
                        sales_without_employees_flag BOOLEAN,
                        missing_amount_flag BOOLEAN,
                        ingestion_date TIMESTAMP
                    )
                    """
                )
            )

        logger.info("[SILVER][SALES] table created successfully")

    except Exception as e:
        logger.error(
            f"[SILVER][SALES] Table creation failed | error={e}"
        )

def create_silver_attendance_table():
    logger.info("[SILVER][ATTENDANCE] table creation started")

    try:
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE IF EXISTS silver_attendance"))

            connection.execute(
                text(
                    """
                    CREATE TABLE silver_attendance (
                    employee_id INT,
                    date DATE,
                    attendance_hours NUMERIC,
                    attendance_without_employees_flag BOOLEAN,
                    missing_attendance_hours_flag BOOLEAN,
                    attendance_status VARCHAR(50),
                    overtime NUMERIC,
                    ingestion_date TIMESTAMP,
                    PRIMARY KEY (employee_id, date)
                );
                    """
                )
            )

        logger.info("[SILVER][ATTENDANCE] table created successfully")

    except Exception as e:
        logger.error(
            f"[SILVER][ATTENDANCE] Table creation failed | error={e}"
        )
     