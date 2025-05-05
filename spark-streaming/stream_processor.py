# stream_processor.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, to_json, col
from pyspark.sql.types import StructType, StructField, StringType, MapType

# 1. Spark 세션 생성
spark = SparkSession.builder \
    .appName("KafkaSparkStructuredStreaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.3.2,org.apache.spark:spark-token-provider-kafka-0-10_2.13:3.3.2,mysql:mysql-connector-java:8.4.0") \
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
def write_to_mysql(batch_df, batch_id):
    if batch_df.isEmpty():
        return

    # details를 펼쳐서 필요한 컬럼 만들기
    df_flat = batch_df.withColumn("player_id", col("details")["player_id"].cast("int")) \
                      .withColumn("target_id", col("details")["target_id"].cast("int")) \
                      .withColumn("damage", col("details")["damage"].cast("int")) \
                      .withColumn("heal_amount", col("details")["heal_amount"].cast("int")) \
                      .withColumn("x", col("details")["x"].cast("int")) \
                      .withColumn("y", col("details")["y"].cast("int"))

    # move 이벤트 처리
    move_df = df_flat.filter(col("event_type") == "player_move")
    if not move_df.isEmpty():
        move_df.select("player_id", "x", "y").write \
            .format("jdbc") \
            .option("url", "jdbc:mysql://localhost:3306/gamelogs") \
            .option("dbtable", "logs_move") \
            .option("user", "root") \
            .option("password", "root") \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .mode("append") \
            .save()

    # attack 이벤트 처리
    attack_df = df_flat.filter(col("event_type") == "player_attack")
    if not attack_df.isEmpty():
        attack_df.select("player_id", "target_id", "damage").write \
            .format("jdbc") \
            .option("url", "jdbc:mysql://localhost:3306/gamelogs") \
            .option("dbtable", "logs_attack") \
            .option("user", "root") \
            .option("password", "root") \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .mode("append") \
            .save()

    # heal 이벤트 처리
    heal_df = df_flat.filter(col("event_type") == "player_heal")
    if not heal_df.isEmpty():
        heal_df.select("player_id", "heal_amount").write \
            .format("jdbc") \
            .option("url", "jdbc:mysql://localhost:3306/gamelogs") \
            .option("dbtable", "logs_heal") \
            .option("user", "root") \
            .option("password", "root") \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .mode("append") \
            .save()

# 6. Streaming 시작
query = df_parsed.writeStream \
    .foreachBatch(write_to_mysql) \
    .outputMode("append") \
    .start()

query.awaitTermination()
