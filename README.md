# aws-study
우분투 20.04 기준 작성 (추후 mac 기준 추가 예정)

#### 버킷 만들기
콘솔 이용하면 쉬움



#### layer를 이용해 Python 모듈을 AWSlambda 내에 import하는 법
```
# 도커 실행
mkdir layer_pandas
cd layer_pandas
mkdir python
docker run --rm -it -v $PWD/python:/layer amazonlinux:1 bash

# 여기서부터는 Docker 이미지에서 실행하는 내용이다. 
yum install -y python38             
cd layer
python3 -m pip install pandas -t .      # Pandas와 의존성 있는 라이브러리를 /layer에 설치한다.
rm -r *.dist-info __pycache__           # 필요 없는 파일을 지운다.
exit                                    # 컨테이너를 종료한다. 

# Layer를 zip 파일로 만든다. (zip파일 내부는 Python/* 형식이어야 함)
zip -r layer_pandas.zip .
```

#### Timeout 늘리는 법
- lambda 함수의 기본 제한시간은 3초이지만, 큰 파일을 df로 생성하는 경우 많은 시간이 필요하다. 따라서 제한시간을 20초로 늘린다.
    - 구성 -> 일반구성 -> 편집 -> 제한 시간 -> 20초
- df를 sql로 저장하는 경우 더욱 큰 시간이 필요하다 제한시간을 최대로 늘린다.
#### IAM 
todo
##### 계정생성
* https://console.aws.amazon.com/iam/ 접속 - 사용자 - 사용자 추가
* 사용자 추가
    * 사용자 이름 설정
    * AWS 액세스 유형 
        * 프로그래밍 방식 액세스 설정
    * 권한설정 
        * 그룹에 사용자 추가 후 그룹 설정 (그룹 추가 확인)
    * 사용자 만들기
        * 성공 후 액세스 키 ID 및 비밀 액세스 키 기록

* 그룹 추가
    * 그룹 이름 지정
    * `AmazonS3FullAccess`, `AWSLambda_FullAccess` 권한 추가
    * 그룹 만들기

#### AWS init
todo 
##### Install
* install
```
$ curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
$ unzip awscliv2.zip
$ sudo ./aws/install
또는
$ sudo apt  install awscli

$ aws --version //설치확인

```
* aws configure
```
$ aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE // 생성한 사용자 액세스 키 ID
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY // 생성한 사용자 비밀 액세스 키
Default region name [None]: us-east-2 // lambda 및 s3 등의 region
Default output format [None]:  // 공백
```



#### Lambda
##### 웹 콘솔에서 Lambda 만들기
    - 함수 생성 -> 블루프린트 사용 체크 -> hello-world-python 검색 후 체크 후 구성 -> 이름 지정 후 함수 생성
##### cli 환경에서 lambda 함수 배포

* 현재 aws 버전 체크
```
$ aws --version 
```
* AWS 리소스에 액세스할 수 있는 권한을 제공하는 실행 역할 생성
```
$ aws iam create-role --role-name lambda-ex --assume-role-policy-document file://trust-policy.json
또는
$ aws iam create-role --role-name lambda-ex --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
```

* 역할에 권한 추가
```
$ aws iam attach-role-policy --role-name lambda-ex --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

* test 함수 생성
```
# test.py
import json

print('Loading function')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    res = "test complete !! your value = " + event['key'] + "\n"
    return res  # Echo back the first key value

```
* 배포 패키지 생성
```
$ zip test.zip test.py
```

* lambda 함수 생성 및 배포
```
$ aws lambda create-function --function-name test-function \
--zip-file fileb://test.zip --handler test.lambda_handler --runtime python3.8 \
--role arn:aws:iam::638435461849:role/tester-ROLE
```

* lambda 함수 사용 테스트
```
// 함수 실행 후 받은 응답 내용을 test_out에 저장
$ aws lambda invoke --function-name test-function --payload '{"key": "seongho"}' test_out --log-type Tail

