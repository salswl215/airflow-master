import pendulum
from airflow.exceptions import AirflowException
from airflow import DAG
from airflow.operators.bash import BashOperator

# DAG 연속 실패 시 자동 DAG Pause 변경 기능(preview)
# config parameter / dag parameter로 제어 가능
with DAG(
        dag_id="dags_consecutive_failed",
        schedule='* * * * *',
        start_date=pendulum.datetime(2025, 3, 1, tz="Asia/Seoul"),
        catchup=False,
        tags=['update:2.10.5','bash','taskflow'],
        max_consecutive_failed_dag_runs=3
) as dag:

    @task(task_id='task_failed')
    def task_failed():
        raise AirflowException('error occured!')

    task_failed()