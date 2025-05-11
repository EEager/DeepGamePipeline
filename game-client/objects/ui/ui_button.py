import pygame
from typing import Tuple, Callable

class UIButton:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font, 
                 color: Tuple[int, int, int] = (50, 120, 255),
                 hover_color: Tuple[int, int, int] = (80, 160, 255),
                 text_color: Tuple[int, int, int] = (255, 255, 255)):
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.on_click: Callable[[], None] = lambda: None

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.on_click()

    def render(self, surface: pygame.Surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect) 