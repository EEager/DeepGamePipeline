# spark-streaming/stream_processor.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, MapType

# 1. SparkSession 생성
spark = SparkSession.builder \
    .appName("KafkaGameLogStreaming") \
    .master("local[*]") \
    .getOrCreate()

# 2. Kafka로부터 스트리밍 읽기
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "game-logs") \
    .option("startingOffsets", "earliest") \
    .load()

# 3. Kafka value는 기본적으로 binary이므로 String으로 변환
df = raw_df.selectExpr("CAST(value AS STRING) as json_str")

# 4. JSON 파싱
schema = StructType() \
    .add("event_type", StringType()) \
    .add("details", MapType(StringType(), StringType()))

parsed_df = df.select(
    from_json(col("json_str"), schema).alias("data")
).select("data.event_type", "data.details")

# 5. 콘솔에 실시간 출력
query = parsed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()
