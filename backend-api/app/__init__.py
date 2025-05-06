# app/__init__.py
from flask import Flask
from app.routes.player_summary import player_summary_bp
from app.routes.player_ranking import player_ranking_bp

def create_app():
    app = Flask(__name__)

    # 블루프린트 등록
    app.register_blueprint(player_summary_bp)
    app.register_blueprint(player_ranking_bp)

    return app
