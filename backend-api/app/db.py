# app/db.py
import mysql.connector
import os

# 환경변수로 dev / docker 구분
mode = os.environ.get("MODE", "dev")

if mode == "dev":
    mysql_host = "localhost"
elif mode == "docker":
    # Docker Compose 환경이면 서비스 이름 (mysql)을 바라봐야 한다
    mysql_host = os.environ.get("MYSQL_HOST", "mysql")
else:
    raise Exception("Invalid MODE. Set MODE=dev or MODE=docker.")

def get_connection():
    return mysql.connector.connect(
        host=mysql_host,
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", "root"),
        database=os.environ.get("MYSQL_DATABASE", "gamelogs"),
    )
