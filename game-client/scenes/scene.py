# scenes/scene.py

import pygame
from abc import ABC, abstractmethod
from typing import Optional

class BaseScene(ABC):
    def __init__(self):
        self.next_scene: Optional[str] = None  # 다음 씬 이름 (없으면 None)

    @abstractmethod
    def update(self, delta_time: float)->None:
        raise NotImplementedError

    @abstractmethod
    def render(self, screen: pygame.Surface)->None:
        raise NotImplementedError

    @abstractmethod
    def enter(self)->None:
        """씬 시작 시 호출"""
        pass
    
    @abstractmethod
    def exit(self)->None:
        """씬 종료 시 호출"""
        pass
    
    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event])->None:
        raise NotImplementedError