$ cat test_out 
```
* 계정의 Lambda 함수 목록 표시
```
$ aws lambda list-functions --max-items 10
```

* 함수 이름으로 Lambda 함수 조회
```
$ aws lambda get-function --function-name test-function
```

* Lambda 함수 삭제
```
$ aws lambda delete-function --function-name test-function
```


##### read excel 활용 예시
```
import json
import pandas as pd
import boto3
import os
from io import BytesIO
from io import StringIO
from sqlalchemy import create_engine
import pymysql
# import numpy as np
import matplotlib.pyplot as plt
print('Loading function')

s3 = boto3.client('s3') 


def lambda_handler(event, context):
    
    
    #s3.create_bucket(Bucket='testkimseonghohoho2')
    #버킷 생성
    # location = {'LocationConstraint': 'us-east-2'}
    # s3.create_bucket(Bucket='testkimseonghohoho2',CreateBucketConfiguration=location)
    # 버킷 리스트 출력
    # response = s3.list_buckets()
    # print(response['Buckets'])
    
    # 버킷, 키, 시트를 테스트 시 event로 받을 수도 있음
    bucketName = event['key1'] # 'laplace-test' 
    keyName = event['key2'] # 'input/superstore.xls'
    sheet = event['key3'] # 'Orders'
    obj = s3.get_object(Bucket= bucketName, Key= keyName)
    # pd.read_excel('경로/파일명.xlsx', sheet_name = '시트명')
    df = pd.read_excel(BytesIO(obj['Body'].read()),sheet_name=sheet)
    
    # df 조작
    #df = df[df['Region']=='South']
    #df = df[df['Sales'] >= df['Sales'].mean()]
    #df = df['State'].value_counts().sort_index()
    #df = df.reindex(columns = ['Customer Name','State','Product Name'])
    
    #val = df['Sales'].sum()
    #val = df['Sales'].mean()
    
    # plt
    #hist = plt.hist(df['Sales'])
    #plt.xlabel("Birth weight (in pounds)")
    #plt.ylabel("Sales")
    #plt.show()
    #plt.close()
    
    # df 생성 시 자동으로 0~n으로 인덱스 지정됨, Row ID를 인덱스로 재지정
    #df=df.set_index('Row ID')
    
    # df를 csv버퍼에 csv로 저장
    #csv_buffer = StringIO()
    #df.to_csv(csv_buffer)
    
    #s3에 csv 저장
    #s3_resource = boto3.resource('s3')
    #s3_resource.Object(bucketName, 'output/superstore.csv').put(Body=csv_buffer.getvalue())
    
    print(df.head()) # 데이터가 너무 많아 헤드만 출력
    #print(val)
    
    # return값을 json으로 주기 위해 parse
    #result = df.to_json(orient="records")
    #parsed = json.loads(result)
    
    #s3에 json 저장
    #s3_resource = boto3.resource('s3')
    #s3_resource.Object(bucketName, 'output/superstore.json').put(Body=(bytes(json.dumps(parsed).encode('UTF-8'))))
    
    #RDS(MySQL)에 저장
    #db_connection_str = 'mysql+pymysql://admin:1q2w3e4r@laplace-test-db.c1ijdymnce3n.us-east-2.rds.amazonaws.com/superstore'
    #db_connection = create_engine(db_connection_str)
    #conn = db_connection.connect()
    #df.to_sql(name=sheet, con=db_connection, if_exists='append',index=False)
    

    return "hi"
    # return parsed 
    
