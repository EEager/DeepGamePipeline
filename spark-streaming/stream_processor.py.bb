from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, to_json, col
from pyspark.sql.types import StructType, StructField, StringType, MapType

# 1. Spark 세션 생성
spark = SparkSession.builder \
    .appName("KafkaSparkStructuredStreaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.3.2,org.apache.spark:spark-token-provider-kafka-0-10_2.13:3.3.2,mysql:mysql-connector-java:8.0.4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Kafka에서 데이터 읽기
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "game-logs") \
    .option("startingOffsets", "latest") \
    .load()

# 3. Kafka 메시지 디코딩
df_decoded = df.selectExpr("CAST(value AS STRING) as json_value")

# 4. JSON 파싱 스키마 정의
schema = StructType([
    StructField("event_type", StringType()),
    StructField("details", MapType(StringType(), StringType()))
])

df_parsed = df_decoded.select(from_json(col("json_value"), schema).alias("data")).select("data.*")



# 5. foreachBatch 함수 정의
def write_to_mysql(df, batch_id):
    df = df.withColumn("details", to_json(col("details")))  # 🛠 details를 JSON 문자열로 변환

    df.write \
      .format("jdbc") \
      .option("url", "jdbc:mysql://localhost:3306/gamelogs") \
      .option("driver", "com.mysql.cj.jdbc.Driver") \
      .option("dbtable", "logs") \
      .option("user", "root") \
      .option("password", "root") \
      .mode("append") \
      .save()

# def write_to_mysql(batch_df, batch_id):
#     batch_df.write \
#         .format("jdbc") \
#         .option("url", "jdbc:mysql://localhost:3306/gamelogs") \
#         .option("driver", "com.mysql.cj.jdbc.Driver") \
#         .option("dbtable", "logs") \
#         .option("user", "root") \
#         .option("password", "root") \
#         .mode("append") \
#         .save()
# 6. Streaming 시작
query = df_parsed.writeStream \
    .foreachBatch(write_to_mysql) \
    .outputMode("append") \
    .start()

query.awaitTermination()
