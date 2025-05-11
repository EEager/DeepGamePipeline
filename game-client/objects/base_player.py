from objects.base_object import BaseObject
import pygame

class BasePlayer(BaseObject):
    def __init__(self, user, color, position=(0, 0)):
        super().__init__(position)
        self.user = user
        self.color = color
        self.ready = False

    def update(self, x, y, ready=None):
        self.position.x = x
        self.position.y = y
        if ready is not None:
            self.ready = ready

    def render(self, surface, font):
        pygame.draw.circle(surface, self.color, (int(self.position.x), int(self.position.y)), 16)
        name_surf = font.render(self.user, True, self.color)
        surface.blit(name_surf, (self.position.x - name_surf.get_width()//2, self.position.y - 32))
        if self.ready:
            ready_surf = font.render("Ready", True, (0, 180, 0))
            surface.blit(ready_surf, (self.position.x - ready_surf.get_width()//2, self.position.y + 18)) 