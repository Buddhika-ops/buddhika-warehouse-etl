from airflow.decorators import dag, task
from datetime import datetime


@dag(
    dag_id="stage1_graph_test",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["learning", "stage1"],
)
def stage1_graph_test():

    @task
    def step_one():
        print("Step 1 running")

    @task
    def step_two():
        print("Step 2 running")

    @task
    def step_three():
        print("Step 3 running")

    step_one() >> step_two() >> step_three()


stage1_graph_test()