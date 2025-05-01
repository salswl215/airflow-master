from airflow import DAG
from airflow.sensors.python import PythonSensor
import pendulum
from airflow.hooks.base import BaseHook

with DAG(
    dag_id='dags_python_sensor',
    start_date=pendulum.datetime(2025,5,1, tz='Asia/Seoul'),
    schedule='10 1 * * *',
    catchup=False
) as dag:
    def check_api_update(http_conn_id, endpoint, base_dt_col, **kwargs):
        import requests
        import json
        from datetime import timedelta

        connection = BaseHook.get_connection(http_conn_id)
        url = f'http://{connection.host}:{connection.port}/{endpoint}/1/100'
        response = requests.get(url)

        contents = json.loads(response.text)
        key_nm = list(contents.keys())[0]
        row_data = contents.get(key_nm).get('row')
        last_dt = row_data[0].get(base_dt_col)
        last_date = last_dt[:10]
        last_date = last_date.replace('.', '-').replace('/', '-')

        try:
            pendulum.from_format(last_date, 'YYYY-MM-DD')
        except:
            from airflow.exceptions import AirflowException
            AirflowException(f'{base_dt_col} 컬럼은 YYYY.MM.DD 또는 YYYY/MM/DD 형태가 아닙니다.')

        data_interval_end = kwargs.get('data_interval_end')
        previous_day = data_interval_end - timedelta(days=1)
        previous_day_ymd = previous_day.in_timezone('Asia/Seoul').strftime('%Y-%m-%d')

        if last_date >= previous_day_ymd:
            print(f'생성 확인(배치 날짜: {previous_day_ymd} / API Last 날짜: {last_date})')
            return True
        else:
            print(f'Update 미완료 (배치 날짜: {previous_day_ymd} / API Last 날짜:{last_date})')
            return False

    sensor_task = PythonSensor(
        task_id = 'sensor_task',
        python_callable =check_api_update,
        op_kwargs={'http_conn_id': 'openapi.seoul.go.kr',
                   'endpoint':'{{var.value.apikey_openapi_seoul_go_kr}}/json/TbUseDaystatusView',
                   'base_dt_col':'DT'},
        poke_interval=60*3,
        mode = 'reschedule'
    )