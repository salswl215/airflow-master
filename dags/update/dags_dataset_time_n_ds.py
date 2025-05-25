import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow import Dataset
from airflow.timetables.trigger import CronTriggerTimetable
from airflow.timetables.datasets import DatasetOrTimeSchedule

# Cron timetable & Dataset 두 개 모두를 이용해 스케줄링 걸기
with DAG(
        dag_id='dags_dataset_time_n_ds',
        schedule=DatasetOrTimeSchedule(
            timetable=CronTriggerTimetable("* * * * *", timezone="Asia/Seoul"),
            datasets=(Dataset('dags_dataset_producer_3') &
                      (Dataset("dags_dataset_producer_1") | Dataset("dags_dataset_producer_2"))
            )
        ),
        start_date=pendulum.datetime(2025, 5, 25, tz='Asia/Seoul'),
        catchup=False,
        tags=['update:2.10.5','asset','consumer']
) as dag:
    @task.bash(task_id='task_bash')
    def task_bash():
        return 'echo "schedule run"'

    task_bash()