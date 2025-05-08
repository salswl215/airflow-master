## Airflow Architecture

### Airflow 아키텍처
![](https://oopy.lazyrockets.com/api/v2/notion/image?src=https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F8890293f-0322-40a8-9f75-7b3a9a1452bd%2Fef86c492-57f0-4ab9-82a6-2c3c2d059cc5%2FUntitled.png&blockId=778dbda7-70ab-4b3e-9529-55c90e741a83)
1. Scheduler는 DAG 파일을 파싱 (어떤 Dag, 어떤 task 구성되어 있는지 파싱) & 관련 정보(스케줄 정보, DAG/Task 관계 정보 등)를 메타DB에 저장
2. Scheduler는 task의 start 시간을 확인하여 스케줄 조건이 만족될 경우 워커에게 작업 지시
3. 실제 작업은 Worker에서 이루어지며, DAG 파일을 읽어 들인 후 처리하고, 필요한 경우 메타DB 정보(Variable, Xcom, Connection 등)를 읽음
4. Worker에서 작업을 마친 경우, Scheduler는 처리 결과를 메타DB에 저장
5. Webserver는 UI 제공

### Executor?
- Executor는 Scheduler 프로세스 안에 존재하는 요소이나, **Task 동작하는 환경과 매커니즘**을 Executor라고 할 수 있음
- Executor 종류
  - 확장 불가
    - **Sequential Executor**: 기본 설치 시 선택되며, 한번에 하나의 Task만 실행 가능. DB는 sqlite만
    - **Local Executor**: 한 번에 여러 개의 Task 실행 가능하나, 아키텍처의 수평구조 확장은 불가함
  - 확장 가능
    - **Celery Executor**: Celery라는 비동기 작업 큐를 사용하여 Worker에 분배하고 결과를 관리함. 수평구조 확장이 가능하며 직접 machine을 pooling해서 관리하는 경우 자주 사용
    - **Kubernetes Executor**: k8s pod를 이용해 task 실행 (각 task 실행 시 pod가 배포되어 실행)
- 참고 : https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/index.html

### Celery Executor
- 대표적인 executor로 파이썬의 celery라는 비동기 큐 라이브러리를 사용
- celery는 redis/rabbitMQ 등의 큐를 사용
- Scheduler/Worker는 동일 서버 있을 필요 없기 때문에 수평 확장 가능!

#### 동작 방식
![](https://img1.daumcdn.net/thumb/R800x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FMDDUE%2FbtsI7Nwoc91%2FIqFl041Jdioo2nmHNUjEb1%2Fimg.gif)
1. Scheduler (=Client) > Redis(메시지 브로거) : Task 전달
2. Redis > Celery Worker : Celery 워커가 메시지 브로커 통해 task 전달받아 실행
3. Celery Worker > Backend DB : Task 처리 결과를 지정된 백엔드 DB에 기록 (우리의 경우 Backend DB = Meta DB)
4. Scheduler는 BackendDB에서 Task 처리 결과를 확인 & 메타DB에 task 상태/처리 결과 기록

#### * python celery 동작 방식
> Client는 Message Broker에 task 전달 후 다른 일 가능! task 결과는 backend에서 확인하면 됨
1. Client > Message Broker : Task 전달
2. Message Broker > Celery Worker : Task를 Celery 워커 중 하나로 전달 (여러개 띄울 수 있음)
3. Celery Worker > Backend : Task 처리 결과를 지정된 백엔드에 저장
4. Cleint > Backend : Task 처리결과 확인

![](https://docs.cloud.sdu.dk/_images/celery.png)

### Kubernetes Executor
- Kubernetes를 이용한 task 실행
- 쿠버네티스는 머리에 해당하는 컨트롤 plane, 손에 해당하는 워커노드로 구성
- 배포할 컨테이너들을 그룹화하여 pod라는 이름으로 배포

![](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/_images/arch-diag-kubernetes.png)
1. Airflow의 scheduler는 k8s의 api 서버를 이용해서 pod(task) 생성/배포를 요청
2. k8s scheduler는 워커노드를 선택하여 pod 생성 > airflow task는 pod로써 배포되며 task 마치면 pod는 제거됨
3. Pod는 task 마치면 etcd에 처리 결과 기록 & airflow scheduler는 etcd를 통해 처리 결과 확인 & 메타DB에 저장

#### *Kubernetes 아키텍처
![](https://cdn.hashnode.com/res/hashnode/image/upload/v1673682551681/a65c7c62-463b-49dc-8783-47babbbcef4e.png?auto=compress,format&format=webp)
1. 컨트롤 plane
   - API Server: 명령 수신
   - etcd: 메타DB
   - scheduler : pod 배포 시 어느 노드에 배포할지 결정 (노드 별 리소스, pod 확인하여~)
   - cntr-manager : cluster 전체적으로 관리/모니터링
2. 워커 노드
   - kubelet : api server와 통신하며 health check
   - pod / docker / kube-proxy 로 구성
   - application은 pod에 배포됨에 따라 유저들은 pod에 접속하게 됨
