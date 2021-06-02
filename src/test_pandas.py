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
    

