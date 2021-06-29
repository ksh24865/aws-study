## Kinesis Producer

- Cafe24에서 온 웹훅을 기준삼아서 레코드를 넣었다.
 
```python
import json
import boto3

client = boto3.client('kinesis')
def lambda_handler(event, context):
    # TODO implement
    response = client.put_records(
				#해당 데이터를 JSON 포맷으로 변환시켜 넣는다.
        Records=[
            {
                'Data': json.dumps(event['resource']),
                'ExplicitHashKey': '0',#임의의 해쉬값을 넣는다.
                'PartitionKey': str(event['event_no'])
            },
        ],
        StreamName='laplace_kinesis' #만든 Kinesis 스트림 이름을 넣는다
    )
    print(response)
    return {
        'statusCode': 200,
        'body': response
    }
```

- 결과
    - 해당 레코드를 넣은 뒤 얻은 response 값

<img width="1269" alt="Untitled (7)" src="https://user-images.githubusercontent.com/55729930/122769264-63de8700-d2df-11eb-9ccd-cf16304a4f54.png">

## Kinesis Consumer

```python
import json
import boto3

client = boto3.client('kinesis')
def lambda_handler(event, context):
    # TODO implement
    response = client.list_shards(StreamName = 'KinesisTutorialStream')
		#shard_id는 여기서 리스트 말고 특정 아이디로만 이용해서 데이터를 뽑는다.
    shard_id = response['Shards'][0]['ShardId']
    starting_seq_num = response['Shards'][0]['SequenceNumberRange']['StartingSequenceNumber']
    #Record를 얻기 전 Shard Iterator 먼저 얻는다.
    response = client.get_shard_iterator(
        StreamName='KinesisTutorialStream',
        ShardId = shard_id,
        ShardIteratorType='AT_SEQUENCE_NUMBER',
        StartingSequenceNumber=starting_seq_num
    )
    
    response = client.get_records(ShardIterator=response['ShardIterator'])
    
    #원한 레코드 리스트를 얻은 후 이벤트만 뽑아서 프린트한다.
    res=[]
    
    for data in response["Records"]:
        if data is None:
            break;
        #print(data['Data'].decode())
        res.append(data['Data'])

    return {
        'statusCode': 200,
        'body': res
    }
```

- 결과
    - 최종 response 결과물에서 이벤트만 뽑아 프린트한 로그
    <img width="1456" alt="Untitled (8)" src="https://user-images.githubusercontent.com/55729930/122769468-8e304480-d2df-11eb-8732-e68c5b0f8dd0.png">



### 실시간으로 Kinesis에서 Query 탐색

Kinesis Data Analytics 애플리케이션을 통해 Kinesis내의 데이터를 실시간 (2~10초간격)으로 데이터를 지속적으로 읽고 분석할 수 있다.

- 하나의 인애플리케이션 스트림(SOURCE_SQL_STREAM_001)으로부터 레코드를 읽고 이를 또 다른 인애플리케이션 스트림(DESTINATION_SQL_STREAM)에 기록한다.
- DESTINATION_SQL_STREAM의 데이터를 쿼리하여 탐색한다.
- 타 DB 및 app 연동 없이 Kinesis Data Analytics에 내장된 기능 만으로 수행 가능하다.

![Untitled (9)](https://user-images.githubusercontent.com/55729930/122769387-7bb60b00-d2df-11eb-9bf9-c28610565d5e.png)
- Kinesis의 data stream을 SQL쿼리하여 그 결과를 S3에 저장
    - 필요한 경우 해당 Lambda가 전처리 수행 가능
        - 시간관련 데이터를 sql에서 timestamp로 읽을 수 있도록 전처리 필요해 보임
    - case1: 저장 할 때 마다 해당 새로운 json파일 생성
        - Lambda code

        ```python
        import json
        import datetime
        import boto3 
        def lambda_handler(event, context):
            bucket = 'laplace-test'
            file_name = str(datetime.datetime.now())[:-7]
            result = upload_file_s3(bucket, 'log/' + file_name + '.json', event)

            if result:
                return {
                    'statusCode': 200,
                    'body': json.dumps("upload success")
                }
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps("upload fail")
                }

        def upload_file_s3(bucket, file_name, file):
            encode_file = bytes(json.dumps(file).encode('UTF-8'))
            s3_resource = boto3.resource('s3')
            try:
                s3_resource.Object(bucket, file_name).put(Body=encode_file)
                #s3.put_object(Bucket=bucket, Key=file_name, Body=encode_file)
                return True
            except:
                return False
        ```

    - S3에 저장된 logs

        ![image](https://user-images.githubusercontent.com/55729930/123809884-f1982300-d92c-11eb-87dd-d1c5d23a526e.png)

    - Athena로 s3의 logs 쿼리

        ```sql
        SELECT * FROM "log_db"."logs" limit 5;
        ```

        ![image](https://user-images.githubusercontent.com/55729930/123809925-f8269a80-d92c-11eb-9675-46f73f4cfe15.png)
    - case2: 한 시간 간격으로 새로운 파일 생성
        - kinesis로 데이터 적재 시 해당 시간을 의미하는 json파일에 추가됨.
        - Lambda code

        ```python
        import json
        import datetime
        import boto3 

        client = boto3.client('kinesis')
        s3 = boto3.client('s3')

        def lambda_handler(event, context):
            
            bucket = 'laplace-test'
            file_name = str(datetime.datetime.now())[:-13]+'.json'
            print(file_name)
            try:
                obj = s3.get_object(Bucket= bucket, Key= 'log/' + file_name)
            except:
                obj = []
            else:
                obj = json.load(obj['Body'])
            obj.append(event)
            result = upload_file_s3(bucket, 'log/' + file_name, obj)
            if result:
                return {
                    'statusCode': 200,
                    'body': json.dumps("upload success")
                }
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps("upload fail")
                }

        def upload_file_s3(bucket, file_name, file):
            encode_file = bytes(json.dumps(file).encode('UTF-8'))
            s3_resource = boto3.resource('s3')
            try:
                s3_resource.Object(bucket, file_name).put(Body=encode_file)
                #s3.put_object(Bucket=bucket, Key=file_name, Body=encode_file)
                return True
            except:
                return False
        ```

        - S3에 저장된  logs

        ![image](https://user-images.githubusercontent.com/55729930/123809977-04125c80-d92d-11eb-938f-add7d15af2e7.png)

        - Athena로 s3의 logs 쿼리

        ```sql
        SELECT * FROM "log_db"."logs2" limit 5;
        ```

        ![image](https://user-images.githubusercontent.com/55729930/123810037-0ffe1e80-d92d-11eb-8771-6263632e30c4.png)

    - lambda 대신에 firehose를 이용해서도 s3에 저장 가능 (전처리는 불가능)
