## lambda 모니터링을 위한 X-Ray 

Lambda는 AWS X-Ray와 통합되어 Lambda 애플리케이션을 추적, 디버깅 및 최적화할 수 있다.

### 설정

- 모니터링 하기 위한 Lambda → 구성 → 모니터링 및 운영도구

    ![image](https://user-images.githubusercontent.com/55729930/122875768-a6e83b00-d36f-11eb-86fe-58bc9b3c40f1.png)

- AWS X-Ray → 활성 추적 활성화

![image](https://user-images.githubusercontent.com/55729930/122875788-aea7df80-d36f-11eb-986f-8629aaf3a1ba.png)

### Lambda 작성

- 아래와 같이 코드 작성

```python
import boto3 
import jsonpickle
import logging
import os
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()

client = boto3.client('lambda')
client.get_account_settings()

def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
		# 함수 작성 
		# ~~~~~~~
		# ~~~~~~~
```

- 함수 실행 성공 후 모니터링
    - 모니터링 → 추적정보

    ![image](https://user-images.githubusercontent.com/55729930/122875910-d5feac80-d36f-11eb-81e5-32ca8747330b.png)


    - Service Map → 기록보기

    ![image](https://user-images.githubusercontent.com/55729930/122875818-b9fb0b00-d36f-11eb-8692-69910fdc3bc4.png)

- result

![image](https://user-images.githubusercontent.com/55729930/122875865-cbdcae00-d36f-11eb-8ba7-e6e4da6be4c1.png)

![image](https://user-images.githubusercontent.com/55729930/122875991-ee6ec700-d36f-11eb-8051-5ca5be030c81.png)

## CloudWatch

총 요청, 지연 시간, 오류율 및 기간을 포함하여 기능에 대한 CloudWatch 메트릭 정보 제공
![image](https://user-images.githubusercontent.com/55729930/123387333-a3082300-d5d2-11eb-9357-de07ab77eff7.png)

### 결론

X-Ray는 Lambda의 실행 루트를 추적하여 각 경로에서 소요된 시간과 에러 유무를 확인할 수 있고, CloudWatch는 Lambda의 요청횟수, 지연시간, 오류율 등의 통계지표를 확인할 수 있음.

lambda를 디버깅하기 위해 사용한다면 lambda 실행 도중 어느 경로에서 에러가 발생하거나 실행 시간이 지연되는지 확인할 수 있는 X-Ray를 사용하는 것이 합리적이라고 생각함.
