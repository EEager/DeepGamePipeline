import pygame
from typing import List, Dict
from .ui_button import UIButton

class LobbyPanel:
    def __init__(self, rect, font):
        self.rect = rect
        self.font = font
        self.players: List[Dict] = []  # [{"user": str, "ready": bool}]
        self.server_status = False  # True: Connected, False: Disconnected
        self.ready_button = UIButton(
            pygame.Rect(rect.x + rect.w - 120, rect.y + rect.h - 50, 100, 36),
            "Ready", font,
            color=(0, 180, 0), hover_color=(0, 220, 0)
        )
        self.on_ready = lambda: None
        self.ready_button.on_click = self._on_ready_click

    def _on_ready_click(self):
        self.on_ready()

    def set_players(self, players: List[Dict]):
        self.players = players

    def set_server_status(self, status: bool):
        self.server_status = status

    def handle_event(self, event: pygame.event.Event):
        self.ready_button.handle_event(event)

    def render(self, surface: pygame.Surface):
        # 패널 배경
        pygame.draw.rect(surface, (245, 245, 255), self.rect)
        pygame.draw.rect(surface, (180, 180, 200), self.rect, 2)
        # 서버 상태
        status_text = "서버 연결됨" if self.server_status else "서버 끊김"
        status_color = (0, 200, 0) if self.server_status else (200, 0, 0)
        status_surf = self.font.render(status_text, True, status_color)
        surface.blit(status_surf, (self.rect.x + self.rect.w - status_surf.get_width() - 10, self.rect.y + 10))
        # 참가자 리스트
        y = self.rect.y + 40
        for p in self.players:
            name = p.get("user", "?")
            ready = p.get("ready", False)
            color = (0, 180, 0) if ready else (180, 0, 0)
            name_surf = self.font.render(name, True, (0, 0, 0))
            ready_surf = self.font.render("Ready" if ready else "Not Ready", True, color)
            surface.blit(name_surf, (self.rect.x + 20, y))
            surface.blit(ready_surf, (self.rect.x + 160, y))
            y += 32
        # Ready 버튼
        self.ready_button.render(surface) 