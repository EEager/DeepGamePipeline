# 스파크 관련 자료

1. stream_processor.py
spark-streaming으로 kafka topic에 들어있는 메세지를 읽고(json), SQL에 write하는 스크립트 
```bash
(venv) jjlee@DESKTOP-T4DM29K:~/workspace/GSBE/project-root/spark-streaming$ $SPARK_HOME/bin/spark-submit --jars ~/workspace/GSBE/mysql-connector-java-8.4.0.jar  --packages org.apache.spark:spark-sql-kafka-0-10_2.13:3.3.2,org.apache.spark:spark-token-provider-kafka-0-10_2.13:3.3.2 stream_processor.py
```
- 저장되는 DB 
1) 실시간 운영용 DB (mySql)
2) 분석용 DB (PostgreSql -> 추후 superset이나 pandas, matplotlib를 사용)
3) 비정령 데이터나 로그는 S3에 저장할 예정

1) sql의 경우 mysql/init.sql 스크립트 수행을 통해 필요한 db와 table을 만들 수 있다.

확인은 mysql -u root -p 로 sql 들어가서 
```sql
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| gamelogs           |
+--------------------+
```
와 같이 카프카 topic이 있는지 확인하자. 
gamelogs는 아래와 같이 테이블이 설정되어있는지 확인하자 
```sql
mysql> SHOW TABLES;
+--------------------+
| Tables_in_gamelogs |
+--------------------+
| logs_attack        |
| logs_heal          |
| logs_move          |
+--------------------+
4 rows in set (0.00 sec)
```


2. transformation_processor.py
spark 분산처리로 SQL->Spark로 집계작업 수행 하는 스크립트 
```bash
$SPARK_HOME/bin/spark-submit --jars ~/workspace/GSBE/mysql-connector-java-8.4.0.jar  --packages org.apache.spark:spark-sql-kafka-0-10_2.13:3.3.2,org.apache.spark:spark-token-provider-kafka-0-10_2.13:3.3.2  transformation_processor.py
```

만약 실행한 이 후 그 결과는 config/transformation_config.yaml 에 정의된 집계 결과가 저장된다 
# config/transformation_config.yaml

logs_move:
  table: logs_move
  group_by: player_id
  aggregations:
    - column: id
      agg: count
      alias: move_count

logs_attack:
  table: logs_attack
  group_by: player_id
  aggregations:
    - column: id
      agg: count
      alias: attack_count
    - column: damage
      agg: sum
      alias: total_damage

logs_heal:
  table: logs_heal
  group_by: player_id
  aggregations:
    - column: id
      agg: count
      alias: heal_count
    - column: heal_amount
      agg: sum
      alias: total_heal