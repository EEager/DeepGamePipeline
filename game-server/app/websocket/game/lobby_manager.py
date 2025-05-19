import asyncio
import random
import sys
import time
import os
import logging
import numpy as np
from typing import List, Dict
from app.websocket.game.objects.lobby_player import LobbyPlayerState
from app.websocket.game.objects.bullet_pool import BulletPool

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

TICK_RATE = 30  # 30 ticks per second

class LobbyManager:

    def __init__(self):
        self.players = {}  # websocket: LobbyPlayerState
        self.user_map = {}  # user: websocket
        self.user_colors = {}  # user: color
        self.bullet_pool = BulletPool()
        self.last_shot_time = {}  # user: last_shot_timestamp
        self.lobby_tick = 0
        self.lock = asyncio.Lock()
        self.running = True  # 로비 루프 실행 상태를 추적하는 플래그
        self.lobby_task = None  # 로비 루프 태스크를 저장하는 변수
        self.PRACTICE_LEFT = 32
        self.PRACTICE_TOP = 32
        self.PRACTICE_RIGHT = self.PRACTICE_LEFT + (1280 - 320 - 32 * 3)  # main_width
        self.PRACTICE_BOTTOM = self.PRACTICE_TOP + (int(720 * 0.52) - 20)
        self.BULLET_SPEED = 200  # 총알 속도 상수
        self.next_owner_id = 1  # owner_id를 1부터 시작하도록 설정

    async def start(self):
        """로비 매니저 시작"""
        self.running = True
        self.lobby_task = asyncio.create_task(self.lobby_loop())
        logging.info("Lobby manager started")

    async def stop(self):
        """로비 매니저 중지"""
        self.running = False
        if self.lobby_task:
            self.lobby_task.cancel()
            try:
                await self.lobby_task
            except asyncio.CancelledError:
                pass
        logging.info("Lobby manager stopped")

    async def lobby_loop(self):
        last_update = time.time()
        while self.running:  # running 플래그를 체크
            current_time = time.time()
            delta_time = current_time - last_update
            last_update = current_time
            
            self.update_lobby_bullets(delta_time)
            await self.broadcast_lobby_state()
            self.lobby_tick += 1
            await asyncio.sleep(1/TICK_RATE)

    def get_player_by_user(self, user):
        """user ID로 플레이어 상태를 가져옵니다."""
        if user in self.user_map:
            websocket = self.user_map[user]
            return self.players.get(websocket)
        return None
    def get_player_by_websocket(self, websocket):
        """websocket으로 플레이어 상태를 가져옵니다."""
        return self.players.get(websocket)

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
                player = self.players[websocket]
                user = player.user
                if user in self.user_map:
                    del self.user_map[user]
                del self.players[websocket]
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

    TIME_DURATION = 3
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
        
        # current_time = time.time()
        # if not hasattr(self, 'last_broadcast_log_time') or current_time - self.last_broadcast_log_time >= self.TIME_DURATION:
        #     logger.debug(f"[broadcast_lobby_state] 브로드캐스트 시작 - tick: {self.lobby_tick}, 플레이어 수: {len(self.players)}, 총알 수: {len(data['bullets'])}")
        await self.broadcast(data)


    async def broadcast(self, data):
        
        current_time = time.time()
        # if not hasattr(self, 'last_broadcast_log_time') or current_time - self.last_broadcast_log_time >= self.TIME_DURATION:
        #     logger.debug(f"[broadcast] 메시지 전송 시작 - type: {data.get('type')}, 연결된 클라이언트 수: {len(self.players)}")
            
        for ws in list(self.players.keys()):
            try:
                await ws.send_json(data)
                
                if not hasattr(self, 'last_broadcast_log_time') or current_time - self.last_broadcast_log_time >= self.TIME_DURATION:
                    logger.debug(f"🔊 [broadcast] 메시지 전송 성공 - type: {data.get('type')}, user: {self.players[ws].user}")
                    self.last_broadcast_log_time = current_time
            except Exception as e:
                logger.error(f"❌ [broadcast] 메시지 전송 실패: {str(e)}")
                self.disconnect(ws)
                
        if not hasattr(self, 'last_broadcast_log_time') or current_time - self.last_broadcast_log_time >= self.TIME_DURATION:
            self.last_broadcast_log_time = current_time

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
        await self.broadcast({"type": "countdown_end"})

# manager 인스턴스 생성(싱글톤)
lobby_manager = LobbyManager()  
