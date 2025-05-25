from operators.seoul_api_to_csv_operator import SeoulApiToCsvOperator
import pendulum
from zlib import crc32
from airflow import DAG
from airflow.decorators import task
from airflow.datasets.metadata import Metadata
from airflow import Dataset


seoul_api_rt_bicycle_info = Dataset('seoul_api_rt_bicycle_info')

with DAG(
        dag_id='dags_dataset_metadata_producer',
        schedule=None,
        catchup=False,
        start_date=pendulum.datetime(2025, 5, 25, tz='Asia/Seoul'),
        tags=['update:2.10.5','dataset','producer','metadata']
) as dag:
    seoul_api_to_csv_operator = SeoulApiToCsvOperator(
        task_id='task_get_rt_bicycle_info',
        dataset_nm='tbCycleStationInfo',
        path='/opt/airflow/files/tbCycleStationInfo/{{data_interval_end.in_timezone("Asia/Seoul") | ds_nodash }}',
        file_name='tbCycleStationInfo.csv'
    )

    @task(task_id='task_producer_with_metadata',
          outlets=[seoul_api_rt_bicycle_info])
    def task_producer_with_metadata(**kwargs):
        dt = kwargs.get('data_interval_end').in_timezone('Asia/Seoul').strftime('%Y%m%d')
        file = f'/opt/airflow/files/tbCycleStationInfo/{dt}/tbCycleStationInfo.csv'
        with open(file) as f:
            contents = f.read()
            crc = crc32(contents.encode())
            cnt = len(contents.split('\n')) - 1
            print('file_name: tbCycleStationInfo.csv')
            print(f'file_crc: {crc}')
            print(f'file_cnt: {cnt}')
        # Dataset에 Metadata를 넣는 방법, 첫 번째: context 변수 접근을 통해 입력
        kwargs["outlet_events"][seoul_api_rt_bicycle_info].extra = {"len_of_bikeList": cnt, 'crc32':crc, 'file_path':file}

        # Dataset에 Metadata를 넣는 방법, 두 번째: Metadata 클래스 + yield 를 이용해 입력
        # yield Metadata(
        #         Asset('ds_with_metadata'),
        #         extra={"len_of_bikeList": cnt, 'crc32':crc}
        #     )

    seoul_api_to_csv_operator >> task_producer_with_metadata()