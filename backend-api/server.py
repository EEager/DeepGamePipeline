import os
from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# 환경변수로 dev / docker 구분
mode = os.environ.get("MODE", "dev")

if mode == "dev":
    mysql_host = "localhost"
elif mode == "docker":
    mysql_host = "host.docker.internal"
else:
    raise Exception("Invalid MODE. Set MODE=dev or MODE=docker.")

connection = mysql.connector.connect(
    host=mysql_host,
    user="root",
    password="root",
    database="gamelogs"
)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Game API is running!"})

@app.route("/player_summary", methods=["GET"])
def get_player_summary_all():
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM player_summary")
    result = cursor.fetchall()
    cursor.close()
    return jsonify(result)

@app.route("/player_summary/<int:player_id>", methods=["GET"])
def get_player_summary_by_id(player_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM player_summary WHERE player_id = %s", (player_id,))
    result = cursor.fetchone()
    cursor.close()

    if result is None:
        abort(404, description="Player not found")

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
    
