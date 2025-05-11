import os
import pygame

FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "D2Coding.ttf")

def get_font(size):
    return pygame.font.Font(FONT_PATH, size)
