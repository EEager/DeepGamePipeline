from typing import List, Optional
from pygame.math import Vector2
from objects.bullet import Bullet
from config.settings import PLAYER_MAX_BULLETS

class BulletPool:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BulletPool, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.active_bullets: List[Bullet] = []
        self.inactive_bullets: List[Bullet] = []
        self.max_pool_size = 1000  # 풀의 최대 크기

    def get_bullet(self, position: Vector2, direction: Vector2, speed: float, color: tuple, owner: str, damage: int = 1) -> Optional[Bullet]:
        # 비활성화된 총알이 있으면 재사용
        if self.inactive_bullets:
            bullet = self.inactive_bullets.pop()
            bullet.reset(position, direction, speed, color, owner, damage)
            self.active_bullets.append(bullet)
            return bullet
        
        # 풀 크기가 최대치에 도달하지 않았다면 새 총알 생성
        if len(self.active_bullets) + len(self.inactive_bullets) < self.max_pool_size:
            bullet = Bullet(position, direction, speed, color, owner, damage)
            self.active_bullets.append(bullet)
            return bullet
        
        return None  # 풀이 가득 찬 경우

    def deactivate_bullet(self, bullet: Bullet):
        if bullet in self.active_bullets:
            self.active_bullets.remove(bullet)
            self.inactive_bullets.append(bullet)
            # inactive 총알이 너무 많으면 오래된 것부터 삭제
            if len(self.inactive_bullets) > self.max_pool_size:
                self.inactive_bullets.pop(0)  # 가장 오래된 것 삭제

    def get_active_bullets(self) -> List[Bullet]:
        return self.active_bullets

    def update(self, delta_time: float):
        # 활성화된 총알들만 업데이트
        for bullet in self.active_bullets[:]:  # 복사본으로 순회
            bullet.update(delta_time)
            if bullet.is_out_of_screen():
                self.active_bullets.remove(bullet)  # 맵 밖으로 나가면 완전히 삭제
            elif not bullet.active:
                self.deactivate_bullet(bullet)

    def render(self, screen):
        # 활성화된 총알들만 렌더링
        for bullet in self.active_bullets:
            bullet.render(screen)

    def clear(self):
        # 모든 총알 비활성화
        for bullet in self.active_bullets[:]:
            self.deactivate_bullet(bullet) 