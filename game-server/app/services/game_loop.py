import asyncio
import time
from collections import defaultdict
import random

TICK_RATE = 30  # 30Hz
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
        self.players = {}  # id: {id, nickname, color, x, y, ...}
        self.bullets = {}  # id: {id, owner, x, y, vx, vy, ...}
        self.items = {}    # id: {id, x, y, ...}
        self.boss = None   # {x, y, radius, health, ...}
        self.tick = 0
        self.grid = SpatialHashGrid(CELL_SIZE)
        self.next_item_id = 0
        self.next_bullet_id = 0
        self.boss_spawned = False
    def update(self):
        self.grid.clear()
        for p in self.players.values():
            self.grid.add(p)
        for b in self.bullets.values():
            self.grid.add(b)
        # 1. 보스 생성/업데이트
        if not self.boss_spawned and self.players:
            self.boss = {"x": 400, "y": 100, "radius": 32, "health": 200}
            self.boss_spawned = True
        if self.boss:
            # 예시: 좌우 이동
            self.boss['x'] += random.choice([-2, 2])
            self.boss['x'] = max(100, min(700, self.boss['x']))
        # 2. 이동/물리 처리
        for b in self.bullets.values():
            b['x'] += b['vx']
            b['y'] += b['vy']
        # 3. nearby 충돌 처리 (총알-플레이어, 총알-보스)
        for b in list(self.bullets.values()):
            # 총알-플레이어
            for p in self.grid.get_nearby(b, self.players):
                if b['owner'] != p['id'] and check_collision(b, p):
                    p['health'] -= b.get('damage', 1)
                    b['active'] = False
            # 총알-보스
            if self.boss and b['owner'] in self.players and check_collision(b, self.boss):
                self.boss['health'] -= b.get('damage', 1)
                b['active'] = False
        # 4. 불필요한 오브젝트 제거
        self.bullets = {k: v for k, v in self.bullets.items() if v.get('active', True)}
        # 5. 아이템 스폰 예시
        if self.tick % 300 == 0:
            self.items[self.next_item_id] = {"x": random.randint(100, 700), "y": random.randint(150, 400), "radius": 10, "heal": 20}
            self.next_item_id += 1
        # 6. 플레이어-아이템 충돌
        for p in self.players.values():
            for iid, item in list(self.items.items()):
                if check_collision(p, item):
                    p['health'] = min(100, p['health'] + item['heal'])
                    del self.items[iid]
        # 7. tick 증가
        self.tick += 1
    def spawn_bullet(self, owner_id, x, y, vx, vy, color):
        self.bullets[self.next_bullet_id] = {
            'id': self.next_bullet_id,
            'owner': owner_id,
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color,
            'active': True,
            'damage': 1
        }
        self.next_bullet_id += 1

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
            await self.broadcast_func(self.world)
            elapsed = time.time() - start
            await asyncio.sleep(max(0, 1.0/TICK_RATE - elapsed))
    def stop(self):
        self.running = False 