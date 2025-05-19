"""
게임 서버 설정 파일
"""

# 서버 설정
SERVER_TICK_RATE = 30  # 서버 업데이트 주기 (FPS)
SERVER_TICK_INTERVAL = 1.0 / SERVER_TICK_RATE  # 서버 틱 간격 (초)

# 플레이어 설정
PLAYER_SPEED = 200  # 플레이어 이동 속도 (픽셀/초)
PLAYER_MAX_HEALTH = 100  # 플레이어 최대 체력
PLAYER_INITIAL_HEALTH = 100  # 플레이어 초기 체력
PLAYER_RADIUS = 12  # 플레이어 반지름 (픽셀)

# 총알 설정
BULLET_SPEED = 400  # 총알 속도 (픽셀/초)
BULLET_RADIUS = 4  # 총알 반지름 (픽셀)
BULLET_DAMAGE = 10  # 총알 데미지

# 보스 설정
BOSS_MAX_HEALTH = 1000  # 보스 최대 체력
BOSS_RADIUS = 40  # 보스 반지름 (픽셀)
BOSS_MOVE_SPEED = 100  # 보스 이동 속도 (픽셀/초)
BOSS_ATTACK_RANGE = 200  # 보스 공격 범위 (픽셀)
BOSS_ATTACK_DAMAGE = 20  # 보스 공격 데미지
BOSS_ATTACK_COOLDOWN = 2.0  # 보스 공격 쿨다운 (초)

# 아이템 설정
ITEM_SPAWN_INTERVAL = 10.0  # 아이템 생성 간격 (초)
ITEM_DURATION = 15.0  # 아이템 지속 시간 (초)
ITEM_HEAL_AMOUNT = 30  # 힐링 아이템 회복량
ITEM_SPEED_BOOST = 1.5  # 스피드 부스트 배율
ITEM_SPEED_BOOST_DURATION = 5.0  # 스피드 부스트 지속 시간 (초)

# 게임 화면 설정
SCREEN_WIDTH = 800  # 게임 화면 너비
SCREEN_HEIGHT = 600  # 게임 화면 높이

# 게임 규칙
MIN_PLAYERS_TO_START = 2  # 게임 시작에 필요한 최소 플레이어 수
MAX_PLAYERS = 4  # 최대 플레이어 수
GAME_DURATION = 300  # 게임 지속 시간 (초) 