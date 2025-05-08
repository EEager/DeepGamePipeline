# transformation_processor.py
'''MODE=dev $SPARK_HOME/bin/spark-submit -
-jars ~/workspace/GSBE/mysql-connector-java-8.4.0.jar  --packages org.apache.spark:spark-sql-kafka-0-10_2.13:3.3.2,
org.apache.spark:spark-token-provider-kafka-0-10_2.13:3.3.2  transformation_processor.py
'''

import yaml
from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as _sum, count as _count
import os

# 1. Spark 세션 생성
spark = SparkSession.builder \
    .appName("KafkaMySQLTransformation") \
    .config("spark.jars.packages", "mysql:mysql-connector-java:8.4.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


# 2. Config 파일 로드
# 현재 파일의 위치를 기준으로 절대경로 생성
base_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_path, "../config/transformation_config.yaml")

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# 3. MySQL 연결 설정
mode = os.environ.get("MODE")
if not mode:
    # 디폴트 'dev'로 세팅 (환경변수 없으면)
    os.environ["MODE"] = "dev"
    mode = "dev"
mysql_host = "mysql" if mode == "docker" else "localhost"

if mode == "docker":
    mysql_host = "mysql"
else:
    mysql_host = "localhost"

jdbc_url = f"jdbc:mysql://{mysql_host}:3306/gamelogs"
properties = {
    "user": "root",
    "password": "root",
    "driver": "com.mysql.cj.jdbc.Driver"
}

# 4. 집계 결과 저장 리스트
summaries = []

# 5. config 기반으로 데이터 읽고 집계
for name, table_conf in config.items():
    df = spark.read.jdbc(url=jdbc_url, table=table_conf["table"], properties=properties)
    
    group_by_col = table_conf["group_by"]
    aggs = []
    
    for agg_conf in table_conf["aggregations"]:
        col = agg_conf["column"]
        agg_func = agg_conf["agg"]
        alias = agg_conf["alias"]

        if agg_func == "sum":
            aggs.append(_sum(col).alias(alias))
        elif agg_func == "count":
            aggs.append(_count(col).alias(alias))
        else:
            raise ValueError(f"Unsupported aggregation: {agg_func}")

    summary = df.groupBy(group_by_col).agg(*aggs)
    summaries.append(summary)

# 6. 여러 요약 테이블 조인
from functools import reduce

final_summary = reduce(lambda df1, df2: df1.join(df2, "player_id", "outer"), summaries)

# 7. 결과를 MySQL에 저장
final_summary.write \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", "player_summary") \
    .option("user", "root") \
    .option("password", "root") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .mode("overwrite") \
    .save()

print("✅ Transformation Complete!")

spark.stop()
