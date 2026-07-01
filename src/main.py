from utils.logger import get_logger
from sql.bronze_scripts import create_bronze_employees_table, create_bronze_sales_table, create_bronze_attendace_table
from src.bronze.load_bronze import load_employees, load_sales, load_attendance
from src.silver.load_silver import load_silver_attendance_table
from sql.silver_scripts import (
    create_silver_employees_table,
    create_silver_employees_rejected_table,
    create_silver_sales_table,
    create_silver_sales_rejected_table,
    create_silver_attendance_table,
)
from src.silver.employee.employees import clean_bronze_employees_table
from src.silver.sales.sales import clean_bronze_sales_table
from src.silver.attendance.attendance import clean_bronze_attendance_table
from data.data_generator import sales, employees,attendance


from src.gold.run_gold_pipeline import gold_pipline
logger = get_logger()

from src.silver.run_silver_pipeline import silver_pipline
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
    # create_silver_employees_rejected_table()
    # create_silver_sales_table()
    # create_silver_sales_rejected_table()
    # create_silver_attendance_table()
    # logger.info("[SILVER] table creation completed")

    # logger.info("[SILVER] data cleaning and loading started")
    # clean_bronze_employees_table()
    # clean_bronze_sales_table()
    # clean_bronze_attendance_table()
    # logger.info("[SILVER] data loading completed")

        # logger.info("[PIPELINE] COMPLETED")

    silver_pipline()


    # gold_pipline()    

if __name__ == "__main__":
    main()