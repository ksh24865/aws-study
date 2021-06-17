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
        res.append(data['Data'].decode())

    return {
        'statusCode': 200,
        'body': res
    }
```





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
