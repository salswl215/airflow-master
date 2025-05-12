## Celery Executor

### Celery Executor
![](https://miro.medium.com/v2/resize:fit:1200/1*2mqTYLHgD1EKy2WEmRA_RA.png)
1. Docker Compose로 Aiflow 설치 시 기본 선택되는 Executor
2. 파이썬 Celery는 task를 요청하는 clinet/task를 처리하는 celery worker가 여러 개인 환경에서도 동작함. 따라서 scheduler, airflow worker를 더 띄울 수 있다.
3. Airflow 모듈을 꼭 컨테이너로 구성할 필요는 없음
   1. 프로세스로써 Airflow 모듈을 start 시키는 것 가능
   2. #> airflow celery worker (celery worker 프로세스 기동)
   3. #> airflow scheduler (scheduler 프로세스 기동)
4. Schedule, Worker를 서로 다른 물리적 서버에 올려도 됨
   1. 단, 동일한 airflow.cfg(환경변수 설정파일) 가지고 있어야 함
   2. 동일한 DAG 소스를 바라봐야 한다.

### Celery Executor 구성 방법
1. 다수 노드에 걸쳐 구성하거나, **프로세스**로써 기동도 가능
2. 또는 **컨테이너**로써 기동 선택 가능
3. 컨테이너로써 기동 시 컨테이너 오케스트레이션 플랫폼인 쿠버네티스 플랫폼 상에 **Pod**로써 기동
5. Kubernetes Executor만 쿠버네티스에서 운영할 수 있는 건 아니다.
   1. 노드1: scheduler/Redis
   2. 노드2/3: Worker
   3. 노드4: Postgres/Webserver(웹서버 여러개인 경우 L4로 로드밸런싱)
   4. 노드5: Webserver / Triggerer

### Cloud SaaS 서비스
- 3대 Cloud Provider인 AWS(MWAA), GCP(Cloud Composer), MS Azure에 Airflow(Azure Data Factory Managed Airflow) 서비스를 완전 관리형으로 제공
- 공통점 : 각 CSP에서 제공하는 쿠버네티스 플랫폼 위에 Airflow를 실행 & Celery Executor 적용

### Flower
- Celery 모니터링하기 위한 파이썬의 라이브러리
- CeleryExecutor를 사용할 때만 사용할 수 있는 airflow 서비스

### Airflow Config 파라미터
- Airflow의 기본 환경설정을 위한 파라미터
- config 파라미터는 airflow.cfg 파일에서 관리 (컨테이너 내 $AIRFLOW_HOME(=/opt/airflow) 디렉토리 내 위치)
- Airflow가 설치된 현 실습환경은 컨테이너 기반이므로 airflow.cfg를 직접 수정 X (휘발성)
- 대신, docker-compose.yaml 파일을 수정하여 airflow.cfg 반영 가능
- airflow.cfg 파일에 존재하는 {key} 파라미터는 docker-compose.yaml에 입력하는 AIRFLOW__{section}__{key} 파라미터와 동일 (파라미터명은 대문자로 작성)
- 전체 config 리스트는 참고 : https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#configuration-reference

### 주요 config 파라미터
#### Core 섹션
| 파라미터 명                     | 설명                                                                 | 기본 값                              |
|-------------------------------|----------------------------------------------------------------------|--------------------------------------|
| `dags_folder`                 | Airflow에서 인식할 dag 폴더, 절대경로로 작성                         | `{AIRFLOW_HOME}/dags`                |
| `plugins_folder`             | Airflow에서 인식할 plugin 폴더, 절대경로로 작성                      | `{AIRFLOW_HOME}/plugins`            |
| `dags_are_paused_at_creation`| DAG 인식시 pause 상태로 로드할 것인지 여부                           | True                                 |
| `executor`                   | Airflow의 기본 executor 지정                                         | SequentialExecutor                   |
| `load_examples`              | Example DAG 출력 여부                                               | True                                 |
| `max_active_runs_per_dag`   | DAG당 동시 수행 가능한 Run 최대 개수                                | 16 (dag에서도 설정 가능)            |
| `max_active_tasks_per_dag`  | DAG당 모든 Run을 통틀어 동시 수행 가능한 Task 최대 개수             | 16 (dag에서도 설정 가능)            |
| `parallelism`                | 스케줄러당 동시 수행할 수 있는 Task의 개수                           | 32 (eg. 스케줄러가 2개라면 64개 가능) |

#### scheduler 섹션
| 파라미터 명              | 설명                                                                                       | 기본 값         |
|--------------------------|--------------------------------------------------------------------------------------------|------------------|
| `dag_dir_list_interval`  | DAG 디렉토리에 DAG 목록 새로고침 주기                                                      | 300 (초)         |
| `min_file_process_interval` | DAG 파일 구문분석 후 반영되기까지의 시간                                                | 30 (초)          |
| `file_parsing_sort_mode` | 스케줄러의 DAG 파싱 시 DAG 파일 정렬 기준<br>(`modified_time`, `random_seeded_by_host`, `alphabetical`) | modified_time    |
| `parsing_processes`      | DAG 구문 분석을 위한 프로세스의 개수 지정                                                  | 2                |

#### Celery/Webserver 섹션
| 파라미터 명                    | 설명                                                           | 기본 값 |
|-------------------------------|----------------------------------------------------------------|---------|
| `worker_concurrency`          | Celery worker 당 동시 수행 가능한 Task의 최대 개수             | 16      |
| `expose_config`               | Admin - config 메뉴에 config 파라미터를 보이게 할 것인지 유무 | False   |
| `hide_paused_dags_by_default` | Pause된 DAG을 숨김처리할 것인지 유무                           | False   |

#### Parallelism & worker_concurrency 파라미터 이해
- Parallelism(Scheduler 당 동시수행 task 수) / Worker_concurrency (Worker 당 동시 수행 task 수)
- 노드 6 개 중 2개가 scheduler / 4개가 worker인 상황에서 동시에 수행될 수 있는 task 개수를 최대 10,000개로 설정하려면?
  - 10000 = 2 * parallelism = 4 * worker_concurrency
  - parallelism = 5000, worker_concurrency = 2500