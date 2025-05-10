# managers/scene_manager.py

from typing import Optional, Self
from scenes.base_scene import BaseScene

class SceneManager:
    _instance: Self | None = None

    def __new__(cls):
        raise RuntimeError("Use SceneManager.get_instance() instead.")

    @classmethod
    def get_instance(cls) -> Self:
        if cls._instance is None:
            instance = super().__new__(cls)
            instance.__init__()  
            cls._instance = instance
        return cls._instance
    
    def __init__(self) -> None:
        self.current_scene: Optional[BaseScene] = None

    def change_scene(self, new_scene: BaseScene) -> None:
        if self.current_scene:
            self.current_scene.on_exit()
        self.current_scene = new_scene
        self.current_scene.on_enter()

    def handle_event(self, event) -> None:
        if self.current_scene:
            self.current_scene.handle_event(event)

    def update(self, delta_time: float) -> None:
        if self.current_scene:
            self.current_scene.update(delta_time)

    def render(self, screen, fps=0) -> None:
        if self.current_scene:
            self.current_scene.render(screen, fps)



