```
event_no 없애고 resource를 하나의 테이블로 만들어야 함
CREATE EXTERNAL TABLE user_log (
  event_no int,
  resource struct<
    mall_id:string,
    event_shop_no:int,
    product_no:int,
    product_code:string,
    created_date:timestamp,
    updated_date:timestamp,
    product_name:string,
    eng_product_name:string,
    supply_product_name:string,
    model_name:string,
    custom_product_code:string,
    product_condition:string,
    summary_description:string,
    simple_description:string,
    description:string,
    display:string,
    selling:string,
    retail_price:string,
    supply_price:string,
    price:string,
    price_content:string,
    adult_certification:string,
    custom_product_code:string,
    manufacturer_code:string,
    supplier_code:string,
    brand_code:string,
    trend_code:string,
    made_date:timestamp,
    release_date:timestamp,
    origin_place_code:int,
    shipping_scope:string,
    translated:string
  >
) PARTITIONED BY (year int, month int, day int)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
LOCATION 's3://laplace-test/log/'

MSCK REPAIR TABLE cafe24_log;
ALTER TABLE user_log ADD PARTITION (year = 년, month = 월, day = 일) LOCATION 's3://laplace-test/log/'


CREATE EXTERNAL TABLE IF NOT EXISTS log_db.logs (
  `event_no` int,
  `resource` map<string,string> 
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1'
) LOCATION 's3://laplace-test/log/'
TBLPROPERTIES ('has_encrypted_data'='false');
```
