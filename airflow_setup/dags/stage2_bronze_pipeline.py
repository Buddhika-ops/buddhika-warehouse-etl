
import sys
import os
from datetime import datetime,timedelta

from airflow.decorators import dag, task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


WAREHOUSE_PATH = "/opt/airflow/warehouse"
sys.path.insert(0, WAREHOUSE_PATH)


@dag(
    dag_id="stage2_bronze_pipeline",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["warehouse", "stage2", "bronze"],
)
def stage2_bronze_pipeline():

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def make_batch_id():
        import uuid
        return str(uuid.uuid4())

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def load_employees_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.bronze.load_bronze import load_employees

        logger = get_logger(__name__, "bronze")
        load_employees(logger, batch_id)
        return batch_id

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def load_attendance_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.bronze.load_bronze import load_attendance

        logger = get_logger(__name__, "bronze")
        load_attendance(logger, batch_id)

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def load_sales_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.bronze.load_bronze import load_sales

        logger = get_logger(__name__, "bronze")
        load_sales(logger, batch_id)


    Trigger_silver = TriggerDagRunOperator(
        task_id="trigger_silver_pipeline",
        trigger_dag_id="stage3_silver_pipeline",
    )

    batch_id = make_batch_id()
    employees_done = load_employees_task(batch_id)
    attendance_done = load_attendance_task(employees_done)
    sales_done = load_sales_task(employees_done)

    [attendance_done,sales_done] >> Trigger_silver


stage2_bronze_pipeline()