from airflow import DAG
import pendulum
import datetime
from airflow.decorators import task
from pprint import pprint

with DAG(
        dag_id="dags_python_show_templates",
        schedule="30 9 * * *",
        start_date=pendulum.datetime(2025, 4, 1, tz="Asia/Seoul"),
        catchup=True
) as dag:

    @task(task_id="python_task")
    def show_templates(**kwargs):
        pprint(kwargs)

    show_templates()