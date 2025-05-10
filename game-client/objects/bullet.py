# objects/bullet.py

import pygame
from pygame.math import Vector2
from objects.base_object import BaseObject
from config.settings import *

class Bullet(BaseObject):
    def __init__(self, position: Vector2, direction: Vector2, speed: float, color: tuple, owner: str, damage: int = 1):
        super().__init__(position)
        self.object_type = "bullet"
        # direction도 복사
        if isinstance(direction, Vector2):
            self.direction = direction.copy().normalize()
        else:
            self.direction = Vector2(direction).normalize()
        self.speed = speed
        self.color = color
        self.owner = owner  # "player" or "boss"
        self.radius = 5
        self.active = True
        self.damage = damage

    def update(self, delta_time: float) -> None:
        self.position += self.direction * self.speed * delta_time
        # 화면 밖으로 나간 총알 제거
        if self.is_out_of_screen():
            self.active = False

    def render(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.position.x - self.radius, 
                         self.position.y - self.radius, 
                         self.radius * 2, 
                         self.radius * 2)

    def is_out_of_screen(self) -> bool:
        return (self.position.x < -self.radius or 
                self.position.x > SCREEN_WIDTH + self.radius or 
                self.position.y < -self.radius or 
                self.position.y > SCREEN_HEIGHT + self.radius)

    def reset(self, position: Vector2, direction: Vector2, speed: float, color: tuple, owner: str, damage: int = 1):
        """총알을 재사용하기 위해 상태를 초기화합니다."""
        self.position = position.copy()
        if isinstance(direction, Vector2):
            self.direction = direction.copy().normalize()
        else:
            self.direction = Vector2(direction).normalize()
        self.speed = speed
        self.color = color
        self.owner = owner
        self.damage = damage
        self.active = True 