# 프로젝트 설명
이 프로젝트는 간단한 게임 로그를 Kafka를 통해 수집하고,
Spark Streaming으로 실시간 처리하여 MySQL 및 AWS S3에 저장하며,
Airflow로 데이터 파이프라인을 스케줄링하는 프로젝트입니다.
또한 강화학습 기반 자동 게임 플레이와 데이터 분석 기능을 포함합니다.

## 구성 요소
- game-client : Python 기반 게임 클라이언트 (Pygame)
- game-agent : 강화학습 에이전트
- backend-api : FastAPI 백엔드 서버
- kafka-producer : Kafka 로그 전송기
- spark-streaming : 실시간 데이터 처리
- airflow-dags : 데이터 적재 스케줄 관리
- warehouse-s3 : S3 업로드 스크립트
- mysql : 데이터베이스 스키마
- ml-analysis : ML/AI 데이터 분석 노트북
- dashboard : Streamlit/Superset 기반 데이터 대시보드

