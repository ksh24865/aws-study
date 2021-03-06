- REST API
- lambda proxy integration 사용
- python 3.8 사용
- 프로덕션, 개발로 분리
    - /api/v1 - 프로덕션
    - /api/beta - 개발
- API Gateway 상에서 프로덕션 API, 개발 API 2개 생성
    - lambda는 버전 관리로
    - 시나리오
        - lambda version 1 개발 완료

        ```python
        import json

        def lambda_handler(event, context):
            return {
                'statusCode': 200,
                'body': json.dumps('This is lambda version 1')
            }
        ```

        - 개발계인 beta API에 배포

        ![image](https://user-images.githubusercontent.com/55729930/123807838-2d31ed80-d92b-11eb-93c4-eade4e73bd52.png)

        - 개발계 API 테스트 완료

        ![image](https://user-images.githubusercontent.com/55729930/123807900-3a4edc80-d92b-11eb-913f-01fd6a48f294.png)

        - 프로덕션인 v1 API에 배포

        ![image](https://user-images.githubusercontent.com/55729930/123807933-42a71780-d92b-11eb-9d5b-9e04cca606b1.png)


        - lambda를 업데이트하여 version 2 생성

        ```python
        import json

        def lambda_handler(event, context):
            return {
                'statusCode': 200,
                'body': json.dumps('This is lambda version 2')
            }
        ```

        - 개발계인 beta API에 배포

        ![image](https://user-images.githubusercontent.com/55729930/123807978-4cc91600-d92b-11eb-945c-34a70b8c9b5c.png)

        - 개발계 API 테스트 완료

        ![image](https://user-images.githubusercontent.com/55729930/123808017-53f02400-d92b-11eb-89d4-fcdf1f78929a.png)

        - 이때 프로덕션 API 는 version 1인 lambda를 계속 바라보고 있어야 함

        ![image](https://user-images.githubusercontent.com/55729930/123808068-62d6d680-d92b-11eb-83b6-2136a66d436c.png)
        
        - 프로덕션인 v1 API에 배포 (lambda version 2가 연결됨)

        ![image](https://user-images.githubusercontent.com/55729930/123808102-6bc7a800-d92b-11eb-9dcf-fcbb952d702c.png)

- REST API
- lambda proxy integration 사용
- python 3.8 사용
- 프로덕션, 개발로 분리
    - ~~/api/v1~~    /v1/api - 프로덕션 
    - ~~/api/beta~~     /beta/api - 개발
    - 배포된 stage가 경로명으로 지정되어 api와 stage의 경로 위치를 교환함.
- API Gateway 상에서 프로덕션 API, 개발 API 2개 생성
    - lambda는 버전 관리로
    - 시나리오
        - lambda version 1 개발 완료

            ```python
            import json

            def lambda_handler(event, context):
                return {
                    'statusCode': 200,
                    'body': json.dumps('This is lambda version 1')
                }
            ```

        - 개발계인 beta API에 배포

            ![Untitled](https://user-images.githubusercontent.com/55729930/122768744-dbf87d00-d2de-11eb-8887-a64a58c043d7.png)

        - 개발계 API 테스트 완료

            ![Untitled (1)](https://user-images.githubusercontent.com/55729930/122768742-db5fe680-d2de-11eb-9db0-d12165396e5f.png)


        - 프로덕션인 v1 API에 배포

            ![Untitled (2)](https://user-images.githubusercontent.com/55729930/122768737-dac75000-d2de-11eb-9f2e-2f2f03c29c32.png)

        - lambda를 업데이트하여 version 2 생성

            ```python
            import json

            def lambda_handler(event, context):
                return {
                    'statusCode': 200,
                    'body': json.dumps('This is lambda version 2')
                }
            ```

        - 개발계인 beta API에 배포

            ![Untitled (3)](https://user-images.githubusercontent.com/55729930/122768731-d9962300-d2de-11eb-9680-c1c45b49effe.png)

        - 개발계 API 테스트 완료

           ![Untitled (4)](https://user-images.githubusercontent.com/55729930/122768733-da2eb980-d2de-11eb-89c3-705eee166e7b.png)

        - 이때 프로덕션 API 는 version 1인 lambda를 계속 바라보고 있어야 함

            ![Untitled (5)](https://user-images.githubusercontent.com/55729930/122768724-d7cc5f80-d2de-11eb-8f24-6bf6b1dc171c.png)
        - 프로덕션인 v1 API에 배포 (lambda version 2가 연결됨)
            ![Untitled (6)](https://user-images.githubusercontent.com/55729930/122768746-dc911380-d2de-11eb-9fab-dc096c1b5036.png)
