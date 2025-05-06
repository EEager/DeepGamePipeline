# airflow-dags/game_logs_pipeline_dag.py

from __future__ import annotations

import pendulum

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

# DAG 정의
with DAG(
    dag_id="player_summary_update",
    default_args={"retries": 1},
    description="Update player_summary table every minute",
    schedule="*/5 * * * *",  # 1분마다 실행
    start_date=pendulum.datetime(2025, 5, 5, tz="Asia/Seoul"),
    catchup=False,
    tags=["player_summary", "transformation"],
) as dag:

    # Transformation 수행 BashOperator
    update_summary = BashOperator(
        task_id="update_player_summary",
        bash_command="cd ~/workspace/GSBE/project-root/spark-streaming && $SPARK_HOME/bin/spark-submit --jars ~/workspace/GSBE/mysql-connector-java-8.4.0.jar --packages org.apache.spark:spark-sql-kafka-0-10_2.13:3.3.2,org.apache.spark:spark-token-provider-kafka-0-10_2.13:3.3.2 transformation_processor.py",
    )

    update_summary
