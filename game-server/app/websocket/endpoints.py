from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import LobbyManager
import asyncio

router = APIRouter()
manager = LobbyManager()

@router.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user = None
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type == "join":
                user = data["user"]
                await manager.connect(websocket, user)
                await manager.broadcast_lobby_state()
            elif msg_type == "move":
                manager.update_position(websocket, data["x"], data["y"])
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
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast_lobby_state()