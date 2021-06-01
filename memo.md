### AWS lambda 를 CLI로 개발하는 방법

- 개발환경
    - Ubuntu(20.04-LTS), python3.8
    - 추후 mac 기준 추가 예정
- IAM 계정생성
    - [https://console.aws.amazon.com/iam/](https://console.aws.amazon.com/iam/) 접속 - 사용자 - 사용자 추가
    - 사용자 추가
        - 사용자 이름 설정
        - AWS 액세스 유형
            - 프로그래밍 방식 액세스 설정
        - 권한설정
            - 그룹에 사용자 추가 후 그룹 설정 (그룹 추가 확인)
        - 사용자 만들기
            - 성공 후 액세스 키 ID 및 비밀 액세스 키 기록
    - 그룹 추가
        - 그룹 이름 지정
        - `AmazonS3FullAccess`, `AWSLambda_FullAccess` 권한 추가
        - 그룹 만들기
- AWS init
    - Install

    ```bash
    $sudo apt  install awscli
    //또는
    $curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    $unzip awscliv2.zip
    $sudo ./aws/install

    $aws --version //설치확인
    // aws-cli/1.18.69 Python/3.8.5 Linux/5.4.0-73-generic botocore/1.16.19
    ```

    - aws configure

    ```bash
    $aws configure
    AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE // 생성한 사용자 액세스 키 ID
    AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY // 생성한 사용자 비밀 액세스 키
    Default region name [None]: us-east-2 // lambda 및 s3 등의 region
    Default output format [None]:  // 공백
    ```

- Lambda
    - 현재 aws 버전 체크

    ```bash
    $aws --version
    ```

    - AWS 리소스에 액세스할 수 있는 권한을 제공하는 실행 역할 생성

    ```bash
    $aws iam create-role --role-name lambda-ex --assume-role-policy-document file://trust-policy.json
    또는
    $aws iam create-role --role-name lambda-ex --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'

    ```

    - 역할에 권한 추가

    ```bash
    $aws iam attach-role-policy --role-name lambda-ex --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

    ```

    - test 함수 배포 1.
    - [test.py](http://test.py/)

    ```python
    # test.py
    import json

    def lambda_handler(event, context):
        #print("Received event: " + json.dumps(event, indent=2))
        res = "test complete !! your value = " + event['key']
        return res  # 테스트 코드

    ```

    - 배포 패키지 생성

    ```bash
    $zip test.zip test.py

    ```

    - lambda 함수 생성 및 배포

    ```bash
    $aws lambda create-function --function-name test-function \\
    --zip-file fileb://test.zip --handler test.lambda_handler --runtime python3.8 \\
    --role arn:aws:iam::638435461849:role/tester-ROLE

    // role의 경우 본인이 생성한 role 사용하였음.

    ```

    - lambda 함수 사용 테스트

    ```bash
    // 함수 실행 후 받은 응답 내용을 test_out에 저장
    $aws lambda invoke --function-name test-function --payload '{"key": "seongho"}' test_out --log-type Tail

    $cat test_out

    ```

    - result

    ![https://s3-us-west-2.amazonaws.com/secure.notion-static.com/f2096606-e6b5-488e-bb75-b43cf154f027/test.jpg](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/f2096606-e6b5-488e-bb75-b43cf154f027/test.jpg)

- test 함수 배포 2.
    - test_pandas.py

```python
# test_pandas.py
import json
import pandas as pd
import boto3
import os
from io import BytesIO

s3 = boto3.client('s3')

def lambda_handler(event, context):

    # print(obj['Body'])
    # 버킷, 키, 시트를 테스트 시 event로 받을 수도 있음
    bucketName = 'laplace-test'
    keyName = 'input/superstore.xls'
    sheet = 'Orders'
    obj = s3.get_object(Bucket= bucketName, Key= keyName)
    # pd.read_excel('경로/파일명.xlsx', sheet_name = '시트명')
    df = pd.read_excel(BytesIO(obj['Body'].read()),sheet_name=sheet)

    # return값을 json으로 주기 위해 parse
    # 데이터가 많아 일단 head만 return하게 하였음
    result = (df.head()).to_json(orient="records")
    parsed = json.loads(result)

    return parsed

```

- 배포 패키지 생성

```bash
$zip test_pandas.zip test_pandas.py

```

- lambda 함수 생성 및 배포

```bash
$aws lambda create-function --function-name test-pandas-function \\
--zip-file fileb://test_pandas.zip --handler test_pandas.lambda_handler --runtime python3.8 \\
--role arn:aws:iam::638435461849:role/tester-ROLE

// role의 경우 본인이 생성한 role 사용하였음.

```

- layer 생성

```bash
$aws lambda publish-layer-version --layer-name my-layer --description "My layer"\\
--content S3Bucket=laplace-test,S3Key=module/layers.zip --compatible-runtimes python3.6 python3.7 python3.8

```

- lambda에 layer 적용

```bash
$ aws lambda update-function-configuration --function-name test-pandas-function \\
--layers arn:aws:lambda:us-east-2:638435461849:layer:my-layer:1

```

- timeout custom

```bash
// lambda 함수의 기본 제한시간은 3초이지만, 큰 파일을 df로 생성하는 경우 많은 시간이 필요하다. 따라서 제한시간을 60초로 늘린다.

$aws lambda update-function-configuration --function-name test-pandas-function --timeout 60

```

- lambda 함수 사용 테스트

```bash
// 함수 실행 후 받은 응답 내용을 test_out에 저장
$aws lambda invoke --function-name test-pandas-function --payload '{"key": "seongho"}' test_out --log-type Tail

$cat test_out

```

- result

    ![https://s3-us-west-2.amazonaws.com/secure.notion-static.com/93debbbb-9349-4cfe-aad2-24278038fee8/test_pandas.jpg](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/93debbbb-9349-4cfe-aad2-24278038fee8/test_pandas.jpg)

    ### AWS EMR을 lambda 사용해서 구동

    - 개발환경
        - Ubuntu(20.04-LTS), python3.8
        - 추후 mac 기준 추가 예정
    - Lmabda로 EMR 실행
        - test_emr.py

        ```python
        #test_emr.py

        import os
        import boto3

        #aws_key = os.environ['AWS_KEY']
        #aws_skey = os.environ['AWS_SKEY']

        def lambda_handler(event, context):
            session = boto3.session.Session(region_name='us-east-2')
            #emr_client = session.client('emr', aws_access_key_id = aws_key, aws_secret_access_key = aws_skey)
            emr_client = session.client('emr')

            response = emr_client.run_job_flow(
                Name='test_emr',
                LogUri='s3://aws-logs-638435461849-us-east-2/elasticmapreduce/', #본인의 log uri
                ReleaseLabel='emr-5.21.0',
                Instances={
                    'InstanceGroups': [
                        {
                            'Name': 'master',
                            'Market': 'SPOT',
                            'InstanceRole': 'MASTER',
                            'InstanceType': 'm4.large',
                            'InstanceCount': 1
                        },
                        {
                            'Name': 'slave',
                            'Market': 'SPOT',
                            'InstanceRole': 'CORE',
                            'InstanceType': 'r3.xlarge',
                            'InstanceCount': 4
                        }],
                    'Ec2KeyName': 'seongho', # 본인의 Ec2KeyName
                    'KeepJobFlowAliveWhenNoSteps': False, #  단계가 없거나 종료되면 EMR이 유지되지 않고 역시 자동 종료됨. 약 7분 정도 실행되는 듯 하다.
                    'TerminationProtected': False,
                    'Ec2SubnetId': 'subnet-2df64d46'#, #본인의 Ec2SubnetId
                    #'AdditionalMasterSecurityGroups': [
                    #    '<additional security group ID>'
                    #]
                },
                Applications=[{
                    'Name': 'Spark'
                }],
                VisibleToAllUsers=False,
                JobFlowRole='EMR_EC2_DefaultRole',
                ServiceRole='EMR_DefaultRole'#,
                '''
                # Spark 단계 추가
                Steps=[{
                    'Name': 'Main',
                    'ActionOnFailure': 'TERMINATE_CLUSTER', # 단계를 실행하다가 실패할 경우에는 TERMINATE_CLUSTER 옵션을 통해서 EMR을 즉시 종료
                    'HadoopJarStep': {
                        'Jar': 'command-runner.jar',
                        'Args': ['spark-submit',
                            '--master', 'yarn', '--deploy-mode', 'client',
                            '--class', 'main class',
                            's3://bucket-name/folder/file.jar'
                        ]
                    }
                }]
                '''
            )
            return response

        ```

        - result

    ![https://s3-us-west-2.amazonaws.com/secure.notion-static.com/5e1f1b9c-e099-48f3-b420-7666b3115576/emr.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/5e1f1b9c-e099-48f3-b420-7666b3115576/emr.png)
