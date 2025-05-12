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
