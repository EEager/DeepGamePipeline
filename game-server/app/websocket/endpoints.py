from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import LobbyManager, game_world, multi_game_loop, queue_input, process_inputs
import asyncio

router = APIRouter()
manager = LobbyManager()

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
            elif msg_type == "shoot":
                manager.handle_shoot(
                    data["user"],
                    data["x"],
                    data["y"],
                    data["vx"],
                    data["vy"],
                    data["color"]
                )
            elif msg_type == "start_multigame":
                game_world.players[user] = {
                    "id": user,
                    "nickname": user,
                    "color": data.get("color", [120,200,100]),
                    "x": 200, "y": 200, "health": 100,
                }
                if not multi_game_loop.running:
                    asyncio.create_task(multi_game_loop.start())
                in_multigame = True
            elif msg_type == "input":
                queue_input(user, data["input"])
    except WebSocketDisconnect:
        try:
            # 명시적으로 WebSocket 연결 종료
            await websocket.close()
        except:
            pass
        manager.disconnect(websocket)
        await manager.broadcast_lobby_state()
        if user and user in game_world.players:
            del game_world.players[user]
        if hasattr(manager, 'user_colors') and user in manager.user_colors:
            del manager.user_colors[user]
        await manager.broadcast({"type": "system", "msg": f"{user}님이 퇴장하셨습니다."})