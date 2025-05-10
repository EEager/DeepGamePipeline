# boss.py

import pygame
import math
import random
import time
from pygame.math import Vector2
from typing import List, Optional, Tuple

from config.settings import *
from objects.base_object import BaseObject
from objects.bullet import Bullet
from objects.bullet_pool import BulletPool

class Boss(BaseObject):
    """보스 객체"""
    def __init__(self, position: Vector2) -> None:
        super().__init__(position)
        self.object_type = "boss"
        self.radius = BOSS_RADIUS
        self.color_normal = (255, 0, 0)
        self.color_hit = (255, 100, 100)

        # y 위치를 강제로 100으로 고정
        self.position = Vector2(position.x, 100)

        self.health = BOSS_MAX_HEALTH
        self.max_health = BOSS_MAX_HEALTH

        # 상태 관리
        self.is_hit = False
        self.hit_time: Optional[float] = None
        self.hit_duration = 0.2  # 맞았을 때 깜빡이는 시간
        self.hit_effect_timer = 0
        self.hit_effect_duration = 0.2

        # 타이머 초기화
        self.pattern_timer = 0
        self.homing_timer = 0
        self.pattern_interval = 2.0  # 방사형 총알 발사 간격
        self.homing_interval = 4.0  # 유도 총알 발사 간격

        # 공격 주기
        self.last_radial_shot = time.time()
        self.last_homing_shot = time.time()

        self.direction = 1  # 1: 오른쪽, -1: 왼쪽
        self.speed = BOSS_SPEED

    def update(self, delta_time: float) -> None:
        self.pattern_timer += delta_time
        self.homing_timer += delta_time

        # 좌우 이동만 수행 (y 위치는 고정)
        self.position.x += self.direction * self.speed
        self.position.y = 100  # y축 고정
        if self.position.x - self.radius <= 0:
            self.position.x = self.radius
            self.direction = 1
        elif self.position.x + self.radius >= SCREEN_WIDTH:
            self.position.x = SCREEN_WIDTH - self.radius
            self.direction = -1

        # 피격 이펙트 지속 시간 갱신
        if self.is_hit:
            self.hit_effect_timer -= delta_time
            if self.hit_effect_timer <= 0:
                self.is_hit = False

        # 방사형 탄막
        if self.pattern_timer >= self.pattern_interval:
            self.shoot_radial()
            self.pattern_timer = 0.0

        # 유도탄
        if self.homing_timer >= self.homing_interval:
            # 플레이어 위치 가져오기
            from objects.object_manager import ObjectManager
            object_manager = ObjectManager.get_instance()
            players = object_manager.get_objects("player")
            if players:
                self.shoot_homing(players[0].position)
            self.homing_timer = 0.0

    def render(self, screen: pygame.Surface) -> None:
        color = self.color_hit if self.is_hit else self.color_normal
        pygame.draw.circle(screen, color, (int(self.position.x), int(self.position.y)), self.radius)

        # 체력바 (보스 아래)
        bar_width = 100
        bar_height = 10
        bar_x = self.position.x - bar_width // 2
        bar_y = self.position.y + self.radius + 5
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.position.x - self.radius, 
                         self.position.y - self.radius, 
                         self.radius * 2, 
                         self.radius * 2)

    def take_damage(self, damage: int) -> None:
        self.health = max(0, self.health - damage)
        self.is_hit = True
        self.hit_effect_timer = self.hit_effect_duration
        if self.health <= 0:
            self.active = False

    def shoot_radial(self) -> None:
        num_bullets = 12
        angle_step = 2 * math.pi / num_bullets

        for i in range(num_bullets):
            angle = i * angle_step
            direction = Vector2(math.cos(angle), math.sin(angle))
            BulletPool().get_bullet(
                self.position.copy(),
                direction,
                BOSS_BULLET_SPEED,
                ORANGE,
                "boss",
                1
            )

    def shoot_homing(self, target_pos: Vector2) -> None:
        direction = (target_pos - self.position)
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            direction = Vector2(0, 1)  # fallback
        BulletPool().get_bullet(
            self.position.copy(),
            direction,
            HOMING_BULLET_SPEED,
            BLACK,
            "boss_homing",
            1
        )
