import asyncio
import random
import sys
import time
import os
import logging

from app.services.game_loop import GameWorld, GameLoop


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
        self.user_colors = {}  # user: color
        self.lobby_bullets = {}  # user: [bullet1, bullet2, ...]
        self.last_shot_time = {}  # user: last_shot_timestamp
        self.next_bullet_id = 0
        self.lobby_tick = 0
        self.lobby_loop_task = asyncio.create_task(self.lobby_loop())
        self.PRACTICE_LEFT = 32
        self.PRACTICE_TOP = 32
        self.PRACTICE_RIGHT = self.PRACTICE_LEFT + (1280 - 320 - 32 * 3)  # main_width
        self.PRACTICE_BOTTOM = self.PRACTICE_TOP + (int(720 * 0.52) - 20)

    async def lobby_loop(self):
        while True:
            self.update_lobby_bullets()
            await self.broadcast_lobby_state()
            self.lobby_tick += 1
            await asyncio.sleep(1/20)

    async def connect(self, websocket, user):
        # 색상은 서버에서만 할당/관리
        if user not in self.user_colors:
            color = tuple(random.randint(80, 220) for _ in range(3))
            self.user_colors[user] = color
        else:
            color = self.user_colors[user]
        self.players[websocket] = PlayerState(user, color)
        self.user_map[user] = websocket
        await self.broadcast({"type": "system", "msg": f"{user}님이 입장하셨습니다."})
        # 상태 브로드캐스트는 tick loop에서만!

    def disconnect(self, websocket):
        if websocket in self.players:
            user = self.players[websocket].user
            logging.debug(f"[Before delete] refcount: {sys.getrefcount(websocket)}")
            del self.user_map[user]
            del self.players[websocket]
            logging.debug(f"[After delete] refcount: {sys.getrefcount(websocket)}")
            # # 색상은 유지 (재접속 시 같은 색상 사용)
            # if user in self.user_colors:
            #     del self.user_colors[user]
            # 퇴장 system 메시지 브로드캐스트
            asyncio.create_task(self.broadcast({"type": "system", "msg": f"{user}님이 퇴장하셨습니다."}))

    def set_ready(self, websocket, ready):
        if websocket in self.players:
            self.players[websocket].ready = ready
        # 상태 브로드캐스트는 tick loop에서만!

    def update_position(self, websocket, x, y):
        if websocket in self.players:
            self.players[websocket].x = x
            self.players[websocket].y = y
        # 상태 브로드캐스트는 tick loop에서만!

    def all_ready(self):
        return self.players and all(p.ready for p in self.players.values())

    def spawn_lobby_bullet(self, user, x, y, vx, vy, color):
        # 연속 발사 제한 (0.2초)
        current_time = time.time()
        if user in self.last_shot_time and current_time - self.last_shot_time[user] < 0.2:
            return False
        
        # 사용자별 총알 리스트 초기화
        if user not in self.lobby_bullets:
            self.lobby_bullets[user] = []
        bullet = {
            'id': self.next_bullet_id,
            'user': user,
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color,
            'active': True
        }
        self.lobby_bullets[user].append(bullet)
        self.next_bullet_id += 1
        self.last_shot_time[user] = current_time
        return True

    def update_lobby_bullets(self):
        if not self.lobby_bullets:
            return  # 총알 없으면 바로 리턴 (오버헤드 거의 없음)
        # 이동 및 화면 밖 제거
        for user, bullets in list(self.lobby_bullets.items()):
            # 연습장 범위 내에 있는 총알만 남김
            self.lobby_bullets[user] = [
                b for b in bullets
                if self.PRACTICE_LEFT <= b['x'] <= self.PRACTICE_RIGHT and self.PRACTICE_TOP <= b['y'] <= self.PRACTICE_BOTTOM
            ]
            for b in self.lobby_bullets[user]:
                b['x'] += b['vx']
                b['y'] += b['vy']
            # 사용자의 모든 총알이 제거되면 리스트도 제거
            if not self.lobby_bullets[user]:
                del self.lobby_bullets[user]

    def handle_shoot(self, user, x, y, vx, vy, color):
        """총알 발사 메시지 처리"""
        self.spawn_lobby_bullet(user, x, y, vx, vy, color)
        # 상태 브로드캐스트는 tick loop에서만!

    async def broadcast_lobby_state(self):
        # 모든 총알을 하나의 리스트로 합치기
        all_bullets = []
        for bullets in self.lobby_bullets.values():
            all_bullets.extend(bullets)
        data = {
            "type": "lobby",
            "players": [
                {"user": p.user, "x": p.x, "y": p.y, "ready": p.ready, "color": p.color}
                for p in self.players.values()
            ],
            "bullets": all_bullets
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

# --- 멀티게임용 싱글톤 월드/루프/입력큐 ---
game_world = GameWorld()
input_queue = []  # [(user, input_dict)]

async def broadcast_state(world):
    # 상태 메시지 예시
    msg = {
        "type": "state",
        "tick": world.tick,
        "players": list(world.players.values()),
        "bullets": list(world.bullets.values()),
        "boss": world.boss,
        "items": list(world.items.values()),
        # ... 기타 오브젝트
    }
    # 실제 연결된 모든 클라이언트에 브로드캐스트
    for ws in list(game_world.players.keys()):
        try:
            await ws.send_json(msg)
        except Exception:
            pass

# 게임 루프 인스턴스
multi_game_loop = GameLoop(game_world, broadcast_state)

def queue_input(user, input_dict):
    input_queue.append((user, input_dict))

# 입력 큐를 world에 반영하는 함수(예시)
def process_inputs():
    while input_queue:
        user, inp = input_queue.pop(0)
        # 예: 이동 입력 반영
        if user in game_world.players:
            p = game_world.players[user]
            p['x'] += inp.get('dx', 0)
            p['y'] += inp.get('dy', 0)
            # 총알 발사 입력 처리
            if inp.get('shoot'):
                # 예시: 플레이어 앞 방향으로 총알 생성
                vx, vy = inp.get('vx', 0), inp.get('vy', -6)
                color = p.get('color', (255,255,0))
                game_world.spawn_bullet(user, p['x'], p['y'], vx, vy, color)
        # 기타 입력 처리