import pygame
from typing import TypeVar

T = TypeVar("T", int, float)

def clamp(value: T, min_value: T, max_value: T) -> T:
    """
    주어진 value를 min_value와 max_value 사이로 제한합니다.
    """
    return max(min_value, min(value, max_value))

def lerp(a: float, b: float, t: float) -> float:
    """
    선형 보간 함수 (Linear Interpolation)
    a에서 b까지 t 비율(0~1)로 보간
    """
    return a + (b - a) * t

def distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """
    두 점 (x1, y1), (x2, y2) 간의 유클리드 거리
    """
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def normalize_vector(x: float, y: float) -> tuple[float, float]:
    """
    2D 벡터 정규화
    """
    length = (x + y) ** 0.5
    if length == 0:
        return 0.0, 0.0
    return x / length, y / length

def is_colliding(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
    """
    두 pygame.Rect 객체 간 충돌 여부 확인
    """
    return rect1.colliderect(rect2)
