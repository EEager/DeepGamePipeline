# objects/base_object.py
from abc import ABC, abstractmethod
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
import pygame
from pygame.math import Vector2
from typing import Optional

class BaseObject(ABC):
    def __init__(self, position):
        # Vector2 타입이면 항상 복사해서 저장
        if isinstance(position, Vector2):
            self.position = position.copy()
        else:
            self.position = position
        self.active = True
        self.object_type: str = "base"  # "player", "boss", "bullet", "heal_item" 등

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """로직 업데이트"""
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """렌더링"""
        pass

    def is_out_of_screen(self) -> bool:
        """화면 밖으로 나갔는지 체크"""
        return (self.position.x < 0 or 
                self.position.x > SCREEN_WIDTH or 
                self.position.y < 0 or 
                self.position.y > SCREEN_HEIGHT)

    def get_rect(self) -> pygame.Rect:
        """충돌 체크를 위한 Rect 반환"""
        return pygame.Rect(self.position.x, self.position.y, 1, 1)  # 기본값, 하위 클래스에서 오버라이드
