import pygame
from scenes.base_scene import BaseScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED
import json
import queue
from utils.font import get_font
import os
import logging
import time

class MultiGameScene(BaseScene):
    def __init__(self, ws, ws_thread, user, color):
        self.ws = ws  # WebSocketApp 인스턴스
        self.ws_thread = ws_thread  # 웹소켓 스레드
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
        self.small_font = get_font(24)
        
        # 게임 상태
        self.game_over = False
        self.game_clear = False
        
        # 커서 생성
        self.cursor = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(self.cursor, (255, 0, 0, 128), (12, 12), 10, 2)
        pygame.draw.line(self.cursor, (255, 0, 0), (12, 2), (12, 22), 2)
        pygame.draw.line(self.cursor, (255, 0, 0), (2, 12), (22, 12), 2)
        
        # 블러 효과를 위한 서피스
        self.blur_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.blur_surface.fill((255, 255, 255))
        self.blur_surface.set_alpha(128)
        
        # WebSocketApp 콜백 등록
        self.ws.on_message = self.on_message
        # 채팅박스 등 추가 가능
        # self.chat_box = ...
        
        self.server_is_ready = False

    def on_message(self, ws, message):
        data = json.loads(message)
        
        if data.get('type') == 'start_multigame':
            self.server_is_ready = True
        elif data.get('type') == 'state':
            self.state_queue.put(data)
        elif data.get('type') == 'system':
            self.system_queue.put(data['msg'])
        elif data.get('type') == 'game_over':
            self.game_over = True
        elif data.get('type') == 'game_clear':
            self.game_clear = True

    def handle_event(self, event: pygame.event.Event) -> None:        
        # 마우스 클릭으로 총알 발사
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.game_over and not self.game_clear:
                mx, my = event.pos
                player = self.players.get(self.user)
                if player:
                    px, py = player['x'], player['y']
                    dx, dy = mx - px, my - py
                    dist = max((dx**2 + dy**2) ** 0.5, 1)
                    vx, vy = dx/dist*6, dy/dist*6
                    msg = {
                        "type": "shoot",
                        "user": self.user,
                        "x": px,
                        "y": py,
                        "vx": vx,
                        "vy": vy,
                        "color": self.color
                    }
                    self.ws.send(json.dumps(msg))

    def update(self, delta_time: float) -> None:
        if self.server_is_ready == False:
            return
        
        
         # 플레이어 이동
        keys = pygame.key.get_pressed()
        if keys:
            me = self.practice_players[self.nickname]
            dx = dy = 0
            # logging.debug(f"[lobby_scene] 연습 플레이어 이동 - {self.nickname}: {keys[pygame.K_a]}, {keys[pygame.K_d]}, {keys[pygame.K_w]}, {keys[pygame.K_s]}")
            # 키 입력 처리 개선
            if keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_d]: dx += 1
            if keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_s]: dy += 1
            
            if dx != 0 or dy != 0:
                # 방향 벡터 정규화
                length = (dx*dx + dy*dy) ** 0.5
                dx /= length
                dy /= length
                
                # 정규화된 방향에 스피드 적용
                new_x = me['pos'][0] + dx * PLAYER_SPEED * delta_time
                new_y = me['pos'][1] + dy * PLAYER_SPEED * delta_time
                
                # 연습 공간 내에서만 이동
                new_x = max(self.practice_rect.x+10, min(self.practice_rect.x+self.practice_rect.w-10, new_x))
                new_y = max(self.practice_rect.y+10, min(self.practice_rect.y+self.practice_rect.h-10, new_y))
                
                # logging.debug(f"[lobby_scene] 연습 플레이어 이동 - {self.nickname}: {new_x}, {new_y}")
                if self.ws:
                    self.ws.send(json.dumps({
                        "type": "lobby_move",
                        "user": self.nickname,
                        "x": new_x,
                        "y": new_y
                    }))

        # 웹소켓 메시지 처리
        try:
            while not self.state_queue.empty():
                message = self.state_queue.get_nowait()
                self.handle_websocket_message(message)
        except queue.Empty:
            pass

        try:
            while not self.system_queue.empty():
                message = self.system_queue.get_nowait()
                logging.info(f"[MultiGame] System message: {message}")
        except queue.Empty:
            pass

    def render(self, screen: pygame.Surface, fps: int = 0) -> None:
        screen.fill((255, 255, 255))
        if self.server_is_ready == False:
            return
        
        # FPS 표시
        fps_text = self.small_font.render(f"FPS: {fps}", True, (0, 0, 0))
        screen.blit(fps_text, (10, 10))
        
        # 플레이어 렌더링
        for p in self.players.values():
            color = tuple(p.get('color', (0,0,255)))
            center = (int(p['x']), int(p['y']))
            pygame.draw.circle(screen, color, center, 16)
            
            # 플레이어 이름
            name_surf = self.small_font.render(p['nickname'], True, color)
            screen.blit(name_surf, (center[0] - name_surf.get_width() // 2, center[1] - 32))
            
            # 체력바
            health = p.get('health', 100)
            max_health = p.get('max_health', 100)
            health_width = 40
            health_height = 4
            health_x = center[0] - health_width // 2
            health_y = center[1] + 20
            
            # 배경 (회색)
            pygame.draw.rect(screen, (100, 100, 100), 
                           (health_x, health_y, health_width, health_height))
            # 체력 (빨간색)
            current_health_width = int(health_width * (health / max_health))
            pygame.draw.rect(screen, (255, 0, 0), 
                           (health_x, health_y, current_health_width, health_height))
        
        # 보스 렌더링
        if self.boss:
            color = (255, 0, 0)
            center = (int(self.boss['x']), int(self.boss['y']))
            radius = self.boss.get('radius', 32)
            pygame.draw.circle(screen, color, center, radius)
            
            # 보스 체력바
            health = self.boss.get('health', 1000)
            max_health = self.boss.get('max_health', 1000)
            health_width = 200
            health_height = 10
            health_x = center[0] - health_width // 2
            health_y = center[1] - radius - 20
            
            # 배경 (회색)
            pygame.draw.rect(screen, (100, 100, 100), 
                           (health_x, health_y, health_width, health_height))
            # 체력 (빨간색)
            current_health_width = int(health_width * (health / max_health))
            pygame.draw.rect(screen, (255, 0, 0), 
                           (health_x, health_y, current_health_width, health_height))
        
        # 총알 렌더링
        for b in self.bullets.values():
            color = tuple(b.get('color', (200, 180, 0)))
            pygame.draw.circle(screen, color, (int(b['x']), int(b['y'])), 5)
        
        # 아이템 렌더링
        for item in self.items.values():
            pygame.draw.circle(screen, (0,255,0), (int(item['x']), int(item['y'])), 10)
        
        # 게임 오버/클리어 화면
        if self.game_over or self.game_clear:
            screen.blit(self.blur_surface, (0, 0))
            text = "Game Over" if self.game_over else "Game Clear"
            text_surface = self.font.render(text, True, (255, 0, 0) if self.game_over else (0, 255, 0))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text_surface, text_rect)
        
        # 커서 그리기
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(self.cursor, (mouse_pos[0] - 12, mouse_pos[1] - 12))

    def on_enter(self):
        logging.debug("Entering Multi Game Scene")
        pygame.mouse.set_visible(False)

    def on_exit(self):
        """씬 종료 시 정리"""
        logging.debug("Exiting Multi Game Scene")
        pygame.mouse.set_visible(True)
        self.running = False 

    def handle_websocket_message(self, message):
        """웹소켓 메시지 처리"""
        if message["type"] == "state":
            # 플레이어 상태 업데이트
            for player_data in message["players"]:
                user = player_data["id"]
                if user != self.user:
                    if user not in self.other_players:
                        self.other_players[user] = {
                            'x': player_data["x"],
                            'y': player_data["y"],
                            'health': player_data["health"],
                            'max_health': player_data["max_health"],
                            'color': player_data["color"],
                            'nickname': player_data["nickname"]
                        }
                    else:
                        self.other_players[user].update({
                            'x': player_data["x"],
                            'y': player_data["y"],
                            'health': player_data["health"],
                            'max_health': player_data["max_health"]
                        })
            
            # 보스 상태 업데이트
            if message.get("boss"):
                self.boss = message["boss"]
            
            # 아이템 상태 업데이트
            self.items = {
                item["id"]: {
                    'x': item["x"],
                    'y': item["y"],
                    'type': item["type"]
                }
                for item in message["items"]
            }
            
            # 총알 상태 업데이트
            for bullet_data in message["bullets"]:
                bullet_id = bullet_data["id"]
                if bullet_id not in self.bullets:
                    self.bullets[bullet_id] = {
                        'x': bullet_data["x"],
                        'y': bullet_data["y"],
                        'vx': bullet_data["vx"],
                        'vy': bullet_data["vy"],
                        'owner': bullet_data["owner"],
                        'color': bullet_data["color"],
                        'last_update': time.time()
                    }
                else:
                    self.bullets[bullet_id].update({
                        'x': bullet_data["x"],
                        'y': bullet_data["y"],
                        'vx': bullet_data["vx"],
                        'vy': bullet_data["vy"],
                        'last_update': time.time()
                    })
            
            # 화면 밖 총알 제거
            self.bullets = {
                bid: b for bid, b in self.bullets.items()
                if 0 <= b['x'] <= SCREEN_WIDTH and 0 <= b['y'] <= SCREEN_HEIGHT
            }
        
        elif message["type"] == "game_over":
            self.game_over = True
            self.game_clear = False
        
        elif message["type"] == "game_clear":
            self.game_over = True
            self.game_clear = True

    def start_game(self):
        """게임 시작"""
        self.game_over = False
        self.game_clear = False
        self.bullets = {}
        self.items = {}
        self.boss = None
        self.other_players = {}
        
        # 서버에 게임 시작 메시지 전송
        self.ws.send_json({
            "type": "multigame_ready",
            "user": self.user,
            "color": self.color
        }) 