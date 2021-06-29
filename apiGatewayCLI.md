# 자동 lambda versioning 및 API 배포

### 1. lambda versioning

`aws lambda update-function-code` 사용 시 자동으로 versioning
 
### 2. API 배포

- api update 및 배포 cli 명령어를 이용하여 만든 실행 shell 파일을 git action에 추가
- lambda의 최신 버전 얻어오기

    ```bash
    aws lambda list-versions-by-function --function-name {람다이름} \
    --query "Versions[-1].[Version]" > latest_ver.txt
    ```

    - example

    ![image](https://user-images.githubusercontent.com/55729930/123808357-a3365480-d92b-11eb-8abb-65d33423e13f.png)


- 최신버전으로 api update

    ```bash
    aws apigateway put-integration --rest-api-id {API_ID} --resource-id {리소스_ID} \
    --http-method GET --type AWS_PROXY --integration-http-method POST \
    --uri arn:aws:apigateway:{지역}:lambda:path/2015-03-31/functions/{람다최신버전arn}/invocations \
    --credentials {apigateway 서비스가 Lambda 함수를 호출하도록 허용하는 정책을 가진 ROLE}
    ```

    - example

        ![image](https://user-images.githubusercontent.com/55729930/123808387-aa5d6280-d92b-11eb-9d90-f1f1d53632ef.png)

        ![image](https://user-images.githubusercontent.com/55729930/123808428-b34e3400-d92b-11eb-8dd2-54a46ab99f6e.png)

- API response 설정( 한 번만 실행하면 돼서 안 해도 될 듯함)

    ```bash
    aws apigateway put-method-response --rest-api-id {API_ID} \
    --resource-id {리소스_ID} --http-method GET \
    --status-code 200 --response-models application/json=Empty
    ```

    - example

        ![image](https://user-images.githubusercontent.com/55729930/123808464-bb0dd880-d92b-11eb-8269-b2839ef9626d.png)

        ![image](https://user-images.githubusercontent.com/55729930/123808485-c234e680-d92b-11eb-8daf-280bded33c42.png)


- 배포

    ```bash
    aws apigateway create-deployment --rest-api-id {API_ID} --stage-name api
    ```

    - example

    ![image](https://user-images.githubusercontent.com/55729930/123808528-cd881200-d92b-11eb-8a11-09b10bd26648.png)

    ![image](https://user-images.githubusercontent.com/55729930/123808560-d37df300-d92b-11eb-9f7d-2e07813cf416.png)

- 최신lambda로 자동 api update하는 shell

    ```bash
    #!/bin/sh
    # api_update.sh

    # 정보 입력
    API_ID="zc4k0oqp3g"
    RSC_ID="diju17"
    REGION="us-east-2"
    AWS_ID="638435461849"
    LAMBDA_ID="tmp_lambda"
    ROLE_ID="tester-ROLE"

    # Lambda의 최신 버전 가져와서 전처리
    VER=$(aws lambda list-versions-by-function --function-name $LAMBDA_ID \
    --query "Versions[-1].[Version]")
    VER=$(echo $VER| tr -d '[ ]"')

    # api update 후 결과 echo
    echo $(aws apigateway put-integration --rest-api-id $API_ID --resource-id $RSC_ID \
    --http-method GET --type AWS_PROXY --integration-http-method POST \
    --uri arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:$AWS_ID:function:$LAMBDA_ID:$VER/invocations \
    --credentials arn:aws:iam::$AWS_ID:role/$ROLE_ID)

    # 배포
    echo $(aws apigateway create-deployment --rest-api-id $API_ID --stage-name api)
    ```

    - example

    ![image](https://user-images.githubusercontent.com/55729930/123808597-dc6ec480-d92b-11eb-8da7-1f8852019217.png)

- 설정

    `aws apigateway put-integration` 명령어에서 설정한 Role의 신뢰관계에 아래 사진과 같이 설정하여 apigateway 권한 부여

    ![image](https://user-images.githubusercontent.com/55729930/123808641-e690c300-d92b-11eb-9a85-bdaa7c3618b2.png)
