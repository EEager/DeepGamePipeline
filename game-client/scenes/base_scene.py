# scenes/base_scene.py

from abc import ABC, abstractmethod
import pygame

class BaseScene(ABC):
    @abstractmethod
    def on_enter(self) -> None:
        """씬이 시작될 때 호출"""
        pass

    @abstractmethod
    def on_exit(self) -> None:
        """씬이 종료될 때 호출"""
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """이벤트 처리"""
        pass

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """로직 업데이트"""
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface, fps: int = 0) -> None:
        """렌더링"""
        pass
