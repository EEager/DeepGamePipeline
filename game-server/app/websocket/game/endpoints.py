from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.game.lobby_manager import lobby_manager
from app.websocket.game.multi_game_manager import multi_game_manager
import asyncio
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user = None
    try:
        while True:
            data = await websocket.receive_json()
            await handle_lobby_message(websocket, data)
                
    except WebSocketDisconnect:
        try:
            logging.debug(f"WebSocket disconnected. User: {user}")
            if user:
                lobby_manager.disconnect(websocket)
                await lobby_manager.broadcast_lobby_state()
        except Exception as e:
            logger.error(f"Error during disconnect handling: {str(e)}", exc_info=True)

async def handle_lobby_message(websocket: WebSocket, data: dict):
    msg_type = data.get("type")
    user = data.get("user")
    
    if msg_type == "join":
        await lobby_manager.connect(websocket, user)
        await lobby_manager.broadcast_lobby_state()
    elif msg_type == "ready":
        lobby_manager.set_ready(websocket, True)
        await lobby_manager.broadcast_lobby_state()
        if lobby_manager.all_ready():
            asyncio.create_task(lobby_manager.start_countdown())
    elif msg_type == "unready":
        lobby_manager.set_ready(websocket, False)
        await lobby_manager.broadcast_lobby_state()
    elif msg_type == "chat":
        player = lobby_manager.get_player_by_websocket(websocket)
        if player:
            await lobby_manager.broadcast({
                "type": "chat", 
                "user": user, 
                "msg": data["msg"],
                "color": player.color
            })
    elif msg_type == "lobby_shoot":
        await lobby_manager.handle_shoot(
            user,
            data["x"],
            data["y"],
            data["vx"],
            data["vy"],
            data["color"]
        )
    elif msg_type == "lobby_move":
        lobby_manager.update_position(websocket, data["x"], data["y"])
    elif msg_type == "ready_multigame":
        logger.debug(f"[ready_multigame] 메시지 수신 - user: {user}")
        player = lobby_manager.get_player_by_websocket(websocket)
        if player:
            player.ready = True
            player.color = data["color"]
            
            # 모든 플레이어가 준비되었는지 확인
            if lobby_manager.all_ready():
                # 로비 매니저 중지
                await lobby_manager.stop()
                
                # 플레이어 데이터를 딕셔너리 형태로 변환
                players_data = [
                    {
                        "user": p.user,
                        "color": p.color
                    }
                    for p in lobby_manager.players.values()
                ]
                game_id = await multi_game_manager.start_game(players_data)
                if game_id:
                    # 멀티게임 시작 메시지 전송
                    await multi_game_manager.broadcast({"type": "start_multigame"})
                else:
                    logger.error("[endpoints] Failed to start multi-game")

async def handle_multi_game_message(websocket: WebSocket, data: dict):
    """멀티게임 메시지 처리"""
    msg_type = data.get("type")
    user = data.get("user")
    
    if not user:
        return
        
    game = multi_game_manager.get_game(user)
    if not game:
        return
        
    if msg_type == "input":
        # 플레이어 입력 처리
        input_data = data.get("input", {})
        game.handle_player_input(user, input_data)
    elif msg_type == "shoot":
        # 총알 발사 처리
        game.handle_shoot(
            user,
            data["x"],
            data["y"],
            data["vx"],
            data["vy"],
            data["color"]
        )
