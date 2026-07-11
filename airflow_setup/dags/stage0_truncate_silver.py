import sys
import os
from datetime import datetime

from airflow.decorators import dag, task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

WAREHOUSE_PATH = "/opt/airflow/warehouse"
sys.path.insert(0, WAREHOUSE_PATH)


@dag(
    dag_id="stage0_truncate_silver",
    schedule=None,  # manual trigger only - this is a reset button, not scheduled
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["warehouse", "utility", "reset"],
)
def stage0_truncate_silver():

    @task
    def truncate_silver_task():
        os.chdir(WAREHOUSE_PATH)
        from scripts.truncate_silver import truncate_silver_tables

        truncate_silver_tables()

    trigger_bronze = TriggerDagRunOperator(
        task_id="trigger_bronze_pipeline",
        trigger_dag_id="stage2_bronze_pipeline",
    )

    truncate_silver_task() >> trigger_bronze


stage0_truncate_silver()