# scenes/main_scene.py

import pygame
from scenes.base_scene import BaseScene
from scenes.game_scene import GameScene
from scenes.scene_manager import SceneManager
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
import os
from scenes.lobby_scene import LobbyScene
from objects.ui.ui_button import UIButton
from utils.font import get_font

#FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "D2Coding.ttf")
FONT_PATH = os.path.expanduser("~/.fonts/D2Coding.ttf")

class MainScene(BaseScene):
    def __init__(self):
        self.font = get_font(48)
        self.fps_font = get_font(24)
        # 싱글/멀티 버튼
        lenX = 480
        lenY = 80
        centerX = SCREEN_WIDTH//2 - lenX//2
        centerY = SCREEN_HEIGHT//2 - lenY//2 - 100
        self.single_btn = UIButton(
            pygame.Rect(centerX, centerY, lenX, lenY),
            "게임 시작(싱글)", self.font
        )
        self.multi_btn = UIButton(
            pygame.Rect(centerX, centerY + lenY*2, lenX, lenY),
            "게임 시작(멀티)", self.font
        )
        self.single_btn.on_click = self.start_single
        self.multi_btn.on_click = self.start_multi

    def start_single(self):
        user = "player"
        color = (0,0,255)
        bullet_color = color
        SceneManager.get_instance().change_scene(GameScene(user, color, bullet_color))

    def start_multi(self):
        SceneManager.get_instance().change_scene(LobbyScene())

    def handle_event(self, event: pygame.event.Event) -> None:
        self.single_btn.handle_event(event)
        self.multi_btn.handle_event(event)

    def update(self, delta_time: float) -> None:
        pass

    def render(self, screen: pygame.Surface, fps: int = 0) -> None:
        screen.fill((230, 240, 255))
        self.single_btn.render(screen)
        self.multi_btn.render(screen)
        # FPS 표시
        fps_text = self.fps_font.render(f"FPS: {fps}", True, (0, 0, 0))
        screen.blit(fps_text, (10, 10))

    def on_enter(self):
        print("Entering Main Scene")
        pass

    def on_exit(self):
        print("Exiting Main Scene")
        pass
