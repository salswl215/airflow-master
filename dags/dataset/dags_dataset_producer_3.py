import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow import Dataset

dataset_dags_dataset_producer_3 = Dataset("dags_dataset_producer_3")

with DAG(
        dag_id='dags_dataset_producer_3',
        schedule=None,
        start_date=pendulum.datetime(2025, 5, 25, tz='Asia/Seoul'),
        catchup=False,
        tags=['update:2.10.5','dataset','producer']
) as dag:
    @task(task_id='task_producer_3',
          outlets=[dataset_dags_dataset_producer_3])
    def task_producer_3():
        print('dataset update complete')

    task_producer_3()