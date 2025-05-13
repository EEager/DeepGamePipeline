import pygame
import sys
import os
import logging
import time
import cProfile
import pstats
from scenes.scene_manager import SceneManager
from scenes.game_scene import GameScene
from scenes.main_scene import MainScene
from scenes.lobby_scene import LobbyScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# 개발/운영 환경별 로그 레벨 분기
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level), format='[%(levelname)s] %(asctime)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

def profile_game():
    """게임 실행을 프로파일링하는 함수"""
    logger.info("프로파일링 시작")
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        main()
    except Exception as e:
        logger.error(f"게임 실행 중 오류 발생: {e}")
    finally:
        profiler.disable()
        # 프로파일 결과를 파일로 저장
        profile_path = os.path.join(os.getcwd(), 'game_profile.prof')
        logger.info(f"프로파일 결과 저장 경로: {profile_path}")
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')  # 누적 시간 기준으로 정렬
        stats.dump_stats(profile_path)
        
        # snakeviz로 결과를 시각화하기 위한 명령어 출력
        print("\n프로파일링 결과를 시각화하려면 다음 명령어를 실행하세요:")
        print(f"snakeviz {profile_path}")
        logger.info("프로파일링 완료")

def main() -> None:
    logger.info("게임 시작")
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Boss Fight Game")
    clock = pygame.time.Clock()
    
    # 더블 버퍼링을 위한 버퍼 서피스 생성
    buffer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # 씬 매니저 초기화
    scene_manager = SceneManager.get_instance()
    scene_manager.change_scene(MainScene())
    
    last_time = time.time()
    frame_count = 0
    fps = 0
    
    running = True
    while running:
        current_time = time.time()
        frame_count += 1
        
        # FPS 계산 (1초마다)
        if current_time - last_time >= 1.0:
            fps = frame_count
            frame_count = 0
            last_time = current_time
        
        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.current_scene.handle_event(event)
        
        # 업데이트
        delta_time = clock.tick(60) / 1000.0  # 60 FPS로 제한
        scene_manager.current_scene.update(delta_time)
        
        # 버퍼 초기화
        buffer.fill((230, 240, 255))  # 배경색
        
        # 현재 씬 렌더링 (버퍼에 그리기)
        scene_manager.current_scene.render(buffer, fps)
        
        # 완성된 버퍼를 화면에 복사
        screen.blit(buffer, (0, 0))
        pygame.display.flip()
    
    logger.info("게임 종료")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # 프로파일링 모드 확인
    is_profile = os.getenv("PROFILE", "false").lower() == "true"
    logger.info(f"프로파일링 모드: {is_profile}")
    
    if is_profile:
        profile_game()
    else:
        main()