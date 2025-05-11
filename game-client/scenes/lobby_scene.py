import pygame
import threading
import json
import time
import random
from scenes.base_scene import BaseScene
from scenes.scene_manager import SceneManager
from scenes.game_scene import GameScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from objects.ui.chat_box import ChatBox
from objects.ui.lobby_panel import LobbyPanel
from utils.font import get_font
import websocket

class LobbyScene(BaseScene):
    def __init__(self):
        self.font = get_font(24)
        self.nickname = f"user{random.randint(1, 1000)}"
        # 레이아웃 조정
        margin = 32
        panel_width = 320
        main_width = SCREEN_WIDTH - panel_width - margin * 3
        practice_height = int(SCREEN_HEIGHT * 0.52)
        chat_height = SCREEN_HEIGHT - practice_height - margin * 2 + 40
        self.practice_rect = pygame.Rect(margin, margin, main_width, practice_height - 20)
        self.chat_box = ChatBox(pygame.Rect(margin, margin + practice_height - 40, main_width, chat_height), get_font(18))
        self.lobby_panel = LobbyPanel(pygame.Rect(SCREEN_WIDTH - panel_width - margin, margin, panel_width, SCREEN_HEIGHT - margin * 2), self.font)
        self.lobby_panel.on_ready = self.send_ready
        self.server_status = False
        self.players = []
        self.player_colors = {}  # user -> color
        self.practice_players = {}  # user -> {'pos': [x, y], 'dir': [dx, dy], 'ready': bool}
        self.practice_bullets = []  # {'pos': [x, y], 'vel': [vx, vy], 'color': (r,g,b)}
        self.ws = None
        self.ws_thread = None
        self.running = True
        self.last_ping = time.time()
        self.ready = False
        self.connect_ws()
        # 내 연습 플레이어 위치 초기화
        self.practice_players[self.nickname] = {
            'pos': [self.practice_rect.x+self.practice_rect.w//2, self.practice_rect.y+self.practice_rect.h//2],
            'dir': [0,0],
            'ready': False
        }
        self.countdown_value = None
        self.countdown_timer = 0

    def connect_ws(self):
        def run():
            self.ws = websocket.WebSocketApp(
                "ws://localhost:8000/ws/game",
                on_message=self.on_message,
                on_open=self.on_open,
                on_close=self.on_close,
                on_error=self.on_error
            )
            self.ws.run_forever()
        self.ws_thread = threading.Thread(target=run, daemon=True)
        self.ws_thread.start()

    def on_open(self, ws):
        print("[WebSocket] on_open: 연결 성공")
        self.server_status = True
        self.lobby_panel.set_server_status(True)
        # join 메시지 전송
        join_msg = {"type": "join", "user": self.nickname}
        ws.send(json.dumps(join_msg))

    def on_close(self, ws, code, msg):
        print(f"[WebSocket] on_close: code={code}, msg={msg}")
        self.server_status = False
        self.lobby_panel.set_server_status(False)

    def on_error(self, ws, error):
        print(f"[WebSocket] on_error: {error}")
        self.server_status = False
        self.lobby_panel.set_server_status(False)

    def get_player_color(self, user):
        if user not in self.player_colors:
            # 랜덤한 밝은 색상
            self.player_colors[user] = tuple(random.randint(80, 220) for _ in range(3))
        return self.player_colors[user]

    def on_message(self, ws, message):
        print(f"[WebSocket] on_message: {message}")
        data = json.loads(message)
        if data["type"] == "chat":
            color = self.get_player_color(data['user'])
            self.chat_box.add_message((data['user'], data['msg'], color))
        elif data["type"] == "lobby":
            # 서버에서 받은 전체 플레이어 상태로 동기화
            self.players = data["players"]
            for p in self.players:
                user = p["user"]
                if user not in self.practice_players:
                    self.practice_players[user] = {
                        'pos': [p["x"], p["y"]],
                        'dir': [0, 0],
                        'ready': p["ready"]
                    }
                else:
                    self.practice_players[user].update({
                        'pos': [p["x"], p["y"]],
                        'ready': p["ready"]
                    })
                self.get_player_color(user)
            self.lobby_panel.set_players(self.players)
        elif data["type"] == "countdown":
            self.countdown_value = str(data["value"])
            self.countdown_timer = 1.0
        elif data["type"] == "start":
            self.countdown_value = "START"
            self.countdown_timer = 1.0
            self.running = False
            user = self.nickname
            color = self.get_player_color(user)
            bullet_color = color
            SceneManager.get_instance().change_scene(GameScene(user, color, bullet_color))

    def send_ready(self):
        if self.ws and self.server_status:
            msg = {"type": "ready", "user": self.nickname}
            self.ws.send(json.dumps(msg))
            self.ready = True

    def handle_event(self, event: pygame.event.Event) -> None:
        self.chat_box.handle_event(event)
        self.lobby_panel.handle_event(event)
        self.chat_box.on_send = self.send_chat

        # 채팅창이 활성화면 플레이어 조작/총알발사 무시
        if self.chat_box.active:
            return

        # 연습 공간 조작
        if not self.chat_box.active:
            # 마우스 클릭으로 총알 발사
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if self.practice_rect.collidepoint(mx, my):
                    px, py = self.practice_players[self.nickname]['pos']
                    dx, dy = mx - px, my - py
                    dist = max((dx**2 + dy**2) ** 0.5, 1)
                    vx, vy = dx/dist*6, dy/dist*6
                    color = self.get_player_color(self.nickname)
                    self.practice_bullets.append({'pos':[px,py],'vel':[vx,vy],'color':color})

    def send_chat(self, msg):
        if self.ws and self.server_status:
            self.ws.send(json.dumps({"type": "chat", "user": self.nickname, "msg": msg}))

    def update(self, delta_time: float) -> None:
        # 서버 연결 상태 갱신
        self.lobby_panel.set_server_status(self.server_status)
        self.lobby_panel.set_players(self.players)

        # 연습 플레이어 이동
        if not self.chat_box.active:
            keys = pygame.key.get_pressed()
            if keys:
                dx = dy = 0
                if keys[pygame.K_a]: dx -= 1
                if keys[pygame.K_d]: dx += 1
                if keys[pygame.K_w]: dy -= 1
                if keys[pygame.K_s]: dy += 1

                if dx != 0 or dy != 0:
                    # 내 플레이어 위치 갱신
                    me = self.practice_players.get(self.nickname)
                    if me:
                        # 대각선 이동 시 속도 정규화
                        if dx != 0 and dy != 0:
                            dx *= 0.7071  # 1/sqrt(2)
                            dy *= 0.7071
                        
                        new_x = me['pos'][0] + dx * 3
                        new_y = me['pos'][1] + dy * 3
                        
                        # 연습 공간 내에서만 이동
                        new_x = max(self.practice_rect.x+10, min(self.practice_rect.x+self.practice_rect.w-10, new_x))
                        new_y = max(self.practice_rect.y+10, min(self.practice_rect.y+self.practice_rect.h-10, new_y))
                        
                        if self.ws and self.server_status:
                            self.ws.send(json.dumps({
                                "type": "move",
                                "user": self.nickname,
                                "x": new_x,
                                "y": new_y
                            }))

        # 연습 총알 이동
        for b in self.practice_bullets:
            b['pos'][0] += b['vel'][0]
            b['pos'][1] += b['vel'][1]
        # 총알이 연습 공간 밖으로 나가면 삭제
        self.practice_bullets = [b for b in self.practice_bullets if self.practice_rect.collidepoint(b['pos'][0], b['pos'][1])]

        if self.countdown_value:
            self.countdown_timer -= delta_time
            if self.countdown_timer <= 0:
                self.countdown_value = None

    def render(self, screen: pygame.Surface, fps: int = 0) -> None:
        screen.fill((230, 240, 255))
        # 연습 공간
        pygame.draw.rect(screen, (220,230,250), self.practice_rect)
        pygame.draw.rect(screen, (120,120,180), self.practice_rect, 2)
        
        # 연습 플레이어
        for user, p in self.practice_players.items():
            color = self.get_player_color(user)
            pygame.draw.circle(screen, color, (int(p['pos'][0]), int(p['pos'][1])), 12)
            name_surf = get_font(14).render(user, True, color)
            screen.blit(name_surf, (p['pos'][0]-name_surf.get_width()//2, p['pos'][1]-24))
            if p['ready']:
                ready_surf = get_font(12).render("READY", True, (0, 200, 0))
                screen.blit(ready_surf, (p['pos'][0]-ready_surf.get_width()//2, p['pos'][1]+20))
        
        # 연습 총알
        for b in self.practice_bullets:
            pygame.draw.circle(screen, b['color'], (int(b['pos'][0]), int(b['pos'][1])), 5)
        
        # 채팅/패널
        self.lobby_panel.render(screen)
        self.chat_box.render(screen)
        
        # 카운트다운 애니메이션
        if self.countdown_value:
            base_size = 120 if self.countdown_value != "START" else 80
            grow = 1.2 - 0.4 * (1.0 - self.countdown_timer)
            alpha = int(255 * min(1.0, self.countdown_timer + 0.2))
            font = get_font(int(base_size * grow))
            text = self.countdown_value
            text_surf = font.render(text, True, (255, 80, 80))
            text_surf.set_alpha(alpha)
            rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text_surf, rect)

    def on_enter(self):
        print("Entering Lobby Scene")
        pass

    def on_exit(self):
        print("Exiting Lobby Scene")
        pass
