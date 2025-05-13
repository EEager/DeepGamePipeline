import numpy as np
import time
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

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