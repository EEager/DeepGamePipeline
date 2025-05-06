from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
import mysql.connector

# MySQL 연결
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="gamelogs"
    )
    return connection

# 플레이어 요약 조회 API
def player_summary(request):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM player_summary")
    result = cursor.fetchall()
    cursor.close()
    connection.close()

    return JsonResponse(result, safe=False)
