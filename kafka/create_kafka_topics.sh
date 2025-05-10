#!/bin/bash

KAFKA_CONTAINER_BIN_DIR=~/workspace/GSBE/kafka/bin
BOOTSTRAP_SERVER=localhost:9092

TOPICS=(
  game-move
  game-attack
  game-heal
  game-meta
)

echo "▶ Kafka 토픽 생성 시작..."

for TOPIC in "${TOPICS[@]}"; do
  echo "  → Creating topic: $TOPIC"
  $KAFKA_CONTAINER_BIN_DIR/kafka-topics.sh \
    --create \
    --if-not-exists \
    --topic "$TOPIC" \
    --bootstrap-server "$BOOTSTRAP_SERVER" \
    --partitions 3 \
    --replication-factor 1
done

echo -e "\n✅ 생성된 Kafka 토픽 목록:"
$KAFKA_CONTAINER_BIN_DIR/kafka-topics.sh \
  --list \
  --bootstrap-server "$BOOTSTRAP_SERVER"
