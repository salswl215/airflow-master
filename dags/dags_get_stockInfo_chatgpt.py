import pendulum
from operators.tistory_write_post_by_chatgpt_operator import GetInfoByChatgptOperator
from airflow import DAG

with DAG(
    dag_id='dags_get_stockInfo_chatgpt',
    start_date=pendulum.datetime(2025, 5, 15, tz='Asia/Seoul'),
    catchup=False,
    schedule='0 13 * * *',
) as dag:
    tistory_write_post_by_chatgpt = GetInfoByChatgptOperator(
        task_id='tistory_write_post_by_chatgpt',
        post_cnt_per_market=3
    )