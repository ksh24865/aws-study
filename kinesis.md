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

- SQL 결과를 Lambda에 전송
    - S3로 저장하는데 이용 가능
	- 인애플리케이션 스트림에 작성되는 모든 것을 Amazon Kinesis 데이터 스트림, Kinesis Data Firehose 전송 스트림 또는 AWS Lambda 함수와 같은 외부 대상에 전송할 수 있음
	- Ex) Kinesis의 data stream을 SQL쿼리하여 그 결과를 S3에 저장
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

		- result
		![image](https://user-images.githubusercontent.com/55729930/122875604-72747f00-d36f-11eb-9f46-be13f9e4d184.png)
	- lambda 대신에 firehose를 이용해서도 s3에 저장 가능 (전처리는 불가능)
