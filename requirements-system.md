# 시스템 요구사항 (WSL 환경)

## 필수 소프트웨어

- Java (default-jdk)
- Kafka (Apache Kafka 2.13-3.6.0)

## 설치 방법

1. Java 설치
```bash
sudo apt update
sudo apt install default-jdk -y
```

2. Kafka 다운로드 및 설치
```bash
cd ~
wget https://archive.apache.org/dist/kafka/3.6.0/kafka_2.13-3.6.0.tgz
#wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz //2024년안전버전
tar -xvzf kafka_2.13-3.6.0.tgz
mv kafka_2.13-3.6.0 kafka
```

3. Zookeeper 실행
```bash
cd ~/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties
```
4. Kafka 서버 실행
```bash
cd ~/kafka
bin/kafka-server-start.sh config/server.properties
```
5. Topic 생성 (예: game-logs)
```bash
bin/kafka-topics.sh --create --topic game-logs --bootstrap-server localhost:9092
```

좋아요! Kafka에서 토픽을 확인하거나 관리하는 명령어들을 알려줄게요. 😊


### 🔹 **토픽 확인**
```sh
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```
➡️ **모든 토픽 목록을 확인**하는 명령어입니다.

```sh
bin/kafka-topics.sh --describe --topic game-logs --bootstrap-server localhost:9092
```
➡️ 특정 토픽(`game-logs`)의 **세부 정보(파티션, 복제 등)**를 확인하는 명령어입니다.

---

### 🔹 **토픽 삭제**
```sh
bin/kafka-topics.sh --delete --topic game-logs --bootstrap-server localhost:9092
```
➡️ 토픽을 삭제하는 명령어입니다.  
⚠️ **토픽 삭제가 활성화되어 있어야 합니다.** (`delete.topic.enable=true` 설정 필요)

---

### 🔹 **메시지 확인**
```sh
bin/kafka-console-consumer.sh --topic game-logs --from-beginning --bootstrap-server localhost:9092
```
➡️ **토픽에서 메시지를 소비(읽기)하는 명령어**입니다. `--from-beginning` 옵션을 붙이면 처음부터 메시지를 읽습니다.

```sh
bin/kafka-console-producer.sh --topic game-logs --bootstrap-server localhost:9092
```
➡️ **토픽에 메시지를 추가(생산)하는 명령어**입니다. 입력하면 터미널에서 직접 메시지를 보낼 수 있습니다.

---

### 🔹 **브로커 상태 확인**
```sh
bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```
➡️ **Kafka 브로커의 API 버전 및 지원 기능을 확인**하는 명령어입니다.

-----------------------------------------------------------------------
#Spark 설치. 
pip install pyspark #venv에서 해줘야함 
cd ~


#이렇게 3.3.2로 ✅ 방법: Spark + Hadoop 번들 버전을 받으면 Scala jar들이 포함돼 있다.
cd ~
wget https://archive.apache.org/dist/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz

wget https://downloads.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
wget https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
tar -xvzf spark-3.5.0-bin-hadoop3.tgz
mv spark-3.5.0-bin-hadoop3 spark

- 환경변수 설정 (~/.bashrc에 추가)
echo "export SPARK_HOME=~/spark" >> ~/.bashrc
echo "export PATH=\$PATH:\$SPARK_HOME/bin" >> ~/.bashrc
source ~/.bashrc

- Spark 버전 확인
spark-submit --version
➡ 여기까지 하면 준비 완료!


------------------------------------------
# DW 용 postgreSQL 설치
sudo apt update
sudo apt install postgresql postgresql-contrib
