import asyncio
import random
import sys
import time
import os
import logging
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from app.services.bullet_pool import BulletPool

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

TICK_RATE = 30  # 30 ticks per second

@dataclass
class BulletPool:
    MAX_BULLETS = 1000
    POSITION_SIZE = 2  # x, y
    VELOCITY_SIZE = 2  # vx, vy
    COLOR_SIZE = 3    # r, g, b
    
    def __init__(self):
        # 위치, 속도, 색상, 활성화 상태를 numpy 배열로 관리
        self.positions = np.zeros((self.MAX_BULLETS, self.POSITION_SIZE), dtype=np.float32)
        self.velocities = np.zeros((self.MAX_BULLETS, self.VELOCITY_SIZE), dtype=np.float32)
        self.colors = np.zeros((self.MAX_BULLETS, self.COLOR_SIZE), dtype=np.uint8)
        self.active = np.zeros(self.MAX_BULLETS, dtype=bool)
        self.owners = np.zeros(self.MAX_BULLETS, dtype=np.int64)  # 플레이어 ID를 int64로 변경
        self.next_id = 0
        self.created_at = np.zeros(self.MAX_BULLETS, dtype=np.float32)
        self.prev_positions = np.zeros((self.MAX_BULLETS, self.POSITION_SIZE), dtype=np.float32)
        self.last_update_time = np.zeros(self.MAX_BULLETS, dtype=np.float32)
        
    def spawn_bullet(self, x: float, y: float, vx: float, vy: float, 
                     color: tuple, owner_id: int) -> Optional[int]:
        logger.debug(f"[spawn_bullet] 시작 - next_id: {self.next_id}, pos: ({x}, {y}), vel: ({vx}, {vy}), owner: {owner_id}")
        
        if self.next_id >= self.MAX_BULLETS:
            logger.debug(f"[spawn_bullet] 실패 - bullet_pool이 가득 참 (next_id: {self.next_id}, MAX_BULLETS: {self.MAX_BULLETS})")
            return None
            
        # active 상태를 먼저 설정
        self.active[self.next_id] = True
        
        # 위치와 이전 위치를 동일하게 설정
        self.positions[self.next_id] = [x, y]
        self.prev_positions[self.next_id] = [x, y]  # 이전 위치도 동일하게 설정
        self.velocities[self.next_id] = [vx, vy]
        self.colors[self.next_id] = color
        self.owners[self.next_id] = owner_id
        self.created_at[self.next_id] = time.time()
        self.last_update_time[self.next_id] = time.time()
        
        bullet_id = self.next_id
        self.next_id = (self.next_id + 1) % self.MAX_BULLETS
        logger.debug(f"[spawn_bullet] 성공 - bullet_id: {bullet_id}, next_id: {self.next_id}")
        return bullet_id
        
    def update(self, bounds: tuple, delta_time: float, bullet_speed: float):
        # 이전 위치 저장
        self.prev_positions[self.active] = self.positions[self.active]
        
        # 위치 업데이트 (벡터화된 연산)
        self.positions[self.active] += self.velocities[self.active] * delta_time * bullet_speed
        
        # 화면 밖 총알 비활성화
        left, top, right, bottom = bounds
        out_of_bounds = (
            (self.positions[:, 0] < left) |
            (self.positions[:, 0] > right) |
            (self.positions[:, 1] < top) |
            (self.positions[:, 1] > bottom)
        )
        self.active[out_of_bounds] = False
        
        # 수명이 지난 총알 비활성화 (5초)
        current_time = time.time()
        expired = (current_time - self.created_at) > 7.0
        self.active[expired] = False
        
        # 마지막 업데이트 시간 갱신
        self.last_update_time[self.active] = current_time
        
    def get_active_bullets(self) -> List[Dict]:
        active_mask = self.active
        return [
            {
                'id': int(i),
                'x': float(self.positions[i, 0]),
                'y': float(self.positions[i, 1]),
                'vx': float(self.velocities[i, 0]),
                'vy': float(self.velocities[i, 1]),
                'color': tuple(map(int, self.colors[i])),
                'owner': int(self.owners[i])
            }
            for i in np.where(active_mask)[0]
        ]

    def deactivate(self, bullet_id: int) -> None:
        """
        특정 총알을 비활성화합니다.
        TODO: 구현 필요
        - bullet_id가 유효한지 확인
        - 해당 총알의 active 상태를 False로 변경
        - 필요한 경우 추가 정리 작업 수행
        """
        pass

    def clear(self) -> None:
        """
        모든 총알을 비활성화합니다.
        TODO: 구현 필요
        - 모든 총알의 active 상태를 False로 변경
        - 필요한 경우 추가 정리 작업 수행
        """
        pass

class LobbyPlayerState:
    def __init__(self, user, color):
        self.user = user
        self.x = 200 + random.randint(0, 200)
        self.y = 150 + random.randint(0, 100)
        self.ready = False
        self.color = color

