# particle_effect.py

import pygame
import random
import math
from typing import List


class Particle:
    """단일 파티클"""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.radius = random.randint(2, 5)
        self.color = (255, random.randint(100, 150), random.randint(100, 150))

        angle = random.uniform(0, 2 * 3.1415)
        speed = random.uniform(2, 5)
        self.dx = speed * math.cos(angle)
        self.dy = speed * math.sin(angle)

        self.lifetime = random.uniform(0.5, 1.0)  # 초 단위
        self.created_time = pygame.time.get_ticks()

    def update(self) -> None:
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def is_expired(self) -> bool:
        current_time = pygame.time.get_ticks()
        return (current_time - self.created_time) > (self.lifetime * 1000)


class ParticleEffectManager:
    """파티클 이펙트 전체 관리"""

    def __init__(self) -> None:
        self.particles: List[Particle] = []

    def spawn_effect(self, x: float, y: float, count: int = 15) -> None:
        for _ in range(count):
            particle = Particle(x, y)
            self.particles.append(particle)

    def update(self) -> None:
        for particle in self.particles:
            particle.update()

        self.particles = [p for p in self.particles if not p.is_expired()]

    def draw(self, screen: pygame.Surface) -> None:
        for particle in self.particles:
            particle.draw(screen)
