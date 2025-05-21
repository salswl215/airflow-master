import pendulum
from operators.seoul_api_to_csv_operator import SeoulApiToCsvOperator
import pandas as pd
from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import get_current_context

with DAG(
    dag_id = 'dags_dynamic_task_mapping_df',
    schedule=None,
    start_date=pendulum.datetime(2025, 5, 20, tz="Asia/Seoul"),
    catchup=False,
    tags=['update:2.10.5', 'dnm_tsk_map']
) as dag:
    task_get_rt_bicycle_info = SeoulApiToCsvOperator(
        task_id='task_get_rt_bicycle_info',
        dataset_nm='tbCycleStationInfo',
        path='/opt/airflow/files/tbCycleStationInfo/{{data_interval_end.in_timezone("Asia/Seoul") | ds_nodash }}',
        file_name='tbCycleStationInfo.csv'
    )

    @task(task_id='task_read_csv_to_dict')
    def task_read_csv_to_dict(**kwargs):
        dt = kwargs.get('data_interval_end').in_timezone('Asia/Seoul').strftime('%Y%m%d')
        file = f'/opt/airflow/files/tbCycleStationInfo/{dt}/tbCycleStationInfo.csv'
        df = pd.read_csv(file)
        bicycle_info_dict = df.where(pd.notnull(df), None).astype(object)[:10].to_dict(orient='index')
        return bicycle_info_dict

    @task(task_id='task_station_info',
          map_index_template="{{ station_name_index }}"
    )
    def task_station_info(station):
        # station 정보는 tuple 로 들어옴 (아래 샘플 참조)
        values_dict = station[1]
        station_nm = values_dict.get('RENT_ID_NM')
        prk_cnt = values_dict.get('HOLD_NUM')
        context = get_current_context()
        context["station_name_index"] = station_nm

        print(f'{station_nm}에 보관중인 자전거 건수: {prk_cnt}')


    task_read_csv_to_dict = task_read_csv_to_dict()
    task_get_rt_bicycle_info >> task_read_csv_to_dict >> task_station_info.expand(station=task_read_csv_to_dict)