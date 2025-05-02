from sensors.seoul_api_date_sensor import SeoulApiDateSensor
from airflow import DAG
import pendulum

with DAG(
    dag_id='dags_custom_sensor',
    start_date=pendulum.datetime(2023,4,1, tz='Asia/Seoul'),
    schedule=None,
    catchup=False
) as dag:

    VwSccStats_sensor = SeoulApiDateSensor(
        task_id = 'VwSccStats_sensor',
        dataset_nm = 'VwSccStats',
        base_dt_col='DALY_DE',
        day_off=0,
        poke_interval=300,
        mode='reschedule'
    )

    VwSccStatsAgeSexdstn_sensor = SeoulApiDateSensor(
        task_id = 'VwSccStatsAgeSexdstn_sensor',
        dataset_nm = 'VwSccStatsAgeSexdstn',
        base_dt_col = 'DALY_DE',
        day_off = -1,
        poke_interval = 300,
        mode = 'reschedule'
    )