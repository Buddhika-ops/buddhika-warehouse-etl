import sys 
import os
from datetime import datetime,timedelta


from airflow.decorators import dag,task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

WAREHOUSE_PATH = "/opt/airflow/warehouse"
sys.path.insert(0, WAREHOUSE_PATH)

@dag(
    dag_id="stage3_silver_pipeline",
    schedule = None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["warehouse", "stage3", "silver"],   
)

def stage3_silver_pipeline():
    @task(retries=2, retry_delay=timedelta(minutes=1))
    def make_batch_id():
        import uuid
        return str(uuid.uuid4())
    
    @task(retries=2, retry_delay=timedelta(minutes=1))
    def employees_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.silver.transformations.employees.clean_employees import employees

        logger = get_logger(__name__, "silver")
        employees(logger, batch_id)
        return batch_id
    
    @task(retries=2, retry_delay=timedelta(minutes=1))
    def attendance_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.silver.transformations.attendance.clean_attendance import attendance

        logger = get_logger(__name__, "silver")
        attendance(logger, batch_id)

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def sales_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.silver.transformations.sales.clean_sales import sales

        logger = get_logger(__name__, "silver")
        sales(logger, batch_id)
    
    Trigger_gold = TriggerDagRunOperator(
        task_id="trigger_gold_pipeline",
        trigger_dag_id="stage4_gold_pipeline",
    )

    batch_id = make_batch_id()
    employees_done = employees_task(batch_id)
    attendance_done = attendance_task(employees_done)
    sales_done = sales_task(employees_done)

    [attendance_done,sales_done] >> Trigger_gold


stage3_silver_pipeline()