# app/routes/player_summary.py
from flask import Blueprint, jsonify, request
from app.db import get_connection

player_summary_bp = Blueprint('player_summary', __name__)

@player_summary_bp.route("/player_summary", methods=["GET"])
def get_player_summary():
    sort_by = request.args.get('sort_by', 'player_id')
    order = request.args.get('order', 'asc')
    min_move_count = request.args.get('min_move_count', None)
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT * FROM player_summary"
    conditions = []
    if min_move_count:
        conditions.append(f"move_count >= {min_move_count}")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += f" ORDER BY {sort_by} {order.upper()}"

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return jsonify(result)

@player_summary_bp.route("/player_detail/<int:player_id>", methods=["GET"])
def get_player_detail(player_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM player_summary WHERE player_id = %s", (player_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return jsonify(result)
