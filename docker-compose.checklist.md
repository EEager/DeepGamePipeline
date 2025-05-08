
# 📌 \[Docker Compose 실행 후 체크사항 요약]

```bash
# Docker Compose 올릴 때 기본 흐름
0. docker ps -a

1. docker-compose up --build

2. docker ps -a 로 모든 컨테이너 상태 확인 (mysql, kafka, zookeeper, spark, backend-api 등)

3. [MySQL 컨테이너에 접속]
   docker exec -it mysql bash
   mysql -u root -p

4. [MySQL 안에서 확인]
   SHOW DATABASES;
   USE gamelogs;
   SHOW TABLES;

5. [정상 체크]
   - gamelogs DB가 있어야 한다.
   - logs_move, logs_attack, logs_heal, logs_transformed, player_summary 테이블이 있어야 한다.

6. [Backend API 정상 연결 확인]
   Postman 등으로 http://localhost:5000/player_summary 호출
   → 200 OK 떠야 정상 (500 에러 = MySQL 연결 문제)

7. [Spark/카프카 정상 여부 확인]
   - spark UI : http://localhost:8080
   - kafka는 별도 브로커/토픽 에러가 없어야 정상
```

---

# 📌 \[도커 사용 시 주의사항 (MySQL 관련)]

```bash
- ⚡ 도커 MySQL 접속은 로컬 mysql 명령어랑 다름
  (sudo mysql -u root -p ❌)

- 반드시 컨테이너 내부로 진입해서 접속
  docker exec -it mysql bash
  mysql -u root -p

- ⚡ docker-compose 실행 시
  기존 볼륨이 있으면 init.sql 은 무시된다.

- 테이블/DB 재생성하려면 반드시
  docker-compose down → docker volume prune → docker-compose up --build
```

---

# 📌 \[오류/이슈 대처 가이드]

| 증상                             | 원인                                 | 조치                                  |
| :----------------------------- | :--------------------------------- | :---------------------------------- |
| USE gamelogs; Unknown database | DB 초기화 안됨                          | docker volume prune 하고 다시 up        |
| 500 Internal Server Error      | backend-api ↔ mysql 연결 실패          | DB명, 테이블명 체크하고 docker-compose 로그 확인 |
| kafka 연결 에러                    | zookeeper/kafka 순서 오류 또는 config 문제 | docker-compose.yml 환경변수 다시 확인       |
| spark-submit 에러                | MODE 설정 잘못 or mysql 연결 오류          | spark-submit 앞에 MODE=dev 명시         |

---

# ✨ 최종 코멘트용 정리문

```python
# Docker-compose 실행 후 점검사항
# - docker ps -a : mysql, kafka, spark, backend-api 정상 기동 확인
# - docker exec -it mysql bash → mysql -u root -p 접속 후
#   USE gamelogs; → 테이블 존재 여부 확인
# - Postman으로 backend-api 정상응답 확인
# - 문제 발생 시 docker-compose down → docker volume prune 후 재시작
# 주의: 로컬 mysql (sudo mysql -u root -p) 이 아니라 도커 mysql 사용해야 함!
```

---

