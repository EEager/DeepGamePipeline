# app/db.py
import mysql.connector
import os

# 환경변수로 dev / docker 구분
mode = os.environ.get("MODE", "dev")

if mode == "dev":
    mysql_host = "localhost"
elif mode == "docker":
    mysql_host = "host.docker.internal"
else:
    raise Exception("Invalid MODE. Set MODE=dev or MODE=docker.")

def get_connection():
    return mysql.connector.connect(
        host=mysql_host,
        user="root",
        password="root",
        database="gamelogs"
    )
