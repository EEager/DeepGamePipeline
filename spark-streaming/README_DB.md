# DB는 아래와같이 구성합니다.

| 목적     | 역할                           | 저장소           | 소비 주체                   |
| ------ | ---------------------------- | ------------- | ----------------------- |
| 운영용 집계 | 실시간 랭킹, 세션 결과 계산             | MySQL         | 게임 클라이언트 (즉시 표시)        |
| 분석용 집계 | 장기 통계, 시즌별 지표, 시각화용 분석       | PostgreSQL DW | Superset, Metabase, 분석툴 |
| 비정형 로그 | 강화학습 상태, 행동, 보상 데이터 (JSON 등) | S3 or MongoDB | AI 학습 파이프라인             |


서버로 부터 실시간 로그를 받아 카프카에 producer로 저장할것입니다. 서버 DB쪽에서는 spark 스트리밍으로 1)운영용 DB와 2)분석용 DB 3)비정형데이터를(추후) 실시간으로 DB에 저장합니다. 
1. 운영용 집계 DB : 서버로 부터 실시간 로그를 받아, 게임 종료시, player_summary또한 저장할 예정
 - mySQL
2. 분석용 집계 DB : 스타스키마 구조이며, 시각화 툴과 연결할 예정입니다. 
 - postgreSQL 


해당 DB를 선택한 이유는 아래와 같습니다. 

좋은 질문이야! 운영용 DB로 MySQL을, 분석용 DW로 PostgreSQL을 쓰는 이유는 다음과 같은 실무적 고려에서 비롯돼:

---

### 왜 MySQL은 운영용(Operational DB)인가?

운영용 DB는 빠른 응답속도, 높은 쓰기 처리량, 낮은 지연이 중요해.

| 항목      | 이유                                     |
| ------- | -------------------------------------- |
| 응답 속도   | 게임 중 실시간으로 사용자 상태(HP/Rank 등)를 읽고 쓰기 위함 |
| 경량      | MySQL은 상대적으로 가볍고 설치/운영이 쉬움             |
| 쓰기 속도   | 쓰기 중심의 구조에 적합 (예: 실시간 로그 INSERT)       |
| 트랜잭션 처리 | MySQL의 InnoDB 엔진은 높은 트랜잭션 성능 제공        |

> 즉, 게임 서버가 빠르게 읽고 쓰는 데는 MySQL이 유리함

---

### 왜 PostgreSQL은 분석용(DW)인가?

분석용 DB(DW)는 쿼리 최적화, 복잡한 조인, 풍부한 함수 지원, SQL 호환성이 중요해.

| 항목              | 이유                                                    |
| --------------- | ----------------------------------------------------- |
| OLAP 적합         | PostgreSQL은 복잡한 쿼리 처리에 뛰어남 (JOIN, GROUP BY, 윈도우 함수 등) |
| JSON, GIS 등 확장성 | 복잡한 데이터 모델링/확장성 좋음                                    |
| 외부 BI 도구 연동     | Superset, Metabase 등과 연동이 뛰어남                         |
| Star Schema에 유리 | 다차원 분석용 테이블 구성에 적합                                    |

> 즉, 로그 분석·통계용 DB는 PostgreSQL이 유리함

---

### ✅ 지금 구성은 이렇게 보면 돼:

* MySQL → `실시간 운영 상태 저장`

  * player\_summary
  * current\_health, current\_position 등

* PostgreSQL (DW) → `분석/통계용 로그 저장`

  * logs\_move, logs\_attack, logs\_attack\_hit, logs\_heal, logs\_damage\_taken, session\_logs 등
  * Star Schema 기반

---