```



#### 파일의 액세스 권한 설정
- 1(안전).
- 정책생성
    - Amazon IAM -> 정책 -> 정책 생성 -> 시각적 편집기 -> 서비스:S3, 작업:수동작업(모든S3작업),리소스:모든리소스 -> 다음다음
- 역할생성
    - Amazon IAM -> 역할 -> 역할 만들기 -> AWS서비스 체크, 사용사례 Lambda체크 -> 다음 -> 생성한 정책과 연결 -> 역할이름 설정 후 만들기
- 역할적용
    - 람다 -> 함수 -> 구성 -> 실행역할 -> 편집 -> 기존역할 : 생성한 역할 -> 저장

- 2(비추).
- lambda 함수가 s3의 파일을 get_object하기 위해서 버킷의 액세스 권한을 오픈해야 한다.
- Amazon S3 -> Bucket -> file클릭 -> 권한 -> ACL(액세스 제어 목록) -> 편집 -> 전부 체크
- Bucket -> 권한 -> 퍼블릭 액세스 차단 편집(버킷 설정) -> 전부

#### S3 메소드
##### import
* import boto3
* s3 = boto3.client('s3') #  S3 Client 생성
##### 버킷 생성
```
location = {'LocationConstraint': 'us-east-2'}
s3.create_bucket(Bucket='버킷이름',CreateBucketConfiguration=location)
```
##### s3로부터 데이터 load
* obj = s3.get_object(Bucket= bucketName, Key= keyName) 
```
bucketName = event['key1'] # 'laplace-test' 
keyName = event['key2'] # 'input/superstore.xls'
sheet = event['key3'] # 'Orders'
obj = s3.get_object(Bucket= bucketName, Key= keyName) # 버킷과 키 이름으로 obj 가져오기
# pd.read_excel('경로/파일명.xlsx', sheet_name = '시트명')
df = pd.read_excel(BytesIO(obj['Body'].read()),sheet_name=sheet) # obj의 body를 읽어 df로 변환
```
```
response = s3.list_buckets() # S3에있는 현재 버킷리스트의 정보를 가져온다. 
print(response['Buckets']) # 버킷리스트 출력
```

##### s3로 데이터 save

```
# DF를 S3에 저장

# CSV
# df 생성 시 자동으로 0~n으로 인덱스 지정됨, Row ID를 인덱스로 재지정
df=df.set_index('Row ID')
csv_buffer = StringIO()
# df를 csv버퍼에 csv로 저장
df.to_csv(csv_buffer)
s3_resource = boto3.resource('s3')
#s3에 저장
s3_resource.Object(bucketName, 'output/superstore.csv').put(Body=csv_buffer.getvalue())

# JSON
# json으로 parse (데이터 많아서 head만)
result = (df.head()).to_json(orient="records")
parsed = json.loads(result)

#s3에 json 저장
s3_resource = boto3.resource('s3')
s3_resource.Object(bucketName, 'df2.json').put(Body=(bytes(json.dumps(parsed).encode('UTF-8'))))
```

#### RDS
* 접속법 
```
$ mysql -u admin --host laplace-test-db.c1ijdymnce3n.us-east-2.rds.amazonaws.com -P 3306 -p

ERROR 2003 (HY000): Can't connect to MySQL server on 이러한 에러문구가 뜬다면 아래의 과정을 시도해본다

AWS의 VPC 콘솔에서 보안그룹을 찾아 클릭
해당 DB 인스턴스의 보안그룹을 찾아 클릭한다
하단의 인바운드 규칙 편집 클릭
소스부분을 무관으로 변경
다시 터미널로 돌아가 아래와같이 입력하면 성공

```
* Lambda에서 RDS로 저장
```
    연결 -> 추가연결구성 -> 퍼블릭 엑세스 가능 -> 예 설정되어있어야 함
    
    db_connection_str = 'mysql+pymysql://admin:1q2w3e4r@laplace-test-db.c1ijdymnce3n.us-east-2.rds.amazonaws.com/superstore'
    db_connection = create_engine(db_connection_str)
    conn = db_connection.connect()
    df.head().to_sql(name=sheet, con=db_connection, if_exists='append',index=False)
    
```

#### EC
 ```
 ssh로 ec에 연결하는 법
 seongho.pem 키파일이 있어야 함(s3 버킷 및 , 우분투pc ~/ec 에 존재
 
 sudo ssh -i "seongho.pem" ubuntu@ec2-18-117-98-143.us-east-2.compute.amazonaws.com
 ```




#### DF to JSON
```
result = (df.head()).to_json(orient="records")
parsed = json.loads(result)
```
