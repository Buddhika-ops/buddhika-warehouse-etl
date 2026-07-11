
from airflow.decorators import dag, task
from datetime import datetime

@dag(
        dag_id="stage1_hello_airflow",
        schedule=None,
        start_date = datetime(2026,1,1),
        catchup = False,
        tags=["learning", "stage1"],
)

def stage1_hello_airflow():

    @task
    def say_hello():
        print('hello from task 1')
        return "hello"
    @task
    def say_world(previous_result: str):
        print(f"Got '{previous_result}' from Task 1, now running Task 2")
        print("World!")

        say_world(say_hello())

stage1_hello_airflow()