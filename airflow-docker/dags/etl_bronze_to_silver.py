from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import sys
sys.path.append("/opt/airflow")

from src.silver.employees.employees import clean_bronze_employees_table
from src.silver.sales.sales import clean_bronze_sales_table
from src.silver.attendance.attendance import clean_bronze_attendance_table


default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="bronze_to_silver_etl",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False
) as dag:

    employees = PythonOperator(
        task_id="employees",
        python_callable=clean_bronze_employees_table
    )

    sales = PythonOperator(
        task_id="sales",
        python_callable=clean_bronze_sales_table
    )

    attendance = PythonOperator(
        task_id="attendance",
        python_callable=clean_bronze_attendance_table
    )

    employees >> [sales, attendance]