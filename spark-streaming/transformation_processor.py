# transformation_processor.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as _sum, count

# 1. Spark 세션 생성
spark = SparkSession.builder \
    .appName("KafkaMySQLTransformation") \
    .config("spark.jars.packages", "mysql:mysql-connector-java:8.4.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. MySQL 테이블 읽기
jdbc_url = "jdbc:mysql://localhost:3306/gamelogs"
properties = {
    "user": "root",
    "password": "root",
    "driver": "com.mysql.cj.jdbc.Driver"
}

logs_move = spark.read.jdbc(url=jdbc_url, table="logs_move", properties=properties)
logs_attack = spark.read.jdbc(url=jdbc_url, table="logs_attack", properties=properties)
logs_heal = spark.read.jdbc(url=jdbc_url, table="logs_heal", properties=properties)

# 3. 데이터 집계
move_summary = logs_move.groupBy("player_id").agg(count("id").alias("move_count"))
attack_summary = logs_attack.groupBy("player_id").agg(
    count("id").alias("attack_count"),
    _sum("damage").alias("total_damage")
)
heal_summary = logs_heal.groupBy("player_id").agg(
    count("id").alias("heal_count"),
    _sum("heal_amount").alias("total_heal")
)

# 4. Summary 조인
summary = move_summary.join(attack_summary, "player_id", "outer") \
                      .join(heal_summary, "player_id", "outer")

# 5. 결과를 MySQL로 저장
summary.write \
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
