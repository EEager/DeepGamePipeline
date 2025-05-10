# config/settings.py

# --- Screen settings ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# --- Colors (R, G, B) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# --- Player settings ---
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30
PLAYER_SPEED = 100
PLAYER_MAX_HEALTH = 5
PLAYER_MAX_BULLETS = 3
PLAYER_RELOAD_TIME = 1.5  # seconds

# --- Boss settings ---
BOSS_RADIUS = 50
BOSS_MAX_HEALTH = 20
BOSS_SHOOT_INTERVAL = (10, 33)  # frame 단위 (랜덤)
BOSS_HOMING_SHOOT_INTERVAL = (40, 67)
BOSS_SPEED = 3

# --- Bullet settings ---
PLAYER_BULLET_SPEED = 200
BOSS_BULLET_SPEED = 36
HOMING_BULLET_SPEED = 60

# --- Heal Item settings ---
HEAL_ITEM_SPEED = 50
HEAL_ITEM_SPAWN_INTERVAL = 3  # seconds
HEAL_ITEM_MAX_COUNT = 2

# --- Kafka settings ---
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
KAFKA_TOPIC = 'game-logs'
