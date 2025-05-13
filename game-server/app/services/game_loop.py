import asyncio
import time
from collections import defaultdict
import random
import math
from typing import Dict, List, Tuple

TICK_RATE = 20  # 20 FPS
CELL_SIZE = 100

def spatial_hash(x, y):
    return (int(x) // CELL_SIZE, int(y) // CELL_SIZE)

class SpatialHashGrid:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.grid = defaultdict(set)
    def clear(self):
        self.grid.clear()
    def add(self, obj):
        key = spatial_hash(obj['x'], obj['y'])
        self.grid[key].add(obj['id'])
    def get_nearby(self, obj, all_objects, radius=1):
        cx, cy = spatial_hash(obj['x'], obj['y'])
        result = set()
        for dx in range(-radius, radius+1):
            for dy in range(-radius, radius+1):
                key = (cx+dx, cy+dy)
                for oid in self.grid.get(key, set()):
                    if oid != obj['id']:
                        result.add(all_objects[oid])
        return result

class GameWorld:
    def __init__(self):
        self.players: Dict[str, dict] = {}  # user: {x, y, health, max_health, color, nickname}
        self.bullets: Dict[int, dict] = {}  # id: {x, y, vx, vy, owner, color, damage}
        self.boss = {
            'x': 640,  # SCREEN_WIDTH // 2
            'y': 100,
            'radius': 32,
            'health': 1000,
            'max_health': 1000,
            'dx': 2,  # 이동 속도
            'pattern_timer': 0,
            'current_pattern': 'move',
            'target_player': None
        }
        self.items: Dict[int, dict] = {}  # id: {x, y, type}
        self.tick = 0
        self.grid = SpatialHashGrid(CELL_SIZE)
        self.next_item_id = 0
        self.next_bullet_id = 0

    def update(self):
        self.grid.clear()
        for p in self.players.values():
            self.grid.add(p)
        for b in self.bullets.values():
            self.grid.add(b)
        
        # 보스 패턴 업데이트
        self.update_boss()
        
        # 총알 이동
        for b in list(self.bullets.values()):
            b['x'] += b['vx']
            b['y'] += b['vy']
            
            # 화면 밖으로 나간 총알 제거
            if (b['x'] < -50 or b['x'] > 1290 or 
                b['y'] < -50 or b['y'] > 770):
                del self.bullets[b['id']]
        
        # 충돌 체크
        game_state = self.check_collisions()
        
        # 힐 아이템 스폰 (10초마다)
        if self.tick % 200 == 0:  # 10초 = 200틱
            self.spawn_heal_item()
        
        # 플레이어-아이템 충돌
        for p in self.players.values():
            for iid, item in list(self.items.items()):
                if check_collision(p, item):
                    p['health'] = min(100, p['health'] + item['heal'])
                    del self.items[iid]
        
        # tick 증가
        self.tick += 1

    def update_boss(self):
        boss = self.boss
        boss['pattern_timer'] += 1/20  # delta_time
        
        # 패턴 전환
        if boss['pattern_timer'] >= 5:  # 5초마다 패턴 전환
            boss['pattern_timer'] = 0
            patterns = ['move', 'radial', 'homing']
            patterns.remove(boss['current_pattern'])
            boss['current_pattern'] = random.choice(patterns)
        
        # 패턴별 동작
        if boss['current_pattern'] == 'move':
            # 좌우 이동
            boss['x'] += boss['dx']
            if boss['x'] <= 100 or boss['x'] >= 1180:  # 화면 경계
                boss['dx'] *= -1
        elif boss['current_pattern'] == 'radial':
            # 방사형 총알 발사
            if boss['pattern_timer'] % 0.5 < 1/20:  # 0.5초마다
                for angle in range(0, 360, 45):  # 8방향
                    rad = math.radians(angle)
                    vx = math.cos(rad) * 5
                    vy = math.sin(rad) * 5
                    self.spawn_bullet(boss['x'], boss['y'], vx, vy, 'boss', (255, 0, 0))
        elif boss['current_pattern'] == 'homing':
            # 유도탄 발사
            if boss['pattern_timer'] % 1.0 < 1/20:  # 1초마다
                # 가장 가까운 플레이어 찾기
                closest_player = None
                min_dist = float('inf')
                for player_id, player in self.players.items():
                    dx = player['x'] - boss['x']
                    dy = player['y'] - boss['y']
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < min_dist:
                        min_dist = dist
                        closest_player = player
                
                if closest_player:
                    # 플레이어 방향으로 총알 발사
                    dx = closest_player['x'] - boss['x']
                    dy = closest_player['y'] - boss['y']
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        vx = (dx/dist) * 4
                        vy = (dy/dist) * 4
                        self.spawn_bullet(boss['x'], boss['y'], vx, vy, 'boss_homing', (255, 100, 100))

    def check_collisions(self):
        # 플레이어와 보스 총알 충돌
        for player_id, player in self.players.items():
            for bullet_id, bullet in list(self.bullets.items()):
                if bullet['owner'] in ('boss', 'boss_homing'):
                    dx = player['x'] - bullet['x']
                    dy = player['y'] - bullet['y']
                    if math.sqrt(dx*dx + dy*dy) < 20:  # 충돌 거리
                        player['health'] -= bullet['damage']
                        del self.bullets[bullet_id]
                        if player['health'] <= 0:
                            del self.players[player_id]
                            # 게임 오버 체크
                            if not self.players:
                                return 'game_over'
        
        # 보스와 플레이어 총알 충돌
        for bullet_id, bullet in list(self.bullets.items()):
            if bullet['owner'] == 'player':
                dx = self.boss['x'] - bullet['x']
                dy = self.boss['y'] - bullet['y']
                if math.sqrt(dx*dx + dy*dy) < self.boss['radius'] + 5:  # 충돌 거리
                    self.boss['health'] -= bullet['damage']
                    del self.bullets[bullet_id]
                    if self.boss['health'] <= 0:
                        return 'game_clear'
        
        return None

    def spawn_bullet(self, x: float, y: float, vx: float, vy: float, owner: str, color: Tuple[int, int, int], damage: int = 10) -> int:
        bullet_id = self.next_bullet_id
        self.next_bullet_id += 1
        self.bullets[bullet_id] = {
            'id': bullet_id,
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy,
            'owner': owner,
            'color': color,
            'damage': damage
        }
        return bullet_id

    def spawn_heal_item(self):
        item_id = self.next_item_id
        self.next_item_id += 1
        self.items[item_id] = {
            'id': item_id,
            'x': random.randint(50, 1230),
            'y': random.randint(50, 670),
            'type': 'heal'
        }

def check_collision(obj1, obj2):
    # 원-원 충돌 예시
    dx = obj1['x'] - obj2['x']
    dy = obj1['y'] - obj2['y']
    dist2 = dx*dx + dy*dy
    r1 = obj1.get('radius', 12)
    r2 = obj2.get('radius', 12)
    return dist2 <= (r1 + r2) ** 2

class GameLoop:
    def __init__(self, world, broadcast_func):
        self.world = world
        self.broadcast_func = broadcast_func
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            start = time.time()
            self.world.update()
            game_state = self.world.check_collisions()
            if game_state:
                await self.broadcast_func(self.world, game_state)
            else:
                await self.broadcast_func(self.world)
            elapsed = time.time() - start
            await asyncio.sleep(max(0, 1.0/TICK_RATE - elapsed))

    def stop(self):
        self.running = False 