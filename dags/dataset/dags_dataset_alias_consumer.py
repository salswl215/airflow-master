from airflow.exceptions import AirflowException
import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow.io.path import ObjectStoragePath
from airflow.datasets import DatasetAlias

BUCKET_NM = 's3://airflow-staging-dataset/staging'
DATASET_PREFIX = f'{BUCKET_NM}/tbCycleStationInfo'
DATASET_ALIAS = 'ds_rt_bicycle_to_s3'

with DAG(
        dag_id='dags_dataset_alias_consumer',
        schedule=[DatasetAlias(DATASET_ALIAS)],
        catchup=False,
        start_date=pendulum.datetime(2025, 5, 25, tz='Asia/Seoul'),
        tags=['update:2.10.5','producer','metadata','asset-alias','bicycle']
) as dag:
    @task(task_id='task_consumer_with_dataset_alias',
          inlets=[DatasetAlias(DATASET_ALIAS)])
    def task_consumer_with_dataset_alias(**kwargs):
        inlet_events = kwargs.get('inlet_events')
        print('inlet_events:',inlet_events)
        events = inlet_events[DatasetAlias(DATASET_ALIAS)]

        # Metadata에서 S3 경로를 얻은 후 ObjectStoragePath 를 이용해 S3에서 로컬로 파일 복사
        print('events:', events)
        src_path = events[-1].extra["path"]      # events[-1]: 가장 최근의 데이터셋
        file_nm = src_path.split('/')[-1]
        src_obj = ObjectStoragePath(src_path, conn_id='conn-amazon-s3-access')
        tgt_obj = ObjectStoragePath(f'file:///opt/airflow/files/download/{file_nm}')

        print(f's3_path: {src_path}')
        print(f'target_path: {tgt_obj}')

        if src_obj.is_file():
            src_obj.copy(tgt_obj)
            print(f'copy complete ({src_obj} -> {tgt_obj})')
        else:
            raise AirflowException(f'Could find a file ({src_path})')

    task_consumer_with_dataset_alias()