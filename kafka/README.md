# kafka
# 카프카관련

### ✅ 자주 쓰는 Kafka 명령어 (Docker 기준)


0. create_kafka_topics.sh 으로 안에 정의한 topic을 만든다. 

1. 토픽 생성 :
```bash
bin/kafka-topics.sh \
--create \
--if-not-exists \
--topic "$TOPIC" \
--bootstrap-server localhost:9092 \
--partitions 3 \
--replication-factor 1
```

2. 토픽 목록 보기:

```bash
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

3. 특정 토픽 설명:

```bash
bin/kafka-topics.sh --describe --topic game-move --bootstrap-server localhost:9092
```

4. 토픽 삭제 (주의! log retention 설정 주의):

```bash
bin/kafka-topics.sh --delete --topic game-move --bootstrap-server localhost:9092
```

5. Kafka 메시지 수동 소비 (consumer test):

--from-beginning 있으면 처음부터 확인 가능
```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic game-move \
  --from-beginning 
```

실시간 --tail 하려면 
```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic game-attack

```

6. Kafka 메시지 수동 전송 (producer test):

```bash
kafka-console-producer.sh \
  --broker-list localhost:9092 \
  --topic game-move
```

7. Docker는 앞에 bin/ 말고 docker exec -i kafka 로 시작. 