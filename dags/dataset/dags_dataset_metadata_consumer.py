import pendulum
from zlib import crc32
from airflow import DAG
from airflow.decorators import task
from airflow import Dataset

seoul_api_rt_bicycle_info = Dataset('seoul_api_rt_bicycle_info')

with DAG(
        dag_id='dags_dataset_metadata_consumer',
        schedule=[seoul_api_rt_bicycle_info],
        catchup=False,
        start_date=pendulum.datetime(2025, 5, 25, tz='Asia/Seoul'),
        tags=['update:2.10.5','dataset','consumer','metadata']
) as dag:
    @task(task_id='task_read_rt_bicycle_info_csv')
    def task_read_rt_bicycle_info_csv(**kwargs):
        dt = kwargs.get('data_interval_end').in_timezone('Asia/Seoul').strftime('%Y%m%d')
        file = f'/opt/airflow/files/tbCycleStationInfo/{dt}/tbCycleStationInfo.csv'
        with open(file, 'r') as f:
            content = f.read()
            crc = crc32(content.encode())
        return crc


    # Task마다 Dataset에 접근하여 저장된 Metadata를 꺼낼수 있어야 함
    @task(task_id='task_consumer_with_metadata',
          inlets=[seoul_api_rt_bicycle_info])
    def task_consumer_with_metadata(file_crc, **kwargs):
        inlet_events = kwargs.get('inlet_events')
        events = inlet_events[Dataset('seoul_api_rt_bicycle_info')]
        print('::group::Dataset Event List')
        for i in events[-5:]:
            print(i)
        print('::endgroup::')

        print('::group::CRC verification process start')
        crc_val_from_ds = events[-1].extra['crc32']
        # file_path = events[-1].extra['file_path']
        # with open(file_path) as f:
        #     contents = f.read()
        #     crc_of_file = crc32(contents.encode())

        print(f'CRC of ds: {crc_val_from_ds}')
        print(f'CRC of file: {file_crc}')
        if file_crc == crc_val_from_ds:
            print('CRC verification Success')
        else:
            print('CRC verification Faile.')
        print('::endgroup::')

    task_consumer_with_metadata(file_crc=task_read_rt_bicycle_info_csv())