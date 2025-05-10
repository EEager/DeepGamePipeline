# sound_manager.py

import pygame
from typing import Dict


class SoundManager:
    """효과음 로딩 및 재생을 담당하는 매니저"""

    def __init__(self) -> None:
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        pygame.mixer.init()

    def load_sound(self, name: str, path: str) -> None:
        """효과음 파일을 로드해서 저장"""
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
        except pygame.error as e:
            print(f"Failed to load sound {name}: {e}")

    def play(self, name: str) -> None:
        """지정한 이름의 효과음 재생"""
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def stop(self, name: str) -> None:
        """지정한 이름의 효과음 중지"""
        sound = self.sounds.get(name)
        if sound:
            sound.stop()

    def set_volume(self, name: str, volume: float) -> None:
        """효과음 볼륨 설정 (0.0 ~ 1.0)"""
        sound = self.sounds.get(name)
        if sound:
            sound.set_volume(volume)
