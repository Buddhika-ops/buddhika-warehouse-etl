import sys
import os
from datetime import datetime,timedelta


from airflow.decorators import dag, task

WAREHOUSE_PATH = "/opt/airflow/warehouse"
sys.path.insert(0, WAREHOUSE_PATH)


@dag(
    dag_id="stage4_gold_pipeline",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["warehouse", "stage4", "gold"],
)
def stage4_gold_pipeline():

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def make_batch_id():
        import uuid
        return str(uuid.uuid4())

    # ---------- Layer 1: Dimensions (parallel) ----------
    @task(retries=2, retry_delay=timedelta(minutes=1))
    def dim_employees_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.gold.builders.dimensions.gold_dim_employees import gold_dim_employees
        logger = get_logger(__name__, "gold")
        gold_dim_employees(logger, batch_id)

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def dim_product_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.gold.builders.dimensions.gold_dim_product import gold_dim_product
        logger = get_logger(__name__, "gold")
        gold_dim_product(logger, batch_id)

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def dim_date_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.gold.builders.dimensions.gold_dim_date import gold_dim_date
        logger = get_logger(__name__, "gold")
        gold_dim_date(logger, batch_id)

    # ---------- Layer 2: Facts (parallel, after dimensions) ----------
    @task(retries=2, retry_delay=timedelta(minutes=1))
    def fact_sales_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.gold.builders.fact.gold_fact_sales import gold_fact_sales
        logger = get_logger(__name__, "gold")
        gold_fact_sales(logger, batch_id)

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def fact_attendance_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.gold.builders.fact.gold_fact_attendance import gold_fact_attendance
        logger = get_logger(__name__, "gold")
        gold_fact_attendance(logger, batch_id)

    # ---------- Layer 3: KPIs (parallel, after facts) ----------
    @task(retries=2, retry_delay=timedelta(minutes=1))
    def employee_monthly_performance_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.gold.builders.kpis_mart.gold_employee_monthly_performance import gold_employee_monthly_performance
        logger = get_logger(__name__, "gold")
        gold_employee_monthly_performance(logger, batch_id)

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def department_monthly_sales_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.gold.builders.kpis_mart.gold_department_monthly_sales import gold_department_monthly_sales
        logger = get_logger(__name__, "gold")
        gold_department_monthly_sales(logger, batch_id)

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def monthly_company_summary_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.gold.builders.kpis_mart.gold_monthly_company_summary import gold_monthly_company_summary
        logger = get_logger(__name__, "gold")
        gold_monthly_company_summary(logger, batch_id)

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def product_performance_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.gold.builders.kpis_mart.gold_product_performance import gold_product_performance
        logger = get_logger(__name__, "gold")
        gold_product_performance(logger, batch_id)

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def city_sales_performance_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.gold.builders.kpis_mart.gold_city_sales_performance import gold_city_sales_performance
        logger = get_logger(__name__, "gold")
        gold_city_sales_performance(logger, batch_id)

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def employee_attendance_summary_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.gold.builders.kpis_mart.gold_employee_attendance_summary import gold_employee_attendance_summary
        logger = get_logger(__name__, "gold")
        gold_employee_attendance_summary(logger, batch_id)

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def top_performers_monthly_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.gold.builders.kpis_mart.gold_top_performers_monthly import gold_top_performers_monthly
        logger = get_logger(__name__, "gold")
        gold_top_performers_monthly(logger, batch_id)

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def data_quality_summary_task(batch_id: str):
        os.chdir(WAREHOUSE_PATH)
        from utils.logger import get_logger
        from src.gold.builders.kpis_mart.gold_data_quality_summary import gold_data_quality_summary
        logger = get_logger(__name__, "gold")
        gold_data_quality_summary(logger, batch_id)

    # ---------- Wiring ----------
    batch_id = make_batch_id()

    # Layer 1: dimensions run in parallel
    dims_done = [
        dim_employees_task(batch_id),
        dim_product_task(batch_id),
        dim_date_task(batch_id),
    ]

    # Layer 2: facts run in parallel, after ALL dimensions finish
    sales_done = fact_sales_task(batch_id)
    attendance_done = fact_attendance_task(batch_id)
    for d in dims_done:
        d >> sales_done
        d >> attendance_done

    # Layer 3: KPIs run in parallel, after BOTH facts finish
    kpi_tasks = [
        employee_monthly_performance_task(batch_id),
        department_monthly_sales_task(batch_id),
        monthly_company_summary_task(batch_id),
        product_performance_task(batch_id),
        city_sales_performance_task(batch_id),
        employee_attendance_summary_task(batch_id),
        top_performers_monthly_task(batch_id),
        data_quality_summary_task(batch_id),
    ]
    for k in kpi_tasks:
        sales_done >> k
        attendance_done >> k


stage4_gold_pipeline()