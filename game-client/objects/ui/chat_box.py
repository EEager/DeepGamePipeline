import pygame
from typing import List, Callable, Tuple, Union

class ChatBox:
    def __init__(self, rect, font, max_messages=30):
        self.rect = rect
        self.font = font
        self.max_messages = max_messages
        self.messages: List[Union[str, Tuple[str, str, Tuple[int,int,int]]]] = []
        self.input_text = ""
        self.active = False
        self.on_send: Callable[[str], None] = lambda msg: None

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                text = self.input_text.strip()
                if text:
                    self.on_send(text)
                    if len(self.messages) > self.max_messages:
                        self.messages = self.messages[-self.max_messages:]
                    self.input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
                try:
                    import pyperclip
                    self.input_text += pyperclip.paste()
                except ImportError:
                    pass
            else:
                if event.unicode and event.key != pygame.K_RETURN:
                    self.input_text += event.unicode

    def add_message(self, msg: Union[str, Tuple[str, str, Tuple[int,int,int]]]):
        self.messages.append(msg)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def render(self, surface: pygame.Surface):
        # 출력창
        chat_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h - 30)
        pygame.draw.rect(surface, (240, 240, 240), chat_rect)
        pygame.draw.rect(surface, (180, 180, 180), chat_rect, 2)
        y = chat_rect.bottom - 8
        for msg in reversed(self.messages[-10:]):
            if isinstance(msg, tuple):
                user, text, color = msg
                name_surf = self.font.render(f"[{user}]", True, color)
                text_surf = self.font.render(f" {text}", True, (0,0,0))
                surface.blit(name_surf, (chat_rect.x + 5, y - name_surf.get_height()))
                surface.blit(text_surf, (chat_rect.x + 5 + name_surf.get_width(), y - text_surf.get_height()))
            else:
                text_surf = self.font.render(str(msg), True, (0, 0, 0))
                surface.blit(text_surf, (chat_rect.x + 5, y - text_surf.get_height()))
            y -= self.font.get_height() + 6

        # 입력창
        input_rect = pygame.Rect(self.rect.x, self.rect.bottom - 28, self.rect.w, 28)
        pygame.draw.rect(surface, (255, 255, 255), input_rect)
        pygame.draw.rect(surface, (0, 120, 255) if self.active else (180, 180, 180), input_rect, 2)
        if self.input_text:
            input_surf = self.font.render(self.input_text, True, (0, 0, 0))
            surface.blit(input_surf, (input_rect.x + 5, input_rect.y + 4))
        else:
            placeholder = "현재 환경에서는 영어/숫자만 입력이 가능합니다"
            placeholder_surf = self.font.render(placeholder, True, (180, 180, 180))
            surface.blit(placeholder_surf, (input_rect.x + 5, input_rect.y + 4))