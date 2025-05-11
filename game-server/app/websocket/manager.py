import asyncio
import random

class ConnectionManager:
    def __init__(self):
        self.active_connections: set = set()

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket):
        self.active_connections.discard(websocket)

    async def broadcast_json(self, message):
        for conn in self.active_connections:
            await conn.send_json(message)

class PlayerState:
    def __init__(self, user, color):
        self.user = user
        self.x = 200 + random.randint(0, 200)
        self.y = 150 + random.randint(0, 100)
        self.ready = False
        self.color = color

class LobbyManager:
    def __init__(self):
        self.players = {}  # websocket: PlayerState
        self.user_map = {}  # user: websocket
        self.countdown_task = None

    async def connect(self, websocket, user):
        color = tuple(random.randint(80, 220) for _ in range(3))
        self.players[websocket] = PlayerState(user, color)
        self.user_map[user] = websocket

    def disconnect(self, websocket):
        if websocket in self.players:
            user = self.players[websocket].user
            del self.user_map[user]
            del self.players[websocket]

    def set_ready(self, websocket, ready):
        if websocket in self.players:
            self.players[websocket].ready = ready

    def update_position(self, websocket, x, y):
        if websocket in self.players:
            self.players[websocket].x = x
            self.players[websocket].y = y

    def all_ready(self):
        return self.players and all(p.ready for p in self.players.values())

    async def broadcast_lobby_state(self):
        data = {
            "type": "lobby",
            "players": [
                {"user": p.user, "x": p.x, "y": p.y, "ready": p.ready, "color": p.color}
                for p in self.players.values()
            ]
        }
        await self.broadcast(data)

    async def broadcast(self, data):
        for ws in list(self.players.keys()):
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect(ws)

    async def start_countdown(self):
        for i in range(3, 0, -1):
            await self.broadcast({"type": "countdown", "value": i})
            await asyncio.sleep(1)
        await self.broadcast({"type": "start"})
        self.countdown_task = None