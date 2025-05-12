import pygame
import sys
import os
import logging
from scenes.scene_manager import SceneManager
from scenes.game_scene import GameScene
from scenes.main_scene import MainScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# 개발/운영 환경별 로그 레벨 분기
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level), format='[%(levelname)s] %(asctime)s %(name)s: %(message)s')

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Boss Fight Game")
    clock = pygame.time.Clock()
    
    # 씬 매니저 초기화
    scene_manager = SceneManager.get_instance()
    scene_manager.change_scene(MainScene())

    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0  # 초 단위로 변환
        fps = int(clock.get_fps())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.handle_event(event)

        scene_manager.update(delta_time)
        scene_manager.render(screen, fps)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()