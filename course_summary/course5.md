## Scheduler 부하 줄이기

### Scheduler 역할
![](https://miintto.github.io/img/posts/airflow-archi-scheduler-loop.png)
1. 작성한 DAG을 run하지는 않으나 구문 분석 시 파이썬 문법을 따라가며 검사 (parsing)
2. Parsing 후 이상없는 DAG 내용을 DB에 저장
3. 스케줄이 만족된 DAG 실행 (Run 생성)
4. 수행해야 할 Task Instance 생성 후 Queue에 넣기

#### Scheduler loop
- 스케줄러는 DAG Run 생성/관리 시 관련 DB 레코드에 lock을 걸어 다른 스케줄러에 의해 DAG와 Task Instance가 반복 실행되지 않도록 함

### 스케줄러 부하 줄이기 : Parsing 단계

#### 1) 라이브러리 Import 구문 작성 방법
- 라이브러리 Import는 python Callable 안으로
```
def python_fuction1(**kwargs):
   import requests, json
      requests.get(...)
     
with DAG(
    dag_id='dags_python_operator_with_args',
    start_date=pendulum.datetime(2025, 4, 1, tz = 'Asia/Seoul'),
    catchup=False
) as dag:
      python_task_1 = PythonOperator(
         task_id = 'python_task_1',
         python_callable = python_function1)
```
#### 2) Custom Operator의 init 함수 작성 방법
- Custom Operator의 init 함수 경량화
```
 def __init__(self, dataset_nm, path, file_name, base_dt=None, **kwargs):
     super().__init__(**kwargs)
     self.http_conn_id = 'openapi.seoul.go.kr'
     self.path = path
     self.file_name = file_name
     self.endpoint = '{{var.value.apikey_openapi_seoul_go_kr}}/json/' + dataset_nm
     self.base_dt = base_dt
     ## self.connection = BaseHook.get_connection(self.http_conn_id)

 def execute(self, context):
     self.connection = BaseHook.get_connection(self.http_conn_id)
```
#### 3) Variable 작성 방법
- Variable 값 추출 시 Operator 변수 내 Template 활용
```
from airflow.oprators.bash import BashOperator
# from airflow.models import Variable

# var_value = Variable.get('sample_key')
bash_var_2 = BashOperator(
      task_id = 'bash_var_2',
      bash_command = f"echo variable.{{var.value.sample_key}}"
      )
```
#### 4) Config 파라미터 조절
- `dag_dir_list_interval` : DAG 디렉토리에 신규 DAG 목록 새로고침 주기
- `min_file_process_interval` : DAG 파일 구문분석 후 반영되기까지의 시간
  - 위의 두 값이 감소한다면? : 스케줄러 부하 증가 / 빠른 DAG 반영 가능
  - 위의 두 값이 증가하다면? : 스케줄러 부하 감소 / DAG 반영 대기 증가
- `parsing_processes` : DAG 구문 분석을 위한 프로세스의 개수 지정
- `file_parsing_sort_mode` : DAG 파일 Sorting 모드 방법 (modified_time, random_seeded_by_host, alphabetical

#### 5) 인프라 환경 확인
- Disk 성능
  - DAG 폴더가 존재하는 파일시스템 구성시 IO 성능이 좋은 SSD Disk 사용

### 스케줄러 부하 줄이기 : 실행 단계

#### 1) DB Proxy 설정 (PGBouncer 사용)
![](https://miro.medium.com/v2/resize:fit:1400/1*RsL8zleiupKsP5wwCGP5Ow@2x.png)
- **PGBouncer** : PostgreSQL 서버와의 커넥션을 맺는 과정은 많은 자원을 소모하기 때문에, 한 번 만들어 둔 커넥션을 재사용할 필요가 존재. 이때 사용하는 것이 커넥션 풀링 도구
- PGBouncer와 Meta DB(Postgres) 사이에 미리 만들어진 Connection Client는 모두 이 커넥션을 재활용하므로 매번 커넥션을 맺을 필요가 없음
- Scheduler/Worker 입장에서 메타 DB와 매번 연결 필요 없이 이미 있는 커넥션 재활용하면 되어 빠름!

#### 2) Config 파라미터 조절
| 파라미터                                 | 설명                                                                                                                                             | 기본 값 |
|------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| `max_dagruns_per_loop_to_schedule`       | 스케줄러가 Loop당 스케줄링을 위해 검사해야 하는 **DAG Run**의 최대 개수<br>멀티 스케줄러 환경에서 이 값이 높으면 특정 스케줄러에 DAG Run 부하가 쏠리는 현상 발생 | 20     |
| `max_dagruns_to_create_per_loop`         | 스케줄러가 Loop당 DAG Run 생성할 수 있는 **DAG** 최대 개수                                                                                            | 10     |
