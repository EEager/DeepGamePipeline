import random

class LobbyPlayerState:
    def __init__(self, user, color):
        self.user = user
        self.x = 200 + random.randint(0, 200)
        self.y = 150 + random.randint(0, 100)
        self.ready = False
        self.color = color