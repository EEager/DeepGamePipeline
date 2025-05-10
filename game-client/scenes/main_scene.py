 # scenes/main_scene.py

import pygame
from scenes.base_scene import BaseScene
from scenes.game_scene import GameScene
from scenes.scene_manager import SceneManager
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
import os

#FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "D2Coding.ttf")
FONT_PATH = os.path.expanduser("~/.fonts/D2Coding.ttf")

class MainScene(BaseScene):
    def __init__(self):
        self.button_rect = pygame.Rect(SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT//2 - 60, 320, 120)
        self.button_color = (50, 120, 255)
        self.button_hover_color = (80, 160, 255)
        self.font = pygame.font.Font(FONT_PATH, 48)
        self.button_text = self.font.render("게임 시작", True, (255,255,255))
        self.fps_font = pygame.font.Font(FONT_PATH, 24)

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                SceneManager.get_instance().change_scene(GameScene())

    def update(self, delta_time: float) -> None:
        pass

    def render(self, screen: pygame.Surface, fps: int = 0) -> None:
        screen.fill((230, 240, 255))
        mouse_pos = pygame.mouse.get_pos()
        color = self.button_hover_color if self.button_rect.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(screen, color, self.button_rect, border_radius=12)
        text_rect = self.button_text.get_rect(center=self.button_rect.center)
        screen.blit(self.button_text, text_rect)
        # FPS 표시
        fps_text = self.fps_font.render(f"FPS: {fps}", True, (0, 0, 0))
        screen.blit(fps_text, (10, 10))
