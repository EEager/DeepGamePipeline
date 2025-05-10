# ui_manager.py

import pygame
from typing import Tuple


class UIManager:
    """플레이어 체력바, 장전바, 탄창 등 HUD 관리"""

    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font

    def draw_health_bar(self, surface: pygame.Surface, pos: Tuple[int, int], health: int, max_health: int) -> None:
        x, y = pos
        width, height = 100, 10
        fill = (health / max_health) * width

        # 배경
        pygame.draw.rect(surface, (255, 0, 0), (x, y, width, height))
        # 체력
        pygame.draw.rect(surface, (0, 255, 0), (x, y, fill, height))

    def draw_reload_bar(self, surface: pygame.Surface, pos: Tuple[int, int], reload_ratio: float) -> None:
        x, y = pos
        width, height = 80, 8
        fill = reload_ratio * width

        # 배경
        pygame.draw.rect(surface, (100, 100, 100), (x, y, width, height))
        # 진행도
        pygame.draw.rect(surface, (0, 150, 255), (x, y, fill, height))

    def draw_bullet_icons(self, surface: pygame.Surface, pos: Tuple[int, int], bullets_left: int, max_bullets: int) -> None:
        x, y = pos
        spacing = 15
        bullet_radius = 5

        for i in range(max_bullets):
            color = (0, 0, 0) if i >= bullets_left else (0, 255, 0)
            center = (x + i * spacing, y)
            pygame.draw.circle(surface, color, center, bullet_radius)

    def draw_text(self, surface: pygame.Surface, text: str, pos: Tuple[int, int], color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        img = self.font.render(text, True, color)
        surface.blit(img, pos)