class LobbyManager:

    def __init__(self):
        self.players = {}  # websocket: LobbyPlayerState
        self.user_map = {}  # user: websocket
        self.countdown_task = None
        self.user_colors = {}  # user: color
        self.bullet_pool = BulletPool()
        self.last_shot_time = {}  # user: last_shot_timestamp
        self.lobby_tick = 0
        self.lobby_loop_task = asyncio.create_task(self.lobby_loop())
        self.PRACTICE_LEFT = 32
        self.PRACTICE_TOP = 32
        self.PRACTICE_RIGHT = self.PRACTICE_LEFT + (1280 - 320 - 32 * 3)  # main_width
        self.PRACTICE_BOTTOM = self.PRACTICE_TOP + (int(720 * 0.52) - 20)
        self.BULLET_SPEED = 200  # 총알 속도 상수
        self.next_owner_id = 1  # owner_id를 1부터 시작하도록 설정

    async def lobby_loop(self):
        last_update = time.time()
        while True:
            current_time = time.time()
            delta_time = current_time - last_update
            last_update = current_time
            
            self.update_lobby_bullets(delta_time)
            await self.broadcast_lobby_state()
            self.lobby_tick += 1
            await asyncio.sleep(1/TICK_RATE)

    async def connect(self, websocket, user):
        # 닉네임/색상은 서버에서만 만들어주고 할당/관리
        if websocket in self.players:
            logger.error(f"[connect] 이미 입장한 유저 - user: {user}")
            return
        
        while True:
            color = tuple(random.randint(40, 220) for _ in range(3))
            if not color in self.user_colors.values():
                self.user_colors[user] = color
                break
                
        nickname = f"user_{random.randint(1, 1000)}"
        self.players[websocket] = LobbyPlayerState(nickname, color)
        self.user_map[user] = websocket
        
         # 방금 접속한 유저 nick, color를 준다
        await self.unicast_to_user(user, {
            "type": "lobby_start",
            "color": color,
            "nickname": nickname
        })
        
        # 모든 유저에게 입장 메시지 브로드캐스트
        await self.broadcast({"type": "system", "msg": f"{nickname}님이 입장하셨습니다."})

    def disconnect(self, websocket):
        try:
            if websocket in self.players:
                user = self.players[websocket].user
                logging.debug(f"[Before delete] refcount: {sys.getrefcount(websocket)}")
                if user in self.user_map:
                    del self.user_map[user]
                del self.players[websocket]
                logging.debug(f"[After delete] refcount: {sys.getrefcount(websocket)}")
                # 퇴장 system 메시지 브로드캐스트
                asyncio.create_task(self.broadcast({"type": "system", "msg": f"{user}님이 퇴장하셨습니다."}))
        except Exception as e:
            logger.error(f"Error in disconnect: {str(e)}", exc_info=True)

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
        logger.debug(f"[spawn_lobby_bullet] 시작 - user: {user}, pos: ({x}, {y}), vel: ({vx}, {vy})")
        
        # 연속 발사 제한 (0.2초)
        current_time = time.time()
        if user in self.last_shot_time and current_time - self.last_shot_time[user] < 0.2:
            logger.debug(f"[spawn_lobby_bullet] 연속 발사 제한 - user: {user}, 마지막 발사: {current_time - self.last_shot_time[user]:.3f}초 전")
            return False
        
        # 총알 생성
        owner_id = self.next_owner_id
        self.next_owner_id += 1  # 다음 ID 준비
        logger.debug(f"[spawn_lobby_bullet] 총알 생성 시도 - owner_id: {owner_id}")
        
        bullet_id = self.bullet_pool.spawn_bullet(x, y, vx, vy, color, owner_id)
        if bullet_id is not None:
            self.last_shot_time[user] = current_time
            logger.debug(f"[spawn_lobby_bullet] 총알 생성 성공 - bullet_id: {bullet_id}")
            return True
            
        logger.debug(f"[spawn_lobby_bullet] 총알 생성 실패 - bullet_pool이 가득 참")
        return False

    def update_lobby_bullets(self, delta_time):
        bounds = (self.PRACTICE_LEFT, self.PRACTICE_TOP, 
                 self.PRACTICE_RIGHT, self.PRACTICE_BOTTOM)
        self.bullet_pool.update(bounds, delta_time, self.BULLET_SPEED)

    async def handle_shoot(self, user, x, y, vx, vy, color):
        """총알 발사 메시지 처리"""
        logger.debug(f"[handle_shoot] 시작 - user: {user}, pos: ({x}, {y}), vel: ({vx}, {vy})")
        self.spawn_lobby_bullet(user, x, y, vx, vy, color)
        # 상태 브로드캐스트는 tick loop에서만!

    async def broadcast_lobby_state(self):
        data = {
            "type": "lobby",
            "tick": self.lobby_tick,
            "players": [
                {"user": p.user, "x": p.x, "y": p.y, "ready": p.ready, "color": p.color}
                for p in self.players.values()
            ],
            "bullets": self.bullet_pool.get_active_bullets()
        }
        logger.debug(f"[broadcast_lobby_state] 브로드캐스트 시작 - tick: {self.lobby_tick}, 플레이어 수: {len(self.players)}, 총알 수: {len(data['bullets'])}")
        await self.broadcast(data)
        logger.debug(f"[broadcast_lobby_state] 브로드캐스트 완료")

    async def broadcast(self, data):
        logger.debug(f"[broadcast] 메시지 전송 시작 - type: {data.get('type')}, 연결된 클라이언트 수: {len(self.players)}")
        for ws in list(self.players.keys()):
            try:
                await ws.send_json(data)
                logger.debug(f"[broadcast] 메시지 전송 성공 - type: {data.get('type')}")
            except Exception as e:
                logger.error(f"[broadcast] 메시지 전송 실패: {str(e)}")
                self.disconnect(ws)

    async def unicast_to_user(self, user: str, message: dict):
        if user in self.user_map:
            websocket = self.user_map[user]
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"❗ {user}에게 메시지 전송 실패: {e}")

    async def start_countdown(self):
        for i in range(3, 0, -1):
            await self.broadcast({"type": "countdown", "value": i})
            await asyncio.sleep(1)
        await self.broadcast({"type": "start"})
        self.countdown_task = None