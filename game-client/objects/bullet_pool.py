import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import time
from pygame.math import Vector2
from config.settings import PLAYER_MAX_BULLETS, SCREEN_WIDTH, SCREEN_HEIGHT
import pygame

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
        self.owners = np.zeros(self.MAX_BULLETS, dtype=np.int32)  # 플레이어 ID
        self.next_id = 0
        self.created_at = np.zeros(self.MAX_BULLETS, dtype=np.float32)
        self.prev_positions = np.zeros((self.MAX_BULLETS, self.POSITION_SIZE), dtype=np.float32)
        self.last_update_time = np.zeros(self.MAX_BULLETS, dtype=np.float32)
        self.interpolation_buffer = np.zeros((self.MAX_BULLETS, self.POSITION_SIZE), dtype=np.float32)
        self.interpolation_alpha = np.zeros(self.MAX_BULLETS, dtype=np.float32)
        
    def spawn_bullet(self, x: float, y: float, vx: float, vy: float, 
                     color: tuple, owner_id: int) -> Optional[int]:
        if self.next_id >= self.MAX_BULLETS:
            return None
            
        self.positions[self.next_id] = [x, y]
        self.prev_positions[self.next_id] = [x, y]
        self.velocities[self.next_id] = [vx, vy]
        self.colors[self.next_id] = color
        self.owners[self.next_id] = owner_id
        self.active[self.next_id] = True
        self.created_at[self.next_id] = time.time()
        self.last_update_time[self.next_id] = time.time()
        
        bullet_id = self.next_id
        self.next_id = (self.next_id + 1) % self.MAX_BULLETS
        return bullet_id
        
    def update_from_server(self, bullets: List[Dict]):
        """서버에서 받은 총알 정보로 업데이트"""
        if not bullets:
            self.active.fill(False)
            return
            
        # 이전 위치 저장
        self.prev_positions[self.active] = self.positions[self.active]
        
        # 모든 총알 비활성화
        self.active.fill(False)
        
        # 서버에서 받은 총알 정보를 numpy 배열로 변환
        bullet_ids = np.array([b['id'] for b in bullets], dtype=np.int32)
        positions = np.array([[b['x'], b['y']] for b in bullets], dtype=np.float32)
        velocities = np.array([[b['vx'], b['vy']] for b in bullets], dtype=np.float32)
        colors = np.array([b['color'] for b in bullets], dtype=np.uint8)
        owners = np.array([b['owner'] for b in bullets], dtype=np.int32)
        
        # 디버그: 총알 위치 확인
        # for i, pos in enumerate(positions):
        #     if pos[0] < 1 or pos[1] < 1:  # 0,0 근처의 총알 체크
        #         print(f"[DEBUG] Suspicious bullet position - ID: {bullet_ids[i]}, Pos: {pos}, Vel: {velocities[i]}")
        
        # 유효한 ID만 처리
        valid_mask = bullet_ids < self.MAX_BULLETS
        if not np.any(valid_mask):
            return
            
        valid_ids = bullet_ids[valid_mask]
        
        # 한 번에 업데이트
        self.positions[valid_ids] = positions[valid_mask]
        self.velocities[valid_ids] = velocities[valid_mask]
        self.colors[valid_ids] = colors[valid_mask]
        self.owners[valid_ids] = owners[valid_mask]
        self.active[valid_ids] = True
        self.created_at[valid_ids] = time.time()
        self.last_update_time[valid_ids] = time.time()
        
        # next_id 업데이트 (서버와 동기화)
        self.next_id = max(self.next_id, (np.max(valid_ids) + 1) % self.MAX_BULLETS)

    def update(self, delta_time: float) -> None:
        # 이전 위치 저장
        self.prev_positions[self.active] = self.positions[self.active]
        
        # 위치 업데이트
        self.positions[self.active] += self.velocities[self.active] * delta_time
        
        # 화면 밖으로 나간 총알 비활성화 (여유 공간 추가)
        num_bullets = min(self.positions.shape[0], self.active.shape[0])
        out_of_bounds = (
            (self.positions[:num_bullets, 0] < -20) |
            (self.positions[:num_bullets, 0] > SCREEN_WIDTH + 20) |
            (self.positions[:num_bullets, 1] < -20) |
            (self.positions[:num_bullets, 1] > SCREEN_HEIGHT + 20)
        )
        self.active[:num_bullets][out_of_bounds] = False  # or use np.copy()
                
    def get_interpolated_positions(self) -> Dict[int, Tuple[float, float]]:
        current_time = time.time()
        interpolated_positions = {}
        
        for i in range(self.MAX_BULLETS):
            if not self.active[i]:
                continue
                
            # 보간 계산
            elapsed = current_time - self.last_update_time[i]
            dt = 1/20  # 서버 업데이트 주기
            t = min(max(elapsed / dt, 0), 1)
            
            # 선형 보간
            pos = self.prev_positions[i] + (self.positions[i] - self.prev_positions[i]) * t
            interpolated_positions[i] = (float(pos[0]), float(pos[1]))
            
        return interpolated_positions
        
    def get_active_bullets(self) -> List[Dict]:
        """활성화된 총알 정보 반환"""
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
            for i in np.where(self.active)[0]
        ]

    def render(self, screen) -> None:
        # 활성화된 총알만 처리
        
        if not np.any(self.active):
            return
            
        # 현재 시간
        current_time = time.time()
        
        # 활성화된 총알의 인덱스 가져오기
        active_indices = np.where(self.active)[0]
        # print(f"active_indice len: {len(active_indices)}")
        
        # 각 총알에 대해 보간 계산
        for idx in active_indices:
            # 보간 계산
            elapsed = current_time - self.last_update_time[idx]
            dt = 1/20  # 서버 업데이트 주기
            t = min(max(elapsed / dt, 0), 1)
            
            # 선형 보간
            pos0 = self.prev_positions[idx]
            pos1 = self.positions[idx]
            interp_pos = pos0 + (pos1 - pos0) * t
            
            # (0,0) 위치의 총알은 건너뛰기
            if np.allclose(interp_pos, [0, 0], atol=1e-6):
                continue
                
            pygame.draw.circle(screen, tuple(self.colors[idx]), 
                             (int(interp_pos[0]), int(interp_pos[1])), 5)

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