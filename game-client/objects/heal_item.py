# objects/heal_item.py

import pygame
from pygame.math import Vector2
from objects.base_object import BaseObject
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, HEAL_ITEM_SPEED

class HealItem(BaseObject):
    def __init__(self, position: Vector2):
        super().__init__(position)
        self.object_type = "heal_item"
        self.radius = 15  # 크기를 15로 증가
        self.color = (0, 255, 0)  # 녹색
        self.heal_amount = 20
        self.speed = HEAL_ITEM_SPEED
        self.active = True

    def update(self, delta_time: float) -> None:
        # 아래로 떨어지기
        self.position.y += self.speed * delta_time
        # 화면 밖으로 나간 힐 아이템 제거
        if self.position.y > pygame.display.get_surface().get_height():
            self.active = False

    def render(self, screen: pygame.Surface) -> None:
        # 녹색 원 그리기
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        # 십자가 모양의 힐 아이템
        pygame.draw.line(screen, (255, 255, 255), 
                        (int(self.position.x - self.radius/2), int(self.position.y)),
                        (int(self.position.x + self.radius/2), int(self.position.y)), 3)
        pygame.draw.line(screen, (255, 255, 255),
                        (int(self.position.x), int(self.position.y - self.radius/2)),
                        (int(self.position.x), int(self.position.y + self.radius/2)), 3)

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