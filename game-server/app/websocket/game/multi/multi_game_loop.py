import asyncio
import logging
import time
from typing import Dict, List
from app.settings import (
    SERVER_TICK_INTERVAL,
    PLAYER_SPEED,
    PLAYER_MAX_HEALTH,
    PLAYER_INITIAL_HEALTH,
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)

class MultiGameLoop:
    def __init__(self, game_id: str, players: List[dict]):
        self.game_id = game_id
        self.players = {p["user"]: {
            "user": p["user"],
            "color": p["color"],
            "x": SCREEN_WIDTH // 2,  # 초기 위치
            "y": SCREEN_HEIGHT // 2,
            "health": PLAYER_INITIAL_HEALTH,
            "max_health": PLAYER_MAX_HEALTH
        } for p in players}
        self.bullets = {}
        self.boss = None
        self.items = {}
        self.running = True
        self.tick_rate = SERVER_TICK_INTERVAL
        self.last_tick = time.time()
        self.bullet_id_counter = 0
        self._manager = None

    def set_manager(self, manager):
        """Set the game manager instance after initialization"""
        self._manager = manager

    async def run(self):
        """게임 루프 실행"""
        logging.info(f"[MultiGameLoop] Starting game loop for game: {self.game_id}")
        while self.running:
            current_time = time.time()
            delta_time = current_time - self.last_tick
            
            if delta_time >= self.tick_rate:
                await self.update(delta_time)
                self.last_tick = current_time
            else:
                await asyncio.sleep(0.001)  # CPU 사용량 감소

    async def update(self, delta_time: float):
        """게임 상태 업데이트"""
        # 총알 이동 업데이트
        for bullet_id, bullet in list(self.bullets.items()):
            bullet["x"] += bullet["vx"] * delta_time
            bullet["y"] += bullet["vy"] * delta_time
            
            # 화면 밖으로 나간 총알 제거
            if (bullet["x"] < 0 or bullet["x"] > SCREEN_WIDTH or 
                bullet["y"] < 0 or bullet["y"] > SCREEN_HEIGHT):
                del self.bullets[bullet_id]
        
        # 충돌 체크
        self.check_collisions()
        
        # 상태 브로드캐스트
        await self.broadcast_state()

    def handle_player_input(self, user: str, input_data: dict):
        """플레이어 입력 처리"""
        if user not in self.players:
            return
            
        player = self.players[user]
        dx = input_data.get("dx", 0)
        dy = input_data.get("dy", 0)
        
        # 이동 속도 계산 (대각선 이동 정규화)
        if dx != 0 and dy != 0:
            dx *= 0.7071  # 1/√2
            dy *= 0.7071
        
        # 위치 업데이트
        player["x"] += dx * PLAYER_SPEED
        player["y"] += dy * PLAYER_SPEED 
        
        # 화면 경계 체크
        player["x"] = max(0, min(SCREEN_WIDTH, player["x"]))
        player["y"] = max(0, min(SCREEN_HEIGHT, player["y"]))

    def handle_shoot(self, user: str, x: float, y: float, vx: float, vy: float, color: tuple):
        """총알 발사 처리"""
        if user not in self.players:
            return
            
        bullet_id = f"bullet_{self.bullet_id_counter}"
        self.bullet_id_counter += 1
        
        self.bullets[bullet_id] = {
            "id": bullet_id,
            "x": x,
            "y": y,
            "vx": vx,
            "vy": vy,
            "owner": user,
            "color": color,
            "last_update": time.time()
        }

    def check_collisions(self):
        """충돌 체크"""
        # TODO: 플레이어-총알, 플레이어-아이템, 총알-보스 등 충돌 체크 구현
        pass

    async def broadcast_state(self):
        """현재 게임 상태를 모든 플레이어에게 브로드캐스트"""
        if not self._manager:
            logging.error("Game manager not set")
            return

        state = {
            "type": "state",
            "players": [
                {
                    "id": user,
                    "x": player["x"],
                    "y": player["y"],
                    "health": player["health"],
                    "max_health": player["max_health"],
                    "color": player["color"],
                    "nickname": user
                }
                for user, player in self.players.items()
            ],
            "bullets": [
                {
                    "id": bid,
                    "x": bullet["x"],
                    "y": bullet["y"],
                    "vx": bullet["vx"],
                    "vy": bullet["vy"],
                    "owner": bullet["owner"],
                    "color": bullet["color"]
                }
                for bid, bullet in self.bullets.items()
            ],
            "boss": self.boss,
            "items": [
                {
                    "id": item_id,
                    "x": item["x"],
                    "y": item["y"],
                    "type": item["type"]
                }
                for item_id, item in self.items.items()
            ]
        }
        
        for user in self.players:
            await self._manager.send_to_player(user, state)

    async def remove_player(self, user_id: str):
        """플레이어 제거"""
        if user_id in self.players:
            del self.players[user_id]
            # 플레이어가 나가면 게임 종료 조건 체크
            if len(self.players) < 2:  # 예시로 2명 미만이면 종료
                await self.end_game()

    async def end_game(self):
        """게임 종료"""
        if not self._manager:
            logging.error("Game manager not set")
            return

        self.running = False
        for user in self.players:
            await self._manager.send_to_player(user, {"type": "game_over"})
        await self._manager.end_game(self.game_id)

    async def cleanup(self):
        """게임 리소스 정리"""
        self.running = False
        self.players.clear()
        self.bullets.clear()
        self.items.clear()
        self.boss = None

    def is_empty(self) -> bool:
        """게임에 플레이어가 없는지 확인"""
        return len(self.players) == 0 