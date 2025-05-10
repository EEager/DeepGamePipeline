import pygame
import sys
from scenes.scene_manager import SceneManager
from scenes.game_scene import GameScene
from scenes.main_scene import MainScene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

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