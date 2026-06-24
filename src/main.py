from utils.logger import get_logger
from sql.bronze_scripts import create_bronze_employees_table, create_bronze_sales_table, create_bronze_attendace_table
from src.bronze.load_bronze import load_employees, load_sales, load_attendance
from src.silver.load_silver import clean_silver_employees_table, load_silver_sales_table,load_silver_attendance_table
from sql.silver_scripts import create_silver_employees_table,create_silver_sales_table,create_silver_attendance_table


logger = get_logger()


def main():
    logger.info("[PIPELINE] STARTED")

    # logger.info("[BRONZE] table creation started")
    # create_bronze_employees_table()
    # create_bronze_sales_table()
    # create_bronze_attendace_table()
    # logger.info("[BRONZE] table creation completed")

    # logger.info("[BRONZE] load started")
    # load_employees()
    # load_sales()
    # load_attendance()
    # logger.info("[BRONZE] load completed")

    # logger.info("[SILVER] table creation started")
    # create_silver_employees_table()
    # create_silver_sales_table()
    # create_silver_attendance_table()
    # logger.info("[SILVER] table creation completed")

    logger.info("[SILVER] data cleaning and loading started")
    clean_silver_employees_table()
    load_silver_sales_table()
    load_silver_attendance_table()
    logger.info("[SILVER] data loading completed")

    logger.info("[PIPELINE] COMPLETED")

if __name__ == "__main__":
    main()