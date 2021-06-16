
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
    "BootstrapBrokerStringTls": "b-1.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2.
amazonaws.com:9094,b-2.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2.amazonaws.com:
9094,b-3.awskafkatutorialcluste.1y8759.c3.kafka.us-east-2.amazonaws.com:9094"
}

<br/>

https://aws.amazon.com/ko/blogs/big-data/govern-how-your-clients-interact-with-apache-kafka-using-api-gateway/
<br/>
https://docs.confluent.io/3.0.0/kafka-rest/docs/index.html
