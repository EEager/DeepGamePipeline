from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import LobbyManager
from app.websocket.lobby_endpoint import handle_lobby_message
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
            
            if msg_type in ["join", "ready", "unready", "chat", "Lobby_shoot", "start_multigame"]:
                await handle_lobby_message(websocket, manager, data)
            elif msg_type == "move":
                logger.debug(f"[websocket] move 메시지 수신 - user: {data['user']}")
                manager.update_position(websocket, data["x"], data["y"])
                logger.debug(f"[websocket] move 메시지 수신 - user: {data['user']}")
            elif msg_type == "input":
                if in_multigame:
                    pass
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