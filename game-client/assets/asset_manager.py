# asset_manager.py

import pygame
from typing import Dict


class AssetManager:
    """이미지, 폰트, 사운드 등 모든 리소스 중앙 관리"""

    def __init__(self) -> None:
        self.images: Dict[str, pygame.Surface] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}

    def load_image(self, name: str, path: str) -> None:
        try:
            image = pygame.image.load(path).convert_alpha()
            self.images[name] = image
        except pygame.error as e:
            print(f"Failed to load image {name}: {e}")

    def get_image(self, name: str) -> pygame.Surface:
        return self.images.get(name)

    def load_font(self, name: str, path: str, size: int) -> None:
        try:
            font = pygame.font.Font(path, size)
            self.fonts[name] = font
        except pygame.error as e:
            print(f"Failed to load font {name}: {e}")

    def get_font(self, name: str) -> pygame.font.Font:
        return self.fonts.get(name)

    def load_sound(self, name: str, path: str) -> None:
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
        except pygame.error as e:
            print(f"Failed to load sound {name}: {e}")

    def get_sound(self, name: str) -> pygame.mixer.Sound:
        return self.sounds.get(name)
