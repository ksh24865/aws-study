## Amazon MSK

쇼핑몰 APP에서 웹 훅이 실행될 때마다 Amazon MSK에 적재하는 데이터 스트리밍 데모

### 개요

쇼핑몰 APP에서 웹 훅 발생 시 이벤트 발생 정보를 API Gateway로 POST 전송한다.

API Gateway를 통해 해당 POST명령은 VPC내의 Kafka-REST client로 전송된다.

Kafka-REST client는 전송받은 메시지를 Kafka Cluster에 적재한다.

![Untitled](https://user-images.githubusercontent.com/55729930/122361270-0de1aa80-cf92-11eb-84f5-13395716bc92.png)

### MSK 클러스터 생성

[https://docs.aws.amazon.com/ko_kr/msk/latest/developerguide/getting-started.html](https://docs.aws.amazon.com/ko_kr/msk/latest/developerguide/getting-started.html)

상단 링크접속 후 튜토리얼의 5단계(토픽 생성)까지만 진행한다.

### Kafka REST 프록시 구성

1. 사전준비
- 아래 명령어를 통해 BootstrapBrokerString을 얻는다.

```bash
aws kafka get-bootstrap-brokers --region <본인region> --cluster-arn <카프카 클러스터 arn>
```

- BootstrapBrokerString과 MSK 클러스터 생성 단계에서 얻었던 ZooKeeperConnectionString을 기록해둔다.

2. Kafka 클라이언트 Amazon EC2 인스턴스에 (ssh 등)연결

3. Kafka-REST client 설치

- confluent 설치
    - REST-API로 동작이 가능한 Kafka client라고 보면 됨.

```bash
curl -O [http://packages.confluent.io/archive/6.2/confluent-6.2.0.tar.gz](http://packages.confluent.io/archive/6.2/confluent-6.2.0.tar.gz)
```

- kafka client 설치
    - 실제 스트리밍 서비스 시에는 필요 없음 (confluent가 client기능 수행)
    - 본 데모에서는 consumer를 통해 Kafka에 적재된 데이터를 확인하기 위해 사용

```bash
wget https://archive.apache.org/dist/kafka/2.6.1/kafka_2.13-2.6.1.tgz
```

4. Kafka REST 서버와 Amazon MSK 클러스터 연결

- [kafka-rest.properties](http://kafka-rest.properties) 설정

    ```bash
    vi /home/ec2-user/confluent-6.2.0/etc/kafka-rest/kafka-rest.properties

    # 사전준비 단계에서 기록한 값들 입력
    zookeeper.connect= ZooKeeperConnectionString
    bootstrap.servers= BootstrapBrokerString
    ```

5. API Gateway 생성

아래 사진을 참고하여 생성

![Untitled (1)](https://user-images.githubusercontent.com/55729930/122361372-24880180-cf92-11eb-87aa-ea8a52eb876b.png)

![Untitled (2)](https://user-images.githubusercontent.com/55729930/122361380-2651c500-cf92-11eb-99a1-59c071563e64.png)

![Untitled (3)](https://user-images.githubusercontent.com/55729930/122361388-28b41f00-cf92-11eb-9a83-c87e1f05a316.png)

회색 부분은 client EC2 인스턴스의 public DNS

6. 생성한 API를 배포 한 후 호출 URL 을 기록

이것을 웹훅 발생 시 전송 URL로 사용

### RESULT

- postman을 사용하여 테스트(테스트 목적으로 짧은 메세지 POST)

![Untitled (4)](https://user-images.githubusercontent.com/55729930/122361399-2a7de280-cf92-11eb-96c8-e8b47352603c.png)
- Kafka consumer에서 결과 확인

<img width="738" alt="_2021-06-17__1 50 37" src="https://user-images.githubusercontent.com/55729930/122361689-73359b80-cf92-11eb-8290-1f161e89c043.png">


---

### 키네시스 프로듀서
```
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
        StreamName='KinesisTutorialStream' #만든 Kinesis 스트림 이름을 넣는다
    )
    print(response)
    return {
        'statusCode': 200,
        'body': response
    }
```
### 키네시스 컨슈머
```
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


---
<br/><br/><br/><br/><br/><br/>
# memo

https://docs.aws.amazon.com/ko_kr/msk/latest/developerguide/create-vpc.html
<br/>

{
    "ClusterInfo": {
        "EncryptionInfo": {
            "EncryptionInTransit": {
                "ClientBroker": "TLS", 
                "InCluster": true
            }, 
            "EncryptionAtRest": {
                "DataVolumeKMSKeyId": "arn:aws:kms:us-east-2:638435461849:key/3aad2414-5e3b-42fb-a7a2-dc790f93c84b"
            }
        }, 
        "BrokerNodeGroupInfo": {
            "BrokerAZDistribution": "DEFAULT", 
            "ClientSubnets": [
                "subnet-004e3c4cee0cd58c8", 
                "subnet-0d5d47ba9d634231d", 
                "subnet-0b6e4ccf5264450ba"
            ], 
            "StorageInfo": {
                "EbsStorageInfo": {
                    "VolumeSize": 1000
                }
            }, 
            "SecurityGroups": [
                "sg-08b4c66ccf55a000f"
            ], 
            "InstanceType": "kafka.m5.large"
        }, 
        "ClusterName": "AWSKafkaTutorialCluster", 
        "CurrentBrokerSoftwareInfo": {
            "KafkaVersion": "2.2.1"
        }, 
        "Tags": {}, 
        "CreationTime": "2021-06-16T02:26:55.75Z", 
        "NumberOfBrokerNodes": 3, 
        "ZookeeperConnectString": "z-1.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2.amazonaws.com:2181,z-2.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2.amazonaws.com:2181,z-3.awsk
afkatutorialcluste.1y8759.c3.kafka.us-east-2.amazonaws.com:2181", 
        "State": "ACTIVE", 
        "CurrentVersion": "K3P5ROKL5A1OLE", 
        "ClusterArn": "arn:aws:kafka:us-east-2:638435461849:cluster/AWSKafkaTutorialCluster/0615f726-77ba-42ab-a718-77b5a0519207-3", 
        "EnhancedMonitoring": "PER_TOPIC_PER_BROKER", 
        "OpenMonitoring": {
            "Prometheus": {
                "NodeExporter": {
                    "EnabledInBroker": false
                }, 
                "JmxExporter": {
                    "EnabledInBroker": false
                }
            }
        }
    }
}


<br/>
{
    "BootstrapBrokerStringTls": "b-1.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2.amazonaws.com:9094,b-2.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2.amazonaws.com:9094,b-3.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2.amazonaws.com:9094"
}

<br/>

```
./kafka-console-producer.sh --broker-list "b-1.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2. amazonaws.com:9094,b-2.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2.amazonaws.com:9094,b-3.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2.amazonaws.com:9094" --producer.config client.properties --topic AWSKafkaTutorialTopic

./kafka-console-consumer.sh --bootstrap-server "b-1.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2.amazonaws.com:9094,b-2.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2.amazonaws.com:9094,b-3.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2.amazonaws.com:9094" --consumer.config client.properties --topic AWSKafkaTutorialTopic --from-beginning
```

<br/>

https://aws.amazon.com/ko/blogs/big-data/govern-how-your-clients-interact-with-apache-kafka-using-api-gateway/
<br/>
https://docs.confluent.io/3.0.0/kafka-rest/docs/index.html

<br/>
confluent-6.2.0
curl -O http://packages.confluent.io/archive/6.2/confluent-6.2.0.tar.gz
