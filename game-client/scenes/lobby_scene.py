import pygame
import threading
import json
import time
import random
from scenes.base_scene import BaseScene
from scenes.scene_manager import SceneManager
from scenes.game_scene import GameScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED
from objects.ui.chat_box import ChatBox
from objects.ui.lobby_panel import LobbyPanel
from utils.font import get_font
import websocket
from scenes.multi_game_scene import MultiGameScene
from utils.utils import lerp_pos
import logging
from objects.bullet_pool import BulletPool

class LobbyScene(BaseScene):
    def __init__(self):
        self.font = get_font(24)
        self.nickname = "not_set"
        self.my_color = (120,120,120)  # 기본 색상으로 초기화
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
        self.bullet_pool = BulletPool()
        self.ws = None
        self.ws_thread = None
        self.last_ping = time.time()
        self.ready = False
        self.countdown_value = None
        self.countdown_timer = 0
        self.player_states = {}  # user: {'prev': {'pos': ...}, 'curr': {'pos': ...}, 'last_update_time': ...}
        self.should_transition_to_multi = False  # 멀티게임 씬 전환 플래그
        self.transition_data = None  # 전환에 필요한 데이터 저장
        
        # 스레드 안전성을 위한 락
        self.lock = threading.Lock()
        
        self.connect_ws()

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
        logging.debug("[WebSocket] connect_ws 연결 시작")
        self.ws_thread = threading.Thread(target=run, daemon=True)
        self.ws_thread.start()

    def on_open(self, ws):
        logging.debug("[WebSocket] on_open: 연결 성공")

        # join 메시지 전송
        join_msg = {"type": "join", "user": self.nickname}
        ws.send(json.dumps(join_msg))

    def on_close(self, ws, code, msg):
        logging.debug(f"[WebSocket] on_close: code={code}, msg={msg}")
        self.server_status = False
        self.lobby_panel.set_server_status(False)

    def on_error(self, ws, error):
        logging.debug(f"[WebSocket] on_error: {error}")
        self.server_status = False
        self.lobby_panel.set_server_status(False)

    def on_message(self, ws, message):
        # logging.debug(f"[WebSocket] on_message: {message}")
        data = json.loads(message)
        with self.lock:
            if data["type"] == "chat":
                self.chat_box.add_message((data['user'], data['msg'], data['color']))
            elif data["type"] == "system":
                # [System] 태그와 회색, 굵은 글씨 등으로 표시
                self.chat_box.add_message(("System", data['msg'], (120,120,120)))
                # 입장 메시지면 내 정보 설정
                if "퇴장" in data['msg']:
                    user = data['msg'].split("님이")[0]
                    if user in self.practice_players:
                        self.practice_players.pop(user, None)
                        if user in self.player_states:
                            self.player_states.pop(user, None)
            elif data["type"] == "lobby_start":
                self.nickname = data['nickname']
                self.my_color = tuple(data['color'])
                self.server_status = True
                self.lobby_panel.set_server_status(True)
            elif data["type"] == "lobby":
                tick = data.get("tick", 0)
                
                # 서버에서 받은 전체 플레이어 상태로 동기화
                self.players = data["players"]
                
                # 연결된 플레이어 정보 업데이트
                for p in self.players:
                    user = p["user"]
                    # 보간용 상태 저장
                    state = self.player_states.setdefault(user, {})
                    state['prev'] = state.get('curr', {'pos': [p["x"], p["y"]]})
                    state['curr'] = {'pos': [p["x"], p["y"]]}
                    state['last_update_time'] = time.time()
                    
                    if user not in self.practice_players:
                        self.practice_players[user] = {
                            'pos': [p["x"], p["y"]],
                            'dir': [0, 0],
                            'ready': p["ready"],
                            'color': tuple(p["color"])  # 서버에서 받은 색상 저장
                        }
                    else:
                        self.practice_players[user].update({
                            'pos': [p["x"], p["y"]],
                            'ready': p["ready"],
                        })
                # 서버에서 받은 총알 정보로 동기화
                self.bullet_pool.update_from_server(data.get("bullets", []))
                self.lobby_panel.set_players(self.players)
            elif data["type"] == "countdown": #서버에서 보내는걸 수신만)
                self.countdown_value = str(data["value"])
                self.countdown_timer = 1.0
            elif data["type"] == "countdown_end": #서버 준비 수신하고 준비되면 ready_multigame 전송
                logging.debug(f"[LobbyScene] 멀티게임 준비 완료 - {self.nickname}")
                
                self.countdown_value = "START"
                self.countdown_timer = 1.0
                # --- 멀티게임씬으로 전환 준비 ---
                
                
                # color = tuple(self.players[self.nickname]['color'])
                # msg = {"type": "ready_multigame", "user": self.nickname, "color": color}
                # ws.send(json.dumps(msg))
                # # 전환 플래그와 데이터 설정
                # self.should_transition_to_multi = True
                # self.transition_data = (self.ws, self.ws_thread, self.nickname, color)
                
                # 현재 플레이어의 정보 찾기
                current_player = next((p for p in self.players if p["user"] == self.nickname), None)
                if current_player:
                    color = tuple(current_player["color"])
                    msg = {"type": "ready_multigame", "user": self.nickname, "color": color}
                    ws.send(json.dumps(msg))
                    # 전환 플래그와 데이터 설정
                    self.should_transition_to_multi = True
                    self.transition_data = (self.ws, self.ws_thread, self.nickname, color)
                else:
                    logging.error(f"[LobbyScene] Player {self.nickname} not found in players list")

    def send_ready(self):
        if self.ws and self.server_status:
            msg = {"type": "ready", "user": self.nickname}
            self.ws.send(json.dumps(msg))
            self.ready = True

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.server_status == False:
            return
        self.chat_box.handle_event(event)
        self.lobby_panel.handle_event(event)
        self.chat_box.on_send = self.send_chat

        # 채팅창이 활성화면 플레이어 조작/총알발사 무시
        if self.chat_box.active:
            return

        # 마우스 클릭으로 총알 발사
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.practice_rect.collidepoint(mx, my): 
                px, py = self.practice_players[self.nickname]['pos']
                dx, dy = mx - px, my - py
                dist = max((dx**2 + dy**2) ** 0.5, 1)
                vx, vy = dx/dist, dy/dist
                color = tuple(self.practice_players[self.nickname]['color'])  # 저장된 색상 사용
                # 서버에 총알 정보 전송
                if self.ws and self.server_status:
                    self.ws.send(json.dumps({
                        "type": "lobby_shoot",
                        "user": self.nickname,
                        "x": px,
                        "y": py,
                        "vx": vx,
                        "vy": vy,
                        "color": color
                    }))

    def send_chat(self, msg):
        if self.ws and self.server_status:
            self.ws.send(json.dumps({"type": "chat", "user": self.nickname, "msg": msg}))

    def update(self, delta_time: float) -> None:
        # 서버 연결 상태 갱신
        if self.server_status == False:
            return
        self.lobby_panel.set_server_status(self.server_status)
        self.lobby_panel.set_players(self.players)

        if self.countdown_value:
            self.countdown_timer -= delta_time
            if self.countdown_timer <= 0:
                self.countdown_value = None
                
        # 멀티게임 씬으로 전환
        if self.should_transition_to_multi and self.transition_data:
            logging.debug(f"[LobbyScene] 멀티게임 씬으로 전환 - {self.nickname}, {self.transition_data}")
            ws, ws_thread, nickname, color = self.transition_data
            SceneManager.get_instance().change_scene(MultiGameScene(ws, ws_thread, nickname, color))
            self.should_transition_to_multi = False
            self.transition_data = None
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

    def render(self, screen: pygame.Surface, fps: int = 0) -> None:
        with self.lock:
            # FPS 표시
            fps_text = self.font.render(f"FPS: {fps}", True, (0, 0, 0))
            screen.blit(fps_text, (10, 10))
            # 연습 공간
            pygame.draw.rect(screen, (220,230,250), self.practice_rect)
            pygame.draw.rect(screen, (120,120,180), self.practice_rect, 2)
            
            # 연습 플레이어 (복사본으로 순회)
            for user, p in list(self.practice_players.items()):
                state = self.player_states.get(user)
                if state and 'prev' in state and 'curr' in state:
                    pos0 = state['prev']['pos']
                    pos1 = state['curr']['pos']
                    dt = 1/30  # 서버 업데이트 주기
                    elapsed = time.time() - state['last_update_time']
                    t = min(max(elapsed / dt, 0), 1)
                    interp_pos = lerp_pos(pos0, pos1, t)
                else:
                    interp_pos = p['pos']
                
                pygame.draw.circle(screen, p['color'], (int(interp_pos[0]), int(interp_pos[1])), 12)
                name_surf = get_font(14).render(user, True, p['color'])
                screen.blit(name_surf, (interp_pos[0]-name_surf.get_width()//2, interp_pos[1]-24))
                if p['ready']:
                    ready_surf = get_font(12).render("READY", True, (0, 200, 0))
                    screen.blit(ready_surf, (interp_pos[0]-ready_surf.get_width()//2, interp_pos[1]+20))
            
            # 연습 총알
            self.bullet_pool.render(screen)
            
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
        logging.debug("Entering Lobby Scene")
        pass

    def on_exit(self):
        logging.debug("Exiting Lobby Scene")
        pass
