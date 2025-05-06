# app/routes/player_ranking.py
from flask import Blueprint, jsonify
from app.db import get_connection

player_ranking_bp = Blueprint('player_ranking', __name__)

@player_ranking_bp.route("/top_damage_players", methods=["GET"])
def top_damage_players():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT player_id, total_damage
        FROM player_summary
        ORDER BY total_damage DESC
        LIMIT 5
    """)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify({"top_damage_players": result})

@player_ranking_bp.route("/top_heal_players", methods=["GET"])
def top_heal_players():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT player_id, total_heal
        FROM player_summary
        ORDER BY total_heal DESC
        LIMIT 5
    """)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify({"top_heal_players": result})
