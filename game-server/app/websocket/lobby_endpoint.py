from fastapi import WebSocket
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

async def handle_lobby_message(websocket: WebSocket, manager, data: dict):
    msg_type = data.get("type")
    user = data.get("user")
    
    if msg_type == "join":
        await manager.connect(websocket, user)
        await manager.broadcast_lobby_state()
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
    elif msg_type == "Lobby_shoot":
        try:
            logger.debug(f"[websocket] Lobby_shoot 메시지 수신 - user: {data['user']}")
            await manager.handle_shoot(
                data["user"],
                data["x"],
                data["y"],
                data["vx"],
                data["vy"],
                data["color"]
            )
            logger.debug(f"[websocket] Lobby_shoot 메시지 처리 완료")
        except Exception as e:
            logger.error(f"[websocket] Lobby_shoot 메시지 처리 중 오류 발생: {str(e)}", exc_info=True)
    elif msg_type == "start_multigame":
        pass  # 멀티게임 시작 로직 