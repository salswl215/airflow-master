## Custom Operator

### CustomOperator 란
- BaseOperator를 기반으로 직접 만들어 사용할 수 있는 클래스를 제공
- BaseOperator 상속시 두 가지 메서드 재정의 필요(Overriding)
  - (1) def __init__
    - 클래스에서 객체 생성시 객체에 대한 초기값 지정하는 함수
  - (2) def execute(self, context)
    - 생성자로 객체를 얻은 후 execute 메서드를 실행시키도록 되어 있음. 비즈니스 로직은 execute에 구현 필요

### CustomOperator 개발 전 유의할 사항
- BaseOperator를 통해 Custom Operator를 개발하기 전 유의할 사항이 몇 가지 있다. 이 점들을 확인한 뒤 개발을 진행하자.
  - 오퍼레이터 기능이 제대로 정의되어 있는가? 
  - 기존 오퍼레이터로 충분히 대체 가능한가? (가능할 경우 기존 오퍼레이터 사용)
  - 오퍼레이터와 dag의 폴더 위치 확인

### CustomOperator 생성 관련 Airflow 공식 문서 확인

- https://airflow.apache.org/docs/apache-airflow/stable/howto/custom-operator.html#creating-a-custom-operator
```python
from airflow.models.baseoperator import BaseOperator

class HelloOperator(BaseOperator):
    def __init__(self, name: str, **kwargs) -> None:
      ## task_id 등 기본 파라미터가 담겨져있는 **kwargs를 super()함수를 통해 BaseOperator에 전달함
        super().__init__(**kwargs)  
        self.name = name

    def execute(self, context):
        message = f"Hello {self.name}"
        print(message)
        return message
```

- Templating : Jinja 템플릿을 사용하여 연산자를 매개변수화 가능
```python
class HelloOperator(BaseOperator):
    # Template 사용할 파라미터 지정
    template_fields: Sequence[str] = ("name",)

    def __init__(self, name: str, world: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name
        self.world = world

    def execute(self, context):
        message = f"Hello {self.world} it's {self.name}!"
        print(message)
        return message
```