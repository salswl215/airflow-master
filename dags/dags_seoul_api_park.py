from operators.seoul_api_to_csv_operator import SeoulApiToCsvOperator
from airflow import DAG
import pendulum

with DAG(
    dag_id='dags_seoul_api_park',
    schedule='0 7 * * *',
    start_date=pendulum.datetime(2023,4,1, tz='Asia/Seoul'),
    catchup=False
) as dag:
    '''서울시 한강공원 월별 이용객 정보'''
    han_park_monthly_users = SeoulApiToCsvOperator(
        task_id='han_park_monthly_users',
        dataset_nm='tbHanParkUtztnMonth',
        path='/opt/airflow/files/tbHanParkUtztnMonth/{{data_interval_end.in_timezone("Asia/Seoul") | ds_nodash }}',
        file_name='tbHanParkUtztnMonth.csv'
    )

    '''서울시 주요 공원 정보'''
    seoul_park_info = SeoulApiToCsvOperator(
        task_id='seoul_park_info',
        dataset_nm='SearchParkInfoService',
        path='/opt/airflow/files/SearchParkInfoService/{{data_interval_end.in_timezone("Asia/Seoul") | ds_nodash }}',
        file_name='SearchParkInfoService.csv'
    )

    han_park_monthly_users >> seoul_park_info