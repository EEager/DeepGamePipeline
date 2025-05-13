from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import LobbyManager #game_world, multi_game_loop, 

#from app.websocket.manager import queue_input, process_inputs
import asyncio
import logging

router = APIRouter()
manager = LobbyManager()
logger = logging.getLogger(__name__)

@router.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user = None
    in_multigame = False
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type == "join":
                user = data["user"]
                await manager.connect(websocket, user)
                await manager.broadcast_lobby_state()
            elif msg_type == "move":
                logger.debug(f"[websocket] move 메시지 수신 - user: {data['user']}")
                manager.update_position(websocket, data["x"], data["y"])
                #await manager.broadcast_lobby_state()
                logger.debug(f"[websocket] move 메시지 수신 - user: {data['user']}")
                
            elif msg_type == "ready":
                manager.set_ready(websocket, True)
                await manager.broadcast_lobby_state()
                if manager.all_ready() and manager.countdown_task is None:
                    manager.countdown_task = asyncio.create_task(manager.start_countdown())
            elif msg_type == "unready":
                manager.set_ready(websocket, False)
                await manager.broadcast_lobby_state()
            elif msg_type == "chat":
                await manager.broadcast({"type": "chat", "user": data["user"], "msg": data["msg"]})
            elif msg_type == "shoot":
                try:
                    logger.debug(f"[websocket] shoot 메시지 수신 - user: {data['user']}")
                    await manager.handle_shoot(
                        data["user"],
                        data["x"],
                        data["y"],
                        data["vx"],
                        data["vy"],
                        data["color"]
                    )
                    logger.debug(f"[websocket] shoot 메시지 처리 완료")
                except Exception as e:
                    logger.error(f"[websocket] shoot 메시지 처리 중 오류 발생: {str(e)}", exc_info=True)
            elif msg_type == "start_multigame":
                # if not in_multigame:
                #     in_multigame = True
                #     # 게임 월드에 플레이어 추가
                #     game_world.players[user] = {
                #         'x': 640,  # SCREEN_WIDTH // 2
                #         'y': 600,  # SCREEN_HEIGHT - 100
                #         'health': 100,
                #         'max_health': 100,
                #         'color': data['color'],
                #         'nickname': user
                #     }
                #     # 게임 루프 시작
                #     if not multi_game_loop.running:
                #         asyncio.create_task(multi_game_loop.start())
                pass
            elif msg_type == "input":
                if in_multigame:
                    pass
                    # queue_input(user, data["input"])
    except WebSocketDisconnect:
        try:
            if user:
                if in_multigame:
                    pass
                else:
                    manager.disconnect(websocket)
                    await manager.broadcast_lobby_state()
        except Exception as e:
            logger.error(f"Error during disconnect handling: {str(e)}", exc_info=True)