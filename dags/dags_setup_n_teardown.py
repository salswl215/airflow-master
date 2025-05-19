import pendulum
from airflow import DAG
from airflow.decorators import task

with DAG(
    dag_id = 'dags_setup_n_teardown',
    schedule=None,
    start_date = pendulum.datetime(2025, 5, 19, tz ='Asia/Seoul'),
    catup = False,
    tags = ['update:2.10.5', 'setup-teardown']
)as dag:
    @task(task_id = 'setup_task')
    def setup_task():
        print('start')

    @task(task_id = 'do_something')
    def do_something():
        # log group 설정 관련
        print("::group::Do Something Group")
        print('do it!')
        print('thank you')
        print('complete')
        print("::endgroup::")

    @task(task_id = 'teardown_task')
    def teardown_task():
        print('teardown!')


    setup_task().as_setup() >> do_something() >> teardown_task().as_teardown()

    # Task 관계는 아래처럼 작성해도 좋음
    # do_something() >> teardown_task().as_teardown(setups=setup_task())