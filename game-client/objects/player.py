# objects/player.py

import pygame
from pygame.math import Vector2
import time
from typing import List, Tuple, Optional
from objects.base_object import BaseObject
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_MAX_HEALTH, PLAYER_MAX_BULLETS, PLAYER_RELOAD_TIME, PLAYER_BULLET_SPEED
from objects.bullet_pool import BulletPool
from objects.base_player import BasePlayer

class Player(BasePlayer):
    """플레이어 캐릭터"""
    def __init__(self, user, color, position=(0, 0), bullet_color=(255,255,0)):
        super().__init__(user, color, position)
        self.object_type = "player"
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH
        self.color = color
        self.image: Optional[pygame.Surface] = None
        self.bullet_pool = None  # BulletPool 인스턴스는 game_scene에서 설정

        self.bullets: List[Vector2] = []
        self.max_bullets = PLAYER_MAX_BULLETS
        self.current_bullets = self.max_bullets
        self.reload_time = PLAYER_RELOAD_TIME * 1000  # 밀리초 단위
        self.last_shot_time = pygame.time.get_ticks()
        self.is_reloading = False
        
        # 타이머 설정
        self.shoot_timer = 0
        self.reload_timer = 0
        self.shoot_cooldown = 0.5  # 0.5초로 발사 딜레이 증가
        self.reload_cooldown = 1.0  # 1초
        
        # 장전바 설정
        self.reload_bar_width = 40
        self.reload_bar_height = 5
        self.keys: Optional[pygame.key.ScancodeWrapper] = None
        self.bullet_color = bullet_color

        # 총알 아이콘 생성
        self.bullet_icon = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.bullet_icon, self.bullet_color, (4, 4), 3)

        self.hit_effect_timer = 0
        self.hit_effect_duration = 0.2

    def handle_input(self, event) -> None:
        pass  # 이벤트에서 키 상태를 저장하지 않고, update에서 항상 get_pressed() 사용

    def update(self, delta_time: float) -> None:
        self.keys = pygame.key.get_pressed()
        if not self.keys:
            return

        # 이동 처리
        move_direction = Vector2(0, 0)
        if self.keys[pygame.K_a]:
            move_direction.x -= 1
        if self.keys[pygame.K_d]:
            move_direction.x += 1
        if self.keys[pygame.K_w]:
            move_direction.y -= 1
        if self.keys[pygame.K_s]:
            move_direction.y += 1

        if move_direction.length() > 0:
            move_direction = move_direction.normalize()
            self.position += move_direction * self.speed * delta_time

        # 화면 경계 체크
        self.position.x = max(0, min(self.position.x, SCREEN_WIDTH - self.width))
        self.position.y = max(0, min(self.position.y, SCREEN_HEIGHT - self.height))

        # 총알 쿨다운 감소
        self.shoot_timer -= delta_time
        self.reload_timer -= delta_time

        # 마우스 클릭 시 총알 발사
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0] and self.shoot_timer <= 0 and self.current_bullets > 0 and not self.is_reloading:
            mouse_pos = Vector2(pygame.mouse.get_pos())
            direction = (mouse_pos - self.position)
            if direction.length() > 0:
                direction = direction.normalize()
                bullet_id = self.bullet_pool.spawn_bullet(
                    (self.position + Vector2(self.width//2, self.height//2)).x,
                    (self.position + Vector2(self.width//2, self.height//2)).y,
                    direction.x * PLAYER_BULLET_SPEED,
                    direction.y * PLAYER_BULLET_SPEED,
                    self.color,
                    0  # owner_id (0은 플레이어)
                )
                if bullet_id is not None:
                    self.current_bullets -= 1
                    self.shoot_timer = self.shoot_cooldown
                    self.last_shot_time = pygame.time.get_ticks()

        # 재장전 (총알이 없을 때만)
        if self.current_bullets == 0 and not self.is_reloading:
            self.is_reloading = True
            self.reload_timer = self.reload_cooldown
            self.last_shot_time = pygame.time.get_ticks()

        if self.is_reloading and self.reload_timer <= 0:
            self.current_bullets = self.max_bullets
            self.is_reloading = False

        # 피격 이펙트 지속 시간 갱신
        if self.hit_effect_timer > 0:
            self.hit_effect_timer -= delta_time
            if self.hit_effect_timer <= 0:
                self.hit_effect_timer = 0

    def render(self, screen: pygame.Surface) -> None:
        color = (100, 200, 255) if self.hit_effect_timer > 0 else self.color
        center = (int(self.position.x + self.width // 2), int(self.position.y + self.height // 2))
        radius = self.width // 2
        
        # 플레이어 원
        pygame.draw.circle(screen, color, center, radius)
        # 닉네임 표시 (원 위)
        name_surf = pygame.font.Font(None, 18).render(self.user, True, color)
        screen.blit(name_surf, (center[0] - name_surf.get_width() // 2, self.position.y - 24))
        
        # 체력바/장전바 공통 길이
        bar_width = int(self.width * 0.8)
        bar_height = 5
        bar_x = center[0] - bar_width // 2
        bar_y = self.position.y + self.height + 7
        health_ratio = float(self.health) / float(self.max_health)
        
        # 체력바
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height))
        bar_fill = bar_width * health_ratio
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_fill, bar_height))
        
        # 총알 표시 (체력바 아래)
        bullet_y = bar_y + bar_height + 3
        bullet_spacing = 12
        total_bullet_width = bullet_spacing * self.max_bullets
        start_x = center[0] - total_bullet_width // 2
        for i in range(self.current_bullets):
            bullet_x = start_x + i * bullet_spacing
            screen.blit(self.bullet_icon, (bullet_x, bullet_y))
        # 장전바 (체력바와 동일한 길이, 체력바 아래)
        if self.is_reloading:
            now = pygame.time.get_ticks()
            elapsed = min((now - self.last_shot_time) / self.reload_time, 1.0)
            bar_fill = bar_width * elapsed
            reload_bar_y = bullet_y
            pygame.draw.rect(screen, (200, 200, 200), (bar_x, reload_bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 128, 255), (bar_x, reload_bar_y, bar_fill, bar_height))

    def get_rect(self) -> pygame.Rect:  
        return pygame.Rect(self.position.x, self.position.y, self.width, self.height)

    def take_damage(self, damage: int) -> None:
        self.health = max(0, self.health - damage)
        self.hit_effect_timer = self.hit_effect_duration
        if self.health <= 0:
            self.active = False

    def heal(self, amount: int) -> None:
        self.health = min(self.max_health, self.health + amount)

    # 필요시 게임 전용 메서드 추가
