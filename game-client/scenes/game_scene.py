# scenes/game_scene.py

import pygame
import random
from scenes.base_scene import BaseScene
from objects.object_manager import ObjectManager
from objects.player import Player
from objects.boss import Boss
from objects.heal_item import HealItem
from objects.bullet import Bullet
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, HEAL_ITEM_SPAWN_INTERVAL
from pygame.math import Vector2
import os
from objects.bullet_pool import BulletPool
import math
from objects.spatial_hash_grid import SpatialHashGrid
from utils.font import get_font
import logging

GRID_SIZE = 100  # 격자 셀 크기

def get_grid_cell(pos):
    return (int(pos.x) // GRID_SIZE, int(pos.y) // GRID_SIZE)

class GameScene(BaseScene):
    def __init__(self, user=None, color=None, bullet_color=None):
        super().__init__()
        self.object_manager = ObjectManager.get_instance()
        self.bullet_pool = BulletPool()
        
        # 폰트 설정
        self.font = get_font(36)
        
        # 플레이어 생성 및 추가
        if user is None:
            user = "player"
        if color is None:
            color = (0,0,255)
        if bullet_color is None:
            bullet_color = color
        player = Player(user, color, Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100), bullet_color)
        self.object_manager.add_object(player, "player")
        
        # 보스 생성 및 추가
        boss = Boss(Vector2(SCREEN_WIDTH // 2, 100))
        self.object_manager.add_object(boss, "boss")
        
        # 게임 상태 변수
        self.game_over = False
        self.game_clear = False
        self.started = False  # 게임 시작 여부
        
        # 힐 아이템 스폰 관련 변수
        self.heal_spawn_timer = 0
        self.heal_spawn_interval = HEAL_ITEM_SPAWN_INTERVAL
        self.max_heal_items = 3
        
        # 커서 생성
        self.cursor = pygame.Surface((24, 24), pygame.SRCALPHA)
        # 반투명 원
        pygame.draw.circle(self.cursor, (255, 0, 0, 128), (12, 12), 10, 2)
        # 십자가 (중앙 기준)
        pygame.draw.line(self.cursor, (255, 0, 0), (12, 2), (12, 22), 2)
        pygame.draw.line(self.cursor, (255, 0, 0), (2, 12), (22, 12), 2)
        self.create_blur_surface()

    def on_enter(self):
        logging.debug("Entering Game Scene")
        pygame.mouse.set_visible(False)

    def on_exit(self) -> None:
        logging.debug("Exiting Game Scene")
        pygame.mouse.set_visible(True)

    def handle_event(self, event: pygame.event.Event) -> None:
        # 게임이 시작되지 않았고, 입력이 들어오면 시작
        if not self.started and (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN):
            self.started = True
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            # 플레이어 이벤트 처리
            for player in self.object_manager.get_objects("player"):
                player.handle_input(event)

    def update(self, delta_time: float) -> None:
        # 보스와 보스 총알은 게임 오버 상태에서도 계속 움직이도록 별도 업데이트
        for boss in self.object_manager.get_objects("boss"):
            boss.update(delta_time)

        # 총알 풀 업데이트
        self.bullet_pool.update(delta_time)

        # 힐 아이템 업데이트 (게임 오버 상태에서도 계속)
        for heal_item in self.object_manager.get_objects("heal_item"):
            heal_item.update(delta_time)

        # 힐 아이템 스폰
        self.heal_spawn_timer += delta_time
        if self.heal_spawn_timer >= self.heal_spawn_interval:
            self.heal_spawn_timer = 0
            self.spawn_heal_item()

        if not self.game_over and not self.game_clear and self.started:
            # 플레이어 업데이트 (게임 시작 후에만)
            for player in self.object_manager.get_objects("player"):
                player.update(delta_time)
            # 충돌 체크
            self.check_collisions()

    def spawn_heal_item(self) -> None:
        # 현재 활성화된 힐 아이템 수 확인
        active_heal_items = len([item for item in self.object_manager.get_objects("heal_item") if item.active])
        if active_heal_items < self.max_heal_items:
            # 랜덤한 x 위치에서 생성
            x = random.randint(50, SCREEN_WIDTH - 50)
            # 화면 위에서 생성 (y=-15로 조정)
            y = -15
            heal_item = HealItem(Vector2(x, y))
            self.object_manager.add_object(heal_item, "heal_item")

    def create_blur_surface(self):
        # 블러 효과를 위한 서피스 생성
        self.blur_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.blur_surface.fill((255, 255, 255))
        self.blur_surface.set_alpha(128)

    def render(self, screen: pygame.Surface, fps: int = 0) -> None:
        screen.fill((255, 255, 255))  # 배경 흰색
        
        # FPS 표시
        font = get_font(24)
        fps_text = font.render(f"FPS: {fps}", True, (0, 0, 0))
        screen.blit(fps_text, (10, 10))
        
        # 모든 오브젝트 렌더링
        self.object_manager.render(screen)
        # 총알 풀 렌더링
        self.bullet_pool.render(screen)

        # 게임 오버/클리어 화면
        if self.game_over or self.game_clear:
            screen.blit(self.blur_surface, (0, 0))
            text = "Game Over" if self.game_over else "Game Clear"
            text_surface = self.font.render(text, True, (255, 0, 0) if self.game_over else (0, 255, 0))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text_surface, text_rect)

        # 커서 그리기
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(self.cursor, (mouse_pos[0] - 10, mouse_pos[1] - 10))

    def get_nearby_bullets(self, obj):
        # obj의 위치 기준 인접 셀(3x3) 내 총알만 반환
        cx, cy = get_grid_cell(obj.position)
        result = []
        for bullet in self.bullet_pool.get_active_bullets():
            bx, by = get_grid_cell(bullet.position)
            if abs(bx - cx) <= 1 and abs(by - cy) <= 1:
                result.append(bullet)
        return result

    def check_collisions(self) -> None:
        # 플레이어와 보스 총알 충돌 체크 (근처 총알만 검사)
        for player in self.object_manager.get_objects("player"):
            for bullet in self.get_nearby_bullets(player):
                if bullet.active and bullet.owner in ("boss", "boss_homing"):
                    if player.get_rect().colliderect(bullet.get_rect()):
                        player.take_damage(bullet.damage)
                        bullet.active = False
                        if player.health <= 0:
                            self.game_over = True

        # 보스와 플레이어 총알 충돌 체크 (근처 총알만 검사)
        for boss in self.object_manager.get_objects("boss"):
            for bullet in self.get_nearby_bullets(boss):
                if bullet.active and bullet.owner == "player":
                    if boss.get_rect().colliderect(bullet.get_rect()):
                        boss.take_damage(bullet.damage)
                        bullet.active = False
                        if boss.health <= 0:
                            self.game_clear = True

        # 플레이어와 힐 아이템 충돌 체크 (힐 아이템이 적으니 전체 순회)
        for player in self.object_manager.get_objects("player"):
            for heal_item in self.object_manager.get_objects("heal_item"):
                if heal_item.active and player.get_rect().colliderect(heal_item.get_rect()):
                    player.heal(heal_item.heal_amount)
                    heal_item.active = False

    def remove_bullet(self, bullet):
        idx = self.active_bullets.index(bullet)
        self.active_bullets[idx] = self.active_bullets[-1]
        self.active_bullets.pop()
