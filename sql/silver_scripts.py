from sqlalchemy import text
from utils.db_engine import get_engine
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
                    CREATE TABLE IF NOT EXISTS silver_employees (
                    employee_id INTEGER PRIMARY KEY,
                    name TEXT,
                    department TEXT,
                    age INTEGER,
                    years_of_experience INTEGER,
                    salary NUMERIC,
                    city TEXT,
                    ingestion_date TIMESTAMP
                    )
                    """
                )
            )

        logger.info("[SILVER][EMPLOYEES] table created successfully")
    except Exception as e:
        logger.error(f"[SILVER][EMPLOYEES] table creation failed | error={e}")


def create_silver_employees_rejected_table():
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE IF EXISTS silver_employees_rejected"))
            connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS silver_employees_rejected (
                        employee_id INTEGER PRIMARY KEY,
                        name TEXT,
                        department TEXT,
                        age NUMERIC,
                        years_of_experience INTEGER,
                        salary NUMERIC,
                        city TEXT,
                        rejection_reason TEXT,
                        rejected_at TIMESTAMP
                    )
                    """
                )
            )

        logger.info("[SILVER][EMPLOYEES][REJECTED] table created successfully")
    except Exception as e:
        logger.error(f"[SILVER][EMPLOYEES][REJECTED] table creation failed | error={e}")


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
                        quantity INT,
                        amount NUMERIC(12,2),
                        date DATE,
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

def create_silver_sales_rejected_table():
    logger.info("[SILVER][SALES][REJECTED] table creation started")
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE IF EXISTS silver_sales_rejected"))
            connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS silver_sales_rejected (
                        sale_id INTEGER PRIMARY KEY,
                        employee_id INTEGER,
                        product TEXT,
                        quantity INTEGER,
                        amount NUMERIC,
                        date DATE,
                        rejection_reason TEXT,
                        rejected_at TIMESTAMP
                    )
                    """
                )
            )
        logger.info("[SILVER][SALES][REJECTED] table created successfully")
    except Exception as e:
        logger.error(
            f"[SILVER][SALES][REJECTED] Table creation failed | error={e}"
        )
     