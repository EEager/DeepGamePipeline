# game-client/main.py

import pygame
import random
import sys
import json
from kafka import KafkaProducer

# Kafka 설정
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Pygame 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boss Fight Game")

# 색상
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# FPS 설정
clock = pygame.time.Clock()
FPS = 60

# 플레이어 설정
player_width, player_height = 50, 50
player_x, player_y = WIDTH // 2, HEIGHT - player_height - 10
player_speed = 5
player_health = 5

# 보스 설정
boss_width, boss_height = 100, 50
boss_x, boss_y = WIDTH // 2 - boss_width // 2, 50
boss_health = 10

# 총알 설정
player_bullets = []
boss_bullets = []

bullet_width, bullet_height = 5, 10
bullet_speed = 7

# 힐 아이템 설정
heal_items = []

# 게임 상태
running = True
game_over = False

# 이벤트 전송 함수
def send_event(event_type, details=None):
    event = {
        "event_type": event_type,
        "details": details,
    }
    producer.send('game-logs', event)

# 글꼴 설정
font = pygame.font.SysFont(None, 30)

# 게임 루프
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            send_event("game_exit")

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
        send_event("player_move", {"player_id": 1, "x": player_x, "y": player_y})
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed
        send_event("player_move", {"player_id": 1, "x": player_x, "y": player_y})
    if keys[pygame.K_SPACE]:
        player_bullets.append([player_x + player_width // 2, player_y])
        send_event("player_attack", {"player_id": 1, "target_id": 99, "damage": 1})

    # 보스 총알 발사 (랜덤 주기)
    if random.randint(0, 50) == 0:
        boss_bullets.append([boss_x + boss_width // 2, boss_y + boss_height])
        send_event("boss_shoot", {"x": boss_x})

    # 힐 아이템 생성
    if random.randint(0, 500) == 0:
        heal_items.append([random.randint(0, WIDTH-30), 0])

    # 총알 이동
    for bullet in player_bullets[:]:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            player_bullets.remove(bullet)
        # 보스와 충돌 체크
        if (boss_x < bullet[0] < boss_x + boss_width) and (boss_y < bullet[1] < boss_y + boss_height):
            boss_health -= 1
            player_bullets.remove(bullet)
            send_event("boss_hit", {"boss_health": boss_health})
            if boss_health <= 0:
                send_event("victory")
                game_over = True

    for bullet in boss_bullets[:]:
        bullet[1] += bullet_speed
        if bullet[1] > HEIGHT:
            boss_bullets.remove(bullet)
        # 플레이어와 충돌 체크
        if (player_x < bullet[0] < player_x + player_width) and (player_y < bullet[1] < player_y + player_height):
            player_health -= 1
            boss_bullets.remove(bullet)
            send_event("player_hit", {"player_id": 1})
            if player_health <= 0:
                send_event("defeat")
                game_over = True

    for heal in heal_items[:]:
        heal[1] += 3
        if heal[1] > HEIGHT:
            heal_items.remove(heal)
        if (player_x < heal[0] < player_x + player_width) and (player_y < heal[1] < player_y + player_height):
            player_health += 1
            heal_items.remove(heal)
            send_event("player_heal", {"player_id": 1, "heal_amount": 1})

    # 화면 그리기
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_width, player_height))
    pygame.draw.rect(screen, RED, (boss_x, boss_y, boss_width, boss_height))

    for bullet in player_bullets:
        pygame.draw.rect(screen, GREEN, (bullet[0], bullet[1], bullet_width, bullet_height))

    for bullet in boss_bullets:
        pygame.draw.rect(screen, RED, (bullet[0], bullet[1], bullet_width, bullet_height))

    for heal in heal_items:
        pygame.draw.rect(screen, (0, 255, 255), (heal[0], heal[1], 30, 30))

    # 플레이어 체력, 보스 체력 표시
    player_hp_text = font.render(f'Player HP: {player_health}', True, BLACK)
    boss_hp_text = font.render(f'Boss HP: {boss_health}', True, BLACK)
    screen.blit(player_hp_text, (10, 10))
    screen.blit(boss_hp_text, (10, 40))

    pygame.display.update()

    if game_over:
        pygame.time.wait(2000)
        running = False

pygame.quit()
producer.flush()
producer.close()
sys.exit()
