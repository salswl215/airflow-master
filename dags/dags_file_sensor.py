from airflow import DAG
from airflow.sensors.filesystem import FileSensor
import pendulum

with DAG(
    dag_id='dags_file_sensor',
    start_date=pendulum.datetime(2025,5,1, tz='Asia/Seoul'),
    schedule='0 7 * * *',
    catchup=False
) as dag:
    SearchParkInfoService_sensor = FileSensor(
        task_id='SearchParkInfoService_sensor',
        fs_conn_id='conn_file_opt_airflow_files',
        filepath='SearchParkInfoService/{{data_interval_end.in_timezone("Asia/Seoul") | ds_nodash }}/SearchParkInfoService.csv',
        recursive=False,
        poke_interval= 60,
        timeout=60*60*24,
        mode = 'reschedule'
    )