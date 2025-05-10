좋아, PostgreSQL 기반 Star Schema 설계를 아래와 같이 구성할게. 이 구조는 향후 분석, 시각화, 리포트 등에 최적화된 형태야.

---

## ✅ 1. Dimension Tables (차원 테이블)

### 1.1 dim\_player

```sql
CREATE TABLE IF NOT EXISTS dim_player (
    player_id SERIAL PRIMARY KEY,
    nickname VARCHAR(50),
    tier VARCHAR(20),
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 1.2 dim\_session

```sql
CREATE TABLE IF NOT EXISTS dim_session (
    session_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES dim_player(player_id),
    game_mode VARCHAR(20),
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);
```

### 1.3 dim\_time

(시간 기반 분석을 위한 표준 테이블 — 날짜, 요일, 주, 월 등)

```sql
CREATE TABLE IF NOT EXISTS dim_time (
    time_id SERIAL PRIMARY KEY,
    event_time TIMESTAMP,
    day_of_week VARCHAR(10),
    day INT,
    week INT,
    month INT,
    year INT
);
```

---

## ✅ 2. Fact Table (사실 테이블)

### 2.1 fact\_game\_log

```sql
CREATE TABLE IF NOT EXISTS fact_game_log (
    log_id SERIAL PRIMARY KEY,
    session_id INT REFERENCES dim_session(session_id),
    player_id INT REFERENCES dim_player(player_id),
    time_id INT REFERENCES dim_time(time_id),
    event_type VARCHAR(50),
    damage INT,
    heal_amount INT,
    x INT,
    y INT
);
```

---

## ✅ 활용 예시

* Superset / Metabase에서 다음과 같은 분석 가능:

  * 시간별/요일별 데미지 합계
  * 사용자 티어별 평균 힐량
  * 게임모드별 세션당 평균 피해량
  * 특정 월간 활동량 히트맵 등

---

원하면 이 쿼리들을 init\_dw\.sql 형태로 저장해줄게.
그리고 Spark가 PostgreSQL로 저장할 때 필요한 접속 문자열이나 포맷도 같이 정리해줄게. 계속 진행할까?
