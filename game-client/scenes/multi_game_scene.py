import pygame
from scenes.base_scene import BaseScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
import json
import queue
from utils.font import get_font
import os
import logging

class MultiGameScene(BaseScene):
    def __init__(self, ws, user, color):
        self.ws = ws  # WebSocketApp 인스턴스
        self.user = user
        self.color = color
        self.players = {}
        self.bullets = {}
        self.boss = None
        self.items = {}
        self.state_queue = queue.Queue()
        self.system_queue = queue.Queue()
        self.running = True
        self.font = get_font(36)
        self.cursor = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(self.cursor, (255, 0, 0, 128), (12, 12), 10, 2)
        pygame.draw.line(self.cursor, (255, 0, 0), (12, 2), (12, 22), 2)
        pygame.draw.line(self.cursor, (255, 0, 0), (2, 12), (22, 12), 2)
        # WebSocketApp 콜백 등록
        self.ws.on_message = self.on_message
        # 채팅박스 등 추가 가능
        # self.chat_box = ...

    def on_message(self, ws, message):
        data = json.loads(message)
        if data.get('type') == 'state':
            self.state_queue.put(data)
        elif data.get('type') == 'system':
            self.system_queue.put(data['msg'])

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_d]: dx += 1
            if keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_s]: dy += 1
            msg = {"type": "input", "user": self.user, "input": {"dx": dx, "dy": dy}}
            self.ws.send(json.dumps(msg))

    def update(self, delta_time: float) -> None:
        # 서버에서 온 최신 상태를 큐에서 꺼내 반영
        while not self.state_queue.empty():
            data = self.state_queue.get()
            # 서버에서 받은 정보로만 완전히 덮어씀 (잔상/색상 꼬임 방지)
            self.players = {p['id']: p for p in data.get('players', [])}
            self.bullets = {b['id']: b for b in data.get('bullets', [])}
            self.boss = data.get('boss')
            self.items = {i: item for i, item in enumerate(data.get('items', []))}
        # system 메시지 처리 예시 (채팅창 등)
        while not self.system_queue.empty():
            msg = self.system_queue.get()
            logging.debug(msg)  # 또는 self.chat_box.add_message(msg)

    def render(self, screen: pygame.Surface, fps: int = 0) -> None:
        screen.fill((255, 255, 255))
        # FPS 표시
        font = get_font(24)
        fps_text = font.render(f"FPS: {fps}", True, (0, 0, 0))
        screen.blit(fps_text, (10, 10))
        # 플레이어 렌더링
        for p in self.players.values():
            color = tuple(p.get('color', (0,0,255)))
            center = (int(p['x']), int(p['y']))
            pygame.draw.circle(screen, color, center, 16)
            name_surf = pygame.font.Font(None, 18).render(p['nickname'], True, color)
            screen.blit(name_surf, (center[0] - name_surf.get_width() // 2, center[1] - 32))
        # 보스 렌더링
        if self.boss:
            color = (255, 0, 0)
            center = (int(self.boss['x']), int(self.boss['y']))
            pygame.draw.circle(screen, color, center, self.boss.get('radius', 32))
        # 총알 렌더링
        for b in self.bullets.values():
            pygame.draw.circle(screen, (200, 180, 0), (int(b['x']), int(b['y'])), 5)
        # 아이템 렌더링
        for item in self.items.values():
            pygame.draw.circle(screen, (0,255,0), (int(item['x']), int(item['y'])), 10)
        # 커서 그리기
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(self.cursor, (mouse_pos[0] - 10, mouse_pos[1] - 10))

    def on_enter(self):
        logging.debug("multi_game_scene on_enter")
        pass
    def on_exit(self):
        logging.debug("multi_game_scene on_exit")
        self.running = False 